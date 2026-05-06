"""
compute_insights.py

Translate part-worth utilities into the four canonical conjoint insights:
    1. Attribute importance (relative %)
    2. Willingness to pay (WTP)
    3. Choice probability per card
    4. Cost-benefit ROI

Each function takes the part_worths dict produced by fit_logistic_conjoint and
returns a tidy DataFrame ready for reporting.
"""

from __future__ import annotations
import numpy as np
import pandas as pd


def compute_attribute_importance(
    part_worths: dict[str, float],
    attribute_groups: dict[str, list[str]],
    price_range: tuple[float, float] | None = None,
    price_var: str = "price",
    binary_separately: bool = True,
) -> pd.DataFrame:
    """
    Compute relative importance of each attribute.

    For categorical attributes: range = max(part-worths) - min(part-worths)
                                 (with implicit reference part-worth = 0)
    For price (continuous):     range = |β_price| × (max_price - min_price)

    Parameters
    ----------
    part_worths : dict[str, float]
        Coefficient dict, e.g. {'UKNOW': 0.137, 'MORKSUKY': 0.463, ...}
    attribute_groups : dict[str, list[str]]
        Maps attribute name to its predictor columns.
    price_range : (min, max), optional
        Required if a price variable is in the model.
    price_var : str
        Name of the price predictor.
    binary_separately : bool, default True
        If True, when a group contains only binary 0/1 features (each its own
        attribute, like "features": ["anti_scratch", "uv_protection"]), each
        feature is reported as a separate row. Set to False to lump them as
        a single attribute group.

    Returns
    -------
    pd.DataFrame with columns: attribute, range, importance_pct
    """
    rows = []
    for attr, predictors in attribute_groups.items():
        if attr.lower() == "price" or price_var in predictors:
            if price_range is None:
                raise ValueError(
                    "price_range must be provided when computing importance "
                    "for a price attribute."
                )
            beta = part_worths.get(price_var, 0)
            attr_range = abs(beta) * (price_range[1] - price_range[0])
            rows.append({"attribute": attr, "range": attr_range})
        elif binary_separately and len(predictors) >= 2 and _looks_like_independent_binaries(predictors):
            # Each binary feature treated as its own attribute
            for p in predictors:
                pw = part_worths.get(p, 0)
                rows.append({"attribute": p, "range": abs(pw)})
        else:
            # Categorical: include implicit reference at 0
            values = [part_worths.get(p, 0) for p in predictors] + [0]
            attr_range = max(values) - min(values)
            rows.append({"attribute": attr, "range": attr_range})

    df = pd.DataFrame(rows)
    total = df["range"].sum()
    if total == 0:
        df["importance_pct"] = 0.0
    else:
        df["importance_pct"] = df["range"] / total * 100
    return df.sort_values("importance_pct", ascending=False).reset_index(drop=True)


def _looks_like_independent_binaries(predictors: list[str]) -> bool:
    """
    Heuristic: predictors that look like independent binary feature flags
    (e.g., "anti_scratch", "uv_protection") rather than dummy levels of a
    single categorical (e.g., "size_145", "size_162" sharing the "size_" prefix).
    """
    # If they share a common prefix, they're likely dummies of one categorical
    common_prefix_chars = 0
    if len(predictors) < 2:
        return False
    p0 = predictors[0]
    for i in range(min(len(p) for p in predictors)):
        if all(p[i] == p0[i] for p in predictors):
            common_prefix_chars += 1
        else:
            break
    # Common prefix > 3 chars suggests they're related dummies
    return common_prefix_chars <= 3


def compute_wtp(
    part_worths: dict[str, float],
    attribute_groups: dict[str, list[str]],
    price_var: str = "price",
) -> pd.DataFrame:
    """
    Compute willingness to pay for each non-reference categorical level.

    WTP(level) = part-worth(level) / |β_price|

    Returns DataFrame with columns: attribute, level, part_worth, wtp_dollars,
    plus a 'reliability' flag.
    """
    if price_var not in part_worths:
        raise ValueError(f"part_worths must contain '{price_var}' for WTP computation.")

    beta_price = part_worths[price_var]
    if beta_price == 0:
        raise ValueError("Price coefficient is 0 — WTP undefined.")

    reliable = beta_price < 0   # economically correct sign
    abs_beta_price = abs(beta_price)

    rows = []
    for attr, predictors in attribute_groups.items():
        if price_var in predictors:
            continue   # skip price itself
        for level in predictors:
            pw = part_worths.get(level, 0)
            wtp = pw / abs_beta_price
            rows.append({
                "attribute": attr,
                "level": level,
                "part_worth": pw,
                "wtp_dollars": wtp,
            })

    df = pd.DataFrame(rows)
    df["reliability"] = "reliable" if reliable else "directional only (β_price > 0)"
    return df.sort_values("wtp_dollars", ascending=False).reset_index(drop=True)


