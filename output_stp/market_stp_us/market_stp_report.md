# URBANER STP Analysis — US Market

- **Reviews analysed**: 4,360 URBANER own-product reviews
- **Products in quality scorecard**: 52
- **Attribute catalog**: 114 attributes, 20 themes, 4 theory families
- **Languages**: en=4360
- **Categories covered**: 001_Beard_Mustache_Trimmers, 002_Nose_Ear Hair_Trimmers, 003_Body_Groomers

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

**What this section does**: Clusters 4,360 reviewers in US by their salience profile across 114 attributes.
**Axis modelling**: Axis A (salience) only.
**Statistical methods**: StandardScaler → PCA (85% variance retained) → K-Means (k=3–6, silhouette + ≥5% guardrail).
**Theories used**: product_positioning (functions, benefits, attributes); maslow (physiological, safety, esteem); purchase_motivation (functional, security).

**Result**: k = 3, silhouette = 0.358. See `segmentation_map.png`.

### Segment 1 — Gift Suitability Men Focus
- **n** = 850 reviews (19.5%)
- **Avg rating** = 3.68★
- **Dominant product** = B0CGHWFF71
- **Category mix** = Beard / Mustache Trimmers 88%, Nose / Ear Trimmers 7%, Body Groomers 6%
- **Language mix** = en 100%
- **Top 5 attributes** = gift_suitability_men, primary_user_gender, ear_hair_trimming_function, attachment_fitment, total_attachments_count

### Segment 2 — Ear Hair Trimming Function Focus
- **n** = 3,337 reviews (76.5%)
- **Avg rating** = 3.18★
- **Dominant product** = B08P4HHSZT
- **Category mix** = Beard / Mustache Trimmers 95%, Nose / Ear Trimmers 4%, Body Groomers 1%
- **Language mix** = en 100%
- **Top 5 attributes** = ear_hair_trimming_function, product_longevity, beard_trimming_function, gift_suitability_men, rechargeable_design

### Segment 3 — Power Source Type Focus
- **n** = 173 reviews (4.0%)
- **Avg rating** = 4.48★
- **Dominant product** = B0FS5TCR3B
- **Category mix** = Beard / Mustache Trimmers 76%, Body Groomers 18%, Nose / Ear Trimmers 6%
- **Language mix** = en 100%
- **Top 5 attributes** = power_source_type, gift_suitability_men, rechargeable_design, beard_trimming_function, ear_hair_trimming_function

### Finding SEG-01
- **finding_statement**: The largest segment in US (segment 2, 76.5% share, n=3,337) is dominated by `ear_hair_trimming_function` concerns.
- **business_implication**: URBANER US listings should lead with messaging that addresses `ear_hair_trimming_function` to capture the modal customer.
- **axes_used**: salience
- **methods_used**: StandardScaler → PCA → K-Means
- **theories_used**: product_positioning, maslow
- **subtheories_used**: functions, benefits, physiological, safety
- **statistical_results**: silhouette=0.358, k=3, n=4360
- **reproducibility**: review_scoring_table.csv → SAL_COLS → StandardScaler → PCA(0.85) → KMeans(k=3..6, silhouette+share guardrail)
  - **evidence_quote** [US_R000001, 1★, B001K85BN2]: "Good awful. The only positive is that this trimmer can be used in the shower. I don’t have a bushy beard and even so this trimmer resulted in a very uneven cut and I was constantly having to rinse the gears hairs out to make sure it kept working. Spend more and get a better trimm"
  - **evidence_quote** [US_R000011, 5★, B008KEJ1LM]: "other shavers i bought had batteries didn't last so i figured buying a panasonic product was a safe choice as they are a major global battery manufacturer. Still going strong after several years. whenever i go on vacation i can leave the charger home not worrying the shaver will "

## Targeting

**What this section does**: Identifies which attributes most discriminate segments via one-way ANOVA, and ranks segments by avg rating and share for prioritization.
**Axis modelling**: Axis A (salience) as the dependent variable across segment groups.
**Statistical methods**: One-way ANOVA per attribute; pairwise priority ranking by avg_rating × share.
**Theories used**: purchase_motivation (functional, security, relational); maslow (safety, esteem, self_actualization); product_positioning (functions, benefits).

**Significant attributes (p<0.05)**: 99 / 114. See `targeting_anova.csv`.

**Top 10 most discriminating attributes**:

