# Attribute Design Worksheet

Use this fillable worksheet during Phase II to document attribute decisions. Save a copy per study and include the completed version as an appendix to the final report.

---

## Study metadata

- **Product category**: ___________________________________________
- **Sample**: __________________________________________________
- **Date**: ____________________________________________________
- **Analyst**: _________________________________________________

---

## Step 1: Attribute candidate pool (from product pages)

List every attribute that appears on at least one product in the sample.

| # | Attribute | Sample products that list it | Universality % |
|---|-----------|------------------------------|----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |

**Universality threshold for inclusion**: 5% < universality < 95%
Attributes outside this range cannot be modeled (no variation).

---

## Step 2: Demand-side themes (from review mining)

| # | Theme | Mention frequency | Sentiment skew | Maps to attribute? |
|---|-------|-------------------|----------------|---------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

---

## Step 3: Triangulation matrix

Cross-check supply-side universality against demand-side mentions. Keep attributes that score on both.

| Attribute | Supply-side universality | Demand-side frequency | Decision | Reason |
|-----------|--------------------------|------------------------|----------|--------|
| | | | ☐ Include ☐ Exclude | |
| | | | ☐ Include ☐ Exclude | |
| | | | ☐ Include ☐ Exclude | |
| | | | ☐ Include ☐ Exclude | |
| | | | ☐ Include ☐ Exclude | |
| | | | ☐ Include ☐ Exclude | |

---

## Step 4: Final attribute and level definition

For each retained attribute, define its levels and pick the reference.

### Attribute 1: ____________________
- Type: ☐ Categorical ☐ Continuous ☐ Binary
- Levels: ____________________________________________
- Reference level: ____________________________________
- Encoding: ___________________________________________

### Attribute 2: ____________________
- Type: ☐ Categorical ☐ Continuous ☐ Binary
- Levels: ____________________________________________
- Reference level: ____________________________________
- Encoding: ___________________________________________

### Attribute 3: ____________________
- Type: ☐ Categorical ☐ Continuous ☐ Binary
- Levels: ____________________________________________
- Reference level: ____________________________________
- Encoding: ___________________________________________

### Attribute 4: ____________________
- Type: ☐ Categorical ☐ Continuous ☐ Binary
- Levels: ____________________________________________
- Reference level: ____________________________________
- Encoding: ___________________________________________

### Attribute 5: ____________________
- Type: ☐ Categorical ☐ Continuous ☐ Binary
- Levels: ____________________________________________
- Reference level: ____________________________________
- Encoding: ___________________________________________

### Attribute 6: ____________________
- Type: ☐ Categorical ☐ Continuous ☐ Binary
- Levels: ____________________________________________
- Reference level: ____________________________________
- Encoding: ___________________________________________

---

## Decision log

Document non-obvious choices made during attribute design.

- Excluded attribute "________" because: ___________________________________
- Chose "________" as reference for attribute "________" because: ____________
- Used binary instead of 3-level for "________" because: ____________________
- Capped continuous "________" at "________" because: _____________________

---

## Pre-modeling checklist

Before proceeding to Phase III:

- ☐ Every retained attribute has at least 2 levels with sufficient sample
- ☐ Reference levels chosen with clear rationale
- ☐ No two attributes are perfectly correlated in the sample
- ☐ Encoding scheme uses (k−1) dummies per categorical attribute
- ☐ Continuous attributes are on a meaningful scale (not standardized away)
- ☐ Decision log is complete enough to reproduce the design
