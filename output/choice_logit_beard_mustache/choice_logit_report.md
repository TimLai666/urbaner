# Choice Logit Report

- Reviews used: 7,118
- Products in choice set: 40
- Alternatives per choice set: 40
- Long-format rows: 284,720
- Model features: 16
- Reviews used for fit: 2,500

## Step 1. Choice Data
Each review is treated as one purchase occasion. The reviewed ASIN becomes the chosen alternative; all other products in the category are coded as 0.

## Step 2. Dummy Encoding
Product-level attribute scores are aggregated from review text, then bucketed into low / mid / high tiers and one-hot encoded. Low tier is the reference category.

### Attributes used
- rechargeable_design: 充電式設計
- blade_sharpness: 刀片鋒利度
- blade_hair_pulling: 刀片拉毛問題
- motor_power_rpm: 馬達功率轉速
- waterproof_rating_ipx8: IPX8防水等級
- adjustable_comb_settings: 可調式導梳長度設定
- ease_of_use_overall: 整體易用性
- price_value_ratio: 性價比

## Step 3. Logit Fit
- Log-likelihood: -8589.749
- Null log-likelihood: -26257.444
- McFadden pseudo R^2: 0.6729
- Top-1 hit rate: 0.0701

## Coefficients
| term | coefficient | std_err | z_value | p_value | odds_ratio | direction |
|---|---:|---:|---:|---:|---:|---|
| ease_of_use_overall_tier_high | 2.0320 | 0.1709 | 11.890 | 0.0000 | 7.630 | positive |
| price_value_ratio_tier_high | 1.2132 | 0.1508 | 8.043 | 0.0000 | 3.364 | positive |
| waterproof_rating_ipx8_tier_mid | 0.8938 | 0.0775 | 11.529 | 0.0000 | 2.444 | positive |
| blade_sharpness_tier_high | 0.8915 | 0.2069 | 4.309 | 0.0000 | 2.439 | positive |
| rechargeable_design_tier_mid | 0.6162 | 0.0888 | 6.942 | 0.0000 | 1.852 | positive |
| motor_power_rpm_tier_high | 0.5415 | 0.1705 | 3.175 | 0.0015 | 1.719 | positive |
| ease_of_use_overall_tier_mid | 0.5148 | 0.0871 | 5.911 | 0.0000 | 1.673 | positive |
| price_value_ratio_tier_mid | 0.3679 | 0.0887 | 4.146 | 0.0000 | 1.445 | positive |
| waterproof_rating_ipx8_tier_high | 0.3365 | 0.2863 | 1.176 | 0.2397 | 1.400 | positive |
| blade_hair_pulling_tier_mid | 0.2961 | 0.1510 | 1.962 | 0.0498 | 1.345 | positive |
| rechargeable_design_tier_high | 0.2828 | 0.1748 | 1.618 | 0.1058 | 1.327 | positive |
| motor_power_rpm_tier_mid | 0.1881 | 0.1167 | 1.612 | 0.1070 | 1.207 | positive |
| blade_sharpness_tier_mid | 0.1134 | 0.0830 | 1.366 | 0.1721 | 1.120 | positive |
| adjustable_comb_settings_tier_mid | -0.9470 | 0.1264 | -7.493 | 0.0000 | 0.388 | negative |
| blade_hair_pulling_tier_high | -1.4617 | 0.1865 | -7.837 | 0.0000 | 0.232 | negative |
| adjustable_comb_settings_tier_high | -3.4765 | 0.2281 | -15.242 | 0.0000 | 0.031 | negative |

## Interpretation
Positive coefficients increase utility and purchase probability relative to the omitted (low) tier. Negative coefficients reduce utility.
The coefficient itself is the part-worth utility on the log-odds scale; exponentiating it gives the odds ratio.