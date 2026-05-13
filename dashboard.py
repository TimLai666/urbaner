"""URBANER 雙市場戰略儀表板
基於 output_conjoint/ 與 output_stp/ 分析結果。
執行：streamlit run dashboard.py
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


# ─────────────────────────────────────────────────────────────
# 全域設定
# ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
OUT_STP_US = ROOT / "output_stp" / "market_stp_us"
OUT_STP_JP = ROOT / "output_stp" / "market_stp_jp"
OUT_CONJOINT = ROOT / "output_conjoint"

PALETTE = {
    "ink": "#0E1E3D",
    "gold": "#C9A36F",
    "gold_soft": "#E5C896",
    "bg": "#F8F6F1",
    "bg_card": "#FFFFFF",
    "charcoal": "#1C1E22",
    "muted": "#6B7280",
    "line": "#E5E1D8",
    "us": "#2E5BFF",
    "us_soft": "#B8C7FF",
    "jp": "#D32F4D",
    "jp_soft": "#F2B5C2",
    "good": "#2E8B57",
    "warn": "#D97706",
}

st.set_page_config(
    page_title="URBANER 雙市場戰略儀表板",
    page_icon="🪒",
    layout="wide",
    initial_sidebar_state="auto",
)


# ─────────────────────────────────────────────────────────────
# 視覺樣式（CSS）
# ─────────────────────────────────────────────────────────────
def inject_css() -> None:
    st.markdown(
        f"""
        <style>
            html, body, [data-testid="stAppViewContainer"] {{
                background: {PALETTE['bg']};
                font-family: 'Inter', 'Noto Sans TC', 'Hiragino Sans', sans-serif;
                color: {PALETTE['charcoal']};
            }}
            [data-testid="stHeader"] {{ background: transparent; }}
            [data-testid="stAppDeployButton"],
            [data-testid="stMainMenu"] {{
                display: none;
            }}
            .modebar-container {{
                display: none !important;
            }}
            .js-plotly-plot .xtick text,
            .js-plotly-plot .ytick text,
            .js-plotly-plot .gtitle,
            .js-plotly-plot .legend text,
            .js-plotly-plot .annotation-text,
            .js-plotly-plot .xtitle,
            .js-plotly-plot .ytitle {{
                fill: {PALETTE['ink']} !important;
                color: {PALETTE['ink']} !important;
            }}
            section[data-testid="stSidebar"] {{
                background: {PALETTE['ink']};
            }}
            section[data-testid="stSidebar"] * {{
                color: {PALETTE['bg']} !important;
            }}
            section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] hr {{
                border-color: rgba(255,255,255,0.15);
            }}
            .block-container {{ padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1380px; }}
            h1, h2, h3, h4 {{ color: {PALETTE['ink']}; letter-spacing: 0; }}
            /* Hero */
            .hero {{
                background: linear-gradient(135deg, {PALETTE['ink']} 0%, #182d5e 60%, #243b73 100%);
                border-radius: 22px;
                padding: 28px 36px;
                color: #F8F6F1;
                margin-bottom: 18px;
                box-shadow: 0 18px 40px -22px rgba(14,30,61,0.55);
                position: relative;
                overflow: hidden;
            }}
            .hero::before {{
                content: "";
                position: absolute; right: -120px; top: -120px;
                width: 320px; height: 320px;
                background: radial-gradient(circle, {PALETTE['gold']}33 0%, transparent 70%);
                border-radius: 50%;
            }}
            .hero h1 {{
                color: #fff; margin: 0; font-size: 2.0rem; font-weight: 700; letter-spacing: 0;
            }}
            .hero .sub {{
                color: {PALETTE['gold_soft']}; margin-top: 6px; font-size: 0.95rem;
                letter-spacing: 0.04em; text-transform: uppercase;
            }}
            .hero .tagline {{
                margin-top: 14px; max-width: 760px; font-size: 1.0rem; color: #E8E5DC; line-height: 1.6;
            }}
            /* KPI cards */
            .kpi {{
                background: {PALETTE['bg_card']};
                border: 1px solid {PALETTE['line']};
                border-radius: 16px;
                padding: 18px 20px;
                box-shadow: 0 6px 16px -10px rgba(0,0,0,0.18);
            }}
            .kpi .label {{
                color: {PALETTE['muted']}; font-size: 0.78rem;
                text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;
            }}
            .kpi .value {{
                color: {PALETTE['ink']}; font-size: 1.85rem; font-weight: 700;
                margin-top: 4px; line-height: 1.1;
            }}
            .kpi .delta {{
                color: {PALETTE['gold']}; font-size: 0.82rem; margin-top: 4px;
                font-weight: 600;
            }}
            .kpi.us {{ border-top: 4px solid {PALETTE['us']}; }}
            .kpi.jp {{ border-top: 4px solid {PALETTE['jp']}; }}
            .kpi.gold {{ border-top: 4px solid {PALETTE['gold']}; }}
            /* Section card — 用 :has(.card-head) 鎖定 st.container(border=True) 容器 */
            [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"]
                .card-head) {{
                background: {PALETTE['bg_card']};
                border: 1px solid {PALETTE['line']} !important;
                border-radius: 18px !important;
                padding: 22px 26px 18px 26px !important;
                box-shadow: 0 6px 16px -10px rgba(0,0,0,0.10);
                margin-bottom: 18px;
            }}
            .card-head h3 {{
                margin: 0 0 14px 0;
                font-size: 1.12rem;
                color: {PALETTE['ink']};
                font-weight: 700;
            }}
            /* 同列卡片高度等高 */
            [data-testid="stHorizontalBlock"] {{
                align-items: stretch;
                gap: 1rem;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                display: flex;
                flex-direction: column;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]
                > [data-testid="stVerticalBlock"] {{
                flex: 1;
            }}
            [data-testid="stHorizontalBlock"] [data-testid="stColumn"]
                [data-testid="stLayoutWrapper"] {{
                height: 100%;
            }}
            [data-testid="stHorizontalBlock"] [data-testid="stColumn"]
                [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {{
                height: 100%;
                display: flex;
                flex-direction: column;
            }}
            /* spec/rec — 同樣讓同列等高 */
            [data-testid="stHorizontalBlock"] [data-testid="stColumn"] .spec,
            [data-testid="stHorizontalBlock"] [data-testid="stColumn"] .rec {{
                height: 100%;
                box-sizing: border-box;
            }}
            .pill {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 600;
                margin-right: 6px;
                letter-spacing: 0.05em;
            }}
            .pill.us {{ background: {PALETTE['us_soft']}; color: {PALETTE['us']}; }}
            .pill.jp {{ background: {PALETTE['jp_soft']}; color: {PALETTE['jp']}; }}
            .pill.gold {{ background: #F4E4C5; color: #8B6914; }}
            .pill.good {{ background: #D4F4DD; color: {PALETTE['good']}; }}
            .pill.warn {{ background: #FCE7C2; color: {PALETTE['warn']}; }}
            .insight-list {{
                display: grid;
                gap: 18px;
                padding: 4px 0 2px 0;
            }}
            .insight-row {{
                display: grid;
                grid-template-columns: 14px minmax(0, 1fr);
                column-gap: 14px;
                align-items: start;
            }}
            .insight-dot {{
                width: 6px;
                height: 6px;
                border-radius: 999px;
                background: {PALETTE['charcoal']};
                margin-top: 12px;
            }}
            .insight-title {{
                display: flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
                color: {PALETTE['ink']};
                font-size: 1.02rem;
                font-weight: 800;
                line-height: 1.4;
                margin-bottom: 5px;
            }}
            .insight-title .pill {{
                margin-right: 0;
                margin-bottom: 0;
                flex: 0 0 auto;
            }}
            .insight-body {{
                color: {PALETTE['charcoal']};
                font-size: 0.95rem;
                line-height: 1.78;
            }}
            .insight-body code {{
                background: #E9F8EF;
                color: #047857;
                border-radius: 5px;
                padding: 1px 5px;
                font-size: 0.88rem;
                font-weight: 700;
            }}
            /* Recommendation card */
            .rec {{
                background: linear-gradient(180deg, #ffffff 0%, #fbf8f1 100%);
                border-left: 4px solid {PALETTE['gold']};
                border-radius: 14px;
                padding: 18px 22px;
                margin-bottom: 14px;
                box-shadow: 0 4px 14px -10px rgba(0,0,0,0.18);
            }}
            .rec.us {{ border-left-color: {PALETTE['us']}; }}
            .rec.jp {{ border-left-color: {PALETTE['jp']}; }}
            .rec .title {{
                font-weight: 700; color: {PALETTE['ink']}; font-size: 1.05rem; margin-bottom: 6px;
            }}
            .rec .body {{ color: {PALETTE['charcoal']}; line-height: 1.65; font-size: 0.93rem; }}
            .rec .kpi-tag {{
                margin-top: 10px; font-size: 0.78rem;
                color: {PALETTE['muted']}; font-weight: 600;
                letter-spacing: 0.04em;
            }}
            /* Best product spec card */
            .spec {{
                background: linear-gradient(160deg, {PALETTE['ink']} 0%, #1d3160 100%);
                color: #F8F6F1; border-radius: 18px;
                padding: 22px 26px;
                box-shadow: 0 12px 28px -14px rgba(14,30,61,0.6);
            }}
            .spec.jp {{
                background: linear-gradient(160deg, #58101c 0%, #8a1f2f 100%);
            }}
            .spec h4 {{
                color: {PALETTE['gold_soft']}; margin: 0 0 4px 0; letter-spacing: 0.06em;
                text-transform: uppercase; font-size: 0.8rem;
            }}
            .spec .name {{
                font-size: 1.55rem; font-weight: 700; color: #fff; margin-bottom: 6px;
            }}
            .spec .meta {{
                color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-bottom: 14px;
            }}
            .spec table {{ width: 100%; border-collapse: collapse; }}
            .spec td {{
                padding: 8px 0;
                border-bottom: 1px solid rgba(255,255,255,0.12);
                font-size: 0.92rem;
            }}
            .spec td:first-child {{ color: rgba(255,255,255,0.65); }}
            .spec td:last-child {{ color: {PALETTE['gold_soft']}; font-weight: 600; text-align: right; }}
            /* Footer */
            .footer {{
                color: {PALETTE['muted']}; font-size: 0.78rem; text-align: center;
                padding: 18px 0 4px 0; border-top: 1px solid {PALETTE['line']}; margin-top: 30px;
            }}
            @media (max-width: 768px) {{
                .block-container {{
                    padding: 2.65rem 1rem 2.25rem 1rem;
                }}
                .hero {{
                    border-radius: 18px;
                    padding: 24px 28px;
                    margin-top: 0.25rem;
                    margin-bottom: 16px;
                }}
                .hero::before {{
                    right: -180px;
                    top: -180px;
                }}
                .hero h1 {{
                    font-size: 1.75rem;
                    line-height: 1.22;
                }}
                .hero .sub {{
                    font-size: 0.82rem;
                    line-height: 1.35;
                }}
                .hero .tagline {{
                    max-width: none;
                    font-size: 0.95rem;
                    line-height: 1.72;
                }}
                .kpi {{
                    border-radius: 14px;
                    padding: 17px 20px;
                    margin-bottom: 0.1rem;
                }}
                .kpi .label,
                .kpi .delta {{
                    line-height: 1.45;
                }}
                .kpi .value {{
                    font-size: 1.62rem;
                    overflow-wrap: anywhere;
                }}
                [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"]
                    .card-head) {{
                    border-radius: 16px !important;
                    padding: 18px 18px 16px 18px !important;
                    margin-bottom: 16px;
                }}
                .card-head h3 {{
                    font-size: 1rem;
                    line-height: 1.38;
                }}
                .pill {{
                    margin-bottom: 4px;
                    line-height: 1.4;
                    white-space: normal;
                }}
                .insight-list {{
                    gap: 16px;
                }}
                .insight-row {{
                    grid-template-columns: 10px minmax(0, 1fr);
                    column-gap: 10px;
                }}
                .insight-title {{
                    font-size: 0.98rem;
                    line-height: 1.45;
                }}
                .insight-body {{
                    font-size: 0.92rem;
                    line-height: 1.75;
                }}
                .rec {{
                    padding: 16px 18px;
                    border-radius: 12px;
                }}
                .spec {{
                    border-radius: 16px;
                    padding: 18px 18px;
                    overflow-x: auto;
                }}
                .spec .name {{
                    font-size: 1.32rem;
                    overflow-wrap: anywhere;
                }}
                .spec td {{
                    font-size: 0.86rem;
                    line-height: 1.45;
                }}
                .spec td:last-child {{
                    padding-left: 12px;
                    text-align: left;
                }}
            }}
            @media (max-width: 420px) {{
                .block-container {{
                    padding-left: 0.85rem;
                    padding-right: 0.85rem;
                }}
                .hero {{
                    padding: 22px 22px;
                }}
                .hero h1 {{
                    font-size: 1.62rem;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# 資料（從報告中精煉）
# ─────────────────────────────────────────────────────────────
ATTR_IMPORTANCE_US = pd.DataFrame(
    [
        ("功能合一數", 51.5, "Multi-function"),
        ("充電方式(USB-C)", 10.5, "USB-C Charging"),
        ("電源類型", 10.4, "Power Source"),
        ("附件件數", 10.4, "Accessories"),
        ("防水等級", 8.1, "Waterproof"),
        ("價格帶", 4.6, "Price Tier"),
        ("長度調整段數", 2.7, "Length Steps"),
        ("機身尺寸", 1.7, "Form Factor"),
    ],
    columns=["屬性", "重要性", "label_en"],
)

ATTR_IMPORTANCE_JP = pd.DataFrame(
    [
        ("價格帶", 16.9, "Price Tier"),
        ("附件件數", 16.0, "Accessories"),
        ("長度調整段數", 15.5, "Length Steps"),
        ("調整精度", 14.9, "Precision (mm)"),
        ("電源類型", 14.9, "Power Source"),
        ("電池續航時間", 10.7, "Battery Life"),
        ("防水等級", 10.1, "Waterproof"),
        ("機身尺寸", 0.9, "Form Factor"),
    ],
    columns=["屬性", "重要性", "label_en"],
)

ANOVA_US_TOP = pd.DataFrame(
    [
        ("gift_suitability_men", 1299.5, "送禮場景"),
        ("primary_user_gender", 1196.5, "使用者性別"),
        ("num_grooming_functions", 1193.3, "多功能套組"),
        ("total_attachments_count", 1014.9, "附件件數"),
        ("attachment_fitment", 975.3, "附件密合度"),
        ("power_source_type", 941.0, "電源類型"),
        ("waterproof_rating_ipx8", 902.8, "防水 IPX8"),
        ("guide_comb_variety", 902.3, "梳齒款式"),
        ("multi_use_versatility_score", 778.9, "多場景使用"),
        ("quick_touch_up_design", 708.7, "快速修整設計"),
    ],
    columns=["attribute", "F", "中文"],
)

ANOVA_JP_TOP = pd.DataFrame(
    [
        ("total_attachments_count", 2630.4, "附件件數"),
        ("guide_comb_variety", 2412.2, "梳齒款式"),
        ("adjustable_comb_settings", 1827.0, "可調梳齒"),
        ("attachment_fitment", 1723.2, "附件密合度"),
        ("product_dimensions_size", 1004.7, "機身尺寸"),
        ("power_source_type", 543.1, "電源類型"),
        ("rechargeable_design", 497.5, "充電式設計"),
        ("beard_trimming_function", 494.5, "鬍鬚修整"),
        ("waterproof_rating_ipx8", 460.9, "防水 IPX8"),
        ("battery_independence", 346.7, "電池獨立性"),
    ],
    columns=["attribute", "F", "中文"],
)

SEGMENTS_US = pd.DataFrame(
    [
        ("S1：父親節送禮客", 850, 19.5, 3.68,
         "Beard 87.5% / Nose-Ear 6.8% / Body 5.6%",
         "為男士挑禮：在意送禮場景、性別感、附件齊全度"),
        ("S2：日常自用大眾", 3337, 76.5, 3.18,
         "Beard 94.8% / Nose-Ear 4.2% / Body 1.0%",
         "買來自己每天用：在意鬍鬚與耳鼻、耐用、可充電"),
        ("S3：USB-C 高端鐵粉", 173, 4.0, 4.48,
         "Beard 75.7% / Body 17.9% / Nose-Ear 6.4%",
         "願付溢價：USB-C 充電、Beard+Body 多場景、滿意度最高"),
    ],
    columns=["區隔", "人數", "占比%", "Avg★", "類別組成", "他們是誰"],
)

SEGMENTS_JP = pd.DataFrame(
    [
        ("S1：CP 值優先大眾", 6559, 91.6, 3.46,
         "Nose-Ear 59.4% / Beard 40.6%",
         "節儉派：愛乾電池款、鼻毛 + 鬍鬚兩用、看重耐用易用"),
        ("S2：鬍鬚講究客", 561, 7.8, 4.01,
         "Beard 75.2% / Nose-Ear 24.8%",
         "深度玩家：38 段精度、多附件、機身大小錙銖必較"),
        ("S3：靜音低振敏感族", 43, 0.6, 3.05,
         "Nose-Ear 62.8% / Beard 37.2%",
         "小眾利基：怕噪音、怕震動、對馬達品質敏感"),
    ],
    columns=["區隔", "人數", "占比%", "Avg★", "類別組成", "他們是誰"],
)

HERO_SKU_US = {
    "asin": "B0FL267TCG",
    "category": "Beard / Mustache Trimmers",
    "distance": 1.601,
    "n_reviews": 29,
    "avg_star": 4.52,
    "preference_share": 39.35,
}
HERO_SKU_JP = {
    "asin": "B0GBWZBMS5",
    "category": "Nose / Ear Trimmers",
    "distance": 1.97,
    "n_reviews": 61,
    "avg_star": 4.61,
    "preference_share": 11.26,
}

BEST_CARD_US = {
    "card": "USB-C × 38 段多附件款",
    "tagline": "全速 USB-C × ≥10 件套組 × 標準機身 × IPX4",
    "p_buy": 0.8326,
    "utility": 51.55,
    "specs": [
        ("長度調整段數", "≥38段"),
        ("電源類型", "USB-C"),
        ("附件件數", "≥10件"),
        ("充電方式", "USB-C 快充"),
        ("機身尺寸", "標準"),
        ("功能合一", "1合1"),
        ("防水", "IPX4"),
    ],
}
BEST_CARD_JP = {
    "card": "IPX7 × 90 分高續航全配款",
    "tagline": "IPX7+ × ≥10 件 × 1mm 刻度 × 大型機身 × USB-C",
    "p_buy": 0.8905,
    "utility": 81.86,
    "specs": [
        ("長度調整段數", "≥38段"),
        ("附件件數", "≥10件"),
        ("電源類型", "USB-C"),
        ("電池續航", "90分鐘+"),
        ("防水", "IPX7+"),
        ("調整精度", "1mm 刻度"),
        ("機身尺寸", "大型"),
    ],
}

# 屬性升級可帶來的偏好份額提升（路線B 模擬）
UPGRADE_US = pd.DataFrame(
    [
        ("機身尺寸", 0.0, 0.7),
        ("附件件數", 0.0, 0.2),
        ("長度調整段數", 0.0, 0.2),
        ("功能合一數", 0.0, 0.1),
        ("充電方式(USB-C)", 0.0, 0.1),
        ("防水等級", 0.0, 0.1),
        ("電源類型", 0.0, 0.0),
    ],
    columns=["升級屬性", "現況份額%", "升至 High 份額%"],
)
UPGRADE_JP = pd.DataFrame(
    [
        ("長度調整段數", 1.6, 94.8),
        ("調整精度", 1.6, 86.2),
        ("附件件數", 1.6, 52.0),
        ("電源類型", 1.6, 44.9),
        ("機身尺寸", 1.6, 7.5),
        ("電池續航時間", 1.6, 3.1),
        ("防水等級", 1.6, 2.8),
    ],
    columns=["升級屬性", "現況份額%", "升至 High 份額%"],
)

# Conjoint WTP（路線A，補真實售價後重估）
WTP_US = pd.DataFrame(
    [
        ("機身尺寸", 89.81, 0.0209, True),
        ("附件件數", 79.86, 0.0172, True),
        ("長度調整段數", 78.18, 0.0114, True),
        ("功能合一數", 59.07, 0.0244, True),
        ("充電方式(USB-C)", 32.39, 0.0346, True),
        ("電源類型", 26.27, 0.0799, False),
        ("防水等級", 24.39, 0.0929, False),
    ],
    columns=["屬性", "WTP (USD/品質分)", "p", "顯著"],
)
WTP_JP = pd.DataFrame(
    [
        ("長度調整段數", 7961, 0.0419, True),
        ("調整精度", 6774, 0.0241, True),
        ("附件件數", 5207, 0.0221, True),
        ("電源類型", 4336, 0.0528, False),
        ("電池續航時間", 4306, 0.0304, True),
        ("機身尺寸", 1812, 0.2128, False),
        ("防水等級", 909, 0.2278, False),
    ],
    columns=["屬性", "WTP (JPY/品質分)", "p", "顯著"],
)

# 行銷劇本
PLAYBOOK_US = [
    {
        "title": "🎁 父親節 × 黑五雙旺季：Gift-Ready 主訴求",
        "body": "Listing A+ 第一屏放「Perfect Gift for Him」訴求，包裝設計可直接送禮（不需重新包裝）。"
                "Q2（5–6 月）父親節主題禮盒、Q4（10–12 月）聖誕節 + 黑五禮物指南。"
                "對映 ANOVA Top1 `gift_suitability_men`（F=1299.5）。",
        "kpi": "目標 Q2/Q4 銷售環比 +35%，Gift 關鍵字 PPC ROAS ≥ 4.5",
    },
    {
        "title": "📦 5-in-1 / 7-in-1 套組為核心 SKU 形態",
        "body": "主圖右上角加件數徽章（≥7 件），主圖第二張示意「all-in-one」功能拼貼。"
                "對映美國重要性 Top1 `功能合一數`（51.5%）+ `附件件數`（10.4%）。",
        "kpi": "主圖 CTR +20%，套組型 SKU 占月銷 ≥ 60%",
    },
    {
        "title": "⚡ USB-C × IPX7 高端標配",
        "body": "Listing 首條 bullet 明確標示電源類型 + USB-C 充電 icon；"
                "主圖右下角嵌入 IPX7 badge，對抗 Manscaped Lawn Mower 5.0 Ultra。",
        "kpi": "高端關鍵字（cordless / waterproof）轉換率 +18%",
    },
    {
        "title": "🇯🇵 日系工藝差異化敘事 vs Wahl / Andis",
        "body": "強調 1977 年起 50 年代工背景與日系刀片工藝（Japanese OEM heritage），對應 Maslow esteem。"
                "建議價格帶 $60–$120，定位於 Conair 之上、Braun Series 9 Pro 之下。",
        "kpi": "品牌搜尋量月成長 +15%，平均客單價 ≥ $79",
    },
]

PLAYBOOK_JP = [
    {
        "title": "🔢 具體數字主導 Listing：規格即賣點",
        "body": "Bullet-1：アタッチメント X 個 / 長さ調整 X 段階（0.5mm 単位）。"
                "Bullet-2：稼働時間 XX 分 / IPX7 防水 / 騒音 XX dB。"
                "對映 ANOVA Top1-3：附件件數（F=2630）、梳齒款式（F=2412）、可調梳齒（F=1827）。",
        "kpi": "Listing 加購率 +25%，2 件以上組合銷售比 ≥ 35%",
    },
    {
        "title": "🏆 権威佐證：専門家・サロン・医療クリニック",
        "body": "在主圖與評論區強化「専門家監修」「サロン推奨」「医療クリニック共同開発」表述。"
                "與 Panasonic ER-GB74-S、Maxell IZN-C240-K 並列規格表，明示 0.5mm 刻度差異。",
        "kpi": "Q3 末權威 PR 露出 ≥ 8 篇，品牌搜尋成長 +20%",
    },
    {
        "title": "🔋 雙線並行：乾電池款別倉促淘汰",
        "body": "JP 最大族群「CP 值優先大眾（S1，91.6%）」仍偏好乾電池款（B07XTLC91J 系列）。"
                "保留乾電池產品線作穩定收入；USB-C 款主打「鬍鬚講究客（S2，7.8%，★4.01）」高滿意度族群。",
        "kpi": "乾電池 SKU 維持月銷量基準 ±5%，USB-C 款 Avg★ ≥ 4.3",
    },
    {
        "title": "🎌 父の日 × 楽天直営：在地化檔期",
        "body": "6 月第三個週日（父の日）：禮盒包裝 + のし対応。"
                "強化楽天市場「URBANER 直営正規品 + 1 年保証」訴求（台灣廠商稀缺資格）。"
                "措辭：身嗜み（みだしなみ）、自然な仕上がり、丸洗いできる。",
        "kpi": "父の日檔期銷售環比 +40%，楽天直営店月銷成長 +25%",
    },
]

PLAYBOOK_COMMON = [
    {
        "title": "💧 IPX7+ 為新品最低門檻",
        "body": "兩市場 ANOVA 都顯示防水為差異化錨點（US 排名 7、JP 排名 9，皆顯著）。"
                "任何 2026 新 SKU 開發以 IPX7 為起點。",
    },
    {
        "title": "🧰 套組 ≥7 件為主流規格",
        "body": "兩市場區隔皆把 `total_attachments_count` 列為 Top 屬性；"
                "新 SKU 套組設計從 4-piece 起跳，理想 7-piece。",
    },
    {
        "title": "🎯 Hero SKU 差異化集中投放",
        "body": "美國資源集中 B0FL267TCG（Beard / Mustache）；"
                "日本資源集中 B0GBWZBMS5（Nose / Ear）。不可互用主推品。",
    },
]


# ── 社群研究資料 ─────────────────────────────────────────────
# 完整社群資料來源 — 每個平台單獨一行，附類型與引用條數
# 引用條數 = 從該平台抓出可用於 insights.md 的觀察筆記數量（質性 WebSearch 合成）
SOCIAL_SOURCES_US = pd.DataFrame(
    [
        ("Reddit", "綜合論壇", 28),
        ("Badger & Blade（B&B）", "刮鬍專門社群", 14),
        ("Sharpologist", "刮鬍評測站", 10),
        ("Whole Dog Journal", "寵物美容雜誌", 9),
        ("ShavingAdvisor", "刮鬍評測站", 8),
        ("redditfavorites.com", "Reddit 聚合站", 7),
        ("TechGearLab", "工具評測站", 5),
        ("Dogster", "寵物評測 Blog", 4),
        ("FashionBeans", "男士 Lifestyle Blog", 4),
        ("HairClippersClub", "刮鬍評測 Blog", 4),
        ("Happy Hounds Grooming", "寵物美容站", 3),
        ("ShaverCheck", "刮鬍評測站", 3),
        ("PoodleForum", "貴賓犬主論壇", 2),
        ("MetaFilter", "綜合論壇", 2),
        ("Bogleheads", "理財／生活綜合論壇", 1),
        ("ResetEra", "綜合論壇", 1),
    ],
    columns=["平台", "類型", "引用條數"],
)

SOCIAL_SOURCES_JP = pd.DataFrame(
    [
        ("Yahoo!知恵袋", "Q&A 論壇", 22),
        ("マイベスト（my-best.com）", "編輯部排行榜", 18),
        ("価格.com（kakaku.com）", "比價 + 評論", 16),
        ("Amazon JP", "電商評論", 14),
        ("楽天みんなのレビュー", "電商評論", 10),
        ("家電 Watch（Impress Watch）", "家電新聞站", 5),
        ("シェーバー比較.com", "刮鬍比較 Blog", 4),
        ("LIPS（lipscosme.com）", "美容評論社群", 4),
        ("note", "個人部落格", 4),
        ("LDK", "雜誌實測（評論轉述）", 3),
        ("5ch 家電板", "匿名論壇 thread", 3),
        ("BIGLOBE 暮らし", "編輯部 Blog", 2),
        ("きちデン", "家電 Blog", 2),
        ("NOJIMA", "通路編輯部", 2),
        ("PEPPY（peppynet.com）", "寵物資訊站", 2),
        ("Petio", "寵物資訊站", 2),
        ("PETOKOTO", "寵物資訊站", 2),
        ("TrustCellar", "美容 Blog", 2),
        ("みんなのブリーダー", "寵物資訊站", 1),
    ],
    columns=["平台", "類型", "引用條數"],
)

# 向後相容 — 仍提供平台名稱 list 給其他地方參考
SOCIAL_PLATFORMS_US = SOCIAL_SOURCES_US["平台"].tolist()
SOCIAL_PLATFORMS_JP = SOCIAL_SOURCES_JP["平台"].tolist()

CROSS_INSIGHTS_US = [
    ("🔈", "靜音是 2024-2026 最強買點", "寵物、嬰兒、男士全身刮鬚全面席捲"),
    ("💡", "LCD/LED 電量顯示", "從高端配件變成中階入門款基本配備"),
    ("🔌", "USB-C 已成新標配", "舊式 micro-USB 開始被嫌"),
    ("💧", "IPX7 防水接近所有正式款的基線", "Manscaped 5.0 Ultra 帶起的標準"),
    ("🧰", "一機多用受歡迎但實際只用 1-2 個附件", "套組形態為主、行銷與實用之間有落差"),
    ("🔋", "電池焦慮：使用中沒電是最大不滿", "battery indicator 為必要 UX"),
    ("🎨", "顏色／外型影響女性 + 嬰兒類購買大", "男性類則重視 professional 感"),
    ("🚀", "Manscaped 行銷成功", "用戶會主動搜尋『Manscaped 替代品』"),
    ("🏥", "醫療診所／脫毛診所推薦", "跨市場信任度（如 Panasonic ES-WF41）"),
    ("📦", "包裝/開箱印象會被寫入評論", "看起來像退貨品 = 1 星差評風險"),
]
CROSS_INSIGHTS_JP = [
    ("🔇", "「静音」ブーム在日本更強", "寵物・嬰兒・男士剃鬚全領域筆頭"),
    ("📏", "デシベル数値の明示成為標準", "60dB → 50dB → 38dB 規格競爭"),
    ("⭐", "マイベスト・価格.com・LDK 決定性影響", "特別是 マイベスト #1 帶來的轉換"),
    ("👨‍⚕️", "理容師・トリマー・医療クリニック監修", "日本特有的「専門家お墨付き」行銷"),
    ("🏆", "Panasonic 在男士・身體・嬰兒類別壟斷", "幾乎不容外資直接挑戰"),
    ("🇯🇵", "「日本製」訴求在爪切等職人技領域強勢", "猫壱、貝印是代表"),
    ("💋", "VIO 敏感部位市場近年急速擴大", "含男士族群"),
    ("📚", "知恵袋 對 40 歲以上影響力大", "ブラウン vs パナソニック 是定番題"),
    ("✍️", "note 是年輕層 DIY 體驗 sharing 主場", "自宅美容内容增多"),
    ("🧵", "5ch 家電板 ヒゲトリマー 専用 thread", "マニア深掘"),
    ("🔁", "手動式根深柢固", "鼻毛（皇家銀彈）、爪切（貝印・猫壱）"),
    ("🌏", "Amazon JP 評價會被翻譯外溢", "韓國・東南亞跨境市場"),
]

# 9 類別深度洞察 — 痛點 / 好評 / 競品
SOCIAL_CATEGORIES = {
    "001 Beard / Mustache Trimmer": {
        "us": {
            "pain": ["廉價款拉扯毛髮、不貼皮膚", "充電 15-16 小時太長", "配件容易壞", "包裝像退貨重售"],
            "love": ["重量感／紮實感", "多 attachment 給長度控制力", "LCD 顯示電量 + 速度", "防水/Wet+Dry 兩用"],
            "brands": ["Braun Series 9 Pro 9460cc（敏感肌）", "Braun + ProGlide 6 件套（性價比）", "Wahl 漸被淘汰", "Andis、ANGFAN 高速無刷馬達崛起"],
        },
        "jp": {
            "pain": ["充電 15-16 時間", "肌荒れ・カミソリ負け", "切れ味が落ちる", "「部分耐水」表記紛らわしい", "電源スイッチが硬い"],
            "love": ["0.5mm 単位の 38-40 段階", "丸洗いできる防水", "LCD ＋ バッテリー表示", "ヒゲ吸引機能", "リチウムイオン長持ち"],
            "brands": ["Panasonic ER-GB74-S（45° 鋭利刃 38段）", "Panasonic ER-SB60-S（リニア）", "Philips MG3720/15（多附件）", "家電量販店一押 Panasonic"],
        },
    },
    "002 Nose / Ear Trimmer": {
        "us": {
            "pain": ["旋轉式刀頭拉毛", "買 5 種電動款仍不滿意", "鼻黏膜被拉極痛", "電池款掃興"],
            "love": ["「無痛」是頭號賣點", "安靜的馬達聲", "美容診所推薦有可信度", "LED 電量顯示"],
            "brands": ["Philips Norelco（低噪音）", "ToiletTree（Reddit 推薦）", "皇家 ET-3 手動款（小眾忠誠）", "Panasonic ER-GN21-K（JP 主導）"],
        },
        "jp": {
            "pain": ["切れ味落ちると毛を引っ張る", "電池式の替え電池面倒", "深く挿入すると痛い", "髪の毛が機械内部に詰まる"],
            "love": ["「ほとんど痛くない」が大半", "丸洗いできる本体", "IPX7 防水", "毛くず吸引機能", "手動式の「永久使える」"],
            "brands": ["Panasonic ER-GN71-K（絶対王者）", "Maxell IZN-C240-K（マイベスト#1）", "日立（手頃価格＋IPX7）", "皇家 ET-3（手動派の隠れ名作）"],
        },
    },
    "003 Body Groomer / VIO": {
        "us": {
            "pain": ["鈍刀/髒刀導致拉扯", "無 guard 容易割傷（陰囊）", "走路後保養不足會 razor bumps"],
            "love": ["緩慢移動 + 拉緊皮膚無 nicks", "IPX7 浴室使用", "充電底座是高端標誌", "Wet/Dry 兩用必備"],
            "brands": ["Manscaped Lawn Mower 5.0 Ultra（黃金標準）", "Philips Norelco Bodygroom（敏感區）", "INVJOY、Meridian（預算）"],
        },
        "jp": {
            "pain": ["剃り残し（膝裏・背中）", "チクチク感、ヒリヒリ感", "VIO 周りの安全性不安"],
            "love": ["ヒリヒリ感ほとんどない", "刃が肌に直接触れない安全設計", "水洗い・浴室 OK"],
            "brands": ["Panasonic ER-GK60-W / GK81-S（日本独占）", "Philips Bodygroom（外資派）"],
        },
    },
    "004 Eyebrow / Face Shaver": {
        "us": {
            "pain": ["機械感重的款式女性嫌不夠精緻", "旋轉刀頭精度不夠", "刀片角度不適合眉毛輪廓"],
            "love": ["診所推薦最有說服力", "粉色/玫紅影響女性決策", "一機多用（眉+鼻+臉）", "無痛訴求"],
            "brands": ["Panasonic ES-WF41 系列（醫療指定）", "NUMIFUN、Ginity（LED + 顏色新興）"],
        },
        "jp": {
            "pain": ["カミソリ負けからの脱出", "機械感が強い", "細かい眉毛輪郭が削れない"],
            "love": ["「カミソリ負けしなくなった」", "眉カバー＋コーム", "4mm まで保護", "医療脱毛クリニック推奨"],
            "brands": ["Panasonic フェリエ ES-WF41-P（圧倒的 No.1, ¥2,000）"],
        },
    },
    "005 Foil Shaver": {
        "us": {
            "pain": ["毛屑掉滿衣服與地板", "Braun 清洗 cartridge 成本高", "鈍刀後性能急劇下降"],
            "love": ["Foil = 最貼皮膚（barber shop close）", "Lambdash 線性馬達不卡毛", "Quiet operation"],
            "brands": ["Braun Series 9（頂級）", "Panasonic Arc 5/Lambdash（CP值）", "BaBylissPRO FX3（理髮師）", "Philips Norelco（旋轉式輕便）"],
        },
        "jp": {
            "pain": ["朝剃って夕方に少し生える", "バッテリー老化", "価格が高い", "フィリップス回転式肌荒れ報告"],
            "love": ["14,000 ストローク/分 + AI 髭濃さ自動制御", "敏感肌で快適", "5層・6層刃"],
            "brands": ["Panasonic Lambdash ES-NLV68-K（日本最強）", "Braun Series 9 Pro", "Philips Series", "IZUMI 低價", "BaBylissPRO 理容師"],
        },
    },
    "006 Pet Electric Clipper": {
        "us": {
            "pain": ["噪音嚇到寵物", "連續使用 15 分發燙", "厚毛 clog", "肉球間刈不到"],
            "love": ["<60dB 對話音量", "振動小不嚇敏感狗", "5-in-1 可調刀片", "輕量機身"],
            "brands": ["Oneisall（Reddit 最安靜入門）", "Wahl Arco（professional 級）", "Yabife（超值）", "Pateker（JP 主導）"],
        },
        "jp": {
            "pain": ["動作音が大きい", "バリカン負け", "発熱", "アタッチメント間に毛詰まり"],
            "love": ["静音設計", "切れ味抜群", "軽量", "充電式コードレス", "12,000Pa 吸引一体型"],
            "brands": ["Pateker（20 年プロ推薦・No.1）", "Looffy", "oneisall 4-in-1（海外勢）", "Panasonic ER-PA10-W"],
        },
    },
    "007 Pet Nail Clipper": {
        "us": {
            "pain": ["黑指甲看不到血線", "高齡飼主握不穩", "大型犬指甲又厚又難剪", "nail guard 鬆動"],
            "love": ["雙面切（plier 式）對狗較溫和", "Millers Forge 維持 1-2 年鋒利", "用鈍直接換新"],
            "brands": ["Millers Forge B07DGMGSYQ（主流）", "Resco SuperCut（traditional）", "HAWATOUR + guard（JP 主流）"],
        },
        "jp": {
            "pain": ["黒爪は血管が見えない", "怖がって暴れる", "切りっぱなしでザラザラ"],
            "love": ["安全ガード付き", "双刃 plier 式", "ステンレス・合金鋼の永久利用感"],
            "brands": ["HAWATOUR B07RSM1NG6（JP No.1 9,964 reviews）", "Safari 770045（プロ用）", "猫壱（日本製合金鋼）", "GoPets（プロ大型）"],
        },
    },
    "008 Dog Nail Grinder": {
        "us": {
            "pain": ["Dremel 聲音讓狗躲", "訓練狗習慣需要時間", "軸承壽命短", "速度太快會打滑"],
            "love": ["比 clipper 安全（不會剪到 quick）", "慢慢磨不留鋒利邊", "LED 照血線", "雙速/多速可控"],
            "brands": ["Casfuy B0FCG1FFVL（最不會被閒置 + 終身保固）", "Dremel PawControl 7760-PET", "Boshel（跨國熱賣）"],
        },
        "jp": {
            "pain": ["音が苦手", "Dremel 軸承 2 年破損", "電動爪ヤスリの慣れ時間"],
            "love": ["失敗が少なく安全", "LED + 静音 50dB", "2 速・3 ポート", "1 時間充電で 3-4 時間稼働"],
            "brands": ["VIWIK B0F2T3GTY5（超静音 JP ヒット）", "Boshel（海外勢）", "CATPICK 2-in-1", "Dremel PawControl"],
        },
    },
    "009 Baby Hair Clipper": {
        "us": {
            "pain": ["內建 vacuum 吸力太弱", "「靜音」實際仍有振動", "嬰兒抗拒時使用難度高"],
            "love": ["完全靜音/低分貝", "內建吸塵", "Sensory issue 兒童也能接受", "防水方便清洗"],
            "brands": ["Bimirth Vacuum（吸力 hit-or-miss）", "KIDIRA Silent（靜音口碑強）", "Rozally（JP 理容師監修跨境）"],
        },
        "jp": {
            "pain": ["「静音」表記でも振動音", "嫌がる子供を強引にカットできない", "セルフカット仕上がり心配"],
            "love": ["38dB（ささやき声）超静音", "50dB 以下為 baby/pet 理想", "防水水洗", "8 種アタッチメント", "0.3mm 単位"],
            "brands": ["エジソンママ 静音バリカン プロ技", "Rozally B0BRNJ14YJ（理容師監修）", "Panasonic ER-3300P-W", "Vista B0DPX4G1D6"],
        },
    },
}

# 跨類別最常被提及的競品（用於品牌地圖長條圖）
TOP_COMPETITOR_MENTIONS = pd.DataFrame(
    [
        # (品牌, 提及類別數, 主要市場)
        ("Panasonic", 9, "JP"),
        ("Braun", 4, "US"),
        ("Philips Norelco", 5, "US"),
        ("Manscaped", 2, "US"),
        ("Wahl", 2, "US"),
        ("Andis", 2, "US"),
        ("BaBylissPRO", 2, "US"),
        ("Oneisall", 1, "US"),
        ("Casfuy", 1, "US"),
        ("Millers Forge", 1, "US"),
        ("Pateker", 2, "JP"),
        ("Maxell IZN", 1, "JP"),
        ("皇家 ET-3", 2, "JP"),
        ("HAWATOUR", 1, "JP"),
        ("VIWIK", 1, "JP"),
        ("エジソンママ", 1, "JP"),
        ("Rozally", 2, "JP"),
        ("猫壱", 1, "JP"),
    ],
    columns=["品牌", "出現類別數", "主要市場"],
)


# ─────────────────────────────────────────────────────────────
# 元件
# ─────────────────────────────────────────────────────────────
def kpi(label: str, value: str, delta: str = "", variant: str = "gold") -> str:
    return f"""
    <div class="kpi {variant}">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {f'<div class="delta">{delta}</div>' if delta else ''}
    </div>
    """


@contextmanager
def card(title: str, badge: str = ""):
    """Streamlit 原生 bordered container — DOM 上是一個真正的 wrapper，
    內含 heading + 後續所有 widget。會被 CSS 拉成同列等高。"""
    badge_html = f'<span class="pill gold">{badge}</span>' if badge else ""
    with st.container(border=True):
        st.markdown(
            f'<div class="card-head"><h3>{badge_html} {title}</h3></div>',
            unsafe_allow_html=True,
        )
        yield


def insight(text: str, label: str = "解讀") -> None:
    """金色 accent 的解讀區塊 — 給每張卡片下方統一樣式的洞察文字。"""
    st.markdown(
        f"""
        <div style="margin-top:14px; padding:12px 18px;
                    background:linear-gradient(135deg, #fbf8f1 0%, #ffffff 100%);
                    border-left:3px solid {PALETTE['gold']};
                    border-radius:10px;
                    color:{PALETTE['charcoal']}; font-size:0.9rem; line-height:1.75;">
            <b style="color:{PALETTE['ink']}; letter-spacing:0.04em;">💡 {label}</b><br/>
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


# 舊 API 相容（暫時保留，現有頁碼還在用）
_card_stack: list = []


def card_open(title: str, badge: str = "") -> None:
    ctx = card(title, badge)
    ctx.__enter__()
    _card_stack.append(ctx)


def card_close() -> None:
    if _card_stack:
        ctx = _card_stack.pop()
        ctx.__exit__(None, None, None)


def style_fig(fig: go.Figure, height: int = 380) -> go.Figure:
    # 取得目前的 title 文字（如果沒設就傳空字串避免 plotly 渲染 "undefined"）
    current_title = ""
    if fig.layout.title and fig.layout.title.text:
        current_title = fig.layout.title.text

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=50 if current_title else 30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Noto Sans TC, sans-serif", color=PALETTE["ink"], size=12),
        title=dict(text=current_title, font=dict(color=PALETTE["ink"], size=15)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0)",
            font=dict(color=PALETTE["ink"], size=12),
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=PALETTE["line"],
            font=dict(color=PALETTE["ink"], family="Inter, Noto Sans TC, sans-serif"),
        ),
    )
    # subplot 標題字體與顏色
    fig.update_annotations(
        font=dict(size=12, color=PALETTE["ink"], family="Inter, Noto Sans TC, sans-serif"),
        selector=lambda a: getattr(a, "yref", None) == "paper" and getattr(a, "y", 0) >= 0.95,
    )
    fig.update_xaxes(
        gridcolor=PALETTE["line"],
        zeroline=False,
        tickfont=dict(color=PALETTE["ink"], size=12),
        title_font=dict(color=PALETTE["ink"], size=12),
        linecolor="#CFC7B8",
        tickcolor="#CFC7B8",
    )
    fig.update_yaxes(
        gridcolor=PALETTE["line"],
        zeroline=False,
        tickfont=dict(color=PALETTE["ink"], size=12),
        title_font=dict(color=PALETTE["ink"], size=12),
        linecolor="#CFC7B8",
        tickcolor="#CFC7B8",
    )
    return fig


# ─────────────────────────────────────────────────────────────
# 圖表
# ─────────────────────────────────────────────────────────────
def fig_importance_compare() -> go.Figure:
    us = ATTR_IMPORTANCE_US.set_index("屬性")["重要性"]
    jp = ATTR_IMPORTANCE_JP.set_index("屬性")["重要性"]
    all_attrs = list(dict.fromkeys(list(us.index) + list(jp.index)))
    us_vals = [us.get(a, 0) for a in all_attrs]
    jp_vals = [jp.get(a, 0) for a in all_attrs]
    fig = go.Figure()
    fig.add_bar(
        y=all_attrs, x=us_vals, name="🇺🇸 美國",
        orientation="h", marker_color=PALETTE["us"],
        hovertemplate="%{y}<br>美國重要性: %{x:.1f}%<extra></extra>",
    )
    fig.add_bar(
        y=all_attrs, x=jp_vals, name="🇯🇵 日本",
        orientation="h", marker_color=PALETTE["jp"],
        hovertemplate="%{y}<br>日本重要性: %{x:.1f}%<extra></extra>",
    )
    fig.update_layout(
        barmode="group", bargap=0.25,
        xaxis_title="重要性 (%)", yaxis=dict(autorange="reversed"),
    )
    return style_fig(fig, height=440)


def fig_anova_panel() -> go.Figure:
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("🇺🇸 美國 Top 10 區隔屬性", "🇯🇵 日本 Top 10 區隔屬性"),
        horizontal_spacing=0.18,
    )
    us = ANOVA_US_TOP.sort_values("F")
    jp = ANOVA_JP_TOP.sort_values("F")
    fig.add_bar(
        x=us["F"], y=us["中文"], orientation="h",
        marker_color=PALETTE["us"], name="US",
        hovertemplate="%{y}<br>F=%{x:.1f}<extra></extra>",
        row=1, col=1,
    )
    fig.add_bar(
        x=jp["F"], y=jp["中文"], orientation="h",
        marker_color=PALETTE["jp"], name="JP",
        hovertemplate="%{y}<br>F=%{x:.1f}<extra></extra>",
        row=1, col=2,
    )
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="F 值（區隔力越大代表分群越分明）", row=1, col=1)
    fig.update_xaxes(title_text="F 值", row=1, col=2)
    return style_fig(fig, height=480)


def fig_segment_sunburst(seg_df: pd.DataFrame, title: str, color: str) -> go.Figure:
    # 簡化區隔短名 — 不在 sunburst 內塞長標籤，避免斷字
    short_names = [f"S{i+1}" for i in range(len(seg_df))]
    labels = ["全體"] + short_names
    parents = [""] + ["全體"] * len(seg_df)
    values = [seg_df["人數"].sum()] + seg_df["人數"].tolist()
    hover_text = ["全體 100%"] + [
        f"{name}<br>{p:.1f}% · ★{s:.2f}" for name, p, s in
        zip(seg_df["區隔"], seg_df["占比%"], seg_df["Avg★"])
    ]
    if color == "us":
        colors = ["#ffffff", PALETTE["us"], PALETTE["us_soft"], "#7E96FF"]
    else:
        colors = ["#ffffff", PALETTE["jp"], PALETTE["jp_soft"], "#F18FA1"]
    fig = go.Figure(go.Sunburst(
        labels=labels, parents=parents, values=values,
        marker=dict(colors=colors, line=dict(color="#fff", width=2)),
        hovertext=hover_text, hovertemplate="%{hovertext}<extra></extra>",
        branchvalues="total", insidetextorientation="horizontal",
        textfont=dict(size=14, color="#fff", family="Inter"),
    ))
    fig.update_layout(title=title)
    return style_fig(fig, height=360)


def fig_upgrade_panel() -> go.Figure:
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "🇺🇸 美國 — 規格做到頂級後的市佔潛力",
            "🇯🇵 日本 — 規格做到頂級後的市佔潛力",
        ),
        horizontal_spacing=0.22,
    )

    def fmt_base(v: float) -> str:
        return f"{v:.1f}%" if v >= 1.0 else ""

    def fmt_gain(v: float) -> str:
        return f"+{v:.1f}%" if v >= 0.5 else ""

    us = UPGRADE_US.sort_values("升至 High 份額%")
    jp = UPGRADE_JP.sort_values("升至 High 份額%")

    # 統一兩側 base color 與 gain color，名稱跨 column 共用一份 legend
    base_color_us, base_color_jp = "#D4D7E3", "#E4D2D6"
    gain_color_us, gain_color_jp = PALETTE["us"], PALETTE["jp"]

    for col, df, base_color, gain_color, legend in [
        (1, us, base_color_us, gain_color_us, "🇺🇸 US"),
        (2, jp, base_color_jp, gain_color_jp, "🇯🇵 JP"),
    ]:
        gain = df["升至 High 份額%"] - df["現況份額%"]
        fig.add_bar(
            y=df["升級屬性"], x=df["現況份額%"], orientation="h",
            marker_color=base_color, name=f"{legend} 現況",
            text=df["現況份額%"].apply(fmt_base),
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color=PALETTE["ink"], size=11, family="Inter"),
            showlegend=False,
            cliponaxis=False,
            row=1, col=col,
        )
        fig.add_bar(
            y=df["升級屬性"], x=gain, orientation="h",
            marker_color=gain_color, name=f"{legend} 升級增量",
            base=df["現況份額%"],
            text=gain.apply(fmt_gain),
            textposition="outside",
            textfont=dict(color=gain_color, size=11, family="Inter"),
            showlegend=False,
            cliponaxis=False,
            row=1, col=col,
        )

    fig.update_layout(barmode="stack")
    # 兩側都預留 25% 右側空間給 outside 文字
    fig.update_xaxes(title_text="市佔潛力 (%) — 規格升頂後的份額", row=1, col=1, range=[0, 1.5])
    fig.update_xaxes(title_text="市佔潛力 (%) — 規格升頂後的份額", row=1, col=2, range=[0, 115])
    return style_fig(fig, height=460)


def fig_wtp_panel() -> go.Figure:
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "🇺🇸 美國 WTP (USD / 品質分)",
            "🇯🇵 日本 WTP (JPY / 品質分) — 方向性參考",
        ),
        horizontal_spacing=0.22,
    )
    us = WTP_US.sort_values("WTP (USD/品質分)")
    jp = WTP_JP.sort_values("WTP (JPY/品質分)")
    us_max = us["WTP (USD/品質分)"].max()
    jp_max = jp["WTP (JPY/品質分)"].max()
    fig.add_bar(
        y=us["屬性"], x=us["WTP (USD/品質分)"], orientation="h",
        marker_color=[PALETTE["us"] if s else "#B8C7FF" for s in us["顯著"]],
        text=us["WTP (USD/品質分)"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside", textfont=dict(size=11, color=PALETTE["ink"], family="Inter"),
        cliponaxis=False,
        hovertemplate="%{y}<br>WTP=$%{x:.2f}<extra></extra>",
        row=1, col=1,
    )
    fig.add_bar(
        y=jp["屬性"], x=jp["WTP (JPY/品質分)"], orientation="h",
        marker_color=[PALETTE["jp"] if s else "#F2B5C2" for s in jp["顯著"]],
        text=jp["WTP (JPY/品質分)"].apply(lambda v: f"¥{v:,.0f}"),
        textposition="outside", textfont=dict(size=11, color=PALETTE["ink"], family="Inter"),
        cliponaxis=False,
        hovertemplate="%{y}<br>WTP=¥%{x:,.0f}<extra></extra>",
        row=1, col=2,
    )
    fig.update_xaxes(range=[0, us_max * 1.25], row=1, col=1)
    fig.update_xaxes(range=[0, jp_max * 1.25], row=1, col=2)
    fig.update_layout(showlegend=False)
    return style_fig(fig, height=440)


def fig_segment_compare_bar() -> go.Figure:
    """區隔占比 + Avg★ — 棄用雙 y 軸，改用 outside 文字一次顯示 占比% 與 ★Avg"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("🇺🇸 美國區隔結構", "🇯🇵 日本區隔結構"),
        horizontal_spacing=0.16,
    )

    for col, df, base_color in [(1, SEGMENTS_US, PALETTE["us"]), (2, SEGMENTS_JP, PALETTE["jp"])]:
        # 名稱已含 "S1：父親節送禮客" 結構 → 拆出 S 編號 + 中文名稱
        x_labels = []
        for n in df["區隔"]:
            if "：" in n:
                code, persona = n.split("：", 1)
                x_labels.append(f"<b>{code}</b><br><span style='font-size:10px'>{persona}</span>")
            else:
                x_labels.append(n)
        bar_text = [
            f"<b>{p:.1f}%</b><br>"
            f"<span style='color:{PALETTE['gold']};font-weight:700'>★{s:.2f}</span>"
            for p, s in zip(df["占比%"], df["Avg★"])
        ]
        fig.add_bar(
            x=x_labels, y=df["占比%"], marker_color=base_color,
            text=bar_text, textposition="outside",
            textfont=dict(size=12, color=PALETTE["ink"], family="Inter"),
            cliponaxis=False,
            customdata=df["區隔"],
            hovertemplate="%{customdata}<br>占比 %{y:.1f}%<extra></extra>",
            row=1, col=col, showlegend=False,
        )

    fig.update_yaxes(title_text="占比 (%)", range=[0, 125], row=1, col=1)
    fig.update_yaxes(title_text="占比 (%)", range=[0, 125], row=1, col=2)
    fig.update_xaxes(tickfont=dict(size=11, color=PALETTE["ink"], family="Inter"))
    return style_fig(fig, height=480)


def fig_choice_set_donut() -> go.Figure:
    """MNL 選擇集份額。

    原本用雙 donut，窄欄位會讓中心標籤、圖例和 modebar 互相打架。
    改用 100% stacked share bar，讓現況份額與最佳設計組合一眼可讀。
    """
    markets = ["US 美國", "JP 日本"]
    competitor = [94.67, 85.60]
    urbaner = [5.21, 11.26]
    best_design = [0.12, 3.14]

    fig = go.Figure()
    fig.add_bar(
        y=markets,
        x=competitor,
        name="競品",
        orientation="h",
        marker_color=["#D4D7E3", "#E4D2D6"],
        hovertemplate="%{y}<br>競品份額 %{x:.2f}%<extra></extra>",
    )
    fig.add_bar(
        y=markets,
        x=urbaner,
        name="URBANER 現況",
        orientation="h",
        marker_color=[PALETTE["us"], PALETTE["jp"]],
        hovertemplate="%{y}<br>URBANER 現況 %{x:.2f}%<extra></extra>",
    )
    fig.add_bar(
        y=markets,
        x=best_design,
        name="最佳設計組合",
        orientation="h",
        marker_color=PALETTE["gold"],
        hovertemplate="%{y}<br>最佳設計組合 %{x:.2f}%<extra></extra>",
    )

    callouts = [
        ("US 美國", "5.21%", "最佳設計 0.12%", PALETTE["us"]),
        ("JP 日本", "11.26%", "最佳設計 3.14%", PALETTE["jp"]),
    ]
    for market, share, best, color in callouts:
        fig.add_annotation(
            x=99.2,
            y=market,
            text=(
                f"<b style='color:{color}; font-size:18px'>{share}</b><br>"
                f"<span style='font-size:11px'>URBANER 現況</span><br>"
                f"<span style='font-size:10px; color:{PALETTE['muted']}'>{best}</span>"
            ),
            xref="x",
            yref="y",
            showarrow=False,
            xanchor="right",
            yanchor="middle",
            align="right",
            bgcolor="rgba(255,255,255,0.86)",
            bordercolor=PALETTE["line"],
            borderpad=6,
            font=dict(color=PALETTE["ink"], family="Inter, Noto Sans TC, sans-serif"),
        )

    fig = style_fig(fig, height=340)
    fig.update_layout(
        barmode="stack",
        bargap=0.42,
        showlegend=False,
        margin=dict(l=12, r=12, t=20, b=52),
    )
    fig.update_xaxes(
        range=[0, 100],
        ticksuffix="%",
        tickvals=[0, 25, 50, 75, 100],
        title_text="MNL 選擇集份額",
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=["JP 日本", "US 美國"],
        tickfont=dict(size=13, color=PALETTE["ink"]),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# 頁面
# ─────────────────────────────────────────────────────────────
def fig_competitor_mentions() -> go.Figure:
    df = TOP_COMPETITOR_MENTIONS.sort_values("出現類別數", ascending=True)
    colors = [PALETTE["us"] if m == "US" else PALETTE["jp"] for m in df["主要市場"]]
    fig = go.Figure()
    fig.add_bar(
        y=df["品牌"], x=df["出現類別數"], orientation="h",
        marker_color=colors,
        text=df["出現類別數"].apply(lambda v: f"{v} 類"),
        textposition="outside", textfont=dict(size=11, color=PALETTE["ink"], family="Inter"),
        cliponaxis=False,
        hovertemplate="%{y}<br>出現於 %{x} 個產品類別<extra></extra>",
    )
    fig.update_layout(
        xaxis_title="出現類別數（最大 9）",
        showlegend=False,
    )
    fig.update_xaxes(range=[0, 11])
    return style_fig(fig, height=540)


def fig_platform_split() -> go.Figure:
    """美日社群平台數量對比 — 簡單條形圖。"""
    fig = go.Figure()
    fig.add_bar(
        x=["美國社群", "日本社群"],
        y=[len(SOCIAL_SOURCES_US), len(SOCIAL_SOURCES_JP)],
        marker_color=[PALETTE["us"], PALETTE["jp"]],
        text=[len(SOCIAL_SOURCES_US), len(SOCIAL_SOURCES_JP)],
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="#fff", size=20, family="Inter"),
        width=0.5,
        hovertemplate="%{x}<br>%{y} 個來源平台<extra></extra>",
    )
    fig.update_layout(
        yaxis_title="平台數",
        showlegend=False,
    )
    return style_fig(fig, height=320)


def fig_sources_panel() -> go.Figure:
    """美日社群完整平台清單 + 引用條數 — 雙欄水平條形圖。"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            f"🇺🇸 美國社群（{len(SOCIAL_SOURCES_US)} 個平台 · "
            f"{SOCIAL_SOURCES_US['引用條數'].sum()} 條觀察筆記）",
            f"🇯🇵 日本社群（{len(SOCIAL_SOURCES_JP)} 個平台 · "
            f"{SOCIAL_SOURCES_JP['引用條數'].sum()} 條觀察筆記）",
        ),
        horizontal_spacing=0.24,
    )
    us = SOCIAL_SOURCES_US.sort_values("引用條數")
    jp = SOCIAL_SOURCES_JP.sort_values("引用條數")
    fig.add_bar(
        y=us["平台"], x=us["引用條數"], orientation="h",
        marker_color=PALETTE["us"],
        text=us["引用條數"].apply(lambda v: f"{v} 條"),
        textposition="outside",
        cliponaxis=False,
        textfont=dict(size=11),
        customdata=us["類型"],
        hovertemplate="<b>%{y}</b><br>類型：%{customdata}<br>引用 %{x} 條<extra></extra>",
        row=1, col=1, showlegend=False,
    )
    fig.add_bar(
        y=jp["平台"], x=jp["引用條數"], orientation="h",
        marker_color=PALETTE["jp"],
        text=jp["引用條數"].apply(lambda v: f"{v} 條"),
        textposition="outside",
        cliponaxis=False,
        textfont=dict(size=11),
        customdata=jp["類型"],
        hovertemplate="<b>%{y}</b><br>類型：%{customdata}<br>引用 %{x} 條<extra></extra>",
        row=1, col=2, showlegend=False,
    )
    us_max = us["引用條數"].max()
    jp_max = jp["引用條數"].max()
    fig.update_xaxes(title_text="引用條數", range=[0, us_max * 1.2], row=1, col=1)
    fig.update_xaxes(title_text="引用條數", range=[0, jp_max * 1.2], row=1, col=2)
    return style_fig(fig, height=620)


def render_hero(subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="sub">URBANER ／ Bright Idea, Great Value</div>
            <h1>雙市場戰略儀表板</h1>
            <div class="tagline">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_overview() -> None:
    render_hero(
        "用 11,523 則 Amazon 評論做完顧客分群與偏好分析後，"
        "盤點 URBANER 在美國（4,360 則）與日本（7,163 則）的競爭位置，"
        "並產出可直接套用到 Listing / 套組設計 / 行銷檔期的策略建議。"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi("總評論數", "11,523", "US 4,360 ｜ JP 7,163", "gold"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("自家 SKU 數", "88", "US 52 ｜ JP 36", "gold"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("US 代表 SKU", "B0FL267TCG", "Beard / Mustache · ★4.52", "us"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("JP 代表 SKU", "B0GBWZBMS5", "Nose / Ear · ★4.61", "jp"), unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi("US 大眾族群", "76.5%", "日常自用大眾 ｜ Avg★ 3.18", "us"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("JP 大眾族群", "91.6%", "CP 值優先大眾 ｜ Avg★ 3.46", "jp"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("US 最佳組合 預估購買率", "83.3%", "USB-C × 38 段 × ≥10 件套組", "gold"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("JP 最佳組合 預估購買率", "89.1%", "IPX7 × 90 分高續航全配款", "gold"), unsafe_allow_html=True)

    st.markdown("---")

    col_l, col_r = st.columns([5, 4])
    with col_l:
        card_open("⚡ 三大核心洞察", "策略總覽")
        st.markdown(
            f"""
            <div class="insight-list">
                <div class="insight-row">
                    <div class="insight-dot"></div>
                    <div>
                        <div class="insight-title">
                            <span class="pill us">US</span>
                            <span>送禮場景 × 多功能套組是市場決策主軸</span>
                        </div>
                        <div class="insight-body">
                            最能拉開不同顧客的兩個屬性 — 「適不適合送禮給男性」與「多功能套組」 — 強度遠超其他項目。
                            父親節 / 聖誕節送禮情境是絕大多數美國電剪購買決策的觸發點。
                        </div>
                    </div>
                </div>
                <div class="insight-row">
                    <div class="insight-dot"></div>
                    <div>
                        <div class="insight-title">
                            <span class="pill jp">JP</span>
                            <span>附件齊全度 × 0.5mm 精度 × 電源類型是日本決策三軸</span>
                        </div>
                        <div class="insight-body">
                            最能拉開不同顧客的前 3 個屬性都是「規格深度」：附件件數、梳齒款式、可調梳齒，
                            強度比第 4 名加起來還高。日本顧客重視 38 段刻度、附件套組完整、CP 值高、
                            <b>丸洗い（整支可水洗）</b>。
                        </div>
                    </div>
                </div>
                <div class="insight-row">
                    <div class="insight-dot"></div>
                    <div>
                        <div class="insight-title">
                            <span class="pill gold">兩市場共識</span>
                            <span>IPX7+ × ≥7 件套組 = 2026 新品最低門檻</span>
                        </div>
                        <div class="insight-body">
                            兩市場的顧客分群分析與社群觀察結論一致；新 SKU 開發必須踩上這道規格線。
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        card_close()

    with col_r:
        card_open("🪒 在競品環伺下，URBANER 目前佔多少？", "市佔位置")
        st.plotly_chart(fig_choice_set_donut(), use_container_width=True)
        st.markdown(
            f"""<div style="color:{PALETTE['muted']}; font-size:0.85rem; line-height:1.6;">
            US 場上 URBANER 僅 5.21%，最佳組合（USB-C × 38 段 × ≥10 件套組）只擠進全選擇集第 33 名；
            <b>痛點在套組形態</b>。JP 較好，已佔 11.26%，且 IPX7 × 90 分高續航全配款排到全場第 9。
            </div>""",
            unsafe_allow_html=True,
        )
        card_close()

    card_open("📊 美日消費者在意什麼？— 屬性重要性一張圖看完", "偏好分析")
    st.plotly_chart(fig_importance_compare(), use_container_width=True)
    st.markdown(
        f"""<div style="color:{PALETTE['muted']}; font-size:0.88rem; line-height:1.7;">
        <b>解讀</b>：美國市場「功能合一數」單項重要性高達 51.5%，是壓倒性決策因子；
        日本市場則分布較均勻，前 6 個屬性都在 10% 以上，且「調整精度（0.5mm 刻度）」是日本獨有的高權重屬性。
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()


def page_dual_market() -> None:
    render_hero(
        "把美國與日本擺在一起看：哪些屬性最區分顧客、各顧客群佔多少人、平均給幾顆星、"
        "兩市場代表 SKU 各是誰。"
    )

    card_open("🌎 哪些屬性最能拉開不同顧客群的差距？")
    st.plotly_chart(fig_anova_panel(), use_container_width=True)
    st.markdown(
        f"""<div style="color:{PALETTE['muted']}; font-size:0.88rem;">
        US 區隔力 Top 1 為「送禮場景」、JP 區隔力 Top 1 為「附件件數」。
        兩市場共同高 F 值屬性包含 <code>attachment_fitment</code>、<code>guide_comb_variety</code>、
        <code>power_source_type</code>、<code>waterproof_rating_ipx8</code> — 這四項是兩市場通用的開發焦點。
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    card_open("👥 各顧客群佔多少人、平均給幾顆星？")
    st.plotly_chart(fig_segment_compare_bar(), use_container_width=True)
    st.markdown(
        """<div style="font-size:0.92rem; line-height:1.7;">
        <b>策略意涵</b>：「日常自用大眾（US S2，76.5%）」與「CP 值優先大眾（JP S1，91.6%）」
        是「大眾痛點群」，Avg★ 偏低（3.18 / 3.46）— 應優先處理痛點而非強推擴張；
        「USB-C 高端鐵粉（US S3，4.0%，★4.48）」與「鬍鬚講究客（JP S2，7.8%，★4.01）」
        是「高滿意可規模化」族群，值得集中行銷資源（Priority）。
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    card_open("🌳 顧客群人數分布（樹狀圖，一眼看比例）")
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(fig_segment_sunburst(SEGMENTS_US, "🇺🇸 美國區隔組成（按人數）", "us"), use_container_width=True)
    with col_r:
        st.plotly_chart(fig_segment_sunburst(SEGMENTS_JP, "🇯🇵 日本區隔組成（按人數）", "jp"), use_container_width=True)
    insight(
        "<b>US 比 JP 更均勻</b> — US 的 S1（送禮）+S3（高端）合計 23.5% 還算有規模；"
        "JP 則高度集中：S1「CP 值優先大眾」一個族群就 91.6%，"
        "S2、S3 加起來只佔 8.4%。<br/>"
        "<b>策略含義</b>：JP 不要追小眾，而是「在大眾族群內找升級訊號」；"
        "US 可以同時跑大眾與高端兩條 product line。",
    )
    card_close()

    card_open("🏆 兩市場代表 SKU — 哪兩款最接近顧客理想？")
    h1, h2 = st.columns(2)
    with h1:
        st.markdown(
            f"""
            <div class="spec">
                <h4>🇺🇸 美國代表 SKU</h4>
                <div class="name">{HERO_SKU_US['asin']}</div>
                <div class="meta">{HERO_SKU_US['category']} ｜ n={HERO_SKU_US['n_reviews']}</div>
                <table>
                    <tr><td>離顧客理想多遠</td><td>{HERO_SKU_US['distance']} ｜ 越小越接近</td></tr>
                    <tr><td>平均星等</td><td>★ {HERO_SKU_US['avg_star']}</td></tr>
                    <tr><td>同類預估市佔</td><td>{HERO_SKU_US['preference_share']}%</td></tr>
                    <tr><td>建議策略</td><td>Father's Day 主推</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with h2:
        st.markdown(
            f"""
            <div class="spec jp">
                <h4>🇯🇵 日本代表 SKU</h4>
                <div class="name">{HERO_SKU_JP['asin']}</div>
                <div class="meta">{HERO_SKU_JP['category']} ｜ n={HERO_SKU_JP['n_reviews']}</div>
                <table>
                    <tr><td>距理想點 RMS</td><td>{HERO_SKU_JP['distance']}</td></tr>
                    <tr><td>平均星等</td><td>★ {HERO_SKU_JP['avg_star']}</td></tr>
                    <tr><td>全場預估市佔</td><td>{HERO_SKU_JP['preference_share']}%</td></tr>
                    <tr><td>建議策略</td><td>父の日 × 楽天直営主打</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    insight(
        "<b>兩市場代表 SKU 完全是不同類別</b> — 美國主推 Beard / Mustache 修鬍器（B0FL267TCG, ★4.52）；"
        "日本主推 Nose / Ear 鼻耳毛機（B0GBWZBMS5, ★4.61）。"
        "「離顧客理想多遠」美國 1.6 < 日本 2.0，代表 URBANER 在美國比較貼近顧客理想規格。<br/>"
        "<b>不要互用主推品</b>：把美國 Beard 款拿去日本推、或把日本 Nose/Ear 款拿去美國推，"
        "都會打到錯誤的決策軸；行銷預算應在各市場集中投到對應的代表 SKU。",
    )
    card_close()


def page_stp() -> None:
    render_hero(
        "STP 三步驟 — 先看「誰在買」（分群）、再決定「要服務誰」（鎖定優先族群）、最後想清楚「我要是誰」（在競爭群裡的位置）。"
        "美日決策軸完全不同 — 美國由「送禮場景」驅動、日本由「規格深度」驅動。"
    )

    def render_segment_card(seg_df: pd.DataFrame, accent: str) -> None:
        for _, row in seg_df.iterrows():
            code, persona = row["區隔"].split("：", 1) if "：" in row["區隔"] else ("", row["區隔"])
            star_color = (
                "#2E8B57" if row["Avg★"] >= 4.0
                else "#D97706" if row["Avg★"] >= 3.5
                else "#B91C1C"
            )
            st.markdown(
                f"""
                <div style="background:#fff; border:1px solid {PALETTE['line']};
                            border-left:5px solid {accent}; border-radius:12px;
                            padding:14px 18px; margin-bottom:12px;
                            box-shadow:0 3px 10px -8px rgba(0,0,0,0.15);">
                  <div style="display:flex; justify-content:space-between;
                              align-items:center; margin-bottom:8px;">
                    <div>
                      <span style="font-weight:700; color:{accent}; font-size:0.9rem;
                                   letter-spacing:0.06em;">{code}</span>
                      <span style="font-weight:700; color:{PALETTE['ink']}; font-size:1.05rem;
                                   margin-left:6px;">{persona}</span>
                    </div>
                    <div style="font-size:0.82rem; color:{PALETTE['muted']};">
                      n={row['人數']:,}
                      &nbsp;·&nbsp; <b style="color:{PALETTE['ink']}">{row['占比%']:.1f}%</b>
                      &nbsp;·&nbsp; <b style="color:{star_color}">★{row['Avg★']:.2f}</b>
                    </div>
                  </div>
                  <div style="font-size:0.83rem; color:{PALETTE['muted']};
                              margin-bottom:6px; letter-spacing:0.02em;">
                    <b style="color:{PALETTE['charcoal']};">類別組成 ·</b> {row['類別組成']}
                  </div>
                  <div style="font-size:0.88rem; color:{PALETTE['charcoal']};
                              line-height:1.6;">
                    <b style="color:{accent};">他們是誰 ·</b> {row['他們是誰']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with card("🎯 顧客分群 — 美日各有 3 種顧客"):
        s1, s2 = st.columns(2)
        with s1:
            st.markdown(
                '<div style="margin-bottom:10px;"><span class="pill us">🇺🇸 US</span></div>',
                unsafe_allow_html=True,
            )
            render_segment_card(SEGMENTS_US, PALETTE["us"])
        with s2:
            st.markdown(
                '<div style="margin-bottom:10px;"><span class="pill jp">🇯🇵 JP</span></div>',
                unsafe_allow_html=True,
            )
            render_segment_card(SEGMENTS_JP, PALETTE["jp"])
        insight(
            "<b>美日大眾族群動機差很多</b>：US 大眾「日常自用」買來自己每天用 — "
            "鬍鬚 + 耳鼻一機通用；JP 大眾「CP 值優先」愛乾電池款，"
            "看重耐用與易用。<br/>"
            "<b>高滿意小族群才是利潤池</b>：US S3 USB-C 高端鐵粉（★4.48）"
            "與 JP S2 鬍鬚講究客（★4.01）— 雖只佔 4% / 7.8%，"
            "但滿意度遠高於大眾，且願意為精度與充電付溢價。",
        )

    card_open("📈 鎖定優先族群 — 哪些屬性最能拉開不同顧客的差距？")
    st.plotly_chart(fig_anova_panel(), use_container_width=True)
    st.markdown(
        """<div style="font-size:0.92rem; line-height:1.75;">
        <ul style="margin-left:-20px;">
          <li><b>US 優先族群：</b>「USB-C 高端鐵粉」（S3，4%，★4.48）— 充電 × 高端 × 送禮場景</li>
          <li><b>JP 優先族群：</b>「鬍鬚講究客」（S2，7.8%，★4.01）— 高精度 × 多附件 × 鬍鬚款</li>
          <li><b>共同 Deprioritized：</b>「日常自用大眾」與「CP 值優先大眾」雖佔比最大但 Avg★ 偏低 — 不是擴張對象，
              應該優先以「痛點修補」應對（如 Listing 更清楚、退換貨、附件齊全度）</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    card_open("🗺️ 市場定位地圖 — URBANER 在競爭群裡離顧客理想多近？")
    p1, p2 = st.columns(2)
    perceptual_us = OUT_STP_US / "perceptual_map.png"
    perceptual_jp = OUT_STP_JP / "perceptual_map.png"
    with p1:
        if perceptual_us.exists():
            st.image(str(perceptual_us), caption="🇺🇸 US — PCA 二維品質投影（Hero = B0FL267TCG）",
                     use_container_width=True)
        else:
            st.info("perceptual_map.png 不存在")
    with p2:
        if perceptual_jp.exists():
            st.image(str(perceptual_jp), caption="🇯🇵 JP — PCA 二維品質投影（Hero = B0GBWZBMS5）",
                     use_container_width=True)
        else:
            st.info("perceptual_map.png 不存在")
    insight(
        "<b>圖上的點越靠近右上角越接近「理想品質」</b>。"
        "URBANER 在兩市場的位置分布不同：US 主力 SKU 偏 Beard 高密度區，"
        "JP 主力 SKU 偏 Nose/Ear 與小型機身區。<br/>"
        "<b>產品開發優先序</b>：盯靠近右上角的 SKU 學它怎麼做、"
        "把落單在左下的 SKU 重新評估是否退場。",
    )
    card_close()

    card_open("🔥 哪個 SKU 在哪個屬性表現最好？— 屬性 × SKU 口碑熱圖")
    h1, h2 = st.columns(2)
    with h1:
        heat_us = OUT_STP_US / "quality_heatmap.png"
        if heat_us.exists():
            st.image(str(heat_us), caption="🇺🇸 US 品質熱圖", use_container_width=True)
    with h2:
        heat_jp = OUT_STP_JP / "quality_heatmap.png"
        if heat_jp.exists():
            st.image(str(heat_jp), caption="🇯🇵 JP 品質熱圖", use_container_width=True)
    insight(
        "<b>橫向看 SKU、縱向看屬性</b> — 一格越綠代表這個 SKU 在該屬性上口碑越好。"
        "找出每一列（屬性）有哪幾個 SKU 是「綠到頂」的，那就是該屬性的標竿學習對象。<br/>"
        "<b>實務用法</b>：選 3 個你最想升級的屬性，"
        "去看熱圖最綠的那兩三顆 SKU，拆解它們的規格／文案／視覺呈現再複製。",
    )
    card_close()


def page_conjoint() -> None:
    render_hero(
        "從 11,523 則 Amazon 評論還原顧客「真正在比什麼」，再用真實售價回推「願意為品質多付多少錢」。"
        "三張圖一起看：消費者在意什麼 → 願意多付多少 → 把規格做上去市佔能跳多少。"
    )

    card_open("⚖️ 消費者最在意哪些屬性？")
    st.plotly_chart(fig_importance_compare(), use_container_width=True)
    insight(
        "<b>美日決策軸完全不同</b>：US 一根「功能合一數」就吃掉 51.5% 重要性 — "
        "套組組合是壓倒性決策因子；JP 前 6 個屬性都在 10% 以上、分布均勻，"
        "代表日本顧客同時看附件數、長度段數、精度、續航。<br/>"
        "<b>產品溝通方向</b>：US Listing 第一張主圖必須講清楚「幾合一」；"
        "JP Listing 第一條 bullet 要把 X 個附件 / X 段 / X mm 全部列出。",
    )
    card_close()

    card_open("💰 為品質升級，消費者願意多付多少錢？")
    st.plotly_chart(fig_wtp_panel(), use_container_width=True)
    st.markdown(
        f"""<div style="color:{PALETTE['muted']}; font-size:0.86rem; line-height:1.7;">
        <b>解讀</b>：把同一項屬性的品質從 0 分做到 10 分，美國消費者「機身尺寸」最多願意多付 $89.81、
        日本消費者「長度調整段數」最多願意多付 ¥7,961（都有統計顯著）。
        <br>深色柱 = 統計顯著（高信心），淺色柱 = 方向性參考。
        <br>⚠️ 日本售價與品質正相關（高價＝高品質訊號），日本 WTP 數字只當「方向參考」，不要直接拿去定價。
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    card_open("🚀 規格做到頂級，市佔會跳多少？")
    st.markdown(
        f"""<div style="color:{PALETTE['muted']}; font-size:0.88rem; line-height:1.7;
                       margin-bottom:8px;">
        模擬：如果把 URBANER 在某個屬性的規格升到「競品頂級水準」
        （例如 段數做到 ≥38 段、附件做到 ≥10 件、防水做到 IPX7+、續航做到 90 分以上），
        重跑市佔模型後，URBANER 的偏好份額能從現在跳到多少。
        <b>這是 R&D 投資 ROI 決策工具：告訴你「砸錢升哪個屬性，市佔回報最大」。</b>
        </div>""",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_upgrade_panel(), use_container_width=True)
    st.markdown(
        """<div style="font-size:0.92rem; line-height:1.7;">
        <b>策略意涵</b>：
        <ul style="margin-left:-20px;">
          <li><b>JP 第一優先：把段數做到 38 段以上</b> — 市佔從 1.6% 跳到 94.8%（多 93 個百分點），是所有升級裡爆發力最大的單一決策。</li>
          <li><b>JP 第二優先：刻度做到 0.5mm</b> — 市佔可跳到 86.2%（多 85 個百分點），與「段數」是兩條互補的升級路徑。</li>
          <li><b>US 不能靠單一升級</b>：個別屬性升級增幅都不到 1 個百分點，問題是「整套套組形態」，建議組合拳：附件 + 多功能 + USB-C 一起升。</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    card_open("📋 每升 1 分品質，消費者願意多付多少錢（完整對照表）")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<span class="pill us">USD / 品質分</span>', unsafe_allow_html=True)
        st.dataframe(WTP_US, hide_index=True, use_container_width=True)
    with c2:
        st.markdown('<span class="pill jp">JPY / 品質分</span>', unsafe_allow_html=True)
        st.dataframe(WTP_JP, hide_index=True, use_container_width=True)
    insight(
        "<b>怎麼用這張表</b>：把 WTP 直接除以「目前 SKU 在該屬性的品質分缺口」，"
        "就能估算「升級 1 個品質分」可以多賣多少錢。<br/>"
        "<b>US 顯著屬性</b>（p&lt;0.05）：機身尺寸 $89.81、附件件數 $79.86、"
        "長度段數 $78.18、功能合一 $59.07、USB-C 充電 $32.39。"
        "<br/><b>JP 顯著屬性</b>：長度段數 ¥7,961、調整精度 ¥6,774、附件件數 ¥5,207、電池續航 ¥4,306。"
        "<br/>JP β_price 為正（高價＝高品質訊號），WTP 數字僅供方向參考，不宜直接定價決策。",
    )
    card_close()


def page_best_product() -> None:
    render_hero(
        "用 Conjoint 偏好分析從 24 種設計組合裡，挑出兩市場「消費者最會買」的產品規格。"
        "兩市場骨幹相同（USB-C × 38 段 × ≥10 件套組），但 US 走「USB-C 快充 × 單一精修」、"
        "JP 走「IPX7 × 90 分續航 × 1mm 精度」。"
    )

    card_open("🏆 兩市場最佳產品組合 — 24 種設計裡挑出消費者最會買的")
    b1, b2 = st.columns(2)
    with b1:
        rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in BEST_CARD_US['specs']])
        st.markdown(
            f"""
            <div class="spec">
                <h4>🇺🇸 美國最佳組合</h4>
                <div class="name">{BEST_CARD_US['card']}</div>
                <div class="meta">{BEST_CARD_US['tagline']}<br/>P(購買) = {BEST_CARD_US['p_buy']:.2%} ｜ Utility = {BEST_CARD_US['utility']:.2f}</div>
                <table>{rows}</table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b2:
        rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in BEST_CARD_JP['specs']])
        st.markdown(
            f"""
            <div class="spec jp">
                <h4>🇯🇵 日本最佳組合</h4>
                <div class="name">{BEST_CARD_JP['card']}</div>
                <div class="meta">{BEST_CARD_JP['tagline']}<br/>P(購買) = {BEST_CARD_JP['p_buy']:.2%} ｜ Utility = {BEST_CARD_JP['utility']:.2f}</div>
                <table>{rows}</table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """<div style="margin-top:18px; font-size:0.95rem; line-height:1.8;">
        <b>兩市場最佳組合差異對照</b>：
        <ul style="margin-left:-20px;">
          <li><b>共同骨幹：</b>長度調整 ≥38 段 × 附件 ≥10 件 × USB-C 電源 — 2026 雙市場新品開發共識規格。</li>
          <li><b>US 偏好：</b>USB-C 快充 × 標準機身 × IPX4 × 1合1 — 美國買單「單一專精 + USB-C + 快充」路線。</li>
          <li><b>JP 偏好：</b>90 分鐘以上續航 × IPX7+ × 1mm 刻度 × 大型機身 — 日本買單「續航 + 防水 + 精度」三軸。</li>
          <li><b>取捨：</b>美國最佳組合採 IPX4（非 IPX7+） — 因為功能合一數重要性壓倒一切，IPX 等級反而成為次要決策。</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    card_open("🎯 在競品環伺下，URBANER 現在在哪？")
    st.plotly_chart(fig_choice_set_donut(), use_container_width=True)
    st.markdown(
        f"""<div style="color:{PALETTE['muted']}; font-size:0.9rem;">
        <b>痛點</b>：美國最佳組合（USB-C × 38 段全附件款）在「URBANER + 競品 + 24 種設計組合」全選擇集中僅排第 33 名，份額 0.09%。
        代表「美國最佳設計組合」距離擊敗競品還有不小距離 — 必須結合行銷檔期 + 套組 + Listing 重做。
        日本最佳組合（IPX7 × 90 分高續航款）表現好得多：全場第 9 名，份額 3.13%。
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()


def render_rec(rec: dict, variant: str = "") -> None:
    cls = f"rec {variant}".strip()
    kpi_html = f'<div class="kpi-tag">📊 {rec["kpi"]}</div>' if "kpi" in rec else ""
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="title">{rec['title']}</div>
            <div class="body">{rec['body']}</div>
            {kpi_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_social() -> None:
    render_hero(
        "從 Reddit、Badger&Blade、Sharpologist、知恵袋、価格.com、マイベスト、note、5ch 等 "
        "20+ 平台彙整出 22 條跨類別共識，以及 9 個產品類別的痛點 × 好評 × 競品偏好。"
    )

    c1, c2, c3, c4 = st.columns(4)
    us_count = SOCIAL_SOURCES_US["引用條數"].sum()
    jp_count = SOCIAL_SOURCES_JP["引用條數"].sum()
    with c1:
        st.markdown(
            kpi("美國社群來源",
                f"{len(SOCIAL_SOURCES_US)} 個",
                f"{us_count} 條筆記 ｜ Reddit · B&B · Sharpologist…", "us"),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            kpi("日本社群來源",
                f"{len(SOCIAL_SOURCES_JP)} 個",
                f"{jp_count} 條筆記 ｜ 知恵袋 · 価格.com · マイベスト…", "jp"),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(kpi("跨類別共識", "22 條", f"US {len(CROSS_INSIGHTS_US)} + JP {len(CROSS_INSIGHTS_JP)}", "gold"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("被提及競品數",
                        str(len(TOP_COMPETITOR_MENTIONS)),
                        "覆蓋 9 個產品類別", "gold"),
                    unsafe_allow_html=True)

    st.markdown("---")

    card_open("📚 資料來源平台 — 我們爬了哪些社群？", "Source Coverage")
    st.markdown(
        f"""<div style="color:{PALETTE['muted']}; font-size:0.9rem;
                       line-height:1.7; margin-bottom:6px;">
        本次社群研究合計爬取
        <b style="color:{PALETTE['us']};">{len(SOCIAL_SOURCES_US)} 個美國平台</b>
        + <b style="color:{PALETTE['jp']};">{len(SOCIAL_SOURCES_JP)} 個日本平台</b>，
        共 <b style="color:{PALETTE['gold']};">
        {SOCIAL_SOURCES_US['引用條數'].sum() + SOCIAL_SOURCES_JP['引用條數'].sum()} 條</b>
        觀察筆記。
        圖上每一條 bar 代表一個獨立平台，長度 = 該平台對我們的洞察所貢獻的觀察筆記數。
        </div>""",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_sources_panel(), use_container_width=True)
    insight(
        "<b>美日資料來源結構不同</b>：美國以 <b>Reddit + 刮鬍／寵物專門評測站</b>為主"
        "（peer-review 文化）；日本以 <b>Yahoo!知恵袋 + マイベスト + 価格.com</b>三大柱"
        "為主（Q&A + 排行榜 + 比價文化）。<br/>"
        "<b>實務意義</b>：美國行銷要去 Reddit、評測 Blog 鋪內容（讓 peer-review 替你說話）；"
        "日本行銷要打進 マイベスト 編輯部排名 + 価格.com 排行榜（用權威背書）。",
    )
    card_close()

    card_open("🌐 美日社群跨類別共通趨勢 — 22 條一眼看完", "跨類別共識")
    cols = st.columns(2)
    with cols[0]:
        st.markdown(
            f'<div style="font-size:0.92rem; font-weight:700; color:{PALETTE["us"]}; '
            f'margin-bottom:10px;">🇺🇸 美國 — Reddit／B&B／評測站</div>',
            unsafe_allow_html=True,
        )
        for icon, title, desc in CROSS_INSIGHTS_US:
            st.markdown(
                f"""
                <div style="background:#fff; border:1px solid {PALETTE['line']};
                            border-left:4px solid {PALETTE['us']};
                            border-radius:10px; padding:10px 14px; margin-bottom:8px;
                            box-shadow:0 2px 6px -4px rgba(0,0,0,0.10);">
                    <div style="font-weight:700; color:{PALETTE['ink']}; font-size:0.93rem;">
                        {icon} {title}
                    </div>
                    <div style="color:{PALETTE['muted']}; font-size:0.85rem; margin-top:3px;
                                line-height:1.55;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with cols[1]:
        st.markdown(
            f'<div style="font-size:0.92rem; font-weight:700; color:{PALETTE["jp"]}; '
            f'margin-bottom:10px;">🇯🇵 日本 — 知恵袋／価格.com／マイベスト</div>',
            unsafe_allow_html=True,
        )
        for icon, title, desc in CROSS_INSIGHTS_JP:
            st.markdown(
                f"""
                <div style="background:#fff; border:1px solid {PALETTE['line']};
                            border-left:4px solid {PALETTE['jp']};
                            border-radius:10px; padding:10px 14px; margin-bottom:8px;
                            box-shadow:0 2px 6px -4px rgba(0,0,0,0.10);">
                    <div style="font-weight:700; color:{PALETTE['ink']}; font-size:0.93rem;">
                        {icon} {title}
                    </div>
                    <div style="color:{PALETTE['muted']}; font-size:0.85rem; margin-top:3px;
                                line-height:1.55;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    insight(
        "<b>美日社群文化差很大</b> — 美國 Reddit／B&B 像消費者互相 peer review，"
        "重視「實際使用感」與「替代品比較」（如『Manscaped 替代品』）；"
        "日本知恵袋／価格.com 像家電專家論壇，"
        "重視「規格數值」（dB、分鐘、IPX）與「専門家監修」的權威認證。<br/>"
        "<b>Listing / 廣告差異化</b>："
        "美國主打「實際痛點解法 + 用戶生活情境」、日本主打「具體規格數字 + 専門家背書」。",
    )
    card_close()

    card_open("🔍 各類別深度洞察 — 痛點 × 好評 × 對標競品", "9 個產品類別")
    cat = st.selectbox("選擇產品類別", list(SOCIAL_CATEGORIES.keys()), index=0)
    data = SOCIAL_CATEGORIES[cat]

    def render_cat_column(market: str, market_data: dict, accent: str) -> None:
        flag = "🇺🇸" if market == "US" else "🇯🇵"
        market_name = "美國" if market == "US" else "日本"
        st.markdown(
            f'<div style="background:linear-gradient(135deg,{accent}15,{accent}05); '
            f'border-radius:12px; padding:14px 16px; border-left:4px solid {accent}; margin-bottom:12px;">'
            f'<div style="font-weight:700; color:{accent}; font-size:1rem; letter-spacing:0.04em;">'
            f'{flag} {market_name} 社群觀察</div></div>',
            unsafe_allow_html=True,
        )
        sub = st.columns(3)
        labels = [
            ("⚠️ 痛點 Pain", "pain", "#D97706"),
            ("💚 好評 Love", "love", "#2E8B57"),
            ("🏷️ 競品偏好 Brands", "brands", PALETTE["gold"]),
        ]
        for col, (label_title, key, color) in zip(sub, labels):
            with col:
                items = "".join([
                    f'<li style="margin-bottom:6px; line-height:1.55;">{x}</li>'
                    for x in market_data[key]
                ])
                st.markdown(
                    f"""
                    <div style="background:#fff; border:1px solid {PALETTE['line']};
                                border-top:3px solid {color};
                                border-radius:12px; padding:14px 16px; min-height:200px;
                                box-shadow:0 3px 10px -6px rgba(0,0,0,0.12);">
                        <div style="font-weight:700; color:{PALETTE['ink']}; font-size:0.92rem;
                                    letter-spacing:0.03em; margin-bottom:8px;">{label_title}</div>
                        <ul style="margin:0; padding-left:18px; color:{PALETTE['charcoal']};
                                  font-size:0.85rem;">{items}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    render_cat_column("US", data["us"], PALETTE["us"])
    render_cat_column("JP", data["jp"], PALETTE["jp"])
    insight(
        f"<b>怎麼用這個區塊</b>：以「{cat}」這個類別為例，"
        "切到上方下拉選單可以瀏覽 9 個類別。每一格代表一個情緒方向。<br/>"
        "<b>痛點欄</b>：列出 Listing 與商品開發時必須避開的地雷（如「拉毛」「漏電」「不防水」）。"
        "<b>好評欄</b>：列出可以拿來當主圖／首條 bullet 的賣點（如「IPX7 可丸洗」「LCD 顯示電量」）。"
        "<b>競品偏好</b>：直接是你的 listing 比較對象（直接寫出對標品 + 規格）。",
        label="閱讀方式",
    )
    card_close()

    card_open("🏷️ 社群被提及的主要競品 — 跨類別覆蓋")
    c_l, c_r = st.columns([3, 2])
    with c_l:
        st.plotly_chart(fig_competitor_mentions(), use_container_width=True)
    with c_r:
        st.plotly_chart(fig_platform_split(), use_container_width=True)
        st.markdown(
            f"""
            <div style="background:{PALETTE['bg']}; border-radius:12px; padding:14px 18px;
                        border:1px solid {PALETTE['line']}; margin-top:10px;
                        font-size:0.88rem; line-height:1.75;">
            <b>解讀</b>：
            <br/>· Panasonic 出現在 9 個類別 — 全市場壟斷者，
            URBANER 在所有類別都會直接對上它（特別是 JP）。
            <br/>· Philips Norelco 跨 5 類別 — US 高端市場的旋轉式代表。
            <br/>· Braun 集中於剃鬚與鬍鬚類別 — 高端標竿。
            <br/>· Manscaped、Casfuy、皇家 ET-3 是品類內 niche
            but high-loyalty 對手。
            </div>
            """,
            unsafe_allow_html=True,
        )
    card_close()

    card_open("🎯 社群觀察 → 明天就能改的 5 個產品/行銷動作", "行動對應")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#fdfaf2,#fff); border-radius:14px;
                    padding:18px 22px; border-left:4px solid {PALETTE['gold']};
                    font-size:0.94rem; line-height:1.85;">
        <b style="color:{PALETTE['ink']};">5 條社群 → 產品的明確對應</b>
        <ol style="margin:8px 0 0 0; padding-left:22px; color:{PALETTE['charcoal']};">
          <li><b>規格欄加入 dB 數值</b> — 日本 38dB／50dB／60dB 心智已建立；
              US 寵物與嬰兒類別也快速跟上。</li>
          <li><b>主圖角落放 IPX7 + USB-C badge</b> — 兩市場社群一致認知為「正式款基線」。</li>
          <li><b>嬰兒、女性類別加入吸力數值或顏色變化</b> — 「12,000Pa」「ピンク／玫瑰」是社群可記憶的訊號。</li>
          <li><b>JP 在 Listing/影片強化「専門家監修」字樣</b> —
              理容師・トリマー・医療クリニックは具體權威佐證。</li>
          <li><b>包裝/開箱拍攝列為品控項</b> — 美國社群會直接寫到評論影響星等。</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
    card_close()


def page_playbook() -> None:
    render_hero(
        "把前面所有統計分析（顧客分群、偏好分析、願付溢價、社群觀察）轉化為「明天就能做」的 11 項具體行銷動作 + 12 個月行銷檔期。"
    )

    card_open("🇺🇸 美國市場劇本 — 主打「禮品 × 多功能套組」")
    for rec in PLAYBOOK_US:
        render_rec(rec, "us")
    card_close()

    card_open("🇯🇵 日本市場劇本 — 主打「精度・耐久・分貝數值化」")
    for rec in PLAYBOOK_JP:
        render_rec(rec, "jp")
    card_close()

    card_open("🌐 兩市場共同的產品開發共識")
    for rec in PLAYBOOK_COMMON:
        render_rec(rec)
    card_close()

    card_open("📅 12 個月行銷檔期建議")
    cal = pd.DataFrame(
        [
            ("2026-Q1", "1–3 月", "🇺🇸 New Year × Valentine", "送禮 + 情人節男士禮盒"),
            ("2026-Q2", "5 月", "🇺🇸 Memorial Day Promo", "黑色週末預熱，Beard 主力檔"),
            ("2026-Q2", "6 月", "🇺🇸🇯🇵 Father's Day / 父の日", "雙市場禮盒 + のし対応"),
            ("2026-Q3", "9 月", "🇯🇵 楽天お買い物マラソン", "楽天直営店倍數活動"),
            ("2026-Q4", "10 月", "🇺🇸 Prime Big Deal Days", "套組型 SKU 主推"),
            ("2026-Q4", "11 月", "🇺🇸 Black Friday × Cyber Monday", "全年最大檔期，Hero SKU 集火"),
            ("2026-Q4", "12 月", "🇺🇸🇯🇵 Christmas × お歳暮", "禮盒包裝 + USB-C 快充 bundle"),
        ],
        columns=["季", "月", "檔期", "重點行動"],
    )
    st.dataframe(cal, hide_index=True, use_container_width=True)
    insight(
        "<b>全年三個非打不可的檔期</b>：6 月父の日（US + JP 雙打）、"
        "11 月 Black Friday × Cyber Monday（US 全年最大）、12 月 お歳暮（JP 禮品旺季）。<br/>"
        "<b>排程節奏</b>：每個檔期前 6 週開始預熱（A+ 素材 + PPC 預算配置），前 2 週進主圖／封面替換，"
        "檔期結束後 2 週清庫存並把高轉換素材回填日常 Listing。<br/>"
        "<b>非檔期月份</b>（4 月、7 月、8 月）做品牌經營：UGC 收集、開箱影片、与 KOL 合作（特別是 JP マイベスト編輯部）。",
    )
    card_close()


# ─────────────────────────────────────────────────────────────
# 主程式
# ─────────────────────────────────────────────────────────────
def main() -> None:
    inject_css()

    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 6px 4px 14px 4px;">
              <div style="color:{PALETTE['gold_soft']}; font-size:0.72rem; letter-spacing:0.18em;
                          text-transform:uppercase; font-weight:600;">URBANER</div>
              <div style="font-size:1.35rem; font-weight:700; color:white; margin-top:4px;">
                  雙市場戰略儀表板</div>
              <div style="color:rgba(255,255,255,0.55); font-size:0.82rem; margin-top:6px;
                          line-height:1.55;">
                  Bright Idea, Great Value<br/>品味源自細節
              </div>
            </div>
            <hr/>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "導覽",
            [
                "📊 執行儀表板",
                "🌎 雙市場對比",
                "🎯 STP 策略分析",
                "⚖️ Conjoint 偏好",
                "🏆 最優產品組合",
                "📣 社群洞察",
                "💡 行銷劇本",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown(
            f"""
            <div style="font-size:0.78rem; color:rgba(255,255,255,0.7); line-height:1.7;">
              <b>資料來源</b><br/>
              · 11,523 則 Amazon US/JP 真實評論<br/>
              · 88 個 URBANER SKU × 114 屬性評分<br/>
              · 兩市場 SKU 真實售價 + 月銷量<br/>
              · 9 類別競品評論 + 社群媒體洞察<br/><br/>
              <b>分析方法</b><br/>
              · 評論顯著度 × 品質雙軸 STP 分群<br/>
              · 觀察型 Conjoint 偏好分析（Logit）<br/>
              · 願付溢價（WTP）+ 市佔模擬（MNL）<br/><br/>
              資料截止 2026-05-05
            </div>
            """,
            unsafe_allow_html=True,
        )

    if page == "📊 執行儀表板":
        page_overview()
    elif page == "🌎 雙市場對比":
        page_dual_market()
    elif page == "🎯 STP 策略分析":
        page_stp()
    elif page == "⚖️ Conjoint 偏好":
        page_conjoint()
    elif page == "🏆 最優產品組合":
        page_best_product()
    elif page == "📣 社群洞察":
        page_social()
    elif page == "💡 行銷劇本":
        page_playbook()

    st.markdown(
        '<div class="footer">© 2026 URBANER × FourSight Lab — 產學合作專案儀表板</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
