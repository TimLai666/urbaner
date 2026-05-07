"""
產品卡片 vs 競品：Multinomial Logit 市場偏好份額分析
選擇集 = 24 張設計卡片 + 全市場競品 SKU
P(i) = exp(Ui) / sum(exp(Uj))  j ∈ 全選擇集
"""

import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path("output_conjoint")

# ── β 係數（來自 conjoint_analysis.py Split-model Dummy Encoding）────────────
US_BETAS = {
    "size":         (-0.9756,  1.2580),
    "power_source": (10.5291, 13.8123),
    "waterproof":   ( 9.1456, 10.6809),
    "attachments":  (10.5291, 13.8123),
    "guide_comb":   (-1.7095,  1.8786),
    "functions":    (None,     None),     # 完全分離，排除
    "charging":     (11.5446, 13.8734),
}

JP_BETAS = {
    "size":         (-0.5144,  0.4411),
    "attachments":  (13.4808, 16.1198),
    "guide_comb":   (14.1244, 15.6059),
    "precision":    (14.1982, 15.0359),
    "power_source": (10.6546, 15.0363),
    "waterproof":   ( 8.8345, 10.1467),
    "battery_life": ( 8.2661, 10.7511),
}

# ── 屬性欄位對應（品質分欄位名稱）────────────────────────────────────────────
US_QUAL_COL = {
    "size":         "product_dimensions_size_quality",
    "power_source": "power_source_type_quality",
    "waterproof":   "waterproof_rating_ipx8_quality",
    "attachments":  "total_attachments_count_quality",
    "guide_comb":   "guide_comb_variety_quality",
    "functions":    "num_grooming_functions_quality",
    "charging":     "usb_c_charging_quality",
}

JP_QUAL_COL = {
    "size":         "product_dimensions_size_quality",
    "attachments":  "total_attachments_count_quality",
    "guide_comb":   "guide_comb_variety_quality",
    "precision":    "adjustable_comb_settings_quality",
    "power_source": "power_source_type_quality",
    "waterproof":   "waterproof_rating_ipx8_quality",
    "battery_life": "battery_life_duration_quality",
}

# ── 設計卡片水準 → dummy encoding ────────────────────────────────────────────
US_LEVEL_MAP = {
    "長度調整段數": {"≤5段": (0,0), "12段": (1,0), "≥38段": (0,1)},
    "電源類型":     {"乾電池": (0,0), "混合供電": (1,0), "USB-C": (0,1)},
    "附件件數":     {"≤3件": (0,0), "7件": (1,0), "≥10件": (0,1)},
    "充電方式":     {"無USB-C": (0,0), "普通充電": (1,0), "USB-C快充": (0,1)},
    "機身尺寸":     {"大型": (0,0), "標準": (1,0), "迷你": (0,1)},
    "功能合一數":   {"1合1": (0,0), "3合1": (1,0), "5合1+": (0,1)},
    "防水等級":     {"無防水": (0,0), "IPX4": (1,0), "IPX7+": (0,1)},
}

JP_LEVEL_MAP = {
    "電源類型":     {"乾電池": (0,0), "混合供電": (1,0), "USB-C": (0,1)},
    "附件件數":     {"≤3件": (0,0), "7件": (1,0), "≥10件": (0,1)},
    "電池續航時間": {"30分鐘": (0,0), "60分鐘": (1,0), "90分鐘+": (0,1)},
    "長度調整段數": {"≤5段": (0,0), "12段": (1,0), "≥38段": (0,1)},
    "防水等級":     {"無防水": (0,0), "IPX4": (1,0), "IPX7+": (0,1)},
    "調整精度":     {"2mm刻度": (0,0), "1mm刻度": (1,0), "0.5mm刻度": (0,1)},
    "機身尺寸":     {"大型": (0,0), "標準": (1,0), "迷你": (0,1)},
}

US_COL_MAP = {
    "guide_comb":   "長度調整段數",
    "power_source": "電源類型",
    "attachments":  "附件件數",
    "charging":     "充電方式",
    "size":         "機身尺寸",
    "functions":    "功能合一數",
    "waterproof":   "防水等級",
}

JP_COL_MAP = {
    "guide_comb":   "長度調整段數",
    "attachments":  "附件件數",
    "power_source": "電源類型",
    "battery_life": "電池續航時間",
    "waterproof":   "防水等級",
    "precision":    "調整精度",
    "size":         "機身尺寸",
}


def safe_beta(b):
    return 0.0 if (b is None or (isinstance(b, float) and np.isnan(b))) else b


