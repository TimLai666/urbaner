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
    initial_sidebar_state="expanded",
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
            h1, h2, h3, h4 {{ color: {PALETTE['ink']}; letter-spacing: -0.01em; }}
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
                color: #fff; margin: 0; font-size: 2.0rem; font-weight: 700; letter-spacing: -0.02em;
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
SOCIAL_PLATFORMS_US = [
    "Reddit (r/Wicked_Edge, r/AsianBeauty, r/pets)",
    "Badger & Blade（B&B）刮鬍社群",
    "Sharpologist 評測站",
    "ShavingAdvisor 評測站",
    "ShaverCheck 比較站",
    "Whole Dog Journal 寵物美容",
    "redditfavorites.com 聚合",
    "PoodleForum / ResetEra",
    "MetaFilter / Bogleheads",
    "TechGearLab / FashionBeans / Dogster",
]
SOCIAL_PLATFORMS_JP = [
    "Yahoo!知恵袋（40+ 歲影響力大）",
    "価格.com 排行榜 + 評論",
    "マイベスト（my-best.com）",
    "Amazon JP / 楽天みんなのレビュー",
    "note（年輕層 DIY 體驗）",
    "NOJIMA / Impress Watch 家電新聞",
    "kakaku.com 比較文化",
    "LIPS（美容類）",
    "LDK（雜誌實測）",
    "5ch 家電板專門 thread",
    "BIGLOBE 暮らし／きちデン",
    "PEPPY / Petio / PETOKOTO 寵物站",
]

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
        font=dict(family="Inter, Noto Sans TC, sans-serif", color=PALETTE["charcoal"], size=12),
        title=dict(text=current_title, font=dict(color=PALETTE["ink"], size=15)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0)",
        ),
    )
    # subplot 標題字體與顏色
    fig.update_annotations(
        font=dict(size=12, color=PALETTE["ink"], family="Inter, Noto Sans TC, sans-serif"),
        selector=lambda a: getattr(a, "yref", None) == "paper" and getattr(a, "y", 0) >= 0.95,
    )
    fig.update_xaxes(gridcolor=PALETTE["line"], zeroline=False)
    fig.update_yaxes(gridcolor=PALETTE["line"], zeroline=False)
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
        subplot_titles=("🇺🇸 美國 — 屬性升級偏好份額", "🇯🇵 日本 — 屬性升級偏好份額"),
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
            textfont=dict(color="#3B3D44", size=11),
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
    fig.update_xaxes(title_text="偏好份額 (%)", row=1, col=1, range=[0, 1.5])
    fig.update_xaxes(title_text="偏好份額 (%)", row=1, col=2, range=[0, 115])
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
        textposition="outside", textfont=dict(size=11),
        cliponaxis=False,
        hovertemplate="%{y}<br>WTP=$%{x:.2f}<extra></extra>",
        row=1, col=1,
    )
    fig.add_bar(
        y=jp["屬性"], x=jp["WTP (JPY/品質分)"], orientation="h",
        marker_color=[PALETTE["jp"] if s else "#F2B5C2" for s in jp["顯著"]],
        text=jp["WTP (JPY/品質分)"].apply(lambda v: f"¥{v:,.0f}"),
        textposition="outside", textfont=dict(size=11),
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
            textfont=dict(size=12, family="Inter"),
            cliponaxis=False,
            customdata=df["區隔"],
            hovertemplate="%{customdata}<br>占比 %{y:.1f}%<extra></extra>",
            row=1, col=col, showlegend=False,
        )

    fig.update_yaxes(title_text="占比 (%)", range=[0, 125], row=1, col=1)
    fig.update_yaxes(title_text="占比 (%)", range=[0, 125], row=1, col=2)
    fig.update_xaxes(tickfont=dict(size=11))
    return style_fig(fig, height=480)


