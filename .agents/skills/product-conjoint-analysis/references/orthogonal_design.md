# Orthogonal Design Reference

How to generate fractional factorial product card sets when you can run a real survey (rather than relying on observed market data). Read this when the user is doing classical conjoint with willing respondents.

## When to use orthogonal design

Use orthogonal design (over realistic cards) when:

- You can ask respondents to evaluate hypothetical products (survey, interview, online panel).
- You need maximum statistical efficiency — orthogonal designs let you fit a single full model with all attributes simultaneously.
- You want to test attribute interactions.

Stick with **realistic cards** when:

- Data comes from observed market behavior (purchases, reviews, clicks).
- Hypothetical combinations would be implausible to respondents (e.g., a Rolex at $50).
- The user explicitly wants to mirror the existing market.

## The full factorial baseline

A full factorial design tests every possible combination:

```
N_full = level₁ × level₂ × ... × levelₖ
```

Example: 3 brands × 3 colors × 3 sizes × 2 anti-scratch × 2 UV = 108 combinations. Most respondents can't rate that many cards reliably (cognitive overload sets in around 15–25 cards). So we use a fraction.

## Fractional factorial design

A **fractional factorial** is a carefully chosen subset of the full factorial that preserves orthogonality — meaning each attribute level appears equally often across the design, and pairs of levels appear in balanced proportions.

### Core property: orthogonality

For any two attributes, the joint distribution of their levels in the design is uniform. This means the regression coefficients can be estimated independently — no multicollinearity by construction.

### Generating designs in Python

Use the `pyDOE2` library:

```python
from pyDOE2 import fracfact_by_res
import numpy as np

# Example: 5 attributes, each at 2 levels, resolution III design
design = fracfact_by_res(5, 3)  # ±1 coded matrix
print(design)
# 8 rows instead of 32 (full factorial)
```

For mixed-level designs (some attributes have 2 levels, others 3+), use `pyDOE2.create_design` or move to R's `AlgDesign` package which has better support.

### Resolution levels

Designs are classified by their **resolution**, which determines what effects are confounded:

| Resolution | Confounding | Use when |
|---|---|---|
| III | Main effects with 2-way interactions | Smallest design; only main effects matter |
| IV | Main effects clean, 2-way interactions confounded with each other | Need main effects but suspect some interactions |
| V | Main effects + 2-way interactions clean | Want to detect interactions; needs more cards |

**Default for conjoint**: Resolution III or IV. Most consumer studies focus on main effects.

### Example: 6-attribute design

Suppose we want to test:
- Brand (3 levels)
- Color (3 levels)
- Price (3 levels)
- Size (3 levels)
- Anti-scratch (2 levels)
- UV protection (2 levels)

Full factorial = 3⁴ × 2² = 324 cards. We need a fraction.

A common choice is an **orthogonal main-effects plan (OMEP)** with 18 cards. Generate using:

```python
# Approximate; for production use specialized tools
import pyDOE2

# For complex mixed designs, fall back to standard published OMEPs
# Reference: NIST/SEMATECH e-Handbook, Table of Standard L18 design
```

For mixed-level OMEPs the simplest path is to look up a published table (Taguchi L9, L18, L27 designs are well-tabulated) rather than generate from scratch.

## Card count guidelines

| Number of attributes | Suggested cards | Notes |
|---|---|---|
| 3–4 | 8–16 | Full factorial may be feasible |
| 5–6 | 16–24 | Fractional factorial standard |
| 7–8 | 24–32 | Push respondents toward limit |
| 9+ | Use MaxDiff or adaptive conjoint | Standard rating becomes unreliable |

Per respondent, 12–20 cards is the reliable rating ceiling. Beyond that, fatigue and inattention dominate.

## Choice-based vs. rating-based with orthogonal design

Even with an orthogonal card set, you can ask respondents in two ways:

### Rating-based

Show each card individually, ask for a 1–7 score. Use OLS regression. Older, simpler, but less realistic.

### Choice-based (CBC)

Show **sets of 2–4 cards**, ask the respondent to pick their favorite. Closer to actual purchase behavior. Use multinomial logit.

For CBC, you need to generate **choice sets** in addition to the orthogonal card design. Tools like Sawtooth Software handle this; for DIY, balance the design so each card appears in choice sets equally often.

## Validating an orthogonal design

After generating, verify:

```python
# Check correlation matrix of the encoded design
import pandas as pd
import numpy as np

design_df = pd.DataFrame(design_matrix, columns=attribute_names)
corr = design_df.corr()
print(corr)

# All off-diagonal values should be 0 (or very close).
# If not, the design is not properly orthogonal.
np.fill_diagonal(corr.values, 0)
print(f"Max off-diagonal correlation: {corr.values.max()}")
# Should be < 0.1 for a clean design
```

If correlations are non-trivial, regenerate with different parameters or pick a published design table.

## When orthogonal design is overkill

For exploratory studies with very small sample sizes (N < 30 respondents), orthogonality matters less than realism. The case study deliberately chose realistic cards because:

- The "respondents" were anonymous review-writers — no opportunity to ask them to rate hypothetical cards.
- Combinations had to map to actual product SKUs to be linkable to reviews.

Orthogonal design is the ideal; realistic cards are the pragmatic fallback when the data-collection method dictates it.
