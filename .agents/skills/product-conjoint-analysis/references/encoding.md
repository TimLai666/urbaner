# Encoding Reference

How to convert attributes into model-ready numeric features. This is one of the most error-prone stages — a wrong reference level or a missed dummy trap can ruin downstream interpretation. Read this file when designing Phase II of a conjoint study.

## Table of contents
- [Categorical attributes (k levels)](#categorical-attributes-k-levels)
- [Choosing the reference level](#choosing-the-reference-level)
- [Binary attributes](#binary-attributes)
- [Continuous attributes](#continuous-attributes)
- [The dummy variable trap explained](#the-dummy-variable-trap-explained)
- [Edge cases](#edge-cases)

---

## Categorical attributes (k levels)

For an attribute with k possible levels, create **(k − 1) dummy columns**, each indicating membership in one non-reference level.

**Example: brand with 3 levels (HTS, UKNOW, MORKSUKY), reference = HTS**

| Brand | UKNOW | MORKSUKY |
|---|---|---|
| HTS | 0 | 0 |
| UKNOW | 1 | 0 |
| MORKSUKY | 0 | 1 |

After fitting:
- HTS utility = 0 (reference, by construction)
- UKNOW utility = β_UKNOW
- MORKSUKY utility = β_MORKSUKY

The interpretation is **always relative to the reference**: "MORKSUKY contributes 0.463 more utility than HTS, all else equal."

## Choosing the reference level

This is a judgment call but it materially affects readability:

| Strategy | When to use | Example |
|---|---|---|
| **Baseline / default** | Most common case | Color → black; Size → smallest standard |
| **Lowest tier** | Pricing analysis | Brand → cheapest brand in sample |
| **Highest market share** | Marketing analysis | Brand → market leader (so others read as challengers) |

**Rule of thumb**: pick the reference so most of the (k−1) coefficients come out positive. A table where most levels show negative effects is hard to read and suggests a poorly chosen reference.

Never pick a level with extremely few observations as the reference — it makes the baseline noisy and amplifies error in every other coefficient.

## Binary attributes

Single 0/1 column. The "0" state is implicit reference.

**Example: anti-scratch feature**

| Has feature? | anti_scratch |
|---|---|
| No | 0 |
| Yes | 1 |

Coefficient β = utility gain from having the feature versus not having it.

If you find yourself wanting to encode "unknown" as a third level, you have a missing data problem, not a 3-level attribute. Decide on an imputation rule or drop those rows.

## Continuous attributes

Two options:

### Option A: keep as raw continuous

```
price → keep as numeric column ($13.98, $14.95, $15.99, ...)
```

Coefficient β = utility change per unit increase. For price specifically, expect β to be negative under economic theory.

**Use this when**: price is the variable of interest, you want WTP calculations, or the value range is wide enough (>30% spread).

### Option B: bin into discrete levels

```
price → low ($13–14), mid ($15–16), high ($17–18)
       → encode as dummies with mid as reference
```

**Use this when**: the relationship may not be linear, or when you have prior reason to believe consumers perceive prices in tiers (e.g., $9.99 vs $10.00 effect).

The case study used Option A and got a positive price coefficient (β = +0.052) because the sampled price range was only $2.01 wide. **Narrow ranges → unreliable continuous estimates**. Switch to Option B (or expand the range) when the continuous coefficient comes out economically wrong.

## The dummy variable trap explained

If you encode all k levels as dummies (one-hot), the columns sum to 1 for every row, which equals the intercept term. This creates **perfect multicollinearity** — the design matrix is singular and the regression cannot solve.

```
# WRONG: one-hot encoding for 3-level attribute
HTS | UKNOW | MORKSUKY
 1  |   0   |    0
 0  |   1   |    0
 0  |   0   |    1
# Sum of each row = 1 = intercept column → singular matrix
```

```
# CORRECT: drop one column (k-1 dummies)
UKNOW | MORKSUKY    (HTS is implicit when both are 0)
  0   |    0
  1   |    0
  0   |    1
```

In `pandas`:

```python
# Use drop_first=True to avoid the trap
dummies = pd.get_dummies(df['brand'], prefix='brand', drop_first=True)
```

## Edge cases

### A level appears in the attribute taxonomy but is absent from the data

Example: theoretically a product could have purple, but no card in the sample is purple. Drop the level from the encoding entirely. Do not create an all-zero dummy column — it adds zero information and consumes a degree of freedom.

### Two levels collapse on the same products

Example: every UKNOW product happens to be 162mm in the sample. The "UKNOW" dummy and "162mm" dummy will be perfectly correlated. The single-model regression will fail or assign all the joint effect to one variable arbitrarily.

This is **the classic case for split-model estimation**. See `model_estimation.md`.

### Ordered categorical (e.g., size S/M/L)

You have a choice:

- Treat as fully categorical (S/M/L as 3 levels with 2 dummies) — captures arbitrary preference patterns but doesn't impose ordering.
- Treat as continuous integer (S=1, M=2, L=3) — imposes linearity, more efficient if the linearity assumption holds.

Default to fully categorical unless you have strong prior reason to believe the effect is linear.

### Many levels (k ≥ 6)

With 6+ levels you'll burn 5+ degrees of freedom on a single attribute, which is expensive in small samples. Consider:

- Grouping levels into meaningful clusters (e.g., 12 colors → "warm/cool/neutral").
- Dropping rare levels and noting the exclusion in the report.
- Switching from rating-based to MaxDiff conjoint, which scales better to many levels.

### Interaction terms

The split-model approach (which the case study uses) cannot estimate interactions. If the user explicitly wants to know "does price sensitivity differ by brand?", you must:

1. Use orthogonal design (not realistic cards), and
2. Fit a single full model with interaction terms (e.g., `price × brand_MORKSUKY`).

Sample size requirement scales quickly with interactions — rule of thumb is 10× the number of total predictors.