def fig_choice_set_donut() -> go.Figure:
    """MNL 選擇集 — 兩個甜甜圈中央顯示 URBANER 份額，
    色塊用 annotation 取代 legend，避免在窄欄位空間內 legend 換行。"""
    fig = make_subplots(
        rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("🇺🇸 美國", "🇯🇵 日本"),
        horizontal_spacing=0.06,
    )
    fig.add_trace(go.Pie(
        labels=["競品", "URBANER", "最佳設計組合"],
        values=[94.67, 5.21, 0.12], hole=0.6, sort=False,
        marker=dict(colors=["#D4D7E3", PALETTE["us"], PALETTE["gold"]],
                    line=dict(color="#fff", width=2)),
        textinfo="none",
        hovertemplate="%{label}<br>%{percent}<extra></extra>",
        pull=[0, 0.02, 0.15],
        showlegend=False,
    ), row=1, col=1)
    fig.add_trace(go.Pie(
        labels=["競品", "URBANER", "最佳設計組合"],
        values=[85.60, 11.26, 3.14], hole=0.6, sort=False,
        marker=dict(colors=["#E4D2D6", PALETTE["jp"], PALETTE["gold"]],
                    line=dict(color="#fff", width=2)),
        textinfo="none",
        hovertemplate="%{label}<br>%{percent}<extra></extra>",
        pull=[0, 0.02, 0.1],
        showlegend=False,
    ), row=1, col=2)
    # 中心 URBANER 份額
    fig.add_annotation(
        text="<b>URBANER</b><br><span style='font-size:22px;color:#2E5BFF'>5.21%</span>",
        x=0.205, y=0.55, showarrow=False, xref="paper", yref="paper",
        font=dict(size=11, color=PALETTE["ink"], family="Inter"),
    )
    fig.add_annotation(
        text="<b>URBANER</b><br><span style='font-size:22px;color:#D32F4D'>11.26%</span>",
        x=0.795, y=0.55, showarrow=False, xref="paper", yref="paper",
        font=dict(size=11, color=PALETTE["ink"], family="Inter"),
    )
    # 自製 legend（用 annotation 排成一行）— 跨欄位下方
    fig.add_annotation(
        text=(
            "<span style='color:#9CA3AF'>■</span> 競品  &nbsp;&nbsp;"
            "<span style='color:#2E5BFF'>■</span> URBANER (US)  &nbsp;&nbsp;"
            "<span style='color:#D32F4D'>■</span> URBANER (JP)  &nbsp;&nbsp;"
            "<span style='color:#C9A36F'>■</span> 最佳設計組合"
        ),
        x=0.5, y=-0.05, showarrow=False, xref="paper", yref="paper",
        font=dict(size=11, color=PALETTE["charcoal"], family="Inter"),
        xanchor="center", yanchor="top",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=60))
    fig.update_annotations(font_size=12, selector=dict(text="🇺🇸 美國"))
    fig.update_annotations(font_size=12, selector=dict(text="🇯🇵 日本"))
    return style_fig(fig, height=460)


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
        textposition="outside", textfont=dict(size=11),
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
    fig = go.Figure()
    fig.add_bar(
        x=["美國社群", "日本社群"],
        y=[len(SOCIAL_PLATFORMS_US), len(SOCIAL_PLATFORMS_JP)],
        marker_color=[PALETTE["us"], PALETTE["jp"]],
        text=[len(SOCIAL_PLATFORMS_US), len(SOCIAL_PLATFORMS_JP)],
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
        "結合 11,523 則評論的 STP 統計與 Conjoint 偏好實證，"
        "盤點 URBANER 在美國（4,360）與日本（7,163）兩市場的競爭位置，"
        "並產出可直接套用到 Listing / 套組 / 行銷檔期的策略建議。"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi("總評論數", "11,523", "US 4,360 ｜ JP 7,163", "gold"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("自家 SKU 數", "88", "US 52 ｜ JP 36", "gold"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("US Hero SKU", "B0FL267TCG", "Beard / Mustache · ★4.52", "us"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("JP Hero SKU", "B0GBWZBMS5", "Nose / Ear · ★4.61", "jp"), unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi("US 大眾族群", "76.5%", "日常自用大眾 ｜ Avg★ 3.18", "us"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("JP 大眾族群", "91.6%", "CP 值優先大眾 ｜ Avg★ 3.46", "jp"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("US 最佳組合 P(購買)", "83.3%", "USB-C × 38 段 × ≥10 件套組", "gold"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("JP 最佳組合 P(購買)", "89.1%", "IPX7 × 90 分高續航全配款", "gold"), unsafe_allow_html=True)

    st.markdown("---")

    col_l, col_r = st.columns([5, 4])
    with col_l:
        card_open("⚡ 三大核心洞察", "Executive")
        st.markdown(
            f"""
- <span class="pill us">US</span> **送禮場景 × 多功能套組是市場決策主軸**
  ANOVA Top 1 `gift_suitability_men` F=1299、Top 3 `num_grooming_functions` F=1193；
  顯示父親節 / 聖誕節送禮情境驅動絕大多數美國電剪購買決策。
- <span class="pill jp">JP</span> **附件齊全度 × 0.5mm 精度 × 電源類型是日本決策三軸**
  ANOVA Top 1-3 累計 F 值 6,870；
  日本顧客重視 38 段刻度、附件套組完整、CP 值高、可丸洗。
- <span class="pill gold">兩市場共識</span> **IPX7+ × ≥7 件套組 = 2026 新品最低門檻**
  兩市場 ANOVA、社群洞察一致；新 SKU 必須踩上這道規格線。
""",
            unsafe_allow_html=True,
        )
        card_close()

    with col_r:
        card_open("🪒 兩市場目前份額位置", "MNL Choice Set")
        st.plotly_chart(fig_choice_set_donut(), use_container_width=True)
        st.markdown(
            f"""<div style="color:{PALETTE['muted']}; font-size:0.85rem; line-height:1.6;">
            US 場上 URBANER 僅 5.21%，最佳組合（USB-C × 38 段 × ≥10 件套組）只擠進全選擇集第 33 名；
            <b>痛點在套組形態</b>。JP 較好，已佔 11.26%，且 IPX7 × 90 分高續航全配款排到全場第 9。
            </div>""",
            unsafe_allow_html=True,
        )
        card_close()

    card_open("📊 屬性重要性對比（兩市場一張圖看完）", "Conjoint")
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
    render_hero("並列檢視美國與日本的競爭結構、屬性重要性、區隔組成與 Hero SKU。")

    card_open("🌎 屬性區隔力 — ANOVA F 值（越大代表區隔越分明）")
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

    card_open("👥 區隔組成 — 占比 × 平均星等")
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

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(fig_segment_sunburst(SEGMENTS_US, "🇺🇸 美國區隔組成（按人數）", "us"), use_container_width=True)
    with col_r:
        st.plotly_chart(fig_segment_sunburst(SEGMENTS_JP, "🇯🇵 日本區隔組成（按人數）", "jp"), use_container_width=True)

    card_open("🏆 Hero SKU 對照 — 兩市場最接近理想點的商品")
    h1, h2 = st.columns(2)
    with h1:
        st.markdown(
            f"""
            <div class="spec">
                <h4>🇺🇸 US Hero SKU</h4>
                <div class="name">{HERO_SKU_US['asin']}</div>
                <div class="meta">{HERO_SKU_US['category']} ｜ n={HERO_SKU_US['n_reviews']}</div>
                <table>
                    <tr><td>距理想點 RMS</td><td>{HERO_SKU_US['distance']}</td></tr>
                    <tr><td>平均星等</td><td>★ {HERO_SKU_US['avg_star']}</td></tr>
                    <tr><td>MNL 同類偏好份額</td><td>{HERO_SKU_US['preference_share']}%</td></tr>
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
                <h4>🇯🇵 JP Hero SKU</h4>
                <div class="name">{HERO_SKU_JP['asin']}</div>
                <div class="meta">{HERO_SKU_JP['category']} ｜ n={HERO_SKU_JP['n_reviews']}</div>
                <table>
                    <tr><td>距理想點 RMS</td><td>{HERO_SKU_JP['distance']}</td></tr>
                    <tr><td>平均星等</td><td>★ {HERO_SKU_JP['avg_star']}</td></tr>
                    <tr><td>MNL 全場偏好份額</td><td>{HERO_SKU_JP['preference_share']}%</td></tr>
                    <tr><td>建議策略</td><td>父の日 × 楽天直営主打</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    card_close()


def page_stp() -> None:
    render_hero(
        "STP 是「先看誰在買、再選要服務誰、最後決定我是誰」。"
        "兩市場的決策軸完全不同 — US 由送禮場景驅動、JP 由規格深度驅動。"
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

    with card("🎯 Segmentation 區隔表 — 兩市場並列"):
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

    card_open("📈 Targeting — 區隔之間最有差異的屬性（ANOVA F）")
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

    card_open("🗺️ Positioning — 兩市場 Perceptual Map")
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
    card_close()

    card_open("🔥 屬性熱圖 — Top 20 屬性 × Top 12 SKU 品質分")
    h1, h2 = st.columns(2)
    with h1:
        heat_us = OUT_STP_US / "quality_heatmap.png"
        if heat_us.exists():
            st.image(str(heat_us), caption="🇺🇸 US 品質熱圖", use_container_width=True)
    with h2:
        heat_jp = OUT_STP_JP / "quality_heatmap.png"
        if heat_jp.exists():
            st.image(str(heat_jp), caption="🇯🇵 JP 品質熱圖", use_container_width=True)
    card_close()


def page_conjoint() -> None:
    render_hero(
        "Conjoint 揭示「消費者真正在比什麼」。"
        "Split-model Logit + 真實售價的 WTP，告訴你每升 1 分品質可以多賣多少錢。"
    )

    card_open("⚖️ 屬性重要性 — Split-Logit Part-Worth")
    st.plotly_chart(fig_importance_compare(), use_container_width=True)
    card_close()

    card_open("💰 WTP 願付溢價（路線 A，真實售價重估）")
    st.plotly_chart(fig_wtp_panel(), use_container_width=True)
    st.markdown(
        f"""<div style="color:{PALETTE['muted']}; font-size:0.86rem; line-height:1.7;">
        <b>解讀</b>：每提升 1 個品質分，美國消費者願意為「機身尺寸」多付 $89.81（p&lt;0.05 顯著）；
        日本消費者願意為「長度調整段數」多付 ¥7,961（p&lt;0.05）。
        <br>顏色深者為統計顯著（p&lt;0.05），淺色為方向性參考。
        JP β_price 為正（高價品質訊號），WTP 數值僅供方向，不宜直接定價。
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    card_open("🚀 升級模擬 — 把 URBANER 屬性升到 High，份額會跳多少？")
    st.plotly_chart(fig_upgrade_panel(), use_container_width=True)
    st.markdown(
        """<div style="font-size:0.92rem; line-height:1.7;">
        <b>策略意涵</b>：
        <ul style="margin-left:-20px;">
          <li><b>JP 應優先升「長度調整段數」</b> — 從 1.6% 跳到 94.8%（+93.2pp），是所有升級項目中爆發力最大的單一決策。</li>
          <li>JP 「調整精度」升至 0.5mm 也帶來 +84.6pp，與「段數」是兩條互補升級路徑。</li>
          <li>US 屬性升級個別增幅都不大（&lt;1pp），代表 US 端的問題不是單屬性而是「整體套組形態」，建議用組合拳：附件 + 功能合一 + USB-C 一起升。</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )
    card_close()

    # WTP 表格輔助
    card_open("📋 WTP 完整對照表")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<span class="pill us">USD / 品質分</span>', unsafe_allow_html=True)
        st.dataframe(WTP_US, hide_index=True, use_container_width=True)
    with c2:
        st.markdown('<span class="pill jp">JPY / 品質分</span>', unsafe_allow_html=True)
        st.dataframe(WTP_JP, hide_index=True, use_container_width=True)
    card_close()


def page_best_product() -> None:
    render_hero(
        "兩市場最佳組合的「骨幹」相同（USB-C × 38 段 × ≥10 件套組），"
        "但 US 把資源放在「USB-C 快充 × 1合1 精修」，JP 把資源放在「IPX7 × 90 分續航 × 1mm 精度」。"
    )

    card_open("🏆 兩市場最佳產品組合（自 24 種設計組合中以 Logit 效用挑選）")
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
    with c1:
        st.markdown(kpi("美國社群來源", str(len(SOCIAL_PLATFORMS_US)), "Reddit · B&B · Sharpologist 等", "us"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("日本社群來源", str(len(SOCIAL_PLATFORMS_JP)), "知恵袋 · 価格.com · マイベスト 等", "jp"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("跨類別共識", "22 條", f"US {len(CROSS_INSIGHTS_US)} + JP {len(CROSS_INSIGHTS_JP)}", "gold"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("被提及競品數",
                        str(len(TOP_COMPETITOR_MENTIONS)),
                        "覆蓋 9 個產品類別", "gold"),
                    unsafe_allow_html=True)

    st.markdown("---")

    card_open("🌐 兩市場社群跨類別共通洞察", "Cross-Category Trends")
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
    card_close()

    card_open("🔍 9 類別深度社群洞察 — 痛點 × 好評 × 競品偏好", "Category Deep Dive")
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

    card_open("🎯 社群洞察轉化為產品 + 行銷規格", "Action Mapping")
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
        "從統計到行動：把 ANOVA、Conjoint、WTP、社群洞察轉化為「明天就能做」的 11 項行銷動作。"
    )

    card_open("🇺🇸 美國市場劇本 — Gift-Ready × Multi-Function Pro")
    for rec in PLAYBOOK_US:
        render_rec(rec, "us")
    card_close()

    card_open("🇯🇵 日本市場劇本 — 精度・耐久・分貝数値化")
    for rec in PLAYBOOK_JP:
        render_rec(rec, "jp")
    card_close()

    card_open("🌐 兩市場通用 R&D 共識")
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
              · Review-Mining STP（Axis A/B）<br/>
              · Revealed-Pref Logistic Conjoint<br/>
              · Hedonic Pricing + MNL Share-of-Pref<br/><br/>
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
