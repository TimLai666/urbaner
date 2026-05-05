# URBANER STP Analysis — JP Market

- **Reviews analysed**: 7,163 URBANER own-product reviews
- **Products in quality scorecard**: 36
- **Attribute catalog**: 114 attributes, 20 themes, 4 theory families
- **Languages**: ja=6924, en=239
- **Categories covered**: 002_Nose_Ear Hair_Trimmers, 001_Beard_Mustache_Trimmers

## Attribute Extraction Summary

| Field | Value |
|-------|-------|
| Target minimum | 30 |
| Actual count | 114 |
| Shortfall reason | none — pre-frozen catalog of 114 attributes reused across markets |
| Theory gap | none |

**Themes discovered (20)**: `Power Source`, `Motor & Blade`, `Waterproof`, `Functions`, `Adjustability`, `Design`, `Portability`, `Accessories`, `Safety`, `Build Quality`, `Ease of Use`, `Gifting`, `Price & Value`, `Target User`, `Blade Specs`, `Brand & Trust`, `Sensory Experience`, `Hair Capability`, `Social Context`, `Eco & Sustainability`

**Theory family coverage**:
- `product_positioning`: attributes, functions, benefits, usage_context_service_experience
- `maslow`: physiological, safety, belongingness, esteem, self_actualization
- `purchase_motivation`: functional, security, relational
- `wom_motivation`: altruistic, social_identity, self_enhancement, emotional_expression

**Scoring axes**:
- **Axis A (Salience 0–7)**: per review × attribute; bilingual keyword presence + length-density weighting.
- **Axis B (Quality 0–10)**: per product × attribute; star-rating baseline adjusted by attribute-specific negative signals + sentiment delta.

## Segmentation

**What this section does**: Clusters 7,163 reviewers in JP by their salience profile across 114 attributes.
**Axis modelling**: Axis A (salience) only.
**Statistical methods**: StandardScaler → PCA (85% variance retained) → K-Means (k=3–6, silhouette + ≥5% guardrail).
**Theories used**: product_positioning (functions, benefits, attributes); maslow (physiological, safety, esteem); purchase_motivation (functional, security).

**Result**: k = 3, silhouette = 0.57. See `segmentation_map.png`.

### Segment 1 — Power Source Type Focus
- **n** = 6,559 reviews (91.6%)
- **Avg rating** = 3.46★
- **Dominant product** = B07XTLC91J
- **Category mix** = Nose / Ear Trimmers 59%, Beard / Mustache Trimmers 41%
- **Language mix** = ja 97%, en 3%
- **Top 5 attributes** = power_source_type, nose_hair_trimming_function, price_value_ratio, ease_of_use_overall, product_longevity

### Segment 2 — Adjustable Comb Settings Focus
- **n** = 561 reviews (7.8%)
- **Avg rating** = 4.01★
- **Dominant product** = B07CYZH2XC
- **Category mix** = Beard / Mustache Trimmers 75%, Nose / Ear Trimmers 25%
- **Language mix** = ja 97%, en 3%
- **Top 5 attributes** = adjustable_comb_settings, power_source_type, product_dimensions_size, total_attachments_count, attachment_fitment

### Segment 3 — Operation Vibration Feel Focus
- **n** = 43 reviews (0.6%)
- **Avg rating** = 3.05★
- **Dominant product** = B07FFGYWJ6
- **Category mix** = Nose / Ear Trimmers 63%, Beard / Mustache Trimmers 37%
- **Language mix** = ja 98%, en 2%
- **Top 5 attributes** = operation_vibration_feel, low_vibration_design, motor_power_rpm, power_source_type, low_noise_operation

### Finding SEG-01
- **finding_statement**: The largest segment in JP (segment 1, 91.6% share, n=6,559) is dominated by `power_source_type` concerns.
- **business_implication**: URBANER JP listings should lead with messaging that addresses `power_source_type` to capture the modal customer.
- **axes_used**: salience
- **methods_used**: StandardScaler → PCA → K-Means
- **theories_used**: product_positioning, maslow
- **subtheories_used**: functions, benefits, physiological, safety
- **statistical_results**: silhouette=0.57, k=3, n=7163
- **reproducibility**: review_scoring_table.csv → SAL_COLS → StandardScaler → PCA(0.85) → KMeans(k=3..6, silhouette+share guardrail)
  - **evidence_quote** [JP_R000010, 5★, B001K85BN2]: "よく剃れるし問題ありません。
以前は充電式を使っていましたが、電池が劣化すると捨てるしかなくなるのでこういった製品は乾電池式一択です。"
  - **evidence_quote** [JP_R000035, 2★, B001K85BN2]: "Not satisfied about the battery life. When the battery drains the speed gets low gradually. We have to use new batteries always for better functionality. So I stopped using this."

## Targeting

**What this section does**: Identifies which attributes most discriminate segments via one-way ANOVA, and ranks segments by avg rating and share for prioritization.
**Axis modelling**: Axis A (salience) as the dependent variable across segment groups.
**Statistical methods**: One-way ANOVA per attribute; pairwise priority ranking by avg_rating × share.
**Theories used**: purchase_motivation (functional, security, relational); maslow (safety, esteem, self_actualization); product_positioning (functions, benefits).

**Significant attributes (p<0.05)**: 58 / 114. See `targeting_anova.csv`.

**Top 10 most discriminating attributes**:

