"""
計算 US/JP 各 24 張產品卡片的購買機率，找出最佳產品組合
β 係數來自 conjoint_analysis.py 的 Split-model Dummy Encoding 結果
"""

import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path("output_conjoint")

# ── β 係數（來自 conjoint_analysis.py Split-model Dummy Encoding 實際結果）──
# 格式：{attr: (β_mid, β_high)}
# |β| > 50 視為完全分離不穩定，以 None 處理（不貢獻效用）
# price 不納入效用加總（用於 WTP 計算，非產品組合評分屬性）

US_BETAS = {
    "size":         (-0.9756,  1.2580),   # 機身尺寸       p=1.0（方向性）
    "power_source": (10.5291, 13.8123),   # 電源類型       p≈0.97（方向性）
    "waterproof":   ( 9.1456, 10.6809),   # 防水等級       p≈0.93（方向性）
    "attachments":  (10.5291, 13.8123),   # 附件件數       p≈0.97（方向性）
    "guide_comb":   (-1.7095,  1.8786),   # 長度調整段數   p=1.0（方向性）
    "functions":    (None,     None),     # 功能合一數：完全分離，排除
    "charging":     (11.5446, 13.8734),   # 充電方式(USB-C) p≈0.97（方向性）
}

JP_BETAS = {
    "size":         (-0.5144,  0.4411),   # 機身尺寸       p=1.0（方向性）
    "attachments":  (13.4808, 16.1198),   # 附件件數       p≈0.99（方向性）
    "guide_comb":   (14.1244, 15.6059),   # 長度調整段數   p≈0.99（方向性）
    "precision":    (14.1982, 15.0359),   # 調整精度       p≈0.99（方向性）
    "power_source": (10.6546, 15.0363),   # 電源類型       p≈0.98（方向性）
    "waterproof":   ( 8.8345, 10.1467),   # 防水等級       p≈0.94（方向性）
    "battery_life": ( 8.2661, 10.7511),   # 電池續航時間   p≈0.95（方向性）
}

# ── 水準對應表：卡片文字 → dummy (mid, high)──────────────────────────────────

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

# attr key → 卡片欄位名稱
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


def compute_card_probs(cards_df, betas, col_map, level_map, card_col="產品卡"):
    results = []
    for _, row in cards_df.iterrows():
        U = 0.0
        detail = {}
        for attr, (bm, bh) in betas.items():
            col  = col_map.get(attr)
            lmap = level_map.get(col, {})
            val  = str(row.get(col, "")).strip()
            mid, high = lmap.get(val, (0, 0))
            bm_use = 0.0 if (bm is None or (isinstance(bm, float) and np.isnan(bm))) else bm
            bh_use = 0.0 if (bh is None or (isinstance(bh, float) and np.isnan(bh))) else bh
            contrib = bm_use * mid + bh_use * high
            U += contrib
            detail[col] = val
        results.append({"卡片": row[card_col], "效用值U": round(U, 4), **detail})

    df = pd.DataFrame(results)

    # Z-score 正規化後 logistic 轉換
    u = df["效用值U"].values.astype(float)
    if u.std() > 0:
        u_norm = (u - u.mean()) / u.std()
    else:
        u_norm = u - u.mean()
    df["購買機率"] = np.round(1 / (1 + np.exp(-u_norm)), 4)
    df = df.sort_values("購買機率", ascending=False).reset_index(drop=True)
    df.insert(0, "排名", range(1, len(df) + 1))
    return df


def md_card_table(df, market_label, attr_cols):
    lines = [
        f"### {market_label}",
        "",
        "| 排名 | 卡片 | 購買機率 | 效用值 | " + " | ".join(attr_cols) + " |",
        "|---:|---|---:|---:|" + "|".join(["---"] * len(attr_cols)) + "|",
    ]
    for _, row in df.iterrows():
        attrs = " | ".join(str(row.get(c, "")) for c in attr_cols)
        lines.append(
            f"| {row['排名']} | {row['卡片']} | **{row['購買機率']:.4f}** "
            f"| {row['效用值U']:.4f} | {attrs} |"
        )
    lines.append("")
    return "\n".join(lines)


