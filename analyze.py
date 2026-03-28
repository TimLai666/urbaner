"""
Urbaner 資料全覽分析腳本
資料來源：rawdata_Urbaner/
  - amazon_reviews/    : 競品評論 (xlsx, 按類別/ASIN)
  - competitor_sales/  : 競品月銷售額 (xlsx, 按類別/ASIN)
  - amazon_sales/      : Urbaner 自身訂單 (txt TSV, US & JP)
"""
import os, sys, warnings
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker

warnings.filterwarnings("ignore")
plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BASE = "rawdata_Urbaner"
CATEGORIES = {
    "001": "Beard/Mustache Trimmers",
    "002": "Nose/Ear Trimmers",
    "003": "Body Groomers",
    "004": "Eyebrow Trimmers",
    "005": "Foil Shavers",
    "006": "Pet Clippers",
    "007": "Pet Nail Clipper",
    "008": "Dog Nail Grinder",
    "009": "Baby Hair Clippers",
}
CAT_SHORT = {
    "001": "Beard",
    "002": "Nose/Ear",
    "003": "Body",
    "004": "Eyebrow",
    "005": "Foil",
    "006": "Pet Clip",
    "007": "Pet Nail",
    "008": "Dog Grind",
    "009": "Baby",
}
COLORS = ["#4C72B0","#DD8452","#55A868","#C44E52","#8172B2",
          "#937860","#DA8BC3","#8C8C8C","#CCB974","#64B5CD"]

# ─────────────────────────────────────────
# 1. 讀取 amazon_reviews
# ─────────────────────────────────────────
print("讀取 amazon_reviews ...")
review_rows = []
review_counts = {}  # cat_key -> count
for cat_key in CATEGORIES:
    cat_folder = next((d for d in os.listdir(f"{BASE}/amazon_reviews")
                       if d.startswith(cat_key)), None)
    if not cat_folder:
        review_counts[cat_key] = 0
        continue
    cat_path = f"{BASE}/amazon_reviews/{cat_folder}"
    files = [f for f in os.listdir(cat_path) if f.endswith(".xlsx")]
    review_counts[cat_key] = 0
    for f in files:
        try:
            df = pd.read_excel(f"{cat_path}/{f}")
            df["category"] = cat_key
            df["asin_file"] = f.replace(".xlsx", "")
            review_rows.append(df)
            review_counts[cat_key] += len(df)
        except Exception as e:
            print(f"  skip {f}: {e}")

reviews_df = pd.concat(review_rows, ignore_index=True) if review_rows else pd.DataFrame()
print(f"  總評論數: {len(reviews_df)}")

# ─────────────────────────────────────────
# 2. 讀取 competitor_sales
# ─────────────────────────────────────────
print("讀取 competitor_sales ...")
comp_rows = []
for cat_key in CATEGORIES:
    cat_folder = next((d for d in os.listdir(f"{BASE}/competitor_sales")
                       if d.startswith(cat_key)), None)
    if not cat_folder:
        continue
    cat_path = f"{BASE}/competitor_sales/{cat_folder}"
    if not os.path.isdir(cat_path):
        continue
    files = [f for f in os.listdir(cat_path) if f.endswith(".xlsx")]
    for f in files:
        try:
            df = pd.read_excel(f"{cat_path}/{f}")
            df["category"] = cat_key
            comp_rows.append(df)
        except Exception as e:
            print(f"  skip {f}: {e}")

comp_df = pd.concat(comp_rows, ignore_index=True) if comp_rows else pd.DataFrame()
print(f"  競品銷售記錄: {len(comp_df)}")

# ─────────────────────────────────────────
# 3. 讀取 amazon_sales (Urbaner 自身)
# ─────────────────────────────────────────
print("讀取 amazon_sales ...")

def read_sales_files(folder, encoding="utf-8"):
    rows = []
    if not os.path.isdir(folder):
        return pd.DataFrame()
    for root, _, files in os.walk(folder):
        for f in files:
            if not f.endswith(".txt"):
                continue
            path = os.path.join(root, f)
            try:
                df = pd.read_csv(path, sep="\t", encoding=encoding,
                                 on_bad_lines="skip")
                rows.append(df)
            except Exception as e:
                print(f"  skip {f}: {e}")
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

