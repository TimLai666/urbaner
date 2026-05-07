import pandas as pd, numpy as np

us_q = pd.read_csv('output_stp/market_stp_us/product_quality_scorecard.csv')
jp_q = pd.read_csv('output_stp/market_stp_jp/product_quality_scorecard.csv')
us_r = pd.read_csv('output_stp/market_stp_us/review_scoring_table.csv')
jp_r = pd.read_csv('output_stp/market_stp_jp/review_scoring_table.csv')
us_avg = us_r.groupby('product')['rating'].mean().rename('avg_star').reset_index()
jp_avg = jp_r.groupby('product')['rating'].mean().rename('avg_star').reset_index()
us = us_q.merge(us_avg, on='product', how='left')
jp = jp_q.merge(jp_avg, on='product', how='left')

US_COLS = {
    'size':         'product_dimensions_size_quality',
    'power_source': 'power_source_type_quality',
    'waterproof':   'waterproof_rating_ipx8_quality',
    'attachments':  'total_attachments_count_quality',
    'guide_comb':   'guide_comb_variety_quality',
    'charging':     'usb_c_charging_quality',
}
JP_COLS = {
    'size':         'product_dimensions_size_quality',
    'attachments':  'total_attachments_count_quality',
    'guide_comb':   'guide_comb_variety_quality',
    'precision':    'adjustable_comb_settings_quality',
    'power_source': 'power_source_type_quality',
    'waterproof':   'waterproof_rating_ipx8_quality',
    'battery_life': 'battery_life_duration_quality',
}

def show_levels(df, cols, market):
    print(f"\n=== {market} 品質分離散化分布 ===")
    for attr, col in cols.items():
        if col not in df.columns:
            continue
        scores = df[col].dropna()
        low  = (scores <= 4).sum()
        mid  = ((scores > 4) & (scores <= 7)).sum()
        high = (scores > 7).sum()
        print(f"  {attr:15s}: Low={low:2d} Mid={mid:2d} High={high:2d}  "
              f"(min={scores.min():.1f} mean={scores.mean():.1f} max={scores.max():.1f})")

us_clean = us.dropna(subset=list(US_COLS.values()))
jp_clean = jp.dropna(subset=list(JP_COLS.values()))
show_levels(us_clean, US_COLS, "US")
show_levels(jp_clean, JP_COLS, "JP")

# 也印出效用值分布
US_BETAS = {
    'size':         (-0.9756,  1.2580),
    'power_source': (10.5291, 13.8123),
    'waterproof':   ( 9.1456, 10.6809),
    'attachments':  (10.5291, 13.8123),
    'guide_comb':   (-1.7095,  1.8786),
    'charging':     (11.5446, 13.8734),
}

def calc_utility(df, cols, betas):
    utils = []
    for _, row in df.iterrows():
        U = 0.0
        for attr, (bm, bh) in betas.items():
            col = cols.get(attr)
            if not col or col not in row.index: continue
            s = row[col]
            if pd.isna(s): continue
            mid  = 1 if (4 < s <= 7) else 0
            high = 1 if s > 7 else 0
            U += (bm or 0)*mid + (bh or 0)*high
        utils.append(U)
    return np.array(utils)

us_utils = calc_utility(us_clean, US_COLS, US_BETAS)
print(f"\nUS SKU 效用值: min={us_utils.min():.1f} mean={us_utils.mean():.1f} max={us_utils.max():.1f}")

# 設計卡片 Card 22 的效用值（US）
# Card 22: ≥38段(high) USB-C(high) ≥10件(high) USB-C快充(high) 標準(mid) 1合1(low) IPX4(mid)
card22_us = (
    US_BETAS['guide_comb'][1] +   # ≥38段 = high
    US_BETAS['power_source'][1] + # USB-C = high
    US_BETAS['attachments'][1] +  # ≥10件 = high
    US_BETAS['charging'][1] +     # USB-C快充 = high
    US_BETAS['size'][0] +         # 標準 = mid
    # 功能合一數排除
    US_BETAS['waterproof'][0]     # IPX4 = mid
)
print(f"Card 22 US 效用值: {card22_us:.1f}")
print(f"US SKU 最高效用值: {us_utils.max():.1f}")
print(f"差距: {us_utils.max() - card22_us:.1f}")