def md_best_combo(df, market_label, attr_cols):
    best = df.iloc[0]
    lines = [
        f"#### {market_label} 最佳產品組合",
        "",
        f"- **卡片**：{best['卡片']}",
        f"- **購買機率**：{best['購買機率']:.4f}",
        f"- **效用值**：{best['效用值U']:.4f}",
        "",
        "| 屬性 | 最佳水準 |",
        "|---|---|",
    ]
    for col in attr_cols:
        lines.append(f"| {col} | **{best.get(col, '—')}** |")
    lines.append("")
    return "\n".join(lines)


def main():
    xl = pd.ExcelFile(OUTPUT_DIR / "product_cards.xlsx")

    # 讀取卡片（sheet 0 = US，sheet 1 = JP）
    us_cards = pd.read_excel(xl, sheet_name=0)
    jp_cards = pd.read_excel(xl, sheet_name=1)

    # 欄位名稱修正（確保「產品卡」欄存在）
    us_cards = us_cards.rename(columns={us_cards.columns[0]: "產品卡"})
    jp_cards = jp_cards.rename(columns={jp_cards.columns[0]: "產品卡"})

    us_attr_cols = list(US_COL_MAP.values())
    jp_attr_cols = list(JP_COL_MAP.values())

    us_result = compute_card_probs(us_cards, US_BETAS, US_COL_MAP, US_LEVEL_MAP)
    jp_result = compute_card_probs(jp_cards, JP_BETAS, JP_COL_MAP, JP_LEVEL_MAP)

    # ── 報告 ──────────────────────────────────────────────────────────────────
    report = [
        "# 產品組合購買機率分析",
        "",
        "> **方法**：Split-model Dummy Encoding Logistic Conjoint  ",
        "> 各產品卡片視為一個完整產品組合，效用值由各屬性的 part-worth 加總得出，  ",
        "> 經 Z-score 正規化後透過 logistic 轉換為購買機率（0–1）。  ",
        "> 購買機率反映市場整體消費者對各產品組合的**平均偏好傾向**，非個人實際購買預測。",
        "",
        "---",
        "",
        "## 一、美國市場（US）— 24 張產品卡片購買機率排名",
        "",
        md_card_table(us_result, "🇺🇸 美國市場", us_attr_cols),
        "---",
        "",
        "## 二、日本市場（JP）— 24 張產品卡片購買機率排名",
        "",
        md_card_table(jp_result, "🇯🇵 日本市場", jp_attr_cols),
        "---",
        "",
        "## 三、最佳產品組合",
        "",
        md_best_combo(us_result, "🇺🇸 美國市場", us_attr_cols),
        md_best_combo(jp_result, "🇯🇵 日本市場", jp_attr_cols),
        "---",
        "",
        "## 四、方法說明與限制",
        "",
        "| 項目 | 說明 |",
        "|---|---|",
        "| β 係數來源 | conjoint_analysis.py Split-model Dummy Encoding Logistic |",
        "| 效用加總 | U = Σ (β_mid × mid_dummy + β_high × high_dummy) |",
        "| 正規化 | Z-score 正規化避免 logistic 飽和 |",
        "| 價格屬性 | 不納入效用加總（作為 WTP 計算分母） |",
        "| 充電方式(US) | 完全分離問題，係數已清除，不貢獻效用 |",
        "| 統計推論力 | 樣本偏小（US n=52, JP n=36），結果為方向性 |",
        "",
        "*分析腳本：`card_choice_prob.py`　　輸出路徑：`output_conjoint/`*",
    ]

    md_path = OUTPUT_DIR / "card_choice_prob_report.md"
    md_path.write_text("\n".join(report), encoding="utf-8")
    print(f"[OK] 報告已儲存：{md_path}")

    # 也輸出 Excel 方便查閱
    with pd.ExcelWriter(OUTPUT_DIR / "card_choice_prob.xlsx", engine="openpyxl") as writer:
        us_result.to_excel(writer, sheet_name="US_購買機率", index=False)
        jp_result.to_excel(writer, sheet_name="JP_購買機率", index=False)
    print("[OK] Excel 已儲存：output_conjoint/card_choice_prob.xlsx")


if __name__ == "__main__":
    main()