| Attribute | F | p |
|---|---|---|
| gift_suitability_men | 1299.469 | 0 |
| primary_user_gender | 1196.508 | 0 |
| num_grooming_functions | 1193.262 | 0 |
| total_attachments_count | 1014.905 | 0 |
| attachment_fitment | 975.252 | 0 |
| power_source_type | 941.026 | 0 |
| waterproof_rating_ipx8 | 902.847 | 0 |
| guide_comb_variety | 902.265 | 0 |
| multi_use_versatility_score | 778.884 | 0 |
| quick_touch_up_design | 708.689 | 0 |

- **Priority segments**: Segment 3
- **Secondary segments**: Segment 1
- **Deprioritized**: Segment 2

### Finding TGT-01
- **finding_statement**: `gift_suitability_men` is the strongest segment-discriminating attribute in US (F=1299.469, p=0.0).
- **business_implication**: URBANER US ad creative and Amazon listing copy should foreground `gift_suitability_men` because it is the axis on which this market's segments diverge most clearly.
- **axes_used**: salience
- **methods_used**: ANOVA
- **theories_used**: product_positioning, purchase_motivation
- **subtheories_used**: functions, benefits, functional
- **reproducibility**: segmentation_variables.csv → groupby(segment) → scipy.stats.f_oneway per salience column → sort by F.
  - **evidence_quote** [US_R000003, 1★, B001K85BN2]: "This was apparantly an export model. The in structions were in Japanese
This purchase was intended to replace a Panasonic ER2430. The unit that was shipped ER2403P has a different configeration  for the heighth adjustment.  My old unit had settings of 3, 4,5,6,, and so on.  This "
  - **evidence_quote** [US_R000010, 5★, B008KEJ1LM]: "Excelente tengo años usandolo y hasta hora no me a fallado lo volveria a comprar"

## Positioning

**What this section does**: Maps URBANER products on a quality perceptual space and computes ideal-point distances.
**Axis modelling**: Axis B (quality 0–10) per product × attribute.
**Statistical methods**: Standardised quality matrix → PCA (2 components); ideal-point distance (RMS distance from 10.0 vector).
**Theories used**: product_positioning (attributes, functions, benefits); maslow (esteem, safety, self_actualization); purchase_motivation (functional, security).
**PCA variance explained**: PC1=51.1%, PC2=4.5%. See `perceptual_map.png` and `quality_heatmap.png`.

**Top 10 URBANER products closest to ideal (lowest RMS distance from quality=10)**:

| Rank | Product | Distance | n_reviews | Category |
|---|---|---|---|---|
| 1 | B0FL267TCG | 1.601 | 29 | Beard / Mustache Trimmers |
| 2 | B0FX4NX6HM | 1.761 | 8 | Body Groomers |
| 3 | B0CDNQ62ML | 1.766 | 8 | Body Groomers |
| 4 | B0GLJRLS5G | 1.814 | 99 | Beard / Mustache Trimmers |
| 5 | B0FHWWPLCP | 1.867 | 8 | Body Groomers |
| 6 | B0G1Z1QKJ8 | 1.896 | 50 | Beard / Mustache Trimmers |
| 7 | B0FS5TCR3B | 1.912 | 158 | Beard / Mustache Trimmers |
| 8 | B092H8XHDG | 2.026 | 8 | Nose / Ear Trimmers |
| 9 | B0F66FZHY3 | 2.029 | 8 | Nose / Ear Trimmers |
| 10 | B0F2RSTDSJ | 2.065 | 73 | Beard / Mustache Trimmers |

**Bottom 5 furthest from ideal**:

| Product | Distance | n_reviews | Category |
|---|---|---|---|
| B07FFGYWJ6 | 6.187 | 6 | Nose / Ear Trimmers |
| B001K85BN2 | 6.106 | 4 | Beard / Mustache Trimmers |
| B09XVP6YPM | 4.845 | 341 | Beard / Mustache Trimmers |
| B0F5VJD5DQ | 4.802 | 77 | Nose / Ear Trimmers |
| B08P4HHSZT | 4.783 | 500 | Beard / Mustache Trimmers |

### Finding POS-01
- **finding_statement**: Product `B0FL267TCG` is the US portfolio leader on the quality perceptual map (RMS distance to ideal = 1.601).
- **business_implication**: Treat `B0FL267TCG` as the US hero SKU — its attribute strengths should anchor brand-level messaging and any cross-sell bundles.
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
