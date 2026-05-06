# Model Estimation Reference

How to fit conjoint models, choose between single vs. split models, and read the diagnostics. Read this when designing Phase IV.

## Table of contents
- [Choosing the model family](#choosing-the-model-family)
- [Single full model](#single-full-model)
- [Split sub-models](#split-sub-models)
- [Rating-based variant (OLS)](#rating-based-variant-ols)
- [Diagnostics and red flags](#diagnostics-and-red-flags)
- [Sample size guidelines](#sample-size-guidelines)

---

## Choosing the model family

| Response variable | Model | Library |
|---|---|---|
| Continuous rating (1–7, 0–100) | OLS linear regression | `statsmodels.OLS` or `sklearn.LinearRegression` |
| Binary choice (chose / didn't choose) | Logistic regression | `statsmodels.Logit` |
| Multinomial choice (picked one of several) | Multinomial logit (MNL) | `statsmodels.MNLogit` or `pylogit` |
| Ranked choices | Rank-ordered logit | `pylogit` or custom |

This skill defaults to **logistic** because revealed-preference data (purchases, reviews, clicks) is binary. Use the table above to switch when needed.

---

## Single full model

All attributes go into one regression. Use this when:

- Cards came from an **orthogonal design** (attributes are uncorrelated by construction), AND
- N ≥ 10 × number of predictors

### Code template

```python
import pandas as pd
import statsmodels.api as sm

# Assume df already has: encoded dummy columns + 'price' + response 'y'
predictor_cols = ['UKNOW', 'MORKSUKY', 'pink', 'purple',
                  'size_145', 'size_162', 'anti_scratch', 'uv_protection', 'price']
X = df[predictor_cols]
X = sm.add_constant(X)            # intercept
y = df['y']                        # 0/1 purchase indicator

model = sm.Logit(y, X).fit(disp=False)
print(model.summary())
```

### What to extract

- `model.params` → part-worth utilities
- `model.pvalues` → significance per coefficient
- `model.llf`, `model.llnull` → for likelihood ratio test
- `model.prsquared` → McFadden's pseudo-R² (treat 0.2–0.4 as good fit)

### When the single model fails

You'll see one or more of these:

- Standard errors > coefficient magnitudes → unstable estimates
- Sign reversals (e.g., negative price coefficient flips positive)
- Convergence warnings during MLE
- VIF > 10 for any predictor → severe multicollinearity

When this happens: **switch to split sub-models**.

---

## Split sub-models

The case-study approach. Each attribute (or group of related attributes) gets its own regression, sharing only the response variable.

### Why this works

With realistic cards, attributes are correlated. A single model attributes shared variance arbitrarily, producing unstable coefficients. Splitting estimates each attribute's effect averaged over the empirical joint distribution of the others — less precise but stable.

### How to group

Default grouping (case study):

| Sub-model | Predictors |
|---|---|
| Brand | brand dummies |
| Color | color dummies |
| Size | size dummies |
| Features | binary feature flags (anti-scratch, UV, etc.) |
| Price | price (continuous) |

Combine binary features into one model only if there's no strong reason to separate them (they share a common "premium product" cluster, etc.). Brand and size each get their own model because they're typically the two highest-importance attributes.

### Code template

```python
def fit_submodel(df, predictor_cols, response='y'):
    X = sm.add_constant(df[predictor_cols])
    y = df[response]
    return sm.Logit(y, X).fit(disp=False)

submodels = {
    'brand':    fit_submodel(df, ['UKNOW', 'MORKSUKY']),
    'color':    fit_submodel(df, ['pink', 'purple']),
    'size':     fit_submodel(df, ['size_145', 'size_162']),
    'features': fit_submodel(df, ['anti_scratch', 'uv_protection']),
    'price':    fit_submodel(df, ['price']),
}

# Collect part-worth utilities into a single dict
part_worths = {}
for name, m in submodels.items():
    for var, coef in m.params.items():
        if var != 'const':
            part_worths[var] = coef

print(part_worths)
```

### Limitations to declare

When using split models, **explicitly state in the report**:

- Cannot estimate interaction effects (e.g., "Does brand X command a premium specifically among 145mm buyers?")
- Each sub-model's intercept is different — don't try to combine them
- Use the **price sub-model's coefficient** as the single price-sensitivity reference for WTP calculations

---

## Rating-based variant (OLS)

If respondents rated each card on a continuous scale (e.g., "How appealing is this on a 1–7 scale?"), switch from logistic to OLS:

```python
model = sm.OLS(y, X).fit()
```

The math for downstream insights (importance, WTP, optimal product) is identical — only the model family changes. The output coefficients are still part-worth utilities.

For OLS, `R²` replaces pseudo-R²; expect 0.4–0.7 for well-designed conjoint surveys.

For ranked-preference data (respondent orders cards 1st, 2nd, 3rd…), use rank-ordered logit (exploded logit). See the `pylogit` documentation. Most beginners just convert ranks to ratings and use OLS, which loses some efficiency but is acceptable.

---

## Diagnostics and red flags

After fitting, always run through this checklist before moving to Phase V.

### Sign check

For **economic-theory-bound** attributes, signs should match expectation:

| Attribute | Expected sign | Action if wrong |
|---|---|---|
| Price (raw) | Negative | Check price range; if narrow, switch to binned price or expand sample |
| Quality / premium feature | Positive | Re-examine reference level; check sample composition |
| Defect / negative feature | Negative | Same as above |

For **purely preferential** attributes (color, brand, style), any sign is acceptable — these reflect consumer taste.

### Magnitude check

If one attribute's coefficient is >5× larger than all others, suspect:
- A coding error (e.g., did you accidentally include the response variable as a predictor?)
- An outlier customer skewing the result
- A misidentified attribute (e.g., a category indicator that actually proxies for the brand)

### Significance — don't over-interpret

P-values in conjoint with realistic cards and small samples are notoriously high. The case study had every p > 0.4, but the directional patterns were still actionable.

**Reporting rule**:
- p < 0.05 → "statistically significant"
- 0.05 ≤ p < 0.20 → "directionally suggestive"
- p ≥ 0.20 → "no reliable signal; magnitude reported for descriptive purposes only"

### Pseudo-R² benchmarks (for logistic)

| McFadden's R² | Interpretation |
|---|---|
| < 0.10 | Weak fit; attributes don't explain choice well |
| 0.10–0.20 | Acceptable for choice models |
| 0.20–0.40 | Good fit |
| > 0.40 | Excellent — but check for data leakage |

These are lower than OLS R² benchmarks. **A pseudo-R² of 0.15 in a logistic conjoint is not a bad model.**

---

## Sample size guidelines

### Minimum useful sample

For **single-model** estimation:

```
N ≥ 10 × (number of predictors including intercept)
```

For an 8-predictor model, that's 80 observations minimum, ideally 200+.

For **split-model** estimation, each sub-model needs:

```
N ≥ 10 × (predictors in that sub-model + 1)
```

Brand sub-model with 2 dummies = 30 observations minimum.

### When data is below minimum

Don't refuse to run — produce results with appropriate caveats:

- Lead the report with a sample-size warning.
- Report all results as "directional, requires validation."
- Recommend specific data collection to expand the sample.

The case study's N=20 customers (160 stacked) is below most thresholds. The report explicitly frames findings as directional and lists "expand sample" as the first future-research priority.
