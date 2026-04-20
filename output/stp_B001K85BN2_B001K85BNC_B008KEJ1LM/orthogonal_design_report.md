# Orthogonal Design Report — L18 Beard Trimmer Product Optimization
**Basis**: STP Analysis of B001K85BN2 / B001K85BNC / B008KEJ1LM
**Array**: L18 (1×2-level + 7×3-level factors) — 18 test combinations
**Utility values**: derived from Axis B quality scores (STP positioning scorecard)
**Importance weights**: derived from Axis B cross-product variance + ANOVA F-statistics

## Factor & Level Definitions

| Factor | Name | Weight | Level 1 | Level 2 | Level 3 |
|--------|------|--------|---------|---------|---------|
| A | Motor Origin (馬達產地) | 10% | A1 Generic Motor (u=5.5) | A2 Japanese Motor (u=7.0) | — |
| B | Charging Type (充電方式) | 18% | B1 AA/AAA Battery (u=4.5) | B2 USB Dock Rechargeable (u=6.6) | B3 USB-C Rechargeable (u=9.9) |
| C | Waterproof Level (防水等級) | 22% | C1 No Waterproofing (u=1.2) | C2 IPX4 Splash Resist (u=5.0) | C3 IPX8 Submersible (u=8.4) |
| D | Min Cut Length (最短裁剪長度) | 12% | D1 3mm Minimum (u=5.1) | D2 1mm Minimum (u=6.3) | D3 0.5mm Minimum (u=7.4) |
| E | Build Quality Tier (質感定位) | 15% | E1 Economy (ABS body) (u=5.1) | E2 Mid (Reinforced) (u=6.7) | E3 Premium (Metal+Steel) (u=8.0) |
| F | Gift Packaging (禮品包裝) | 8% | F1 Basic Retail Box (u=2.5) | F2 Gift-Ready Box (u=4.8) | F3 Premium Gift Set (u=7.5) |
| G | Length Adjustment (長度調節方式) | 8% | G1 Fixed / 1–2 Pos (u=4.5) | G2 3–5 Step Comb (u=6.2) | G3 Stepless Dial (u=7.1) |
| H | Grooming Functions (修容功能數) | 7% | H1 1 Function (Beard) (u=5.0) | H2 2–3 Functions (u=6.4) | H3 4+ Functions (u=7.5) |

## L18 Orthogonal Array — All 18 Combinations

| Run | A | B | C | D | E | F | G | H | Utility | Est.Price | Rank | Target Segment |
|-----|---|---|---|---|---|---|---|---|---------|-----------|------|----------------|
| R09 | A1 | B3 | C3 | D1 | E3 | F2 | G1 | H2 | 7.184 | $33.0 | #1 | Niche |
| R18 | A2 | B3 | C3 | D2 | E1 | F2 | G3 | H1 | 7.153 | $33.5 | #2 | Convenience, Performance |
| R03 | A1 | B1 | C3 | D3 | E3 | F3 | G3 | H3 | 6.989 | $39.5 | #3 | Premium-Gift |
| R15 | A2 | B2 | C3 | D1 | E2 | F3 | G2 | H1 | 6.799 | $34.5 | #4 | Convenience, Premium-Gift |
| R17 | A2 | B3 | C2 | D1 | E3 | F1 | G2 | H3 | 6.615 | $36.0 | #5 | Convenience |
| R08 | A1 | B3 | C2 | D3 | E2 | F1 | G3 | H1 | 6.443 | $31.0 | #6 | Convenience |
| R06 | A1 | B2 | C3 | D3 | E1 | F1 | G2 | H2 | 6.383 | $29.5 | #7 | Convenience |
| R12 | A2 | B1 | C3 | D2 | E2 | F1 | G1 | H3 | 6.204 | $30.5 | #8 | Performance |
| R05 | A1 | B2 | C2 | D2 | E3 | F3 | G1 | H1 | 6.104 | $31.0 | #9 | Premium-Gift |
| R16 | A2 | B3 | C1 | D3 | E2 | F3 | G1 | H2 | 6.047 | $33.0 | #10 | Premium-Gift |
| R14 | A2 | B2 | C2 | D3 | E1 | F2 | G1 | H3 | 5.910 | $30.5 | #11 | Niche |
| R07 | A1 | B3 | C1 | D2 | E1 | F3 | G2 | H3 | 5.738 | $28.0 | #12 | Niche |
| R11 | A2 | B1 | C2 | D1 | E1 | F3 | G3 | H2 | 5.603 | $27.5 | #13 | Niche |
| R02 | A1 | B1 | C2 | D2 | E2 | F2 | G2 | H2 | 5.549 | $26.5 | #14 | Niche |
| R13 | A2 | B2 | C1 | D2 | E3 | F1 | G3 | H2 | 5.324 | $33.0 | #15 | Niche |
| R04 | A1 | B2 | C1 | D1 | E2 | F2 | G3 | H3 | 5.096 | $27.0 | #16 | Niche |
| R10 | A2 | B1 | C1 | D3 | E3 | F2 | G2 | H1 | 5.092 | $28.0 | #17 | Niche |
| R01 | A1 | B1 | C1 | D1 | E1 | F1 | G1 | H1 | 3.911 | $9.5 | #18 | Value |

## Main Effects Analysis

