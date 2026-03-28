from __future__ import annotations

from typing import Any

from .io import derive_role_columns, find_artifact, read_json


def load_targeting_inputs(
    artifact_paths: list,
    generated_segmentation: dict[str, Any] | None,
) -> tuple[Any, dict[str, Any], dict[str, list[str]] | None] | None:
    import pandas as pd

    dataset_path = find_artifact(artifact_paths, "targeting_dataset.csv")
    if dataset_path is None:
        return None

    if generated_segmentation is None:
        segment_profiles_path = find_artifact(artifact_paths, "segment_profiles.json")
        if segment_profiles_path is None:
            return None
        segmentation = read_json(segment_profiles_path)
    else:
        segmentation = generated_segmentation

    foundation: dict[str, Any] = {}
    foundation_path = find_artifact(artifact_paths, "review_foundation.json")
    if foundation_path is not None:
        foundation = read_json(foundation_path)
    elif isinstance(segmentation.get("review_foundation"), dict):
        foundation = segmentation["review_foundation"]

    dataset = pd.read_csv(dataset_path)
    role_columns = derive_role_columns(foundation) if foundation else None
    return dataset, segmentation, role_columns


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _build_profile_significance_summary(dataset: Any) -> dict[str, Any]:
    from scipy.stats import chi2_contingency
    import pandas as pd

    profile_columns = [column for column in dataset.columns if column.startswith("profile_")]
    if not profile_columns:
        return {
            "status": "not_available",
            "alpha": 0.05,
            "variables": [],
            "significant_variables": [],
            "reason": "No profile_* columns were provided in targeting_dataset.csv.",
        }

    profile_results = []
    for column in profile_columns:
        table = pd.crosstab(dataset["cluster"], dataset[column])
        if table.shape[0] < 2 or table.shape[1] < 2:
            continue
        chi2, p_value, dof, _ = chi2_contingency(table)
        profile_results.append(
            {
                "variable": column,
                "method": "chi_square",
                "chi2": _safe_float(chi2),
                "p_value": _safe_float(p_value),
                "dof": int(dof),
                "significant": bool(p_value < 0.05),
            }
        )

    if not profile_results:
        return {
            "status": "not_available",
            "alpha": 0.05,
            "variables": [],
            "significant_variables": [],
            "reason": "Profile columns lacked enough categorical variation for chi-square testing.",
        }

    return {
        "status": "available",
        "alpha": 0.05,
        "variables": profile_results,
        "significant_variables": [
            item["variable"] for item in profile_results if bool(item["significant"])
        ],
        "reason": "",
    }


def _build_pairwise_comparison_table(dataset: Any, columns: list[str]) -> list[dict[str, Any]]:
    from statsmodels.stats.multicomp import pairwise_tukeyhsd

    results: list[dict[str, Any]] = []
    for column in list(dict.fromkeys(columns)):
        if column not in dataset.columns:
            continue
        sample = dataset[["cluster", column]].dropna()
        if sample["cluster"].nunique() < 2 or sample[column].nunique() < 2:
            continue
        try:
            tukey = pairwise_tukeyhsd(endog=sample[column], groups=sample["cluster"], alpha=0.05)
        except Exception:
            continue
        table_data = tukey.summary().data
        headers = [str(value) for value in table_data[0]]
        for row_values in table_data[1:]:
            row = dict(zip(headers, row_values))
            reject_value = row.get("reject", False)
            significant = (
                reject_value if isinstance(reject_value, bool) else str(reject_value).lower() == "true"
            )
            results.append(
                {
                    "variable": column,
                    "method": "tukey_hsd",
                    "group1": str(row.get("group1")),
                    "group2": str(row.get("group2")),
                    "comparison": f"{row.get('group1')} vs {row.get('group2')}",
                    "mean_diff": _safe_float(row.get("meandiff")),
                    "p_value": _safe_float(row.get("p-adj")),
                    "lower": _safe_float(row.get("lower")),
                    "upper": _safe_float(row.get("upper")),
                    "significant": bool(significant),
                    "alpha": 0.05,
                }
            )
    return results


