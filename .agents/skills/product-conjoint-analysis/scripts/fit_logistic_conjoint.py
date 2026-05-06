"""
fit_logistic_conjoint.py

Fit logistic conjoint models, with built-in support for split-model estimation
when realistic cards introduce attribute correlation.

Two main entry points:
    - fit_single_model(stacked_df, predictors): one full model
    - fit_split_models(stacked_df, attribute_groups): one model per attribute group

Both return a structured result dict with coefficients, p-values, and diagnostics.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import warnings


def fit_single_model(stacked: pd.DataFrame, predictors: list[str], response: str = "y") -> dict:
    """
    Fit one logistic regression with all predictors.

    Use when cards came from an orthogonal design and N >= 10 * len(predictors).
    """
    import statsmodels.api as sm

    X = stacked[predictors].copy()
    X = sm.add_constant(X)
    y = stacked[response]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = sm.Logit(y, X).fit(disp=False)

    return _summarize_model(model, model_name="full")


def fit_split_models(
    stacked: pd.DataFrame,
    attribute_groups: dict[str, list[str]],
    response: str = "y",
) -> dict:
    """
    Fit one logistic regression per attribute group. Recommended default for
    realistic-card conjoint where attributes are partially correlated.

    Parameters
    ----------
    attribute_groups : dict
        e.g. {
            "brand":    ["UKNOW", "MORKSUKY"],
            "color":    ["pink", "purple"],
            "size":     ["size_145", "size_162"],
            "features": ["anti_scratch", "uv_protection"],
            "price":    ["price"],
        }
    """
    import statsmodels.api as sm

    results = {}
    combined_part_worths = {}
    combined_pvalues = {}

    for group_name, predictors in attribute_groups.items():
        X = stacked[predictors].copy()
        X = sm.add_constant(X)
        y = stacked[response]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = sm.Logit(y, X).fit(disp=False)

        results[group_name] = _summarize_model(model, model_name=group_name)

        for var in predictors:
            combined_part_worths[var] = model.params[var]
            combined_pvalues[var] = model.pvalues[var]

    return {
        "submodels": results,
        "part_worths": combined_part_worths,
        "pvalues": combined_pvalues,
        "approach": "split",
    }


def _summarize_model(model, model_name: str) -> dict:
    """Extract the bits we care about from a fitted statsmodels Logit result."""
    return {
        "name": model_name,
        "coefficients": model.params.to_dict(),
        "p_values": model.pvalues.to_dict(),
        "std_errors": model.bse.to_dict(),
        "log_likelihood": model.llf,
        "null_log_likelihood": model.llnull,
        "pseudo_r2": model.prsquared,
        "n_obs": int(model.nobs),
        "model_object": model,
    }


def diagnostic_report(result: dict) -> str:
    """
    Produce a human-readable diagnostic summary. Flags common red flags:
    - wrong sign on price
    - very high p-values
    - extreme coefficient magnitudes
    """
    lines = []
    lines.append("=" * 60)
    lines.append("CONJOINT MODEL DIAGNOSTICS")
    lines.append("=" * 60)

    if result.get("approach") == "split":
        lines.append(f"\nApproach: split sub-models ({len(result['submodels'])} groups)")
        for name, sm_result in result["submodels"].items():
            lines.append(f"\n  [{name}]")
            lines.append(f"    Pseudo-R²: {sm_result['pseudo_r2']:.3f}")
            lines.append(f"    N obs:     {sm_result['n_obs']}")
            for var, coef in sm_result["coefficients"].items():
                if var == "const":
                    continue
                p = sm_result["p_values"][var]
                marker = ""
                if p < 0.05:
                    marker = " ***"
                elif p < 0.20:
                    marker = " (directional)"
                lines.append(f"    {var:25s}  β={coef:+.3f}  p={p:.3f}{marker}")
    else:
        lines.append("\nApproach: single full model")
        lines.append(f"Pseudo-R²: {result['pseudo_r2']:.3f}")
        for var, coef in result["coefficients"].items():
            if var == "const":
                continue
            p = result["p_values"][var]
            marker = ""
            if p < 0.05:
                marker = " ***"
            elif p < 0.20:
                marker = " (directional)"
            lines.append(f"  {var:25s}  β={coef:+.3f}  p={p:.3f}{marker}")

    # Red-flag checks
    lines.append("\n" + "-" * 60)
    lines.append("RED FLAG CHECKS")
    lines.append("-" * 60)

    pw = result.get("part_worths", result.get("coefficients", {}))
    if "price" in pw:
        if pw["price"] > 0:
            lines.append("⚠ Price coefficient is POSITIVE — economically wrong sign.")
            lines.append("  Likely cause: price range too narrow. WTP estimates unreliable.")
        else:
            lines.append("✓ Price coefficient sign is correct (negative).")

    extreme = [v for v, c in pw.items() if abs(c) > 5]
    if extreme:
        lines.append(f"⚠ Extreme coefficients (|β| > 5): {extreme}")
        lines.append("  Check for coding errors or outlier observations.")

    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Demo
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # Reproduce the case-study split-model result
    from build_stacked_data import build_stacked_data

    cards = pd.DataFrame([
        {"card_id": 1, "UKNOW": 0, "MORKSUKY": 0, "price": 15.99, "pink": 0, "purple": 0, "size_145": 0, "size_162": 0, "anti_scratch": 1, "uv_protection": 1},
        {"card_id": 2, "UKNOW": 0, "MORKSUKY": 0, "price": 15.99, "pink": 1, "purple": 0, "size_145": 0, "size_162": 0, "anti_scratch": 1, "uv_protection": 1},
        {"card_id": 3, "UKNOW": 1, "MORKSUKY": 0, "price": 13.98, "pink": 0, "purple": 0, "size_145": 0, "size_162": 1, "anti_scratch": 0, "uv_protection": 1},
        {"card_id": 4, "UKNOW": 1, "MORKSUKY": 0, "price": 13.98, "pink": 1, "purple": 0, "size_145": 0, "size_162": 1, "anti_scratch": 0, "uv_protection": 1},
        {"card_id": 5, "UKNOW": 1, "MORKSUKY": 0, "price": 13.98, "pink": 0, "purple": 1, "size_145": 0, "size_162": 1, "anti_scratch": 0, "uv_protection": 1},
        {"card_id": 6, "UKNOW": 0, "MORKSUKY": 1, "price": 14.95, "pink": 0, "purple": 0, "size_145": 1, "size_162": 0, "anti_scratch": 1, "uv_protection": 0},
        {"card_id": 7, "UKNOW": 0, "MORKSUKY": 1, "price": 14.95, "pink": 1, "purple": 0, "size_145": 1, "size_162": 0, "anti_scratch": 1, "uv_protection": 0},
        {"card_id": 8, "UKNOW": 0, "MORKSUKY": 1, "price": 14.95, "pink": 0, "purple": 1, "size_145": 1, "size_162": 0, "anti_scratch": 1, "uv_protection": 0},
    ])
    np.random.seed(42)
    purchases = pd.DataFrame([
        {"customer_id": i+1, "card_id": np.random.choice([6, 7, 8, 6, 7, 8, 1, 3])}
        for i in range(20)
    ])
    stacked = build_stacked_data(cards, purchases)

    groups = {
        "brand":    ["UKNOW", "MORKSUKY"],
        "color":    ["pink", "purple"],
        "size":     ["size_145", "size_162"],
        "features": ["anti_scratch", "uv_protection"],
        "price":    ["price"],
    }
    result = fit_split_models(stacked, groups)
    print(diagnostic_report(result))
