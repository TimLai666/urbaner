# Insight Translation Reference

How to convert raw part-worth utilities into business-grade insights. The four canonical transforms — importance, WTP, choice probability, ROI — answer four distinct questions. Always produce all four for a complete conjoint report.

## Table of contents
- [1. Attribute importance](#1-attribute-importance)
- [2. Willingness to pay (WTP)](#2-willingness-to-pay-wtp)
- [3. Choice probability](#3-choice-probability)
- [4. Cost-benefit ROI](#4-cost-benefit-roi)
- [Reliability flags](#reliability-flags)

---

## 1. Attribute importance

**Question answered**: "Which attribute drives the most variation in consumer choice?"

### Formula

```
For each attribute i:
    range_i = max(part-worths in attribute i) − min(part-worths in attribute i)

For PRICE specifically:
    range_price = |β_price| × (max_price − min_price)

importance_i = range_i / Σ(all ranges) × 100%
```

### Why price needs rescaling

Categorical part-worths are already on a "relative-to-reference" scale — the range directly reflects influence on choice.

Price's coefficient β is a **marginal-per-unit** effect (e.g., per dollar). Treating it identically would understate price by a factor equal to the price spread. Multiplying by the actual price range puts it back on a comparable scale.

**Concrete example from case study**:
- β_price = 0.052
- Price range = $15.99 − $13.98 = $2.01
- Effective range = 0.052 × 2.01 = 0.105

Without rescaling, "price range" would have been treated as 0.052 — making price look ~20× less important than reality.

### Worked example

| Attribute | Max β | Min β | Range | Importance |
|---|---|---|---|---|
| Brand | 0.463 | 0 | 0.463 | 27.4% |
| Size | 0.463 | 0 | 0.463 | 27.4% |
| UV protection | 0 | −0.382 | 0.382 | 22.6% |
| Color | 0.153 | 0 | 0.153 | 9.1% |
| Anti-scratch | 0.121 | 0 | 0.121 | 7.2% |
| Price | (rescaled) | | 0.105 | 6.2% |
| **Total** | | | **1.687** | **100%** |

### Interpretation rules

- Top-3 attributes typically account for 60–80% of importance — focus product/marketing decisions there.
- An attribute with importance < 5% is essentially noise. Consider whether to drop it from future studies.
- If two attributes are tied (case study: brand & size both 27.4%), say so explicitly. Don't artificially break the tie.

---

## 2. Willingness to pay (WTP)

**Question answered**: "How many extra dollars would consumers pay for this attribute level?"

### Formula

```
WTP(level) = part-worth(level) / |β_price|
```

### Interpretation

- **Positive WTP**: Consumer would pay extra for this level versus the reference. WTP = $5 means "up to $5 premium is justified."
- **Negative WTP**: Consumer needs a discount to accept this level. WTP = −$3 means "this level destroys value; would need a $3 price cut to be neutral."

### Worked example

Using β_price = 0.052 (note: positive, which is itself a flag — see below):

| Level | β | WTP |
|---|---|---|
| MORKSUKY (vs HTS) | 0.463 | +$8.90 |
| 145mm (vs 140mm) | 0.463 | +$8.90 |
| Pink (vs black) | 0.153 | +$2.94 |
| Anti-scratch (vs none) | 0.121 | +$2.33 |
| UV protection (vs none) | −0.382 | −$7.35 |

### When WTP is unreliable

WTP is only meaningful if the price coefficient itself is reliable. **Flag and downgrade WTP to "directional only" if any of these hold**:

| Flag | Cause | Action |
|---|---|---|
| β_price > 0 | Price range too narrow, or sample unusual | Mark all WTP as directional |
| β_price has p > 0.5 | Insufficient data | Mark all WTP as directional |
| Some WTP > max(price) | Extreme effect or unstable price coef | Cap at max price; flag as outlier |
| Some WTP < −max(price) | Same as above for negative | Cap; flag |

The case study had β_price = +0.052 (theoretically wrong sign because the $13.98–$15.99 range was too narrow). All WTP values in that report should be read as directional.

### Pricing strategy applications

When WTP is reliable, the typical uses are:

- **Feature pricing**: charge up to WTP for an add-on feature.
- **Tier ladder**: design product tiers where each upgrade's price increment ≤ its WTP.
- **Competitive positioning**: if Brand A's WTP is +$8 over Brand B, A can sustain an $8 price premium.

---

## 3. Choice probability

**Question answered**: "Among candidate product configurations, which has highest market appeal?"

### Single-product probability (logistic transform)

For a card with attributes Xᵢ and intercept β₀:

```
U = β₀ + Σ βᵢ × Xᵢ                  (total utility)
P = exp(U) / (1 + exp(U))            (logistic transform)
```

This gives a 0–1 probability. The card with the highest P is the **predicted optimal product**.

### Worked example (case study)

| Card | Brand | Size | Color | Features | U | P |
|---|---|---|---|---|---|---|
| 7 | MORKSUKY | 145mm | pink | scratch, no UV | −0.735 | **32.4%** |
| 8 | MORKSUKY | 145mm | purple | scratch, no UV | −0.814 | 30.7% |
| 6 | MORKSUKY | 145mm | black | scratch, no UV | −0.888 | 29.2% |
| 2 | HTS | 140mm | pink | scratch, UV | −1.989 | 12.0% |
| 1 | HTS | 140mm | black | scratch, UV | −2.142 | 10.5% |

Card 7 has the highest predicted choice probability → predicted optimal configuration.

### Multi-product share-of-preference (multinomial)

When you want to know the **share** each candidate captures within a competitive set, use the multinomial form:

```
share(k) = exp(U_k) / Σⱼ exp(U_j)
```

Sums to 100% across the consideration set. This is what you'd use for market simulation: "If we launched product A alongside competitors B and C, A would capture X%."

### Interpreting the gap

If the optimal card is far ahead (e.g., 32% vs second place 17%), preferences are concentrated and the optimal configuration is robust. If top-3 cards are bunched (32% / 31% / 29%), preferences are diffuse and the "optimal" is barely better than alternatives — recommend a portfolio strategy rather than betting on one configuration.

---

## 4. Cost-benefit ROI

**Question answered**: "Where should we invest R&D / production budget for maximum customer value?"

### Formula

```
For each attribute upgrade (level X vs reference):
    ROI = part-worth gain / unit cost increase
```

### Worked example

| Upgrade | Δ Cost (USD) | Δ Utility | ROI |
|---|---|---|---|
| 145mm size (from 140mm) | 0.30 | 0.463 | **1.54** |
| Pink color (from black) | 0.25 | 0.153 | 0.61 |
| Purple color (from black) | 0.25 | 0.074 | 0.30 |
| 162mm size (from 140mm) | 0.50 | 0.137 | 0.27 |
| Anti-scratch | 0.60 | 0.121 | 0.20 |
| UV protection | 0.40 | −0.382 | −0.96 |

### How to interpret

- **ROI ≥ 1.0**: high-value upgrade. Each dollar invested produces ≥1 utility unit. Pursue.
- **0 < ROI < 1.0**: positive but inefficient. Consider only if low-cost or strategic.
- **ROI ≤ 0**: destroying value. Drop the feature or make it optional.

### Where the cost numbers come from

Almost always estimates supplied by the user. Ask them for:

1. **Product spec data**: BOM (bill of materials) costs from manufacturing.
2. **Market intelligence**: competitor pricing analysis revealing typical premium.
3. **Internal estimates**: even a back-of-envelope number is enough for prioritization.

If the user has no cost data at all, set Δcost = 1 for all attributes and compute ROI as pure utility ranking. This still produces a useful priority order.

### Strategic interpretation

The case study's findings:
- **Invest first**: Size 145mm (ROI 1.54) — this is the highest-leverage product change.
- **Add second**: Pink color (ROI 0.61) — moderate cost, moderate utility, broadens appeal.
- **Reconsider**: UV protection (ROI −0.96) — strip from standard, offer as optional, or invest in marketing the value.

---

## Reliability flags

Before presenting any of the four insights, run through this final checklist:

| Insight | Reliable when… | Flag when… |
|---|---|---|
| Importance | Always computable; meaningful even with insignificant p-values | Total range across attributes < 0.5 (model has very weak signal) |
| WTP | β_price < 0 with p < 0.3 | β_price has wrong sign OR p > 0.5 OR WTP exceeds max price |
| Choice probability | All sub-models converged | Probabilities all below 20% (intercept dominates) → small-sample artifact |
| ROI | Cost data is consistent | Cost source is "guess" — note this |

Always report flagged insights with a caveat sentence in plain English. The user's strategic decisions depend on their understanding what's solid versus directional.
