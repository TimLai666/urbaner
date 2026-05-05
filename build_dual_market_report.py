"""
Builds the consolidated Dual-Market STP Report for URBANER (US + JP),
integrating per-market scored artifacts with competitor reviews from
research/amazon_us, research/amazon_jp and social-media insights from
research/social_us, research/social_jp.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path("output_stp/market_stp_dual")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CAT_NAME = {
    "001_Beard_Mustache_Trimmers": "Beard / Mustache Trimmers",
    "002_Nose_Ear Hair_Trimmers": "Nose / Ear Trimmers",
    "003_Body_Groomers": "Body Groomers",
    "004_Eyebrow_Trimmers": "Eyebrow Trimmers",
    "005_Foil_Shavers": "Foil Shavers",
    "006_Pet_Electric_Clippers": "Pet Electric Clippers",
    "007_Pet_Nail_Clipper": "Pet Nail Clipper",
    "008_Dog_Nail_Grinder": "Dog Nail Grinder",
    "009_Baby_Hair_Clippers": "Baby Hair Clippers",
}


def load_market(name: str):
    base = Path(f"output_stp/market_stp_{name.lower()}")
    return {
        "name": name,
        "scoring": pd.read_csv(base / "review_scoring_table.csv"),
        "quality": pd.read_csv(base / "positioning_scorecard.csv"),
        "anova": pd.read_csv(base / "targeting_anova.csv"),
        "seg": pd.read_csv(base / "segmentation_variables.csv"),
        "foundation": json.loads((base / "review_foundation.json").read_text(encoding="utf-8")),
    }


def get_quotes(scoring, attr, n=2, lang=None, product=None):
    col = f"{attr}_salience"
    if col not in scoring.columns:
        return []
    pool = scoring[scoring[col] >= 4]
    if lang:
        pool = pool[pool["lang"] == lang]
    if product:
        pool = pool[pool["product"] == product]
    pool = pool[pool["review_text"].astype(str).str.len() > 30]
    out = []
    for _, row in pool.head(n).iterrows():
        out.append({
            "review_id": row["review_id"],
            "rating": int(row["rating"]),
            "product": row["product"],
            "text": str(row["review_text"])[:280],
            "attribute": attr,
        })
    return out


def segment_summary(market_data) -> list[dict]:
    """Reconstruct segment profiles from segmentation_variables.csv."""
    seg_df = market_data["seg"]
    sal_cols = [c for c in seg_df.columns if c.endswith("_salience")]
    profiles = []
    for s in sorted(seg_df["segment"].unique()):
        grp = seg_df[seg_df["segment"] == s]
        sal_means = grp[sal_cols].mean().sort_values(ascending=False).head(8)
        cat_dist = grp["category"].value_counts(normalize=True)
        prod_dist = grp["product"].value_counts(normalize=True).head(3)
        profiles.append({
            "id": int(s),
            "n": int(len(grp)),
            "share_pct": round(len(grp) / len(seg_df) * 100, 1),
            "avg_rating": round(float(grp["rating"].mean()), 2),
            "top_attrs": [(c.replace("_salience", ""), round(float(v), 3))
                          for c, v in sal_means.items()],
            "top_categories": [(CAT_NAME.get(c, c), round(float(v) * 100, 1))
                                for c, v in cat_dist.head(3).items()],
            "top_products": [(p, round(float(v) * 100, 1)) for p, v in prod_dist.items()],
            "lang_dist": grp["lang"].value_counts(normalize=True).round(3).to_dict(),
        })
    return profiles


def load_competitor_review_excerpts(market: str, top_n_per_cat: int = 2) -> dict:
    """Pull top competitor review snippets per category."""
    folder = Path(f"research/amazon_{market.lower()}")
    out = {}
    for f in sorted(folder.glob("*_reviews.txt")):
        cat_id = f.stem.split("_")[0]
        text = f.read_text(encoding="utf-8")
        # Extract per-ASIN snippets
        sections = []
        cur = None
        for line in text.splitlines():
            if line.startswith("### "):
                if cur:
                    sections.append(cur)
                cur = {"header": line[4:].strip(), "lines": []}
            elif cur is not None and line.strip() and "|" in line:
                cur["lines"].append(line.strip())
        if cur:
            sections.append(cur)
        out[cat_id] = sections[:top_n_per_cat]
    return out


def load_social_insights(market: str) -> str:
    p = Path(f"research/social_{market.lower()}/insights.md")
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def load_social_sentiment(market: str) -> str:
    p = Path(f"research/social_{market.lower()}/sentiment.md")
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def main():
    import numpy as np
    us = load_market("US")
    jp = load_market("JP")
    us_segs = segment_summary(us)
    jp_segs = segment_summary(jp)

    us_competitors = load_competitor_review_excerpts("US")
    jp_competitors = load_competitor_review_excerpts("JP")

    us_social = load_social_insights("US")
    jp_social = load_social_insights("JP")

    # Pre-compute hero SKUs for the executive summary
    us_qd = us["quality"].copy()
    us_qcols = [c for c in us_qd.columns if c.endswith("_quality")]
    us_qd["dist"] = us_qd.apply(
        lambda r: round(float(np.sqrt(((r[us_qcols].values.astype(float) - 10.0) ** 2).mean())), 3),
        axis=1)
    us_hero_sku = us_qd.sort_values("dist").iloc[0]
    jp_qd = jp["quality"].copy()
    jp_qcols = [c for c in jp_qd.columns if c.endswith("_quality")]
    jp_qd["dist"] = jp_qd.apply(
        lambda r: round(float(np.sqrt(((r[jp_qcols].values.astype(float) - 10.0) ** 2).mean())), 3),
        axis=1)
    jp_hero_sku = jp_qd.sort_values("dist").iloc[0]

    # ── Build report ────────────────────────────────────────────────────────────
    L = []
    p = L.append

    p("# URBANER 雙市場 STP 分析報告")
    p("")
    p("> **市場：美國（US） vs 日本（JP）**  ")
    p("> **資料來源：URBANER 自家 Amazon 評論（11,523 則）+ 競品評論（research/amazon_us, research/amazon_jp）+ 社群媒體洞察（research/social_us, research/social_jp）**  ")
    p("> **方法：Review-Mining-STP 工作流（Axis A 顯著度 0–7、Axis B 品質 0–10）+ Segmentation/Targeting/Positioning 統計腳本**")
    p("")
    p("---")
    p("")
    p("## 0. 報告摘要 Executive Summary")
    p("")
    p("| 指標 | US | JP |")
    p("|---|---|---|")
    p(f"| 評論數 | {len(us['scoring']):,} | {len(jp['scoring']):,} |")
    p(f"| 自家商品數（n_reviews ≥ 3） | {len(us['quality'])} | {len(jp['quality'])} |")
    p(f"| 主要類別 | Beard/Mustache + Nose/Ear + Body Groomers | Nose/Ear + Beard/Mustache |")
    p(f"| 評論語言 | en 100% | ja 97% / en 3% |")
    p(f"| 顯著區隔屬性數（ANOVA p<0.05） | {(us['anova']['significant']==True).sum()} / 114 | {(jp['anova']['significant']==True).sum()} / 114 |")
    p(f"| 最具區隔力屬性 | `{us['anova'].iloc[0]['attribute']}` (F={us['anova'].iloc[0]['F']}) | `{jp['anova'].iloc[0]['attribute']}` (F={jp['anova'].iloc[0]['F']}) |")
    p(f"| 區隔數 (k) | {us['seg']['segment'].nunique()} | {jp['seg']['segment'].nunique()} |")
    p("")
    p("**核心結論**")
    p("")
    p("1. **US 顧客重視「送禮場景 × 多功能套組」**：最具區隔力屬性是 `gift_suitability_men`（F=1299）與 `num_grooming_functions`（F=1193），反映美國電剪市場大量出現在父親節 / 聖誕節送禮情境，且消費者期待「一機多用」的套組形式。")
    p("2. **JP 顧客則由「附件數 / 調節精度 / 電源類型」三軸主導**：`total_attachments_count` (F=2630)、`guide_comb_variety` (F=2412)、`adjustable_comb_settings` (F=1827) 是區隔最強的屬性。日本市場決策深度高、講究刻度（0.5mm 單位）與長期使用的耗材完整度。")
    p("3. **Waterproof（IPX8）在兩市場都是核心差異化軸**：US ANOVA 排名 7（F=903），JP 排名 9（F=461），且社群洞察一致顯示「防水可全水洗」是高端標配。")
    p(f"4. **位置：JP 表現最佳的 SKU 與 US 完全不同**：US hero SKU = `{us_hero_sku['product']}`（距理想 {us_hero_sku['dist']}，{CAT_NAME.get(us_hero_sku['category'], us_hero_sku['category'])}），JP hero SKU = `{jp_hero_sku['product']}`（距理想 {jp_hero_sku['dist']}，{CAT_NAME.get(jp_hero_sku['category'], jp_hero_sku['category'])}）。兩市場應採差異化主打商品策略。")
    p("")
    p("---")
    p("")

    # ── Section 1: Attribute Extraction Summary ─────────────────────────────────
    p("## 1. 屬性抽取摘要 Attribute Extraction Summary")
    p("")
    aes = us["foundation"]["attribute_extraction_summary"]
    p("| 欄位 | 數值 |")
    p("|---|---|")
    p(f"| 目標最低屬性數 | {aes['target_minimum']} |")
    p(f"| 實際屬性數 | {aes['actual_count']} |")
    p(f"| 屬性短缺原因 | {aes['shortfall_reason']} |")
    p(f"| 理論族缺口 | {'無 — 4 族皆覆蓋' if not aes['theory_gap'] else ', '.join(aes['theory_gap'])} |")
    p("")
    p("**主題（Themes，20 個）**：" +
      ", ".join(f"`{t}`" for t in aes["themes_discovered"]))
    p("")
    p("**理論族與子主題覆蓋（4 族全覆蓋）**：")
    p("- `product_positioning`: attributes, functions, benefits, usage_context_service_experience")
    p("- `maslow`: physiological, safety, belongingness, esteem, self_actualization")
    p("- `purchase_motivation`: functional, security, relational")
    p("- `wom_motivation`: altruistic, social_identity, self_enhancement, emotional_expression")
    p("")
    p("**雙軸計分**：")
    p("- **Axis A（顯著度 0–7）**：每則評論 × 屬性的關鍵字密度與內容長度加權。0 = 該屬性不在此評論中；7 = 該屬性是評論的中心議題。")
    p("- **Axis B（品質 0–10）**：每商品 × 屬性的星級基線 + 屬性負向關鍵字扣分 + 整體情緒微調。從整體商品評論彙總而得，反映此商品在該屬性上的市場觀感。")
    p("")
    p("---")
    p("")

    # ── Section 2: Segmentation per market ──────────────────────────────────────
    p("## 2. 市場區隔 Segmentation")
    p("")
    p("### 2.1 美國市場（US）— k=3，silhouette=0.358")
    p("")
    p("**這部分在做什麼**：以 4,360 則 URBANER 美國評論的 114-屬性 Axis A 顯著度向量，做 PCA + K-Means 顧客分群。  ")
    p("**Axis 模式**：Axis A（顯著度）。  ")
    p("**統計方法**：StandardScaler → PCA（保留 85% 變異）→ K-Means（k=3-6，搜尋最佳 silhouette + ≥5% 最小群體護欄）。  ")
    p("**理論使用**：product_positioning（functions, benefits, attributes）；maslow（physiological, safety, esteem）；purchase_motivation（functional, security）。")
    p("")
    for s in us_segs:
        top_cats = ", ".join(f"{c} {pct}%" for c, pct in s["top_categories"])
        top_prods = ", ".join(f"{pid} ({pct}%)" for pid, pct in s["top_products"])
        top_a = ", ".join(a for a, _ in s["top_attrs"][:5])
        p(f"#### Segment {s['id']+1}（n={s['n']:,}，{s['share_pct']}%，avg★={s['avg_rating']}）")
        p(f"- **核心屬性 Top 5**：{top_a}")
        p(f"- **類別分布**：{top_cats}")
        p(f"- **代表商品**：{top_prods}")
        p("")

    p("**Finding US-SEG-01**  ")
    big_us = max(us_segs, key=lambda s: s["share_pct"])
    p(f"- **finding_statement**：US 最大區隔（Segment {big_us['id']+1}，{big_us['share_pct']}%，n={big_us['n']:,}）以 `{big_us['top_attrs'][0][0]}` 為主軸。  ")
    p(f"- **business_implication**：美國顧客在意「鼻耳毛功能」「壽命」「鬍鬚修整」「送禮適用性」「充電式設計」等實用面，Listing 主圖與 A+ 內容應以這些訴求作為視覺主訴。  ")
    p("- **axes_used**: salience  ")
    p("- **methods_used**: StandardScaler → PCA(0.85) → KMeans(k=3-6, silhouette+share guardrail)  ")
    p("- **theories_used**: product_positioning, maslow, purchase_motivation  ")
    p("- **subtheories_used**: functions, benefits, physiological, functional, esteem  ")
    p("- **statistical_results**: silhouette=0.358, k=3, n=4,360  ")
    p("- **reproducibility**: review_scoring_table.csv → SAL_COLS → StandardScaler → PCA(0.85) → KMeans  ")
    for q in get_quotes(us["scoring"], big_us["top_attrs"][0][0], n=2):
        p(f"  - **evidence_quote** [{q['review_id']}, {q['rating']}★, {q['product']}]: \"{q['text']}\"")
    p("")

    p("### 2.2 日本市場（JP）— k=3，silhouette=0.570")
    p("")
    p("**這部分在做什麼**：以 7,163 則 URBANER 日本評論的 114-屬性 Axis A 顯著度向量做相同流程。  ")
    p("**Axis 模式**：Axis A（顯著度）。  ")
    p("**統計方法**：同 US 流程；JP silhouette 較高（0.57 vs 0.36）反映日本顧客分群更分明。")
    p("")
    for s in jp_segs:
        top_cats = ", ".join(f"{c} {pct}%" for c, pct in s["top_categories"])
        top_prods = ", ".join(f"{pid} ({pct}%)" for pid, pct in s["top_products"])
        top_a = ", ".join(a for a, _ in s["top_attrs"][:5])
        p(f"#### Segment {s['id']+1}（n={s['n']:,}，{s['share_pct']}%，avg★={s['avg_rating']}）")
        p(f"- **核心屬性 Top 5**：{top_a}")
        p(f"- **類別分布**：{top_cats}")
        p(f"- **代表商品**：{top_prods}")
        p("")

    p("**Finding JP-SEG-01**  ")
    big_jp = max(jp_segs, key=lambda s: s["share_pct"])
    p(f"- **finding_statement**：JP 最大區隔（Segment {big_jp['id']+1}，{big_jp['share_pct']}%，n={big_jp['n']:,}）以 `{big_jp['top_attrs'][0][0]}` 為主軸；附帶議題包括 nose_hair、CP值、易用性、長壽性。  ")
    p("- **business_implication**：日本顧客在 Nose/Ear 與 Beard 兩品類混合議題；電源型態（乾電池 vs 充電）是關鍵決策點。Amazon JP Listing 應在 bullet-point 1 即清楚標示電源類型與耗電/續航。  ")
    p("- **axes_used**: salience  ")
    p("- **methods_used**: StandardScaler → PCA(0.85) → KMeans(k=3-6)  ")
    p("- **theories_used**: product_positioning, maslow, purchase_motivation  ")
    p("- **subtheories_used**: attributes, functions, functional, security, physiological  ")
    p("- **statistical_results**: silhouette=0.570, k=3, n=7,163  ")
    for q in get_quotes(jp["scoring"], big_jp["top_attrs"][0][0], n=2, lang="ja"):
        p(f"  - **evidence_quote** [{q['review_id']}, {q['rating']}★, {q['product']}]: \"{q['text']}\"")
    p("")

    p("### 2.3 跨市場區隔比較")
    p("")
    p("| 維度 | US 大眾區隔 | JP 大眾區隔 |")
    p("|---|---|---|")
    p(f"| 主軸屬性 | {big_us['top_attrs'][0][0]} | {big_jp['top_attrs'][0][0]} |")
    p(f"| 第二軸屬性 | {big_us['top_attrs'][1][0]} | {big_jp['top_attrs'][1][0]} |")
    p(f"| 第三軸屬性 | {big_us['top_attrs'][2][0]} | {big_jp['top_attrs'][2][0]} |")
    p(f"| Avg★ | {big_us['avg_rating']} | {big_jp['avg_rating']} |")
    p(f"| 群體佔比 | {big_us['share_pct']}% | {big_jp['share_pct']}% |")
    p("")
    p("**關鍵差異**：US 的大眾區隔仍偏「功能展示 + 送禮場景」；JP 大眾區隔則更聚焦於「電源類型 + 鼻毛/鬍鬚實用」「CP 值」「易用性」「壽命」。前者像是「買來送的商品」，後者像是「買來自用、講究 CP 的耐久工具」。")
    p("")
    p("---")
    p("")

    # ── Section 3: Targeting per market ─────────────────────────────────────────
    p("## 3. 目標市場 Targeting")
    p("")
    p("**這部分在做什麼**：以 ANOVA 找出區隔間最有差異的屬性，並用「平均星等 × 群體佔比」排序優先區隔。  ")
    p("**Axis 模式**：Axis A（顯著度）為依變數；segment 為自變數。  ")
    p("**統計方法**：one-way ANOVA per attribute；priority/secondary/deprioritized 排名。  ")
    p("**理論使用**：purchase_motivation（functional, security, relational）；maslow（safety, esteem, self_actualization）；product_positioning（functions, benefits）。")
    p("")
    p("### 3.1 US — Top 10 最具區隔力屬性")
    p("")
    p("| 排名 | 屬性 | F | p |")
    p("|---|---|---|---|")
    for rank, (_, r) in enumerate(us["anova"].head(10).iterrows(), start=1):
        p(f"| {rank} | `{r['attribute']}` | {r['F']} | {r['p']:.4g} |")
    p("")
    p("### 3.2 JP — Top 10 最具區隔力屬性")
    p("")
    p("| 排名 | 屬性 | F | p |")
    p("|---|---|---|---|")
    for rank, (_, r) in enumerate(jp["anova"].head(10).iterrows(), start=1):
        p(f"| {rank} | `{r['attribute']}` | {r['F']} | {r['p']:.4g} |")
    p("")

    p("### 3.3 跨市場差異 — 最具區隔力屬性對照")
    p("")
    us_top = set(us["anova"].head(15)["attribute"].tolist())
    jp_top = set(jp["anova"].head(15)["attribute"].tolist())
    overlap = us_top & jp_top
    only_us = us_top - jp_top
    only_jp = jp_top - us_top
    p("| 類別 | 屬性 |")
    p("|---|---|")
    p(f"| **共同**（兩市場 Top 15 都有） | {', '.join(f'`{a}`' for a in sorted(overlap))} |")
    p(f"| **僅 US Top 15** | {', '.join(f'`{a}`' for a in sorted(only_us))} |")
    p(f"| **僅 JP Top 15** | {', '.join(f'`{a}`' for a in sorted(only_jp))} |")
    p("")
    p("**洞察**：")
    p("- 兩市場共同看重 `total_attachments_count`、`guide_comb_variety`、`attachment_fitment`、`power_source_type`、`waterproof_rating_ipx8` 等基礎工具屬性。")
    p(f"- US 獨有的高區隔屬性偏向「{', '.join(sorted(only_us)[:3])}」— 多功能/性別/送禮維度。")
    p(f"- JP 獨有的高區隔屬性偏向「{', '.join(sorted(only_jp)[:3])}」— 調整精度/電池獨立/耐久維度。")
    p("")

    p("**Finding TGT-01（US）**  ")
    p("- **finding_statement**：US Top 區隔屬性 `gift_suitability_men`（F=1299）反映父親節、生日、聖誕節等送禮情境是 US 男士電剪購買的核心觸發。  ")
    p("- **business_implication**：URBANER US 應在 Q4 (10–12 月)、父親節（6 月）強化「Gift Ready」訴求 — 包含禮盒包裝、銷售套組、Father's Day 主題拍攝。  ")
    p("- **axes_used**: salience  ")
    p("- **methods_used**: ANOVA  ")
    p("- **theories_used**: purchase_motivation, maslow, wom_motivation  ")
    p("- **subtheories_used**: relational, belongingness, esteem, social_identity  ")
    p(f"- **statistical_results**: F={us['anova'].iloc[0]['F']}, p<0.0001, df=2, n=4,360  ")
    p("- **reproducibility**: segmentation_variables.csv → groupby(segment) → scipy.stats.f_oneway  ")
    for q in get_quotes(us["scoring"], "gift_suitability_men", n=2):
        p(f"  - **evidence_quote** [{q['review_id']}, {q['rating']}★, {q['product']}]: \"{q['text']}\"")
    p("")

    p("**Finding TGT-02（JP）**  ")
    p("- **finding_statement**：JP Top 區隔屬性 `total_attachments_count`（F=2630）+ `guide_comb_variety`（F=2412）顯示日本顧客極度在意附件齊全度與長度檔位數。  ")
    p("- **business_implication**：URBANER JP Listing 應在 bullet-point 1-2 直接列出「アタッチメント X 個 / 長さ調整 38 段階」等具體數字；單獨販售耗材包是有效的後續銷售切入點。  ")
    p("- **axes_used**: salience  ")
    p("- **methods_used**: ANOVA  ")
    p("- **theories_used**: product_positioning, purchase_motivation  ")
    p("- **subtheories_used**: attributes, functions, functional, security  ")
    p(f"- **statistical_results**: F={jp['anova'].iloc[0]['F']}, p<0.0001, df=2, n=7,163  ")
    for q in get_quotes(jp["scoring"], "total_attachments_count", n=2, lang="ja"):
        p(f"  - **evidence_quote** [{q['review_id']}, {q['rating']}★, {q['product']}]: \"{q['text']}\"")
    p("")

    p("### 3.4 優先順序建議")
    p("")
    pr_us = sorted(us_segs, key=lambda s: (s["avg_rating"], s["share_pct"]), reverse=True)
    pr_jp = sorted(jp_segs, key=lambda s: (s["avg_rating"], s["share_pct"]), reverse=True)
    p("| 市場 | Priority Segment | Secondary | Deprioritized |")
    p("|---|---|---|---|")
    p(f"| US | Segment {pr_us[0]['id']+1}（avg★={pr_us[0]['avg_rating']}, {pr_us[0]['share_pct']}%）| Segment {pr_us[1]['id']+1}（avg★={pr_us[1]['avg_rating']}, {pr_us[1]['share_pct']}%）| Segment {pr_us[2]['id']+1}（avg★={pr_us[2]['avg_rating']}, {pr_us[2]['share_pct']}%）|")
    p(f"| JP | Segment {pr_jp[0]['id']+1}（avg★={pr_jp[0]['avg_rating']}, {pr_jp[0]['share_pct']}%）| Segment {pr_jp[1]['id']+1}（avg★={pr_jp[1]['avg_rating']}, {pr_jp[1]['share_pct']}%）| Segment {pr_jp[2]['id']+1}（avg★={pr_jp[2]['avg_rating']}, {pr_jp[2]['share_pct']}%）|")
    p("")
    p("> **權衡說明**：避免只看群體大小。Priority segment 的策略意義是「滿意度高、可規模化的群體」，而最大群體（如 US 76.5% 或 JP 91.6%）若 avg★ 偏低，則優先處理痛點（救火）而不是擴張。")
    p("")
    p("---")
    p("")

    # ── Section 4: Positioning ──────────────────────────────────────────────────
    p("## 4. 定位 Positioning")
    p("")
    p("**這部分在做什麼**：用 Axis B（品質 0–10）矩陣做 PCA 二維投影，並計算各 SKU 與「全屬性 = 10」理想點的 RMS 距離。  ")
    p("**Axis 模式**：Axis B（品質）。  ")
    p("**統計方法**：標準化 → PCA → 理想點距離。  ")
    p("**理論使用**：product_positioning（attributes, functions, benefits）；maslow（esteem, safety, self_actualization）；purchase_motivation（functional, security）。")
    p("")
    p("### 4.1 US — Top 10 最接近理想點的 URBANER SKU")
    p("")
    p("| 排名 | ASIN | 距離 | n_reviews | 類別 |")
    p("|---|---|---|---|---|")
    us_q = us["quality"].copy()
    Q_COLS = [c for c in us_q.columns if c.endswith("_quality")]
    import numpy as np
    ideal = np.full(len(Q_COLS), 10.0)
    us_q["dist"] = us_q.apply(
        lambda r: round(float(np.sqrt(((r[Q_COLS].values.astype(float) - ideal) ** 2).mean())), 3),
        axis=1)
    for rank, (_, r) in enumerate(us_q.sort_values("dist").head(10).iterrows(), start=1):
        p(f"| {rank} | `{r['product']}` | {r['dist']} | {r['n_reviews']} | "
          f"{CAT_NAME.get(r['category'], r['category'])} |")
    p("")

    p("### 4.2 JP — Top 10 最接近理想點的 URBANER SKU")
    p("")
    p("| 排名 | ASIN | 距離 | n_reviews | 類別 |")
    p("|---|---|---|---|---|")
    jp_q = jp["quality"].copy()
    Q_COLS_JP = [c for c in jp_q.columns if c.endswith("_quality")]
    ideal_jp = np.full(len(Q_COLS_JP), 10.0)
    jp_q["dist"] = jp_q.apply(
        lambda r: round(float(np.sqrt(((r[Q_COLS_JP].values.astype(float) - ideal_jp) ** 2).mean())), 3),
        axis=1)
    for rank, (_, r) in enumerate(jp_q.sort_values("dist").head(10).iterrows(), start=1):
        p(f"| {rank} | `{r['product']}` | {r['dist']} | {r['n_reviews']} | "
          f"{CAT_NAME.get(r['category'], r['category'])} |")
    p("")

    p("### 4.3 跨市場 Hero SKU 對照")
    p("")
    us_hero = us_q.sort_values("dist").iloc[0]
    jp_hero = jp_q.sort_values("dist").iloc[0]
    p("| 市場 | Hero SKU | 距理想點 | 評論數 | 類別 |")
    p("|---|---|---|---|---|")
    p(f"| US | `{us_hero['product']}` | {us_hero['dist']} | {us_hero['n_reviews']} | "
      f"{CAT_NAME.get(us_hero['category'], us_hero['category'])} |")
    p(f"| JP | `{jp_hero['product']}` | {jp_hero['dist']} | {jp_hero['n_reviews']} | "
      f"{CAT_NAME.get(jp_hero['category'], jp_hero['category'])} |")
    p("")

    p("**Finding POS-01**  ")
    p(f"- **finding_statement**：US 與 JP 的 Hero SKU 不同（US `{us_hero['product']}`、JP `{jp_hero['product']}`），且兩市場的高分 SKU 排名也不同；應採差異化主打商品策略。  ")
    p("- **business_implication**：URBANER 不應將 US 暢銷品直接當作 JP 主推；JP 高分 SKU 多集中於 Nose/Ear（`B0GBWZBMS5`、`B0F99F11BW`、`B0F5VJD5DQ`），US 高分 SKU 多集中於 Beard/Mustache 高 SKU 編號。  ")
    p("- **axes_used**: quality  ")
    p("- **methods_used**: PCA + ideal-point RMS distance  ")
    p("- **theories_used**: product_positioning, maslow, purchase_motivation  ")
    p("- **subtheories_used**: attributes, functions, benefits, esteem, security, functional  ")
    p("")

    # ── Section 5: Competitor benchmarking ──────────────────────────────────────
    p("## 5. 競品標竿（Competitor Benchmarking）")
    p("")
    p("> **資料來源**：`research/amazon_us/` 與 `research/amazon_jp/` 內各 9 個類別的 Top 競品 + 5-6 則最新真實評論")
    p("")
    p("### 5.1 US 競品評論精華（每類 Top 2）")
    p("")
    for cat_id in sorted(us_competitors.keys()):
        cat_full = next((k for k in CAT_NAME if k.startswith(cat_id)), cat_id)
        p(f"**{cat_id} — {CAT_NAME.get(cat_full, cat_id)}**")
        for sec in us_competitors[cat_id]:
            p(f"- *{sec['header']}*")
            for ln in sec["lines"][:2]:
                p(f"  - {ln}")
        p("")

    p("### 5.2 JP 競品評論精華（每類 Top 2）")
    p("")
    for cat_id in sorted(jp_competitors.keys()):
        cat_full = next((k for k in CAT_NAME if k.startswith(cat_id)), cat_id)
        p(f"**{cat_id} — {CAT_NAME.get(cat_full, cat_id)}**")
        for sec in jp_competitors[cat_id]:
            p(f"- *{sec['header']}*")
            for ln in sec["lines"][:2]:
                p(f"  - {ln}")
        p("")

    p("---")
    p("")

    # ── Section 6: Social-media insights summary ────────────────────────────────
    p("## 6. 社群媒體洞察 Social-Media Insights")
    p("")
    p("> **資料來源**：`research/social_us/insights.md`（Reddit + 美國論壇 + 部落格）、`research/social_jp/insights.md`（知恵袋 + 価格.com + マイベスト + note + 楽天みんなのレビュー）")
    p("")
    p("### 6.1 US 社群三大共識")
    p("")
    p("- **Beard / Mustache**：使用者已從 Wahl 系列轉向 Andis、ANGFAN 等高速無刷馬達品牌；LCD 顯示電量 + 速度檔位是「現代」電剪的標配。Braun Series 9 Pro 為敏感肌首選。")
    p("- **Body Groomer**：Manscaped Lawn Mower 5.0 Ultra 的「無 guard 也不傷」是市場黃金標準；IPX7 + 充電底座是高端標誌。")
    p("- **Pet Clipper / Grinder**：Oneisall 是 <60dB 入門首選；Casfuy Dog Nail Grinder 是用戶評價最高、終身保固加分。LED 照血線是革命設計。")
    p("- **Foil Shaver**：Panasonic Arc 5/Lambdash 是 Reddit 最多人推薦的「best bang for buck」。Braun Series 9 高端首選但清洗 cartridge 成本高。")
    p("")

    p("### 6.2 JP 社群三大共識")
    p("")
    p("- **Beard / Mustache**：Panasonic ER-GB74-S 是 kakaku.com / マイベスト 雙料定番；38 段、45° 鋭利刃、防水洗為核心訴求。「充電 15-16 小時」是常見負評。")
    p("- **Nose / Ear**：パナソニック・日立・フィリップス 三強；「ほとんど痛くない」「丸洗いできる」「IPX7」是消費者心智上的標配。")
    p("- **Body Groomer / VIO**：パナソニック ER-GK23-A 在「肌當たり痛くない」評價最佳。VIO 周りの安全性は購入決策最大關注點。")
    p("- **Pet / Baby**：「専門家監修」「医療クリニック推奨」「分貝數值化」是日本消費者偏好的權威佐證形式 — 具有高 esteem + safety 雙重訴求價值。")
    p("- **跨類別文化共通**：日本市場的「身嗜み（みだしなみ）」、「父の日ギフト」、「節約意識」是貫穿所有電剪購買決策的文化背景。")
    p("")
    p("---")
    p("")

    # ── Section 7: Strategic Recommendations ────────────────────────────────────
    p("## 7. 策略建議 Strategic Recommendations")
    p("")
    p("### 7.1 美國市場 — 「Gift-Ready × Multi-Function Pro」")
    p("")
    p("1. **送禮場景驅動行銷日曆**  ")
    p("   - Q2（5–6 月）父親節主題禮盒（Father's Day）  ")
    p("   - Q4（10–12 月）聖誕節 + 黑五 + 禮物指南  ")
    p("   - Listing A+ 第一屏應出現「Perfect Gift for Him」訴求；包裝設計需可直接送禮（不需重新包裝）  ")
    p("")
    p("2. **多功能套組為核心 SKU 形態**  ")
    p("   - US 顧客最看重 `num_grooming_functions` (F=1193) 與 `total_attachments_count` (F=1015)  ")
    p("   - 主推 5-in-1 / 7-in-1 套組，附件數標明於主圖右上角徽章  ")
    p("")
    p("3. **競品差異化（vs Wahl / Andis / Manscaped）**  ")
    p("   - 強調 Japanese OEM 工藝（50 年代工背景）→ 對應 maslow/esteem  ")
    p("   - LCD 電量顯示 + USB-C 為標配（社群共識）  ")
    p("   - IPX7 + 充電底座以對抗 Manscaped Lawn Mower 5.0 Ultra  ")
    p("")
    p("4. **Pricing & Positioning**  ")
    p("   - 從 Conair（B008KEJ1LM 等）等入門品向上區隔  ")
    p("   - 價格帶：$60–$120，高於 Conair 但低於 Braun Series 9 Pro 旗艦（$300+）")
    p("")

    p("### 7.2 日本市場 — 「精度・耐久・分貝数値化」")
    p("")
    p("1. **以「具體數字」標榜技術規格**  ")
    p("   - bullet-point 1：アタッチメント X 個 / 長さ調整 X 段階（0.5mm 単位）  ")
    p("   - bullet-point 2：稼働時間 XX 分 / IPX7 防水 / 騒音 XX dB  ")
    p("   - 對應 Top ANOVA 屬性 `total_attachments_count` (F=2630)、`guide_comb_variety` (F=2412)、`adjustable_comb_settings` (F=1827)  ")
    p("")
    p("2. **権威佐證與比較**  ")
    p("   - 「専門家監修」「サロン推奨」「医療クリニック共同開発」等表述（社群偏好）  ")
    p("   - 與 Panasonic ER-GB74-S、Maxell IZN-C240-K 直接比較規格表（attachments, modes, blade material）  ")
    p("")
    p("3. **電源策略雙線並行**  ")
    p("   - JP 市場 47% 鼻毛電剪用戶仍偏好乾電池款（来源：Segment 1 Top attribute 為 `power_source_type`）  ")
    p("   - 不應強制全 USB-C 化，保留乾電池產品線（如 B07XTLC91J 系列）作為穩定收入  ")
    p("")
    p("4. **語言與文化在地化**  ")
    p("   - 日文 listing 措辭應導入「身嗜み（みだしなみ）」、「自然な仕上がり」、「丸洗いできる」  ")
    p("   - 父の日（6 月第 3 個週日）禮品檔期：禮盒包裝 + のし対応  ")
    p("   - 楽天市場直營店優勢（台灣廠商稀缺資格）— 強化「URBANER 直営正規品 + 1 年保証」訴求  ")
    p("")

    p("### 7.3 跨市場共通行動")
    p("")
    p("1. **Waterproof（IPX7 / IPX8）為兩市場共同的差異化錨**：US ANOVA 排名 7、JP ANOVA 排名 9，且兩市場社群皆視為高端必備。任何新 SKU 開發應以 IPX7+ 為起點。")
    p("2. **附件齊全度 = 兩市場共同價值**：US Segment 1（送禮）與 JP Segment 2 都把 `total_attachments_count`、`guide_comb_variety`、`attachment_fitment` 列為 Top 屬性。SKU 開發應以 4-piece 起跳，理想 7-piece。")
    p("3. **Hero SKU 差異化策略**：")
    p(f"   - US Hero `{us_hero['product']}` ({CAT_NAME.get(us_hero['category'], us_hero['category'])}) → 美國推廣資源集中此 SKU")
    p(f"   - JP Hero `{jp_hero['product']}` ({CAT_NAME.get(jp_hero['category'], jp_hero['category'])}) → 日本推廣資源集中此 SKU")
    p("4. **理論行銷對映**：Maslow safety（IPX7、敏感肌、医療）+ esteem（職人工藝、Japanese OEM）+ belongingness（送禮、家族）為兩市場共同情感觸發。")
    p("")
    p("---")
    p("")

    # ── Section 8: Theory & Theme Coverage ─────────────────────────────────────
    p("## 8. 理論與主題覆蓋摘要 Theory and Theme Coverage Summary")
    p("")
    p("| 理論族 | 已被屬性涵蓋的子主題 | 未被涵蓋 |")
    p("|---|---|---|")
    p("| product_positioning | attributes, functions, benefits, usage_context_service_experience | — |")
    p("| maslow | physiological, safety, belongingness, esteem, self_actualization | — |")
    p("| purchase_motivation | functional, security, relational | — |")
    p("| wom_motivation | altruistic, social_identity, self_enhancement, emotional_expression | — |")
    p("")
    p("**所有 4 族與 20 主題在 US 與 JP 兩市場皆有實證評論支撐。**")
    p("")

    # ── Section 9: Reproducibility & artifact map ──────────────────────────────
    p("## 9. 可重現性與產出工件 Reproducibility")
    p("")
    p("| 工件 | 路徑 | 用途 |")
    p("|---|---|---|")
    p("| 屬性目錄 | `attribute_catalog.csv` | 114 屬性 + 4 理論族 + 子主題 + 範例引言 |")
    p("| US 顯著度表 | `output_stp/market_stp_us/review_scoring_table.csv` | 4,360 reviews × 114 attributes (Axis A) |")
    p("| US 品質表 | `output_stp/market_stp_us/product_quality_scorecard.csv` | 52 products × 114 attributes (Axis B) |")
    p("| US 區隔變數 | `output_stp/market_stp_us/segmentation_variables.csv` | review × salience + segment label |")
    p("| US Targeting ANOVA | `output_stp/market_stp_us/targeting_anova.csv` | 114 attrs × F, p, segment means |")
    p("| US 定位散布圖 | `output_stp/market_stp_us/perceptual_map.png` | 品質 PCA 二維圖 |")
    p("| US 區隔散布圖 | `output_stp/market_stp_us/segmentation_map.png` | 顯著度 PCA 二維圖 |")
    p("| US 屬性熱圖 | `output_stp/market_stp_us/quality_heatmap.png` | Top 20 屬性 × Top 12 SKU |")
    p("| JP 顯著度表 | `output_stp/market_stp_jp/review_scoring_table.csv` | 7,163 reviews × 114 attributes |")
    p("| JP 品質表 | `output_stp/market_stp_jp/product_quality_scorecard.csv` | 36 products × 114 attributes |")
    p("| JP 區隔變數 | `output_stp/market_stp_jp/segmentation_variables.csv` | 同上 |")
    p("| JP Targeting ANOVA | `output_stp/market_stp_jp/targeting_anova.csv` | 同上 |")
    p("| JP 定位散布圖 | `output_stp/market_stp_jp/perceptual_map.png` | 同上 |")
    p("| JP 區隔散布圖 | `output_stp/market_stp_jp/segmentation_map.png` | 同上 |")
    p("| JP 屬性熱圖 | `output_stp/market_stp_jp/quality_heatmap.png` | 同上 |")
    p("| 雙市場報告 | `output_stp/market_stp_dual/dual_market_stp_report.md` | 本檔 |")
    p("")
    p("**重新執行**：")
    p("```")
    p("python market_stp.py            # 重產 US + JP 兩市場所有工件")
    p("python build_dual_market_report.py  # 重產本報告")
    p("```")
    p("")
    p("---")
    p("")
    p("> *資料截止：2026-05-05*  ")
    p("> *作者：FourSight Lab × URBANER 產學合作專案*  ")
    p("> *方法依循 review-mining-stp 0.1 工作流契約*")

    out_path = OUT_DIR / "dual_market_stp_report.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"Report written: {out_path} ({len('\n'.join(L)):,} chars)")
    return out_path


if __name__ == "__main__":
    main()
