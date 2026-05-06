# [Product Category] Conjoint Analysis Report

**Author**: ___________
**Date**: _____________
**Sample**: N=___ customers, M=___ cards, ___ stacked observations

---

## Executive summary

Three sentences max. State the optimal product configuration, the most important attribute, and the headline strategic recommendation.

---

## 1. Research scope and data sources

### Category and sample

[Describe the product category, the platform / data source, and the sample selection criteria.]

### Two-track data collection

| Track | Source | Volume | Purpose |
|-------|--------|--------|---------|
| Supply-side | [e.g., Amazon product pages] | [N products] | Identify encodable attributes |
| Demand-side | [e.g., reviews via X tool] | [N reviews] | Identify salient attributes |

---

## 2. Attribute design

### Final attribute set

| Attribute | Levels | Reference | Type |
|-----------|--------|-----------|------|
| [Attribute 1] | [Level A, B, C] | [Reference level] | [Categorical / Continuous / Binary] |
| [Attribute 2] | | | |
| [Attribute 3] | | | |
| [Attribute 4] | | | |
| [Attribute 5] | | | |
| [Attribute 6] | | | |

### Excluded attributes

| Attribute considered | Reason for exclusion |
|----------------------|----------------------|
| [Attribute X] | [e.g., universality > 95%] |

### Encoding

[Describe the dummy coding scheme. List the binary indicator columns generated.]

---

## 3. Experimental design

### Card set

[Either: realistic cards from observed market, or orthogonal design]

| Card | Attribute 1 | Attribute 2 | ... |
|------|-------------|-------------|-----|
| 1 | | | |
| 2 | | | |
| ... | | | |

### Response variable

[Define what y=1 means: chose the card, purchased it, gave it a high rating, etc.]

### Stacked data structure

```
N customers × M cards = ___ stacked observations
```

[Note any consideration set assumptions.]

---

## 4. Model results

### Approach

[Single full model OR split sub-models. Justify the choice.]

### Coefficient table

| Variable | β | Std. Err | p-value | Interpretation |
|----------|------|----------|---------|----------------|
| (Intercept) | | | | |
| Variable A | | | | |
| Variable B | | | | |

### Diagnostics

- Pseudo-R²: ___
- Sample size adequacy: [comment]
- Sign checks: [confirm price has expected sign, etc.]
- Significance: [most coefficients are statistically significant / directional only]

---

## 5. Insights

### 5.1 Attribute importance

| Rank | Attribute | Importance % | Interpretation |
|------|-----------|--------------|----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

**Headline finding**: [Top 2 attributes drive __% of choice; focus product/marketing decisions there.]

### 5.2 Willingness to pay

⚠ Reliability flag: [If β_price has wrong sign or weak significance, mark WTP as directional only.]

| Attribute level | WTP (USD) | Note |
|-----------------|-----------|------|
| | | |
| | | |
| | | |

### 5.3 Choice probability and optimal product

| Rank | Card | Configuration summary | Choice probability % |
|------|------|----------------------|----------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Predicted optimal product**: [Card description]

### 5.4 Cost-benefit ROI

| Upgrade | Δ Cost | Δ Utility | ROI | Recommendation |
|---------|--------|-----------|-----|----------------|
| | | | | |
| | | | | |

---

## 6. Strategic recommendations

### Product configuration
- **Lead SKU**: [recommended optimal product]
- **Tier alternatives**: [if portfolio strategy makes sense]

### Pricing
- [Pricing logic based on WTP and competitive positioning]

### R&D priorities
1. [Highest-ROI upgrade]
2. [Second priority]
3. [Features to deprioritize or remove]

### Marketing
- [Communication priorities based on attribute importance]

---

## 7. Limitations and future research

### Limitations
1. **Sample size**: [N customers, statistical power implications]
2. **Price range**: [If narrow, WTP estimates are unreliable]
3. **Consideration set**: [Assumptions about what customers compared]
4. **Self-selection**: [If using reviews, who writes reviews vs who buys]
5. **No interactions**: [If split models were used, can't see e.g. brand × price]

### Future research
1. [Suggested data expansion]
2. [Suggested methodological improvements]
3. [Suggested follow-up studies]

---

## Appendices

### Appendix A: Attribute design worksheet
[See `attribute_design_worksheet.md`]

### Appendix B: Raw coefficient output
[Full statsmodels summary text]

### Appendix C: Robustness checks
[Optional: alternative reference levels, alternative groupings, etc.]