def utility_from_quality(row, betas, qual_col_map):
    """從品質分（0–10）計算效用：先離散化為 dummy，再乘 β"""
    U = 0.0
    for attr, (bm, bh) in betas.items():
        col = qual_col_map.get(attr)
        if col is None or col not in row.index:
            continue
        score = row[col]
        if pd.isna(score):
            continue
        # 離散化：Low(0–4)=00, Mid(4–7)=10, High(7–10)=01
        if score <= 4:
            mid, high = 0, 0
        elif score <= 7:
            mid, high = 1, 0
        else:
            mid, high = 0, 1
        U += safe_beta(bm) * mid + safe_beta(bh) * high
    return U


def utility_from_card(row, betas, col_map, level_map):
    """從產品卡片文字水準計算效用"""
    U = 0.0
    for attr, (bm, bh) in betas.items():
        card_col = col_map.get(attr)
        lmap = level_map.get(card_col, {})
        val = str(row.get(card_col, "")).strip()
        mid, high = lmap.get(val, (0, 0))
        U += safe_beta(bm) * mid + safe_beta(bh) * high
    return U


def mnl_share(utilities):
    """Multinomial Logit 份額"""
    exp_u = np.exp(utilities - utilities.max())  # 數值穩定
    return exp_u / exp_u.sum()


def run_market_analysis(market, cards_df, card_col_map, card_level_map,
                        betas, qual_col_map, skus_df,
                        urbaner_asins, card_col_name="產品卡"):
    # 1. 計算各 SKU 效用
    sku_utils = []
    for _, row in skus_df.iterrows():
        u = utility_from_quality(row, betas, qual_col_map)
        brand = "URBANER" if row["product"] in urbaner_asins else "競品"
        sku_utils.append({
            "類型": brand,
            "ID": row["product"],
            "效用值": u,
            "avg_star": row.get("avg_star", np.nan),
        })

    # 2. 計算各設計卡片效用
    card_utils = []
    for _, row in cards_df.iterrows():
        u = utility_from_card(row, betas, card_col_map, card_level_map)
        card_utils.append({
            "類型": "設計卡片",
            "ID": row[card_col_name],
            "效用值": u,
            "avg_star": np.nan,
        })

    all_items = pd.DataFrame(sku_utils + card_utils).reset_index(drop=True)
    all_items["偏好份額"] = mnl_share(all_items["效用值"].values)
    all_items = all_items.sort_values("偏好份額", ascending=False).reset_index(drop=True)
    all_items.insert(0, "排名", range(1, len(all_items) + 1))

    return all_items


def md_full_ranking(df, market_label, top_n=15):
    lines = [
        f"### {market_label} — 完整選擇集偏好份額排名（前 {top_n}）",
        "",
        "| 排名 | 類型 | ID | 偏好份額 | avg★ |",
        "|---:|:---:|---|---:|---:|",
    ]
    for _, row in df.head(top_n).iterrows():
        star = f"{row['avg_star']:.2f}" if not np.isnan(row["avg_star"]) else "—"
        lines.append(
            f"| {row['排名']} | {row['類型']} | `{row['ID']}` "
            f"| **{row['偏好份額']:.4f}** | {star} |"
        )
    lines.append("")
    return "\n".join(lines)


def md_card_ranking(df, market_label):
    cards = df[df["類型"] == "設計卡片"].copy()
    cards = cards.reset_index(drop=True)
    cards.insert(0, "卡片排名", range(1, len(cards) + 1))

    # 計算在全選擇集中的排名
    lines = [
        f"### {market_label} — 設計卡片偏好份額排名",
        "",
        "| 卡片排名 | 全場排名 | 卡片 | 偏好份額 |",
        "|---:|---:|---|---:|",
    ]
    for _, row in cards.iterrows():
        lines.append(
            f"| {row['卡片排名']} | {row['排名']} | `{row['ID']}` "
            f"| **{row['偏好份額']:.4f}** |"
        )
    lines.append("")
    return "\n".join(lines)


def md_group_summary(df, market_label):
    grp = df.groupby("類型")["偏好份額"].sum().reset_index()
    lines = [
        f"### {market_label} — 群組偏好份額合計",
        "",
        "| 群組 | 合計份額 |",
        "|---|---:|",
    ]
    for _, row in grp.sort_values("偏好份額", ascending=False).iterrows():
        lines.append(f"| {row['類型']} | **{row['偏好份額']:.4f}** |")
    lines.append("")
    return "\n".join(lines)


def md_best_card(df, market_label):
    cards = df[df["類型"] == "設計卡片"]
    if cards.empty:
        return ""
    best = cards.iloc[0]
    lines = [
        f"#### {market_label} 最具競爭力設計卡片",
        "",
        f"- **卡片**：{best['ID']}",
        f"- **偏好份額**：{best['偏好份額']:.4f}（全選擇集排名第 {best['排名']} 名）",
        "",
    ]
    return "\n".join(lines)


