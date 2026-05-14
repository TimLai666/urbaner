"""逐一檢查 84 個自稱「自家」ASIN 的評論，找出品牌污染。
規則：
  - 若評論內容多次提到 urbaner / ウルバナー → 確認 URBANER
  - 若評論多次提到其他特定品牌（ufree, panasonic, braun, philips, manscaped,
    wahl, andis 等）→ 標記為疑似污染
  - 若評論裡兩種都沒有 → 中性（無法直接判斷，附評論數）
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
RAW = ROOT / "rawdata_Urbaner" / "amazon_reviews"

URBANER_PATTERNS = re.compile(r"urbaner|ｕｒｂａｎｅｒ|ウルバナー|奧本|奥本", re.IGNORECASE)
COMPETITOR_BRANDS = {
    "ufree": re.compile(r"\bufree\b", re.IGNORECASE),
    "panasonic": re.compile(r"\bpanasonic|パナソニック", re.IGNORECASE),
    "braun": re.compile(r"\bbraun|ブラウン", re.IGNORECASE),
    "philips": re.compile(r"\bphilips|フィリップス|ノレルコ|norelco", re.IGNORECASE),
    "manscaped": re.compile(r"\bmanscaped", re.IGNORECASE),
    "wahl": re.compile(r"\bwahl", re.IGNORECASE),
    "andis": re.compile(r"\bandis", re.IGNORECASE),
    "remington": re.compile(r"\bremington", re.IGNORECASE),
    "conair": re.compile(r"\bconair", re.IGNORECASE),
    "hatteker": re.compile(r"\bhatteker", re.IGNORECASE),
    "kemei": re.compile(r"\bkemei|科美", re.IGNORECASE),
    "izumi": re.compile(r"\bizumi|イズミ", re.IGNORECASE),
    "hitachi": re.compile(r"\bhitachi|日立", re.IGNORECASE),
    "maxell": re.compile(r"\bmaxell|マクセル", re.IGNORECASE),
    "babyliss": re.compile(r"\bbabyliss", re.IGNORECASE),
    "casfuy": re.compile(r"\bcasfuy", re.IGNORECASE),
}

results = []
for category_dir in sorted(RAW.iterdir()):
    if not category_dir.is_dir():
        continue
    for xlsx in sorted(category_dir.glob("*.xlsx")):
        asin = xlsx.stem
        try:
            df = pd.read_excel(xlsx)
        except Exception as e:
            results.append({"asin": asin, "category": category_dir.name, "error": str(e)})
            continue

        contents = df["内容"].fillna("").astype(str)
        titles = df["标题"].fillna("").astype(str)
        all_text = (contents + " " + titles).str.cat(sep=" ")

        urbaner_hits = len(URBANER_PATTERNS.findall(all_text))
        brand_hits: dict[str, int] = {}
        for brand, pattern in COMPETITOR_BRANDS.items():
            n = len(pattern.findall(all_text))
            if n > 0:
                brand_hits[brand] = n

        top_brand = max(brand_hits.items(), key=lambda kv: kv[1], default=(None, 0))
        results.append({
            "asin": asin,
            "category": category_dir.name,
            "n_reviews": len(df),
            "urbaner_mentions": urbaner_hits,
            "top_competitor": top_brand[0],
            "top_competitor_mentions": top_brand[1],
            "all_brand_hits": ", ".join(f"{b}={c}" for b, c in sorted(brand_hits.items(), key=lambda kv: -kv[1])[:3]),
        })

df_out = pd.DataFrame(results)


def classify(row) -> str:
    if row.get("urbaner_mentions", 0) >= 2:
        return "confirmed_urbaner"
    if row.get("top_competitor_mentions", 0) >= 3:
        return "likely_contaminated"
    if row.get("top_competitor_mentions", 0) >= 1 and row.get("urbaner_mentions", 0) == 0:
        return "suspicious"
    return "neutral"


df_out["verdict"] = df_out.apply(classify, axis=1)

# 1) 完整輸出
df_out.to_csv(ROOT / "_asin_verification.csv", index=False, encoding="utf-8-sig")

# 2) 摘要
print(f"Total ASINs scanned: {len(df_out)}")
print()
print("Verdict distribution:")
print(df_out["verdict"].value_counts().to_string())
print()
print("=== confirmed_urbaner (前 20) ===")
print(df_out[df_out["verdict"] == "confirmed_urbaner"].head(20)[["asin", "category", "urbaner_mentions"]].to_string(index=False))
print()
print("=== likely_contaminated (確定汙染) ===")
print(df_out[df_out["verdict"] == "likely_contaminated"][["asin", "category", "top_competitor", "top_competitor_mentions", "all_brand_hits"]].to_string(index=False))
print()
print("=== suspicious (≥1 競品提及、無 URBANER) ===")
print(df_out[df_out["verdict"] == "suspicious"][["asin", "category", "top_competitor", "top_competitor_mentions", "all_brand_hits"]].to_string(index=False))
print()
print("=== neutral 中前 20 個（兩邊都無提及，需另外查證）===")
print(df_out[df_out["verdict"] == "neutral"].head(20)[["asin", "category", "n_reviews"]].to_string(index=False))