us_df = read_sales_files(f"{BASE}/amazon_sales/US_sales", "utf-8")
jp_df = read_sales_files(f"{BASE}/amazon_sales/JP_sales", "shift-jis")
print(f"  US 訂單: {len(us_df)}, JP 訂單: {len(jp_df)}")

# 處理日期 & 篩選已出貨
def prep_orders(df, market):
    if df.empty:
        return df
    df = df.copy()
    df["market"] = market
    df["purchase-date"] = pd.to_datetime(df["purchase-date"], errors="coerce", utc=True)
    df["year_month"] = df["purchase-date"].dt.to_period("M")
    df["quantity"] = pd.to_numeric(df.get("quantity", 0), errors="coerce").fillna(0)
    df["item-price"] = pd.to_numeric(df.get("item-price", 0), errors="coerce").fillna(0)
    df["revenue"] = df["quantity"] * df["item-price"]
    return df

us_df = prep_orders(us_df, "US")
jp_df = prep_orders(jp_df, "JP")
all_orders = pd.concat([us_df, jp_df], ignore_index=True)
shipped = all_orders[all_orders.get("order-status", pd.Series(dtype=str)) == "Shipped"].copy()
print(f"  已出貨訂單: {len(shipped)}")

# ─────────────────────────────────────────
# 4. 視覺化
# ─────────────────────────────────────────
print("繪製圖表 ...")
fig = plt.figure(figsize=(22, 28))
fig.patch.set_facecolor("#F8F9FA")
gs = GridSpec(4, 3, figure=fig, hspace=0.55, wspace=0.38,
              top=0.93, bottom=0.05, left=0.07, right=0.97)

# ── 標題 ──────────────────────────────────
fig.text(0.5, 0.965, "Urbaner Amazon 資料全覽",
         ha="center", va="top", fontsize=22, fontweight="bold", color="#1A1A2E")
fig.text(0.5, 0.948, "資料來源：amazon_reviews / competitor_sales / amazon_sales (US & JP)",
         ha="center", va="top", fontsize=11, color="#555")

# ── A. 各類別評論數量 ─────────────────────
ax_a = fig.add_subplot(gs[0, 0])
cats_list = list(CATEGORIES.keys())
rev_counts = [review_counts.get(k, 0) for k in cats_list]
bars = ax_a.barh([CAT_SHORT[k] for k in cats_list], rev_counts,
                 color=[COLORS[i] for i in range(len(cats_list))], edgecolor="white", linewidth=0.5)
ax_a.set_title("各類別 評論數量", fontsize=12, fontweight="bold", pad=8)
ax_a.set_xlabel("評論筆數")
ax_a.bar_label(bars, fmt="%d", padding=3, fontsize=9)
ax_a.set_xlim(0, max(rev_counts) * 1.25 if max(rev_counts) > 0 else 1)
ax_a.invert_yaxis()
ax_a.set_facecolor("#FAFAFA")

# ── B. 評論星級分佈 ───────────────────────
ax_b = fig.add_subplot(gs[0, 1])
if not reviews_df.empty and "星级" in reviews_df.columns:
    star_col = "星级"
    star_dist = reviews_df[star_col].value_counts().sort_index()
    star_colors = ["#d32f2f","#ef6c00","#f9a825","#558b2f","#1565c0"]
    bars_b = ax_b.bar(star_dist.index.astype(str), star_dist.values,
                      color=star_colors[:len(star_dist)], edgecolor="white")
    ax_b.set_title("評論 星級分佈", fontsize=12, fontweight="bold", pad=8)
    ax_b.set_xlabel("星級")
    ax_b.set_ylabel("評論數")
    ax_b.bar_label(bars_b, fmt="%d", padding=3, fontsize=9)
    avg = reviews_df[star_col].mean()
    ax_b.axhline(0, color="gray", linewidth=0.5)
    ax_b.text(0.98, 0.95, f"平均 {avg:.2f} ★",
              transform=ax_b.transAxes, ha="right", va="top",
              fontsize=10, color="#1565c0", fontweight="bold")
ax_b.set_facecolor("#FAFAFA")

