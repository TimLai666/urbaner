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


def detect_language(text: str) -> str:
    if not isinstance(text, str):
        return "en"
    ja_chars = sum(1 for c in text if "\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff")
    return "ja" if ja_chars > 5 else "en"


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


def extract_brand_from_title(title: str) -> str:
    title = str(title).strip()
    if not title:
        return "Competitor"
    first_token = re.split(r"[\s\-–—]", title, maxsplit=1)[0].strip()
    return first_token or "Competitor"


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


def hit_to_score(hits: int) -> int | None:
    if hits <= 0:
        return None
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


def load_research_reviews(folder: Path) -> list[dict[str, object]]:
    review_rows: list[dict[str, object]] = []

    for path in sorted(folder.glob("**/*.txt")):
        if path.name.lower() == "own_asins.txt":
            continue

        category_code = ""
        market = ""
        current_asin = ""
        current_title = ""

        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue

                category_match = re.match(r"^CATEGORY:\s*(.+?)\s*\((JP|US)\)\s*$", line)
                if category_match:
                    category_code = category_match.group(1).strip()
                    market = category_match.group(2).strip()
                    continue

                section_match = re.match(r"^###\s+([A-Z0-9]+)\s+-\s+(.+?)\s+\((\d+)\)\s*$", line)
                if section_match:
                    current_asin = section_match.group(1).strip()
                    current_title = section_match.group(2).strip()
                    continue

                if line.startswith("-") or line.startswith("=") or line.startswith("###"):
                    continue

                if "|" not in line or not current_asin:
                    continue

                parts = line.split("|", 2)
                if len(parts) != 3:
                    continue

                rating_text, review_date, review_text = parts
                review_rows.append(
                    {
                        "source": "research",
                        "source_file": path.relative_to(BASE_DIR).as_posix(),
                        "category_code": category_code,
                        "market": market,
                        "asin": current_asin,
                        "brand": extract_brand_from_title(current_title),
                        "title": "",
                        "review_text": review_text.strip(),
                        "rating": rating_text.strip(),
                        "review_date": review_date.strip(),
                    }
                )

    return review_rows


def build_strength_df(scores_df: pd.DataFrame, attr_cols: list[str]) -> pd.DataFrame:
    strength_rows: list[dict[str, object]] = []

    for product, grp in scores_df.groupby("product"):
        row: dict[str, object] = {"product": product}
        for attr_col in attr_cols:
            series = grp[attr_col]
            # Stage 2 uses only Stage-1 scored reviews (non-NA) for each attribute.
            if series.notna().any():
                row[f"{attr_col}_strength"] = round(float(series.mean(skipna=True)), 2)
            else:
                row[f"{attr_col}_strength"] = pd.NA
        strength_rows.append(row)

    return pd.DataFrame(strength_rows)


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

    raw_review_rows: list[dict[str, object]] = []
    product_reviews = load_three_products(REVIEW_DIR)

    for product_id, df in product_reviews.items():
        text_col = pick_text_col(df)
        title_col = pick_title_col(df)

        for _, row in df.reset_index(drop=True).iterrows():
            content = "" if pd.isna(row.get(text_col)) else str(row.get(text_col))
            title = ""
            if title_col is not None and not pd.isna(row.get(title_col)):
                title = str(row.get(title_col))

            raw_review_rows.append(
                {
                    "source": "rawdata",
                    "source_file": f"rawdata_Urbaner/amazon_reviews/001_Beard_Mustache_Trimmers/{product_id}.xlsx",
                    "category_code": "001_Beard_Mustache_Trimmers",
                    "market": "JP",
                    "asin": product_id,
                    "brand": product_id,
                    "title": title,
                    "review_text": content,
                    "rating": row.get("星级", row.get("rating", pd.NA)),
                    "review_date": row.get("评论时间", row.get("review_date", pd.NA)),
                }
            )

    combined_rows = raw_review_rows + load_research_reviews(BASE_DIR / "research")
    combined_df = pd.DataFrame(combined_rows)
    if combined_df.empty:
        raise ValueError("沒有可用的評論資料")

    combined_df["review_text"] = combined_df["review_text"].fillna("").astype(str)
    combined_df["title"] = combined_df["title"].fillna("").astype(str)
    combined_df["combined_text"] = combined_df["title"].str.strip() + " " + combined_df["review_text"]
    combined_df["combined_text"] = combined_df["combined_text"].str.strip()
    combined_df["rating"] = pd.to_numeric(combined_df["rating"], errors="coerce").fillna(3)
    combined_df["lang"] = combined_df["combined_text"].apply(detect_language)
    combined_df["review_id"] = [f"R{i + 1:05d}" for i in range(len(combined_df))]
    combined_df["unit_id"] = combined_df["review_id"]
    combined_df["product"] = combined_df["asin"].astype(str)

    score_rows: list[dict[str, object]] = []
    for _, row in combined_df.iterrows():
        text = norm_text(str(row["combined_text"]))
        if len(text) < 8:
            continue

        scored = {
            "source": row["source"],
            "source_file": row["source_file"],
            "category_code": row["category_code"],
            "market": row["market"],
            "product": row["product"],
            "asin": row["asin"],
            "review_id": row["review_id"],
            "unit_id": row["unit_id"],
            "brand": row["brand"],
            "title": row["title"],
            "review_text": row["review_text"],
            "rating": row["rating"],
            "review_date": row["review_date"],
            "lang": row["lang"],
        }

        for attr in attr_rows:
            hits = keyword_hit_count(text, attr["keywords"])
            scored[attr["attribute_key"]] = hit_to_score(hits)

        score_rows.append(scored)

    scores_df = pd.DataFrame(score_rows)
    attr_cols = [a["attribute_key"] for a in attr_rows]

    scores_df[attr_cols] = scores_df[attr_cols].apply(pd.to_numeric, errors="coerce")

    summary_df = (
        scores_df.groupby("product", as_index=False)[attr_cols]
        .mean(numeric_only=True)
        .round(2)
    )

    mention_df = (
        scores_df.groupby("product", as_index=False)[attr_cols]
        .agg(lambda x: x.gt(0).fillna(False).mean())
        .round(4)
    )
    mention_df = mention_df.rename(columns={c: f"{c}_mention_rate" for c in attr_cols})

    strength_df = build_strength_df(scores_df, attr_cols)

    product_count = scores_df.groupby("product", as_index=False).size().rename(columns={"size": "review_count"})

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        scores_df.to_excel(writer, index=False, sheet_name="review_scores")
        summary_df.to_excel(writer, index=False, sheet_name="product_avg_scores")
        mention_df.to_excel(writer, index=False, sheet_name="product_mention_rate")
        strength_df.to_excel(writer, index=False, sheet_name="product_strength_scores")
        product_count.to_excel(writer, index=False, sheet_name="meta")

    print(f"輸出完成：{OUTPUT_XLSX}")
    print("產品評論數：")
    print(product_count.to_string(index=False))


if __name__ == "__main__":
    main()