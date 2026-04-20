from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "attribute_catalog.csv"
REVIEW_DIR = BASE_DIR / "rawdata_Urbaner" / "amazon_reviews" / "001_Beard_Mustache_Trimmers"
OUTPUT_XLSX = BASE_DIR / "review_attribute_scores.xlsx"


EN_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "have",
    "has",
    "are",
    "was",
    "were",
    "when",
    "what",
    "where",
    "which",
    "into",
    "while",
    "about",
    "after",
    "before",
    "over",
    "under",
    "only",
    "very",
    "more",
    "most",
    "less",
    "also",
    "well",
    "than",
    "then",
    "through",
    "your",
    "their",
    "they",
    "them",
    "you",
    "its",
    "just",
    "good",
    "great",
    "easy",
    "overall",
    "product",
    "function",
    "feature",
    "quality",
    "design",
    "using",
    "use",
    "used",
}


def norm_text(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def pick_text_col(df: pd.DataFrame) -> str:
    for col in ["內容", "内容", "content", "review", "body", "text"]:
        if col in df.columns:
            return col
    raise ValueError(f"找不到評論文字欄位，現有欄位：{list(df.columns)}")


def pick_title_col(df: pd.DataFrame) -> str | None:
    for col in ["標題", "标题", "title", "subject"]:
        if col in df.columns:
            return col
    return None


def extract_keywords(row: pd.Series) -> list[str]:
    candidates: list[str] = []

    key = str(row.get("attribute_key", "")).strip().lower()
    label = str(row.get("label", "")).strip().lower()
    label_zh = str(row.get("label_zh", "")).strip()
    definition = str(row.get("definition", "")).strip().lower()

    if key:
        candidates.extend(key.split("_"))
        candidates.append(key.replace("_", " "))

    if label:
        candidates.append(label)
        candidates.extend(re.findall(r"[a-z][a-z0-9\-]{2,}", label))

    if definition:
        candidates.extend(re.findall(r"[a-z][a-z0-9\-]{3,}", definition))

    if label_zh:
        candidates.append(label_zh)

    cleaned: list[str] = []
    for kw in candidates:
        kw = kw.strip().lower()
        if not kw:
            continue
        if kw in EN_STOPWORDS:
            continue
        if len(kw) <= 2 and kw.isascii():
            continue
        cleaned.append(kw)

    seen = set()
    result = []
    for kw in cleaned:
        if kw not in seen:
            seen.add(kw)
            result.append(kw)
    return result


def keyword_hit_count(text: str, keywords: list[str]) -> int:
    hits = 0
    for kw in keywords:
        if not kw:
            continue
        if any(ord(ch) > 127 for ch in kw):
            if kw in text:
                hits += 1
            continue

        if " " in kw or "-" in kw:
            if kw in text:
                hits += 1
            continue

        if re.search(rf"\b{re.escape(kw)}\b", text):
            hits += 1
    return hits


def hit_to_score(hits: int) -> int:
    if hits <= 0:
        return 0
    if hits == 1:
        return 2
    if hits == 2:
        return 4
    if hits == 3:
        return 5
    if hits <= 5:
        return 6
    return 7


def load_three_products(folder: Path) -> dict[str, pd.DataFrame]:
    files = sorted(folder.glob("*.xlsx"))[:3]
    if len(files) < 3:
        raise ValueError(f"{folder} 底下不到 3 個產品檔案")

    out: dict[str, pd.DataFrame] = {}
    for path in files:
        df = pd.read_excel(path, sheet_name=0)
        out[path.stem] = df
    return out


def main() -> None:
    attrs = pd.read_csv(CATALOG_PATH)
    attrs = attrs.fillna("")

    attr_rows = []
    for _, row in attrs.iterrows():
        key = str(row["attribute_key"]).strip()
        if not key:
            continue
        attr_rows.append(
            {
                "attribute_key": key,
                "label": str(row.get("label", "")).strip(),
                "label_zh": str(row.get("label_zh", "")).strip(),
                "keywords": extract_keywords(row),
            }
        )

    product_reviews = load_three_products(REVIEW_DIR)

    score_rows: list[dict[str, object]] = []
    for product_id, df in product_reviews.items():
        text_col = pick_text_col(df)
        title_col = pick_title_col(df)

        for i, row in df.reset_index(drop=True).iterrows():
            content = "" if pd.isna(row.get(text_col)) else str(row.get(text_col))
            title = ""
            if title_col is not None and not pd.isna(row.get(title_col)):
                title = str(row.get(title_col))

            text = norm_text(f"{title} {content}")
            if len(text) < 8:
                continue

            scored = {
                "product": product_id,
                "review_id": f"{product_id}_{i + 1}",
                "title": title,
                "review_text": content,
            }

            for attr in attr_rows:
                hits = keyword_hit_count(text, attr["keywords"])
                scored[attr["attribute_key"]] = hit_to_score(hits)

            score_rows.append(scored)

    scores_df = pd.DataFrame(score_rows)
    attr_cols = [a["attribute_key"] for a in attr_rows]

    summary_df = (
        scores_df.groupby("product", as_index=False)[attr_cols]
        .mean(numeric_only=True)
        .round(2)
    )

    mention_df = (
        scores_df.groupby("product", as_index=False)[attr_cols]
        .apply(lambda x: (x > 0).mean())
        .round(4)
    )
    mention_df = mention_df.rename(columns={c: f"{c}_mention_rate" for c in attr_cols})

    product_count = scores_df.groupby("product", as_index=False).size().rename(columns={"size": "review_count"})

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        scores_df.to_excel(writer, index=False, sheet_name="review_scores")
        summary_df.to_excel(writer, index=False, sheet_name="product_avg_scores")
        mention_df.to_excel(writer, index=False, sheet_name="product_mention_rate")
        product_count.to_excel(writer, index=False, sheet_name="meta")

    print(f"輸出完成：{OUTPUT_XLSX}")
    print("產品評論數：")
    print(product_count.to_string(index=False))


if __name__ == "__main__":
    main()