def main():
    # 讀取品質分資料
    us_q = pd.read_csv("output_stp/market_stp_us/product_quality_scorecard.csv")
    jp_q = pd.read_csv("output_stp/market_stp_jp/product_quality_scorecard.csv")
    us_r = pd.read_csv("output_stp/market_stp_us/review_scoring_table.csv")
    jp_r = pd.read_csv("output_stp/market_stp_jp/review_scoring_table.csv")
    us_avg = us_r.groupby("product")["rating"].mean().rename("avg_star").reset_index()
    jp_avg = jp_r.groupby("product")["rating"].mean().rename("avg_star").reset_index()
    us_skus = us_q.merge(us_avg, on="product", how="left").dropna(
        subset=list(US_QUAL_COL.values()))
    jp_skus = jp_q.merge(jp_avg, on="product", how="left").dropna(
        subset=list(JP_QUAL_COL.values()))

    URBANER_US = ["B0823PD6XD", "B0BVVKKXFZ", "B0GL2DKVQH", "B0GL2GP74J"]
    URBANER_JP = ["B07CYQVK16", "B07CYZH2XC", "B07CZ3KDN9",
                  "B0BL2YWH3N", "B0DSB44YJZ", "B0G492LXS9"]

    # 讀取設計卡片
    xl = pd.ExcelFile(OUTPUT_DIR / "product_cards.xlsx")
    us_cards = pd.read_excel(xl, sheet_name=0)
    jp_cards = pd.read_excel(xl, sheet_name=1)
    us_cards = us_cards.rename(columns={us_cards.columns[0]: "產品卡"})
    jp_cards = jp_cards.rename(columns={jp_cards.columns[0]: "產品卡"})

    # 執行分析
    us_result = run_market_analysis(
        "US", us_cards, US_COL_MAP, US_LEVEL_MAP,
        US_BETAS, US_QUAL_COL, us_skus, URBANER_US)
    jp_result = run_market_analysis(
        "JP", jp_cards, JP_COL_MAP, JP_LEVEL_MAP,
        JP_BETAS, JP_QUAL_COL, jp_skus, URBANER_JP)

    # 生成報告
    report = [
        "# 產品組合市場競爭力分析（含競品選擇集）",
        "",
        "> **方法**：Multinomial Logit（MNL）偏好份額模型  ",
        "> **選擇集**：24 張設計卡片 ＋ 全市場 SKU（US: 52 個，JP: 36 個）  ",
        "> **公式**：P(i) = exp(Uᵢ) / Σ exp(Uⱼ)，j ∈ 全選擇集  ",
        "> 偏好份額反映「在真實競爭環境下，各產品方案相對於所有競品的市場吸引力」。",
        "",
        "---",
        "",
        "## 一、美國市場（US）",
        "",
        md_group_summary(us_result, "🇺🇸 美國市場"),
        md_full_ranking(us_result, "🇺🇸 美國市場"),
        md_card_ranking(us_result, "🇺🇸 美國市場"),
        md_best_card(us_result, "🇺🇸 美國市場"),
        "---",
        "",
        "## 二、日本市場（JP）",
        "",
        md_group_summary(jp_result, "🇯🇵 日本市場"),
        md_full_ranking(jp_result, "🇯🇵 日本市場"),
        md_card_ranking(jp_result, "🇯🇵 日本市場"),
        md_best_card(jp_result, "🇯🇵 日本市場"),
        "---",
        "",
        "## 三、方法說明與限制",
        "",
        "| 項目 | 說明 |",
        "|---|---|",
        "| 效用函數 | U = Σ (β_mid × mid_dummy + β_high × high_dummy)，β 來自 Split-model Logit |",
        "| 競品效用 | 品質分（0–10）離散化為 Low/Mid/High dummy 後代入同一效用函數 |",
        "| 設計卡片效用 | 卡片屬性水準直接對應 dummy encoding |",
        "| MNL 假設 | IIA（無關替代方案獨立性），競品間替代效果視為對稱 |",
        "| 功能合一數(US) | 完全分離，β 排除，不貢獻效用 |",
        "| 統計推論力 | β 係數 p 值多不顯著，結果為方向性分析 |",
        "",
        "*分析腳本：`card_mnl_market.py`　　輸出路徑：`output_conjoint/`*",
    ]

    md_path = OUTPUT_DIR / "card_mnl_market_report.md"
    md_path.write_text("\n".join(report), encoding="utf-8")
    print(f"[OK] 報告已儲存：{md_path}")

    with pd.ExcelWriter(OUTPUT_DIR / "card_mnl_market.xlsx", engine="openpyxl") as writer:
        us_result.to_excel(writer, sheet_name="US_市場競爭力", index=False)
        jp_result.to_excel(writer, sheet_name="JP_市場競爭力", index=False)
    print("[OK] Excel 已儲存：output_conjoint/card_mnl_market.xlsx")


if __name__ == "__main__":
    main()
