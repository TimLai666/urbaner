"""
URBANER 延伸分析 — 視覺化圖表生成
為路線A/B/C 各生成對應圖表，存於 output_conjoint/charts/
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import glob
import warnings
import statsmodels.api as sm
warnings.filterwarnings("ignore")
from pathlib import Path

# ── 字型設定 ──────────────────────────────────────────────────────────────────
plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

CHART_DIR = Path("output_conjoint/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

URBANER_COLOR = "#E8472A"   # 品牌紅
COMP_COLOR    = "#7A8FA6"   # 競品灰藍
ACCENT_COLOR  = "#F5A623"   # 強調橘
BG_COLOR      = "#F8F9FA"
GRID_COLOR    = "#E0E0E0"

ATTR_ZH = {
    "power_source": "電源類型",
    "waterproof":   "防水等級",
    "attachments":  "附件件數",
    "guide_comb":   "長度調整段數",
    "functions":    "功能合一數",
    "charging":     "充電方式(USB-C)",
    "size":         "機身尺寸",
    "precision":    "調整精度",
    "battery_life": "電池續航時間",
}

URBANER_US_001 = ["B0823PD6XD", "B0BVVKKXFZ", "B0GL2DKVQH", "B0GL2GP74J"]
URBANER_JP_001 = ["B07CYQVK16", "B07CYZH2XC", "B07CZ3KDN9", "B0BL2YWH3N", "B0DSB44YJZ", "B0G492LXS9"]
COMP_US_001    = ["B008KEJ1LM","B08P4HHSZT","B09XVP6YPM","B0BQ1GZY7H","B0CGHWFF71",
                  "B0CQKZ3N5G","B0D97YBP2X","B0F2RSTDSJ","B0FCYBJK6T","B0FHXTJ8JN",
                  "B0FL267TCG","B0FS5TCR3B","B0G1Z1QKJ8","B0GHS5T1Y3","B0GLJRLS5G"]
COMP_JP_001    = ["B001K85BN2","B001K85BNC","B016JNKVHI","B0742G961R","B07YFFLDQB",
                  "B08LGGMP5W","B0B7R5TJLD","B0BVQDYVTS","B0BY18J8D9","B0BY1KRJZ1",
                  "B0F2M2NSBX","B0FJS3QR1W","B0FJS3TF3V","B0FQW4KWRD","B0FQWLR3BW"]

US_ATTR_COLS = {
    "power_source": "power_source_type_quality",
    "waterproof":   "waterproof_rating_ipx8_quality",
    "attachments":  "total_attachments_count_quality",
    "guide_comb":   "guide_comb_variety_quality",
    "functions":    "num_grooming_functions_quality",
    "charging":     "usb_c_charging_quality",
    "size":         "product_dimensions_size_quality",
}
JP_ATTR_COLS = {
    "attachments":  "total_attachments_count_quality",
    "guide_comb":   "guide_comb_variety_quality",
    "precision":    "adjustable_comb_settings_quality",
    "power_source": "power_source_type_quality",
    "waterproof":   "waterproof_rating_ipx8_quality",
    "battery_life": "battery_life_duration_quality",
    "size":         "product_dimensions_size_quality",
}

# ══════════════════════════════════════════════════════════════════════════════
# 資料重建（與 extended_analysis.py 相同邏輯）
# ══════════════════════════════════════════════════════════════════════════════

us_q = pd.read_csv("output_stp/market_stp_us/product_quality_scorecard.csv")
jp_q = pd.read_csv("output_stp/market_stp_jp/product_quality_scorecard.csv")
us_r = pd.read_csv("output_stp/market_stp_us/review_scoring_table.csv")
jp_r = pd.read_csv("output_stp/market_stp_jp/review_scoring_table.csv")
us_q = us_q.merge(us_r.groupby("product")["rating"].mean().rename("avg_star").reset_index(), on="product", how="left")
jp_q = jp_q.merge(jp_r.groupby("product")["rating"].mean().rename("avg_star").reset_index(), on="product", how="left")

def load_prices():
    us_dfs, jp_dfs = [], []
    for f in glob.glob("rawdata_Urbaner/amazon_sales/US_sales/**/*.txt", recursive=True):
        try:
            us_dfs.append(pd.read_csv(f, sep="\t", encoding="utf-8", on_bad_lines="skip", usecols=["asin","item-price"]))
        except: pass
    for f in glob.glob("rawdata_Urbaner/amazon_sales/JP_sales/**/*.txt", recursive=True):
        try:
            jp_dfs.append(pd.read_csv(f, sep="\t", encoding="shift-jis", on_bad_lines="skip", usecols=["asin","item-price"]))
        except: pass
    us_ord = pd.concat(us_dfs, ignore_index=True)
    jp_ord = pd.concat(jp_dfs, ignore_index=True)
    us_ord["item-price"] = pd.to_numeric(us_ord["item-price"], errors="coerce")
    jp_ord["item-price"] = pd.to_numeric(jp_ord["item-price"], errors="coerce")
    us_p = us_ord[us_ord["item-price"]>0].groupby("asin")["item-price"].median().reset_index().rename(columns={"asin":"product","item-price":"price_usd"})
    jp_p = jp_ord[jp_ord["item-price"]>0].groupby("asin")["item-price"].median().reset_index().rename(columns={"asin":"product","item-price":"price_jpy"})
    return us_p, jp_p

def load_comp():
    dfs = [pd.read_excel(f) for f in glob.glob("rawdata_Urbaner/competitor_sales/001_Beard_Mustache_Trimmers/*.xlsx")]
    all_comp = pd.concat(dfs, ignore_index=True)
    us_cp = all_comp[all_comp["站点"]=="US"].groupby("ASIN")["平均单价($)"].mean().reset_index().rename(columns={"ASIN":"product","平均单价($)":"price_usd"})
    jp_cp = all_comp[all_comp["站点"]=="JP"].groupby("ASIN")["平均单价(￥)"].mean().reset_index().rename(columns={"ASIN":"product","平均单价(￥)":"price_jpy"})
    latest = all_comp[all_comp["最近几月"]==all_comp["最近几月"].max()]
    us_vol = latest[latest["站点"]=="US"][["ASIN","月销量","商品"]].rename(columns={"ASIN":"product","月销量":"monthly_sales","商品":"name"})
    jp_vol = latest[latest["站点"]=="JP"][["ASIN","月销量","商品"]].rename(columns={"ASIN":"product","月销量":"monthly_sales","商品":"name"})
    return us_cp, jp_cp, us_vol, jp_vol

urb_us_p, urb_jp_p = load_prices()
comp_us_p, comp_jp_p, comp_us_vol, comp_jp_vol = load_comp()

def merge_price(scorecard, urb_p, urb_col, comp_asins, comp_p, comp_col):
    df = scorecard.merge(urb_p, on="product", how="left")
    comp_map = comp_p.set_index("product")[comp_col]
    mask = df["product"].isin(comp_asins)
    df.loc[mask, urb_col] = df.loc[mask, "product"].map(comp_map)
    return df

us_df = merge_price(us_q, urb_us_p, "price_usd", COMP_US_001, comp_us_p, "price_usd")
jp_df = merge_price(jp_q, urb_jp_p, "price_jpy", COMP_JP_001, comp_jp_p, "price_jpy")

def run_splits(df, attr_cols, price_col):
    df2 = df.dropna(subset=[price_col]+list(attr_cols.values()))
    df2["preferred"] = (df2["avg_star"] >= df2["avg_star"].median()).astype(int)
    # price
    Xp = sm.add_constant(df2[[price_col]])
    try:
        mp = sm.Logit(df2["preferred"], Xp).fit(disp=False, maxiter=200)
        beta_price = mp.params[price_col]
        pval_price = mp.pvalues[price_col]
    except:
        beta_price = pval_price = np.nan
    parts = {}
    for attr, col in attr_cols.items():
        X = sm.add_constant(df2[[col]])
        try:
            m = sm.Logit(df2["preferred"], X).fit(disp=False, maxiter=200)
            parts[attr] = {"coef": m.params[col], "pval": m.pvalues[col]}
        except:
            parts[attr] = {"coef": np.nan, "pval": np.nan}
    return beta_price, pval_price, parts, df2

bp_us, pp_us, parts_us, us_df2 = run_splits(us_df, US_ATTR_COLS, "price_usd")
bp_jp, pp_jp, parts_jp, jp_df2 = run_splits(jp_df, JP_ATTR_COLS, "price_jpy")

def compute_sop(scorecard, attr_cols, parts, urbaner_asins, comp_asins, vol_df, price_col):
    all_asins = urbaner_asins + comp_asins
    df = scorecard[scorecard["product"].isin(all_asins)].copy()
    utilities = []
    for _, row in df.iterrows():
        U = sum(parts.get(a,{}).get("coef",0)*row.get(c,0)
                for a,c in attr_cols.items()
                if not np.isnan(parts.get(a,{}).get("coef",np.nan) or np.nan)
                and not np.isnan(row.get(c, np.nan)))
        utilities.append(U)
    utilities = np.array(utilities, dtype=float)
    exp_u = np.exp(utilities - utilities.max())
    shares = exp_u / exp_u.sum() * 100
    df = df.copy()
    df["sop_pct"] = shares
    df["is_urbaner"] = df["product"].isin(urbaner_asins)
    df = df.merge(vol_df[["product","monthly_sales"]], on="product", how="left")
    return df.sort_values("sop_pct", ascending=False)

sop_us = compute_sop(us_q, US_ATTR_COLS, parts_us, URBANER_US_001, COMP_US_001, comp_us_vol, "price_usd")
sop_jp = compute_sop(jp_q, JP_ATTR_COLS, parts_jp, URBANER_JP_001, COMP_JP_001, comp_jp_vol, "price_jpy")

def upgrade_sims(sop_df, attr_cols, parts, urbaner_asins):
    sims = []
    for attr, col in attr_cols.items():
        if col not in sop_df.columns: continue
        urb_vals = sop_df[sop_df["product"].isin(urbaner_asins)][col]
        if urb_vals.empty or urb_vals.mean() >= 9: continue
        df_new = sop_df.copy()
        df_new.loc[df_new["product"].isin(urbaner_asins), col] = 10.0
        utils = []
        for _, row in df_new.iterrows():
            U = sum(parts.get(a,{}).get("coef",0)*row.get(c,0)
                    for a,c in attr_cols.items()
                    if not np.isnan(parts.get(a,{}).get("coef",np.nan) or np.nan)
                    and not np.isnan(row.get(c, np.nan)))
            utils.append(U)
        utils = np.array(utils, dtype=float)
        exp_u = np.exp(utils - utils.max())
        new_shares = exp_u / exp_u.sum() * 100
        df_new["sop_new"] = new_shares
        orig = sop_df[sop_df["product"].isin(urbaner_asins)]["sop_pct"].sum()
        new  = df_new[df_new["product"].isin(urbaner_asins)]["sop_new"].sum()
        sims.append({"attr": attr, "orig": round(orig,2), "new": round(new,2), "delta": round(new-orig,2)})
    return sorted(sims, key=lambda x: -x["delta"])

sims_us = upgrade_sims(sop_us, US_ATTR_COLS, parts_us, URBANER_US_001)
sims_jp = upgrade_sims(sop_jp, JP_ATTR_COLS, parts_jp, URBANER_JP_001)

# ══════════════════════════════════════════════════════════════════════════════
# 圖表1：路線A — WTP 水平條形圖（US + JP 並排）
# ══════════════════════════════════════════════════════════════════════════════

def plot_wtp(parts_us, bp_us, parts_jp, bp_jp):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.patch.set_facecolor(BG_COLOR)

    for ax, parts, bp, label, sym, currency in [
        (axes[0], parts_us, bp_us, "🇺🇸 美國市場", "$", "USD"),
        (axes[1], parts_jp, bp_jp, "🇯🇵 日本市場", "¥", "JPY"),
    ]:
        ax.set_facecolor(BG_COLOR)
        attrs = [(a, v) for a, v in parts.items() if not np.isnan(v.get("coef", np.nan))]
        attrs_sorted = sorted(attrs, key=lambda x: abs(x[1]["coef"]), reverse=True)

        names = [ATTR_ZH.get(a, a) for a, _ in attrs_sorted]
        coefs = [v["coef"] for _, v in attrs_sorted]
        pvals = [v["pval"] for _, v in attrs_sorted]

        if not np.isnan(bp) and bp < 0:
            wtp_vals = [c / abs(bp) for c in coefs]
            xlabel = f"WTP（{sym}/品質分）"
            reliable = True
        else:
            wtp_vals = coefs
            xlabel = "β 係數（方向性，β_price > 0）"
            reliable = False

        colors = [URBANER_COLOR if p < 0.05 else ACCENT_COLOR if p < 0.1 else COMP_COLOR
                  for p in pvals]
        bars = ax.barh(names[::-1], wtp_vals[::-1], color=colors[::-1],
                       edgecolor="white", linewidth=0.5, height=0.6)

        for bar, val, pv in zip(bars, wtp_vals[::-1], pvals[::-1]):
            sign = "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else "†" if pv < 0.1 else ""
            xpos = bar.get_width() + (max(abs(v) for v in wtp_vals) * 0.02)
            ax.text(xpos, bar.get_y() + bar.get_height()/2,
                    f"{val:+.2f} {sign}", va="center", ha="left", fontsize=9,
                    color="#333333")

        ax.axvline(0, color="#666666", linewidth=1, linestyle="--")
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_title(f"{label}\nWTP 估計（n={len(attrs)}屬性，β_price={bp:.4f}）",
                     fontsize=11, fontweight="bold", pad=10)
        ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8)
        ax.spines[["top","right","left"]].set_visible(False)

        if not reliable:
            ax.text(0.5, -0.18, "⚠ β_price > 0，數值為方向性參考",
                    transform=ax.transAxes, ha="center", fontsize=8.5,
                    color="#E8472A", style="italic")

    legend_els = [
        mpatches.Patch(color=URBANER_COLOR, label="p < 0.05（顯著）"),
        mpatches.Patch(color=ACCENT_COLOR,  label="p < 0.10（邊際）"),
        mpatches.Patch(color=COMP_COLOR,    label="p ≥ 0.10（不顯著）"),
    ]
    fig.legend(handles=legend_els, loc="lower center", ncol=3,
               fontsize=9, framealpha=0.9, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("路線A：各屬性 WTP 願付溢價", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out = CHART_DIR / "chartA_wtp.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"  ✅ {out}")


# ══════════════════════════════════════════════════════════════════════════════
# 圖表2：路線B — 市佔圓餅 + 升級條形圖
# ══════════════════════════════════════════════════════════════════════════════

def plot_sop(sop_us, sop_jp, sims_us, sims_jp):
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor(BG_COLOR)
    gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    for row_idx, (sop_df, sims, urbaner_asins, mkt_label) in enumerate([
        (sop_us, sims_us, URBANER_US_001, "🇺🇸 美國市場"),
        (sop_jp, sims_jp, URBANER_JP_001, "🇯🇵 日本市場"),
    ]):
        # ── 子圖1：市佔圓餅 ────────────────────────────────────────────────
        ax_pie = fig.add_subplot(gs[row_idx, 0])
        ax_pie.set_facecolor(BG_COLOR)
        urb_share = sop_df[sop_df["product"].isin(urbaner_asins)]["sop_pct"].sum()
        comp_share = 100 - urb_share
        wedges, texts, autotexts = ax_pie.pie(
            [urb_share, comp_share],
            labels=["URBANER", "競品"],
            colors=[URBANER_COLOR, COMP_COLOR],
            autopct="%1.1f%%", startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 10},
        )
        for at in autotexts:
            at.set_fontsize(11)
            at.set_fontweight("bold")
            at.set_color("white")
        ax_pie.set_title(f"{mkt_label}\n偏好市佔份額", fontsize=11, fontweight="bold")

        # ── 子圖2：Top 8 SKU 橫條 ──────────────────────────────────────────
        ax_bar = fig.add_subplot(gs[row_idx, 1])
        ax_bar.set_facecolor(BG_COLOR)
        top8 = sop_df.head(8).copy()
        top8["short_id"] = top8["product"].str[-6:]
        top8["label"] = top8.apply(
            lambda r: f"★{r['short_id']}" if r["product"] in urbaner_asins else r["short_id"], axis=1
        )
        bar_colors = [URBANER_COLOR if p in urbaner_asins else COMP_COLOR
                      for p in top8["product"]]
        bars = ax_bar.barh(top8["label"][::-1], top8["sop_pct"][::-1],
                           color=bar_colors[::-1], edgecolor="white", height=0.6)
        for bar, val, prod in zip(bars, top8["sop_pct"][::-1], top8["product"].tolist()[::-1]):
            label_txt = f"{val:.1f}%"
            ax_bar.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                        label_txt, va="center", ha="left", fontsize=8.5)
        ax_bar.set_xlabel("偏好份額 (%)", fontsize=9)
        ax_bar.set_title("Top 8 SKU 偏好份額\n（★ = URBANER）", fontsize=10, fontweight="bold")
        ax_bar.grid(axis="x", color=GRID_COLOR, linewidth=0.7)
        ax_bar.spines[["top","right","left"]].set_visible(False)

        # ── 子圖3：升級模擬 ─────────────────────────────────────────────────
        ax_sim = fig.add_subplot(gs[row_idx, 2])
        ax_sim.set_facecolor(BG_COLOR)
        if sims:
            sim_names  = [ATTR_ZH.get(s["attr"], s["attr"]) for s in sims]
            sim_deltas = [s["delta"] for s in sims]
            sim_orig   = [s["orig"] for s in sims]
            bar_cols = [URBANER_COLOR if d == max(sim_deltas) else ACCENT_COLOR if d > 0 else COMP_COLOR
                        for d in sim_deltas]
            bars2 = ax_sim.barh(sim_names[::-1], sim_deltas[::-1],
                                color=bar_cols[::-1], edgecolor="white", height=0.6)
            for bar, dlt, orig in zip(bars2, sim_deltas[::-1], sim_orig[::-1]):
                ax_sim.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                            f"+{dlt:.2f}%", va="center", ha="left", fontsize=8.5,
                            color=URBANER_COLOR)
            ax_sim.axvline(0, color="#666", linewidth=1, linestyle="--")
            ax_sim.set_xlabel("市佔增幅 (%pt)", fontsize=9)
        ax_sim.set_title("屬性升至 High（10分）\n後的市佔增益", fontsize=10, fontweight="bold")
        ax_sim.grid(axis="x", color=GRID_COLOR, linewidth=0.7)
        ax_sim.spines[["top","right","left"]].set_visible(False)

    fig.suptitle("路線B：Share-of-Preference 偏好市佔模擬", fontsize=14,
                 fontweight="bold", y=1.01)
    out = CHART_DIR / "chartB_sop.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"  ✅ {out}")


# ══════════════════════════════════════════════════════════════════════════════
# 圖表3：路線C — Hedonic Pricing 係數圖 + 價格 vs 品質分散點
# ══════════════════════════════════════════════════════════════════════════════

def run_hedonic_full(scorecard, attr_cols, urb_p, urb_col, comp_asins, comp_p, comp_col, urbaner_asins):
    df = scorecard.merge(urb_p, on="product", how="left")
    comp_map = comp_p.set_index("product")[comp_col]
    mask = df["product"].isin(comp_asins)
    df.loc[mask, urb_col] = df.loc[mask, "product"].map(comp_map)
    df = df.dropna(subset=[urb_col])
    df = df[df[urb_col] > 0]
    df["log_price"] = np.log(df[urb_col])
    df["is_urbaner"] = df["product"].isin(urbaner_asins)
    valid_cols = {a: c for a, c in attr_cols.items() if c in df.columns}
    df2 = df.dropna(subset=list(valid_cols.values()))
    X = sm.add_constant(df2[[c for c in valid_cols.values()]])
    y = df2["log_price"]
    try:
        model = sm.OLS(y, X).fit()
        results = {a: {"coef": model.params.get(c, np.nan), "pval": model.pvalues.get(c, np.nan)}
                   for a, c in valid_cols.items()}
        r2 = model.rsquared
    except:
        results = {a: {"coef": np.nan, "pval": np.nan} for a in valid_cols}
        r2 = np.nan
    return results, r2, df2

hed_us_res, hed_us_r2, hed_us_df = run_hedonic_full(
    us_q, US_ATTR_COLS, urb_us_p, "price_usd", COMP_US_001, comp_us_p, "price_usd", URBANER_US_001)
hed_jp_res, hed_jp_r2, hed_jp_df = run_hedonic_full(
    jp_q, JP_ATTR_COLS, urb_jp_p, "price_jpy", COMP_JP_001, comp_jp_p, "price_jpy", URBANER_JP_001)


def plot_hedonic(hed_us_res, hed_us_r2, hed_us_df,
                 hed_jp_res, hed_jp_r2, hed_jp_df):
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor(BG_COLOR)

    for row_idx, (res, r2, df2, mkt_label, price_col, sym, urbaner_asins, attr_cols) in enumerate([
        (hed_us_res, hed_us_r2, hed_us_df, "🇺🇸 美國市場", "price_usd", "$", URBANER_US_001, US_ATTR_COLS),
        (hed_jp_res, hed_jp_r2, hed_jp_df, "🇯🇵 日本市場", "price_jpy", "¥", URBANER_JP_001, JP_ATTR_COLS),
    ]):
        # ── 左：係數橫條圖 ──────────────────────────────────────────────────
        ax_coef = axes[row_idx][0]
        ax_coef.set_facecolor(BG_COLOR)
        valid = [(a, v) for a, v in res.items() if not np.isnan(v.get("coef", np.nan))]
        valid_sorted = sorted(valid, key=lambda x: x[1]["coef"], reverse=True)
        names  = [ATTR_ZH.get(a, a) for a, _ in valid_sorted]
        coefs  = [v["coef"] for _, v in valid_sorted]
        pvals  = [v["pval"] for _, v in valid_sorted]
        colors = [URBANER_COLOR if p < 0.05 else ACCENT_COLOR if p < 0.1 else COMP_COLOR
                  for p in pvals]
        bars = ax_coef.barh(names[::-1], coefs[::-1], color=colors[::-1],
                            edgecolor="white", height=0.6)
        for bar, coef, pv in zip(bars, coefs[::-1], pvals[::-1]):
            sign = "***" if pv < 0.001 else "**" if pv < 0.01 else "*" if pv < 0.05 else "†" if pv < 0.1 else ""
            ax_coef.text(bar.get_width() + 0.002,
                         bar.get_y() + bar.get_height()/2,
                         f"{coef:+.3f} {sign}", va="center", ha="left", fontsize=9)
        ax_coef.axvline(0, color="#666", linewidth=1, linestyle="--")
        ax_coef.set_xlabel("β 係數（半對數：%ΔPrice / 品質分）", fontsize=9)
        ax_coef.set_title(f"{mkt_label} Hedonic 係數\nR² = {r2:.3f}", fontsize=11, fontweight="bold")
        ax_coef.grid(axis="x", color=GRID_COLOR, linewidth=0.7)
        ax_coef.spines[["top","right","left"]].set_visible(False)

        # ── 右：售價 vs 綜合品質分散點圖 ───────────────────────────────────
        ax_scatter = axes[row_idx][1]
        ax_scatter.set_facecolor(BG_COLOR)
        qual_cols = [c for c in attr_cols.values() if c in df2.columns]
        df2["avg_quality"] = df2[qual_cols].mean(axis=1)

        urb_mask = df2["is_urbaner"]
        ax_scatter.scatter(
            df2.loc[~urb_mask, "avg_quality"], df2.loc[~urb_mask, price_col],
            color=COMP_COLOR, alpha=0.7, s=60, label="競品", zorder=2
        )
        ax_scatter.scatter(
            df2.loc[urb_mask, "avg_quality"], df2.loc[urb_mask, price_col],
            color=URBANER_COLOR, alpha=0.95, s=100, marker="*",
            label="URBANER", zorder=3
        )

        # 趨勢線
        x_all = df2["avg_quality"].values
        y_all = df2[price_col].values
        if len(x_all) > 2:
            z = np.polyfit(x_all, y_all, 1)
            p_fit = np.poly1d(z)
            x_line = np.linspace(x_all.min(), x_all.max(), 100)
            ax_scatter.plot(x_line, p_fit(x_line), color="#888", linewidth=1.5,
                            linestyle="--", label="趨勢線", zorder=1)

        # 標注 Urbaner ASIN
        for _, row in df2[urb_mask].iterrows():
            ax_scatter.annotate(
                row["product"][-6:],
                (row["avg_quality"], row[price_col]),
                textcoords="offset points", xytext=(5, 4),
                fontsize=7.5, color=URBANER_COLOR
            )

        ax_scatter.set_xlabel("平均屬性品質分（0–10）", fontsize=9)
        ax_scatter.set_ylabel(f"售價（{sym}）", fontsize=9)
        ax_scatter.set_title(f"{mkt_label} 售價 vs 品質分\n（散點圖）", fontsize=11, fontweight="bold")
        ax_scatter.legend(fontsize=8.5, framealpha=0.9)
        ax_scatter.grid(color=GRID_COLOR, linewidth=0.7)
        ax_scatter.spines[["top","right"]].set_visible(False)

    legend_els = [
        mpatches.Patch(color=URBANER_COLOR, label="p < 0.05（顯著）"),
        mpatches.Patch(color=ACCENT_COLOR,  label="p < 0.10（邊際）"),
        mpatches.Patch(color=COMP_COLOR,    label="p ≥ 0.10（不顯著）"),
    ]
    fig.legend(handles=legend_els, loc="lower center", ncol=3,
               fontsize=9, framealpha=0.9, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("路線C：Hedonic Pricing 市場定價回歸", fontsize=14,
                 fontweight="bold", y=1.01)
    plt.tight_layout()
    out = CHART_DIR / "chartC_hedonic.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"  ✅ {out}")


# ══════════════════════════════════════════════════════════════════════════════
# 執行所有圖表
# ══════════════════════════════════════════════════════════════════════════════
print("生成圖表...")
plot_wtp(parts_us, bp_us, parts_jp, bp_jp)
plot_sop(sop_us, sop_jp, sims_us, sims_jp)
plot_hedonic(hed_us_res, hed_us_r2, hed_us_df, hed_jp_res, hed_jp_r2, hed_jp_df)
print("\n所有圖表生成完畢")
print(f"存放路徑：{CHART_DIR}")