def _numeric_columns(dataset: Any) -> list[str]:
    return [
        column
        for column in dataset.select_dtypes(include=["number"]).columns.tolist()
        if column != "cluster"
    ]


def _split_binary_and_continuous(dataset: Any, columns: list[str]) -> tuple[list[str], list[str]]:
    binary: list[str] = []
    continuous: list[str] = []
    for column in columns:
        if column not in dataset.columns:
            continue
        series = dataset[column].dropna()
        if series.empty:
            continue
        unique_values = {float(value) for value in series.tolist()}
        if unique_values.issubset({0.0, 1.0}):
            binary.append(column)
        else:
            continuous.append(column)
    return binary, continuous


def _resolve_target_columns(
    dataset: Any,
    role_columns: dict[str, list[str]] | None,
) -> tuple[list[str], list[str], list[str]]:
    numeric_columns = _numeric_columns(dataset)
    if role_columns:
        current_candidates = [
            column for column in role_columns.get("current_target", []) if column in numeric_columns
        ]
        potential_candidates = [
            column for column in role_columns.get("potential_target", []) if column in numeric_columns
        ]
        comparison_candidates = [
            column for column in role_columns.get("comparison_axis", []) if column in numeric_columns
        ]
    else:
        current_candidates = [
            column
            for column in ["current_value", "loyalty_score", "active_rate"]
            if column in numeric_columns
        ]
        potential_candidates = [
            column
            for column in ["potential_conversion", "tried_before", "intent_score"]
            if column in numeric_columns
        ]
        comparison_candidates = []

    if not current_candidates:
        current_candidates = numeric_columns[: max(1, min(3, len(numeric_columns)))]
    if not potential_candidates:
        potential_candidates = [
            column for column in numeric_columns if column not in current_candidates
        ]
    return current_candidates, potential_candidates, comparison_candidates


def _resolve_comparison_axes(
    dataset: Any,
    comparison_axes: list[str],
    current_columns: list[str],
    potential_columns: list[str],
    role_comparison_columns: list[str],
) -> list[str]:
    requested: list[str] = []
    available_columns = set(dataset.columns)
    for column in comparison_axes:
        column_name = str(column)
        if column_name in available_columns:
            requested.append(column_name)
            continue
        salience_column = f"{column_name}_salience"
        valence_column = f"{column_name}_valence"
        for expanded in [salience_column, valence_column]:
            if expanded in available_columns:
                requested.append(expanded)
    if requested:
        return list(dict.fromkeys(requested))
    if role_comparison_columns:
        return role_comparison_columns
    return list(dict.fromkeys(current_columns + potential_columns))


