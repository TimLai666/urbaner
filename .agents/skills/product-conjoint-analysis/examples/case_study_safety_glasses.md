# Case Study: Safety Glasses (Fit Over) on Amazon

A fully worked example showing how the skill is applied end-to-end. Read this when you want to see what a real conjoint study looks like or to verify your work matches the expected pattern.

---

## Background

- **Category**: safety-glasses (fit over) on Amazon
- **Sample**: top-3 brands by sales rank — HTS, UKNOW, MORKSUKY
- **Time**: original study completed Dec 2024
- **Sample size**: 20 customers (review writers) → 8 cards × 20 customers = 160 stacked observations

---

## Phase I: Data acquisition

### Supply-side
Scraped Amazon product pages for each of the 3 brands. Catalogued: brand, color, price, frame size (mm), anti-fog, anti-scratch, UV protection.

### Demand-side
Pulled customer reviews via "賣家精靈" (Sellerly), then ran AI-based theme extraction with Maslow's needs hierarchy as the interpretive frame.

**Top demand themes**: frame-size compatibility, anti-fog, anti-scratch.

---

## Phase II: Attribute engineering

### Universality filter
Anti-fog appeared on ~100% of products → **dropped** (no variance).
Anti-scratch and UV protection at 90%+ → **kept** (cross-brand variation exists).

### Final attributes (6)

| Attribute | Levels | Reference |
|-----------|--------|-----------|
| Brand | HTS, UKNOW, MORKSUKY | HTS |
| Color | Black, Pink, Purple | Black |
| Price | $13.98 / $14.95 / $15.99 | (continuous) |
| Frame size | 140 / 145 / 162 mm | 140 mm |
| Anti-scratch | Yes / No | No |
| UV protection | Yes / No | No |

---

## Phase III: Experimental design

8 product cards based on actual market combinations (not orthogonal):

| Card | Brand | Color | Price | Size | Anti-scratch | UV |
|------|-------|-------|-------|------|--------------|-----|
| 1 | HTS | Black | $15.99 | 140 | Yes | Yes |
| 2 | HTS | Pink | $15.99 | 140 | Yes | Yes |
| 3 | UKNOW | Black | $13.98 | 162 | No | Yes |
| 4 | UKNOW | Pink | $13.98 | 162 | No | Yes |
| 5 | UKNOW | Purple | $13.98 | 162 | No | Yes |
| 6 | MORKSUKY | Black | $14.95 | 145 | Yes | No |
| 7 | MORKSUKY | Pink | $14.95 | 145 | Yes | No |
| 8 | MORKSUKY | Purple | $14.95 | 145 | Yes | No |

Response variable: y = 1 if the customer's purchased product matches this card, else 0.
Consideration set assumption: each customer compared all 8 cards.
Stacked structure: 20 × 8 = 160 observations.

**Note the correlation**: every MORKSUKY card is 145mm + anti-scratch + no UV, every UKNOW is 162mm + no anti-scratch + UV. This collinearity *forces* the use of split models in Phase IV.

---

## Phase IV: Model estimation

### Approach: split sub-models

Five sub-models, one per attribute group:

| Sub-model | Predictors | Why grouped |
|-----------|------------|-------------|
| Brand | UKNOW, MORKSUKY | Same attribute |
| Color | pink, purple | Same attribute |
| Size | size_145, size_162 | Same attribute |
| Features | anti_scratch, uv_protection | Both binary product flags |
| Price | price | Continuous, isolated for sensitivity reference |

### Coefficients (key ones)

| Variable | β | Interpretation |
|----------|--------|----------------|
| MORKSUKY | +0.463 | Strongly preferred over HTS |
| UKNOW | +0.137 | Mildly preferred over HTS |
| pink | +0.153 | Mildly preferred over black |
| purple | +0.074 | Slightly preferred over black |
| size_145 | +0.463 | Strongly preferred over 140mm |
| size_162 | +0.137 | Mildly preferred over 140mm |
| anti_scratch | +0.121 | Mild positive |
| uv_protection | −0.382 | **Negative** — economically counter-intuitive |
| price | +0.052 | **Wrong sign** — price range too narrow |

All p-values > 0.4. Findings reported as **directional only**.

---

## Phase V: Insight translation

### Importance

| Attribute | Importance |
|-----------|-----------|
| Brand | 27.4% |
| Frame size | 27.4% |
| UV protection | 22.6% |
| Color | 9.1% |
| Anti-scratch | 7.2% |
| Price | 6.2% |

Two-thirds of choice variation comes from brand and size combined.

### WTP (flagged as directional only)

- MORKSUKY vs HTS: +$8.90
- 145mm vs 140mm: +$8.90
- Pink vs Black: +$2.94
- Anti-scratch: +$2.33
- **UV protection: −$7.35** (consumers want a discount to accept it)

### Optimal product

Card 7 — MORKSUKY / Pink / $14.95 / 145mm / anti-scratch / no UV
Predicted choice probability: **32.4%** (highest among all cards).

### ROI

| Upgrade | Δ Cost | Δ Utility | ROI |
|---------|--------|-----------|------|
| 145mm size | $0.30 | 0.463 | **1.54** ← invest first |
| Pink color | $0.25 | 0.153 | 0.61 |
| Anti-scratch | $0.60 | 0.121 | 0.20 |
| UV protection | $0.40 | −0.382 | **−0.96** ← drop or make optional |

---

## Strategic recommendations

1. **Lead SKU**: MORKSUKY-style fit-over with 145mm frame, pink option, anti-scratch coating, no UV protection by default, priced ~$14.95.
2. **R&D priority**: Frame size optimization (highest ROI per dollar).
3. **Reposition UV**: Move from standard inclusion to optional add-on, or revise marketing communication to elevate perceived value.

---

## Limitations explicitly stated

1. N=20 is small. All findings are directional.
2. Price range $13.98–$15.99 ($2.01 spread) is too narrow → price coefficient is unreliable, WTP is directional only.
3. Cannot estimate interaction effects (split-model trade-off).
4. Review writers may not be representative of all buyers (self-selection).

---

## What this case study illustrates

**About methodology**:
- How to do conjoint when you can't run a survey.
- When to use split models instead of one full model.
- How to handle a price coefficient that comes out wrong.
- Why universality filtering matters (anti-fog dropped despite high mention count).

**About interpretation**:
- High mention frequency in reviews ≠ inclusion in model.
- Wrong-sign coefficients are usually a data problem, not a customer-behavior insight.
- Negative WTP can be real (consumer rejects a feature) but is more often a sign of confounding.
- Small samples support directional conclusions, not inferential ones — say so.

**About reporting**:
- Lead with the optimal product, not the methodology.
- State limitations clearly enough that the next analyst can improve on them.
- Include the worksheet appendix for reproducibility.