| Factor | Effect Range | Best Level | Interpretation |
|--------|-------------|-----------|----------------|
| C: Waterproof Level (防水等級) | 1.5840 | C3 IPX8 Submersible | IPX8 (C3) is by far the highest-utility waterproof level (std=3.85 in STP). |
| B: Charging Type (充電方式) | 0.9720 | B3 USB-C Rechargeable | USB-C (B3) dramatically outperforms battery — rechargeable is non-negotiable. |
| E: Build Quality Tier (質感定位) | 0.4350 | E3 Premium (Metal+Steel) | Premium build (E3) clearly preferred; quality perception is a key purchase driver. |
| F: Gift Packaging (禮品包裝) | 0.4000 | F3 Premium Gift Set | Premium gift set (F3) captures US gift-market segment at minimal utility loss. |
| D: Min Cut Length (最短裁剪長度) | 0.2760 | D3 0.5mm Minimum | 0.5mm minimum (D3) addresses Panasonic ER-GB42's top complaint. |
| G: Length Adjustment (長度調節方式) | 0.2080 | G3 Stepless Dial | Stepless dial (G3) preferred but gap vs 3-5 step is smaller — cost/benefit trade-off. |
| H: Grooming Functions (修容功能數) | 0.1750 | H3 4+ Functions | 4+ functions (H3) preferred; broader function set expands addressable market. |
| A: Motor Origin (馬達產地) | 0.1500 | A2 Japanese Motor | Japanese motor adds trust signal; switch from generic to JP motor is a must. |

## Optimal Combination

**Estimated weighted utility**: 8.111 / 10.0
**Estimated price (BOM basis)**: $48.5 USD

| Factor | Optimal Level | Specification |
|--------|--------------|---------------|
| A: Motor Origin (馬達產地) | A2 | Japanese Motor (utility=7.0, BOM +$3.5) |
| B: Charging Type (充電方式) | B3 | USB-C Rechargeable (utility=9.9, BOM +$3.5) |
| C: Waterproof Level (防水等級) | C3 | IPX8 Submersible (utility=8.4, BOM +$4) |
| D: Min Cut Length (最短裁剪長度) | D3 | 0.5mm Minimum (utility=7.4, BOM +$3) |
| E: Build Quality Tier (質感定位) | E3 | Premium (Metal+Steel) (utility=8.0, BOM +$5) |
| F: Gift Packaging (禮品包裝) | F3 | Premium Gift Set (utility=7.5, BOM +$4) |
| G: Length Adjustment (長度調節方式) | G3 | Stepless Dial (utility=7.1, BOM +$2.5) |
| H: Grooming Functions (修容功能數) | H3 | 4+ Functions (utility=7.5, BOM +$3) |

## Top 5 L18 Designs vs Benchmark Products

| # | Design | Utility | Est.Price | Target Segment | vs Benchmarks |
|---|--------|---------|-----------|----------------|---------------|
| 1 | Run 9: A1+B3+C3+D1+E3+F2+G1+H2 | 7.184 | $33.0 | Niche | Outperforms all 3 benchmarks |
| 2 | Run 18: A2+B3+C3+D2+E1+F2+G3+H1 | 7.153 | $33.5 | Convenience, Performance | Outperforms all 3 benchmarks |
| 3 | Run 3: A1+B1+C3+D3+E3+F3+G3+H3 | 6.989 | $39.5 | Premium-Gift | Outperforms all 3 benchmarks |
| 4 | Run 15: A2+B2+C3+D1+E2+F3+G2+H1 | 6.799 | $34.5 | Convenience, Premium-Gift | Outperforms all 3 benchmarks |
| 5 | Run 17: A2+B3+C2+D1+E3+F1+G2+H3 | 6.615 | $36.0 | Convenience | Outperforms all 3 benchmarks |

**Benchmark utilities for comparison**:
- Panasonic ER-GB42 (B001K85BN2): utility=4.535, est_price=$22.0
- Panasonic ER-GB62 (B001K85BNC): utility=6.642, est_price=$36.0
- Conair GMT175CS (B008KEJ1LM): utility=5.543, est_price=$24.0
- Urbaner (Target): utility=8.111, est_price=$48.5

## Strategic Design Recommendations

Based on the L18 orthogonal design and STP analysis:

1. **Factor C (Waterproof) is the #1 lever** — Effect range is highest. IPX8 vs None = +4.3 raw utility units. Every Urbaner US SKU should carry IPX8.

2. **Factor B (Charging) is #2** — USB-C rechargeable (B3) utility=9.9 vs battery=4.5. Gap is enormous. Eliminate AA/AAA battery products from US lineup.

3. **Premium Build (E3) + Japanese Motor (A2) together** give the clearest premium signal for mid-tier pricing ($30–45 USD retail).

4. **Min Cut Length 0.5mm (D3)** directly attacks Panasonic ER-GB42's top-reviewed weakness. High copy value for Amazon A+ content comparison tables.

5. **Gift Packaging (F3)** is worth including for the US launch SKU — utility gain justifies $4 BOM add given 13.6% of reviewers are in the 'longevity + gifting' segment.

6. **Recommended hero SKU**: A2+B3+C3+D3+E3+F3+G3+H3 ("Urbaner Target" combo)
   - Estimated weighted utility: 8.111 (vs ER-GB62 benchmark: 6.642)
   - Estimated BOM: $48.5 USD → suggest retail $39–49

## Visualizations
- [OD_main_effects.png](OD_main_effects.png) — Main effects plot for all 8 factors
- [OD_utility_price_space.png](OD_utility_price_space.png) — Utility × Price scatter for all 18 runs
- [OD_radar_comparison.png](OD_radar_comparison.png) — Radar: Top 3 L18 designs vs benchmarks
- [OD_factor_importance.png](OD_factor_importance.png) — Factor importance by effect range