def run_targeting(
    dataset: Any,
    segmentation: dict[str, Any],
    comparison_axes: list[str],
    role_columns: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    import pandas as pd
    from scipy.stats import chi2_contingency, f_oneway
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    import statsmodels.api as sm

    cluster_profiles = {
        item["cluster"]: item for item in segmentation.get("segment_profiles", [])
    }
    current_candidates, potential_candidates, comparison_candidates = _resolve_target_columns(
        dataset,
        role_columns,
    )
    potential_binary, potential_continuous = _split_binary_and_continuous(dataset, potential_candidates)
    _, current_continuous = _split_binary_and_continuous(dataset, current_candidates)
    if not current_continuous:
        current_continuous = [
            column for column in _numeric_columns(dataset) if column not in potential_binary
        ]
    comparison_axes_used = _resolve_comparison_axes(
        dataset,
        comparison_axes,
        current_continuous,
        potential_binary + potential_continuous,
        comparison_candidates,
    )

    current_results = []
    for column in current_continuous:
        groups = [group[column].dropna().to_numpy() for _, group in dataset.groupby("cluster")]
        groups = [group for group in groups if len(group) > 0]
        if len(groups) < 2:
            continue
        try:
            f_stat, p_value = f_oneway(*groups)
        except Exception:
            f_stat, p_value = 0.0, 1.0
        design = pd.get_dummies(dataset["cluster"], drop_first=True, dtype=float)
        model = sm.OLS(dataset[column], sm.add_constant(design)).fit()
        current_results.append(
            {
                "variable": column,
                "method": "anova_regression",
                "anova": {"f_stat": float(f_stat), "p_value": float(p_value)},
                "regression_r2": float(model.rsquared),
            }
        )

    potential_results = []
    for column in potential_binary:
        table = pd.crosstab(dataset["cluster"], dataset[column])
        if table.shape[0] < 2 or table.shape[1] < 2:
            continue
        chi2, p_value, _, _ = chi2_contingency(table)
        design = pd.get_dummies(dataset["cluster"], drop_first=True, dtype=float)
        scaler = StandardScaler(with_mean=False)
        design_scaled = scaler.fit_transform(design)
        model = LogisticRegression(max_iter=1000)
        model.fit(design_scaled, dataset[column])
        potential_results.append(
            {
                "variable": column,
                "method": "chi_square_logistic_regression",
                "chi_square": {"chi2": float(chi2), "p_value": float(p_value)},
                "coefficients": [
                    {"cluster_dummy": design.columns[idx], "coefficient": float(value)}
                    for idx, value in enumerate(model.coef_[0])
                ],
            }
        )
    for column in potential_continuous:
        groups = [group[column].dropna().to_numpy() for _, group in dataset.groupby("cluster")]
        groups = [group for group in groups if len(group) > 0]
        if len(groups) < 2:
            continue
        try:
            f_stat, p_value = f_oneway(*groups)
        except Exception:
            f_stat, p_value = 0.0, 1.0
        potential_results.append(
            {
                "variable": column,
                "method": "anova",
                "anova": {"f_stat": float(f_stat), "p_value": float(p_value)},
            }
        )

    numeric_axes = [column for column in comparison_axes_used if column in _numeric_columns(dataset)]
    if not numeric_axes:
        numeric_axes = current_continuous[:]
    cluster_scores = dataset.groupby("cluster")[numeric_axes].mean(numeric_only=True)
    normalized = (cluster_scores - cluster_scores.min()) / (
        (cluster_scores.max() - cluster_scores.min()).replace(0, 1)
    )
    normalized["score"] = normalized.mean(axis=1)
    normalized = normalized.sort_values("score", ascending=False)
    selected_cluster = str(normalized["score"].idxmax())

    profile_significance_summary = _build_profile_significance_summary(dataset)
    pairwise_comparison_table = _build_pairwise_comparison_table(
        dataset,
        current_continuous + potential_continuous,
    )

    ranked_clusters = normalized.reset_index().rename(columns={"index": "cluster"}).to_dict("records")
    for idx, record in enumerate(ranked_clusters, start=1):
        record["rank"] = idx

    priority_segments = [ranked_clusters[0]["cluster"]] if ranked_clusters else []
    secondary_segments = [record["cluster"] for record in ranked_clusters[1:-1]]
    deprioritized_segments = [ranked_clusters[-1]["cluster"]] if len(ranked_clusters) > 1 else []
    target_selection_rationale = (
        f"{selected_cluster} ranks highest across comparison axes: "
        + ", ".join(numeric_axes)
        + "."
    )

    persona = cluster_profiles.get(selected_cluster, {}).get("persona", "")

    return {
        "current_target_market": current_results,
        "potential_target_market": potential_results,
        "method_selection": {
            "continuous_response": "ANOVA / regression",
            "binary_response": "chi-square / logistic regression",
            "pairwise_post_hoc": "Tukey HSD (alpha=0.05)",
            "comparison_axes_used": numeric_axes,
        },
        "profile_significance_summary": profile_significance_summary,
        "pairwise_comparison_table": pairwise_comparison_table,
        "target_selection_decision": {
            "selected_cluster": selected_cluster,
            "score": round(float(normalized.loc[selected_cluster, "score"]), 4),
            "priority_segments": priority_segments,
            "secondary_segments": secondary_segments,
            "deprioritized_segments": deprioritized_segments,
            "comparison_axes_used": numeric_axes,
            "rationale": target_selection_rationale,
            "persona": persona,
        },
        "target_selection_rationale": target_selection_rationale,
        "cluster_score_table": ranked_clusters,
    }