| Attribute | F | p |
|---|---|---|
| total_attachments_count | 2630.384 | 0 |
| guide_comb_variety | 2412.195 | 0 |
| adjustable_comb_settings | 1826.965 | 0 |
| attachment_fitment | 1723.208 | 0 |
| product_dimensions_size | 1004.693 | 0 |
| power_source_type | 543.117 | 0 |
| rechargeable_design | 497.535 | 0 |
| beard_trimming_function | 494.451 | 0 |
| waterproof_rating_ipx8 | 460.933 | 0 |
| battery_independence | 346.662 | 0 |

- **Priority segments**: Segment 2
- **Secondary segments**: Segment 1
- **Deprioritized**: Segment 3

### Finding TGT-01
- **finding_statement**: `total_attachments_count` is the strongest segment-discriminating attribute in JP (F=2630.384, p=0.0).
- **business_implication**: URBANER JP ad creative and Amazon listing copy should foreground `total_attachments_count` because it is the axis on which this market's segments diverge most clearly.
- **axes_used**: salience
- **methods_used**: ANOVA
- **theories_used**: product_positioning, purchase_motivation
- **subtheories_used**: functions, benefits, functional
- **reproducibility**: segmentation_variables.csv → groupby(segment) → scipy.stats.f_oneway per salience column → sort by F.
  - **evidence_quote** [JP_R000145, 1★, B001K85BN2]: "前のモデルのアタッチメントが壊れた（本体はまだ使える）ので進化を確かめるべく購入。結果はかっこよくなっただけ。性能はむしろ落ちたかも。パワーが落ちたのは他の人も触れているが単3から単4に変化。トリム機構は変わって無いから必要十分でスペックダウンしたわけでは無さそう。新しい方の3㎜は本当に3㎜でそろう。前のは幾分短い刈高。なので長く感じる。また完了までの時間が掛かる様になった。デザインがかっこよくなり機能を落として本質が見えていない。おそらく開発側は変える必要を感じていなかったんじゃないか？　ただヒゲトリマーは怪しいメーカーか中華品がはびこっていて、3㎜以"
  - **evidence_quote** [JP_R000181, 4★, B001K85BN2]: "良い商品だとは思いますがちょっと髭を短く残したいみたいな使い方をしたかった自分にとってはアタッチメントを1番短くセットしても髭に届かず意味のないものになってしまいました。代わりに眉毛を整えるのに使ってます。"

## Positioning

**What this section does**: Maps URBANER products on a quality perceptual space and computes ideal-point distances.
**Axis modelling**: Axis B (quality 0–10) per product × attribute.
**Statistical methods**: Standardised quality matrix → PCA (2 components); ideal-point distance (RMS distance from 10.0 vector).
**Theories used**: product_positioning (attributes, functions, benefits); maslow (esteem, safety, self_actualization); purchase_motivation (functional, security).
**PCA variance explained**: PC1=29.5%, PC2=7.5%. See `perceptual_map.png` and `quality_heatmap.png`.

**Top 10 URBANER products closest to ideal (lowest RMS distance from quality=10)**:

| Rank | Product | Distance | n_reviews | Category |
|---|---|---|---|---|
| 1 | B0GBWZBMS5 | 1.97 | 61 | Nose / Ear Trimmers |
| 2 | B0742G961R | 2.23 | 40 | Beard / Mustache Trimmers |
| 3 | B0F99F11BW | 2.316 | 142 | Nose / Ear Trimmers |
| 4 | B0F5VJD5DQ | 2.537 | 150 | Nose / Ear Trimmers |
| 5 | B0BL2YWH3N | 2.657 | 43 | Beard / Mustache Trimmers |
| 6 | B0FJS3QR1W | 2.817 | 141 | Beard / Mustache Trimmers |
| 7 | B0FJS3TF3V | 2.817 | 141 | Beard / Mustache Trimmers |
| 8 | B016JNKVHI | 2.918 | 215 | Beard / Mustache Trimmers |
| 9 | B0BY1KRJZ1 | 2.953 | 115 | Beard / Mustache Trimmers |
| 10 | B0FHKR48NR | 3.113 | 16 | Nose / Ear Trimmers |

**Bottom 5 furthest from ideal**:

| Product | Distance | n_reviews | Category |
|---|---|---|---|
| B07CYQVK16 | 4.966 | 16 | Beard / Mustache Trimmers |
| B07XTLC91J | 4.739 | 500 | Nose / Ear Trimmers |
| B0DKJVC5B2 | 4.699 | 393 | Nose / Ear Trimmers |
| B08LGGMP5W | 4.658 | 300 | Beard / Mustache Trimmers |
| B001K85BN2 | 4.587 | 394 | Beard / Mustache Trimmers |

### Finding POS-01
- **finding_statement**: Product `B0GBWZBMS5` is the JP portfolio leader on the quality perceptual map (RMS distance to ideal = 1.97).
- **business_implication**: Treat `B0GBWZBMS5` as the JP hero SKU — its attribute strengths should anchor brand-level messaging and any cross-sell bundles.
- **axes_used**: quality
- **methods_used**: PCA + ideal-point RMS distance
- **theories_used**: product_positioning, maslow, purchase_motivation
- **subtheories_used**: attributes, functions, benefits, esteem, security, functional

## Theory and Theme Coverage Summary

| Theory family | Subtheories evidenced | Subtheories not evidenced |
|---|---|---|
| product_positioning | attributes, functions, benefits, usage_context_service_experience | — |
| maslow | physiological, safety, belongingness, esteem, self_actualization | — |
| purchase_motivation | functional, security, relational | — |
| wom_motivation | altruistic, social_identity, self_enhancement, emotional_expression | — |