def compute_choice_probability(
    cards: pd.DataFrame,
    part_worths: dict[str, float],
    intercept: float = 0.0,
    card_id_col: str = "card_id",
) -> pd.DataFrame:
    """
    For each card, compute total utility and logistic-transformed choice probability.

    P = exp(U) / (1 + exp(U))

    Parameters
    ----------
    cards : pd.DataFrame
        Card definitions with predictor columns matching keys in part_worths.
    part_worths : dict
        Coefficients from the fitted model(s).
    intercept : float
        Intercept term (β₀). For split-model approaches, use the price sub-model's
        intercept by convention, or 0 if the user wants relative comparison only.

    Returns
    -------
    DataFrame with: card_id, utility, prob_pct, rank
    """
    rows = []
    for _, card in cards.iterrows():
        u = intercept
        for var, coef in part_worths.items():
            if var in card.index:
                u += coef * card[var]
        p = np.exp(u) / (1 + np.exp(u))
        rows.append({
            "card_id": card[card_id_col],
            "utility": u,
            "prob_pct": p * 100,
        })

    df = pd.DataFrame(rows).sort_values("prob_pct", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def compute_share_of_preference(
    cards: pd.DataFrame,
    part_worths: dict[str, float],
    card_id_col: str = "card_id",
) -> pd.DataFrame:
    """
    Multinomial share-of-preference: each card's exp(U) divided by total.

    Use this when the question is 'in this competitive set, what share would
    each card capture?' Sums to 100% across the input set.
    """
    rows = []
    utilities = []
    for _, card in cards.iterrows():
        u = 0.0
        for var, coef in part_worths.items():
            if var in card.index:
                u += coef * card[var]
        utilities.append(u)
        rows.append({"card_id": card[card_id_col], "utility": u})

    exp_u = np.exp(utilities)
    shares = exp_u / exp_u.sum()
    df = pd.DataFrame(rows)
    df["share_pct"] = shares * 100
    return df.sort_values("share_pct", ascending=False).reset_index(drop=True)


def compute_cost_benefit_roi(
    part_worths: dict[str, float],
    attribute_costs: dict[str, float],
) -> pd.DataFrame:
    """
    Compute ROI for each attribute upgrade.

    ROI = part_worth / unit_cost

    Parameters
    ----------
    part_worths : dict
        Coefficient for each attribute level.
    attribute_costs : dict
        Estimated unit cost increase for each level (versus reference).
        Same keys as part_worths (subset is fine).

    Returns
    -------
    DataFrame: level, part_worth, unit_cost, roi, recommendation
    """
    rows = []
    for level, cost in attribute_costs.items():
        if level not in part_worths:
            continue
        pw = part_worths[level]
        if cost <= 0:
            roi = np.nan
            rec = "cost data missing"
        else:
            roi = pw / cost
            if roi >= 1.0:
                rec = "high-value upgrade — pursue"
            elif roi > 0:
                rec = "moderate value — consider"
            else:
                rec = "destroys value — drop or make optional"
        rows.append({
            "level": level,
            "part_worth": pw,
            "unit_cost": cost,
            "roi": roi,
            "recommendation": rec,
        })

    df = pd.DataFrame(rows).sort_values("roi", ascending=False, na_position="last")
    return df.reset_index(drop=True)


# ----------------------------------------------------------------------------
# Demo with case-study numbers
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # Part-worths from the case study
    part_worths = {
        "UKNOW": 0.137, "MORKSUKY": 0.463,
        "pink": 0.153, "purple": 0.074,
        "size_145": 0.463, "size_162": 0.137,
        "anti_scratch": 0.121,
        "uv_protection": -0.382,
        "price": 0.052,   # note: positive sign, will trigger reliability flag
    }
    groups = {
        "brand":    ["UKNOW", "MORKSUKY"],
        "color":    ["pink", "purple"],
        "size":     ["size_145", "size_162"],
        "features": ["anti_scratch", "uv_protection"],
        "price":    ["price"],
    }

    # For the importance table, structure groups so each independently-priced
    # feature becomes its own attribute (matching case-study reporting style).
    importance_groups = {
        "brand":         ["UKNOW", "MORKSUKY"],
        "color":         ["pink", "purple"],
        "size":          ["size_145", "size_162"],
        "anti_scratch":  ["anti_scratch"],
        "uv_protection": ["uv_protection"],
        "price":         ["price"],
    }

    print("=== ATTRIBUTE IMPORTANCE (案例研究風格:屬性層級) ===")
    imp = compute_attribute_importance(
        part_worths, importance_groups,
        price_range=(13.98, 15.99),
        binary_separately=False,
    )
    print(imp.to_string(index=False), "\n")

    print("=== WTP ===")
    wtp = compute_wtp(part_worths, groups)
    print(wtp.to_string(index=False), "\n")

    # Choice probability
    cards = pd.DataFrame([
        {"card_id": 7, "UKNOW": 0, "MORKSUKY": 1, "pink": 1, "purple": 0,
         "size_145": 1, "size_162": 0, "anti_scratch": 1, "uv_protection": 0,
         "price": 14.95},
        {"card_id": 1, "UKNOW": 0, "MORKSUKY": 0, "pink": 0, "purple": 0,
         "size_145": 0, "size_162": 0, "anti_scratch": 1, "uv_protection": 1,
         "price": 15.99},
    ])
    print("=== CHOICE PROBABILITY ===")
    prob = compute_choice_probability(cards, part_worths, intercept=-2.712)
    print(prob.to_string(index=False), "\n")

    print("=== COST-BENEFIT ROI ===")
    costs = {
        "pink": 0.25, "purple": 0.25,
        "size_145": 0.30, "size_162": 0.50,
        "anti_scratch": 0.60, "uv_protection": 0.40,
    }
    roi = compute_cost_benefit_roi(part_worths, costs)
    print(roi.to_string(index=False))