# ── C. 各類別評論平均星級 ─────────────────
ax_c = fig.add_subplot(gs[0, 2])
if not reviews_df.empty and "星级" in reviews_df.columns:
    avg_stars = reviews_df.groupby("category")["星级"].mean()
    cat_labels = [CAT_SHORT[k] for k in avg_stars.index]
    bars_c = ax_c.barh(cat_labels, avg_stars.values,
                       color=[COLORS[cats_list.index(k)] for k in avg_stars.index],
                       edgecolor="white")
    ax_c.set_title("各類別 平均星級", fontsize=12, fontweight="bold", pad=8)
    ax_c.set_xlabel("平均星級")
    ax_c.set_xlim(1, 6)
    ax_c.axvline(4.0, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax_c.bar_label(bars_c, fmt="%.2f", padding=3, fontsize=9)
    ax_c.invert_yaxis()
ax_c.set_facecolor("#FAFAFA")

# ── D. 競品月銷量 Top 產品 ────────────────
ax_d = fig.add_subplot(gs[1, :2])
if not comp_df.empty:
    col_vol = "月销量"
    col_asin = "ASIN"
    col_prod = "商品"
    if col_vol in comp_df.columns:
        # 以最新一個月為準
        latest_month = comp_df["最近几月"].max()
        latest = comp_df[comp_df["最近几月"] == latest_month].copy()
        top15 = latest.nlargest(15, col_vol)
        # 截短產品名稱
        top15["short_name"] = top15[col_prod].str[:25] + "…"
        bars_d = ax_d.barh(top15["short_name"], top15[col_vol],
                           color=COLORS[0], edgecolor="white", alpha=0.85)
        ax_d.set_title(f"競品 月銷量 Top 15（{latest_month}）", fontsize=12, fontweight="bold", pad=8)
        ax_d.set_xlabel("月銷量（件）")
        ax_d.bar_label(bars_d, fmt="%d", padding=3, fontsize=8)
        ax_d.invert_yaxis()
ax_d.set_facecolor("#FAFAFA")

# ── E. 競品月銷額趨勢 ─────────────────────
ax_e = fig.add_subplot(gs[1, 2])
if not comp_df.empty and "月销售额(￥)" in comp_df.columns and "最近几月" in comp_df.columns:
    monthly_rev = comp_df.groupby("最近几月")["月销售额(￥)"].sum().sort_index()
    ax_e.plot(monthly_rev.index, monthly_rev.values / 1e6,
              marker="o", color=COLORS[1], linewidth=2, markersize=5)
    ax_e.fill_between(monthly_rev.index, monthly_rev.values / 1e6, alpha=0.15, color=COLORS[1])
    ax_e.set_title("競品市場 月總銷售額趨勢", fontsize=12, fontweight="bold", pad=8)
    ax_e.set_ylabel("銷售額（百萬 ¥）")
    ax_e.tick_params(axis="x", rotation=45, labelsize=7)
    ax_e.yaxis.set_major_formatter(mticker.FormatStrFormatter("¥%.1fM"))
ax_e.set_facecolor("#FAFAFA")

# ── F. Urbaner US 月銷量趨勢 ─────────────
ax_f = fig.add_subplot(gs[2, :2])
if not shipped.empty:
    us_shipped = shipped[shipped["market"] == "US"].copy()
    jp_shipped = shipped[shipped["market"] == "JP"].copy()

    if not us_shipped.empty:
        us_monthly = us_shipped.groupby("year_month")["quantity"].sum().sort_index()
        ax_f.plot([str(p) for p in us_monthly.index], us_monthly.values,
                  marker="o", color=COLORS[0], linewidth=2, markersize=4, label="US")
    if not jp_shipped.empty:
        jp_monthly = jp_shipped.groupby("year_month")["quantity"].sum().sort_index()
        ax_f.plot([str(p) for p in jp_monthly.index], jp_monthly.values,
                  marker="s", color=COLORS[2], linewidth=2, markersize=4, label="JP")

    ax_f.set_title("Urbaner 月出貨量趨勢（US vs JP）", fontsize=12, fontweight="bold", pad=8)
    ax_f.set_ylabel("出貨件數")
    ax_f.tick_params(axis="x", rotation=45, labelsize=7)
    ax_f.legend()
ax_f.set_facecolor("#FAFAFA")

# ── G. Urbaner SKU 出貨量排行 ────────────
ax_g = fig.add_subplot(gs[2, 2])
if not shipped.empty and "sku" in shipped.columns:
    sku_vol = shipped.groupby("sku")["quantity"].sum().nlargest(10)
    bars_g = ax_g.barh(sku_vol.index, sku_vol.values,
                       color=COLORS[:len(sku_vol)], edgecolor="white")
    ax_g.set_title("Urbaner SKU 出貨量 Top 10", fontsize=12, fontweight="bold", pad=8)
    ax_g.set_xlabel("累計出貨件數")
    ax_g.bar_label(bars_g, fmt="%d", padding=3, fontsize=8)
    ax_g.invert_yaxis()
ax_g.set_facecolor("#FAFAFA")

# ── H. 評論時間趨勢（月） ────────────────
ax_h = fig.add_subplot(gs[3, :2])
if not reviews_df.empty and "评论时间" in reviews_df.columns:
    reviews_df["review_date"] = pd.to_datetime(reviews_df["评论时间"], errors="coerce")
    reviews_df["review_ym"] = reviews_df["review_date"].dt.to_period("M")
    rev_trend = reviews_df.groupby(["review_ym","category"]).size().unstack(fill_value=0).sort_index()
    # 只畫有資料的類別
    for i, cat in enumerate(rev_trend.columns):
        if rev_trend[cat].sum() > 0:
            ax_h.plot([str(p) for p in rev_trend.index], rev_trend[cat].values,
                      marker=".", linewidth=1.5, label=CAT_SHORT.get(cat, cat),
                      color=COLORS[cats_list.index(cat) % len(COLORS)])
    ax_h.set_title("競品評論 月新增趨勢（按類別）", fontsize=12, fontweight="bold", pad=8)
    ax_h.set_ylabel("新增評論數")
    ax_h.tick_params(axis="x", rotation=45, labelsize=7)
    ax_h.legend(fontsize=8)
ax_h.set_facecolor("#FAFAFA")

# ── I. 資料摘要 KPI 框 ───────────────────
ax_i = fig.add_subplot(gs[3, 2])
ax_i.axis("off")
ax_i.set_facecolor("#FAFAFA")

total_reviews = len(reviews_df)
total_comp_products = comp_df["ASIN"].nunique() if not comp_df.empty else 0
total_comp_rev = comp_df["月销售额(￥)"].sum() if not comp_df.empty and "月销售额(￥)" in comp_df.columns else 0
us_units = shipped[shipped["market"]=="US"]["quantity"].sum() if not shipped.empty else 0
jp_units = shipped[shipped["market"]=="JP"]["quantity"].sum() if not shipped.empty else 0
avg_star = reviews_df["星级"].mean() if not reviews_df.empty and "星级" in reviews_df.columns else 0

kpis = [
    ("競品評論總數", f"{total_reviews:,}"),
    ("競品產品數 (ASIN)", f"{total_comp_products:,}"),
    ("競品市場累計銷售額", f"¥{total_comp_rev/1e6:.1f}M"),
    ("Urbaner US 出貨量", f"{int(us_units):,} 件"),
    ("Urbaner JP 出貨量", f"{int(jp_units):,} 件"),
    ("競品平均評分", f"{avg_star:.2f} ★"),
]

ax_i.set_title("資料摘要", fontsize=12, fontweight="bold", pad=8)
for idx, (label, val) in enumerate(kpis):
    y = 0.88 - idx * 0.145
    ax_i.text(0.05, y, label, transform=ax_i.transAxes,
              fontsize=9, color="#555")
    ax_i.text(0.95, y, val, transform=ax_i.transAxes,
              fontsize=12, color="#1A1A2E", fontweight="bold", ha="right")
    ax_i.plot([0.05, 0.95], [y - 0.04, y - 0.04],
              transform=ax_i.transAxes, color="#DDD", linewidth=0.6)

plt.savefig("urbaner_overview.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
sys.stdout.buffer.write("Done: urbaner_overview.png\n".encode("utf-8"))
