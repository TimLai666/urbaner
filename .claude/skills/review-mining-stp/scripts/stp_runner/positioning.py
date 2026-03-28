from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from .io import find_artifact, read_json


def load_positioning_inputs(
    artifact_paths: list[Path], ideal_point_file: str | None, brands_file: str | None
) -> tuple[Any, dict[str, Any], dict[str, Any]] | None:
    import pandas as pd

    scorecard_path = find_artifact(artifact_paths, "positioning_scorecard.csv")
    if scorecard_path is None:
        return None

    brands_path = Path(brands_file) if brands_file else find_artifact(artifact_paths, "brands.json")
    ideal_path = Path(ideal_point_file) if ideal_point_file else find_artifact(artifact_paths, "ideal_point.json")
    if brands_path is None or ideal_path is None or not brands_path.exists() or not ideal_path.exists():
        return None

    scorecard = pd.read_csv(scorecard_path)
    brands = read_json(brands_path)
    ideal_point = read_json(ideal_path)
    return scorecard, brands, ideal_point


def _ideal_value_for_axis(raw_value: Any, axis: str) -> float:
    if isinstance(raw_value, dict):
        axis_value = raw_value.get(axis)
        if axis_value is None:
            raise SystemExit(f"ideal_point.json attribute entry is missing '{axis}'.")
        return float(axis_value)
    scalar = float(raw_value)
    if axis == "salience":
        return max(0.0, min(7.0, scalar))
    return max(0.0, min(10.0, scalar + 3.0))


def _build_ideal_feature_map(scorecard: Any, ideal_point: dict[str, Any]) -> dict[str, float]:
    feature_map: dict[str, float] = {}
    ideal_attributes = ideal_point.get("attributes", {})
    if not isinstance(ideal_attributes, dict) or not ideal_attributes:
        raise SystemExit("ideal_point.json must define a non-empty attributes object.")
    for row in scorecard[["attribute", "axis", "feature"]].drop_duplicates().to_dict("records"):
        attribute = str(row["attribute"])
        axis = str(row["axis"])
        feature = str(row["feature"])
        if attribute not in ideal_attributes:
            continue
        feature_map[feature] = _ideal_value_for_axis(ideal_attributes[attribute], axis)
    if not feature_map:
        raise SystemExit(
            "ideal_point.json did not provide any attributes that match positioning_scorecard.csv."
        )
    return feature_map


def _feature_meta(scorecard: Any, shared_columns: list[str]) -> dict[str, dict[str, str]]:
    rows = scorecard[scorecard["feature"].isin(shared_columns)][["attribute", "axis", "feature"]]
    return {
        str(row["feature"]): {
            "attribute": str(row["attribute"]),
            "axis": str(row["axis"]),
        }
        for row in rows.drop_duplicates().to_dict("records")
    }


def _top_axis_features(rows: list[dict[str, Any]], axis: str, *, reverse: bool) -> list[dict[str, Any]]:
    axis_rows = [row for row in rows if str(row.get("axis")) == axis]
    axis_rows.sort(key=lambda row: float(row.get("leader_score", 0.0)), reverse=reverse)
    return axis_rows[:5]


def run_positioning(
    scorecard: Any, brands: dict[str, Any], ideal_point: dict[str, Any], method: str, output_dir: Path
) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import FactorAnalysis
    from sklearn.manifold import MDS
    from sklearn.preprocessing import StandardScaler

    required_scorecard_columns = {"brand", "attribute", "axis", "feature", "score"}
    if not required_scorecard_columns.issubset(scorecard.columns):
        missing = sorted(required_scorecard_columns - set(scorecard.columns))
        raise SystemExit(
            "positioning_scorecard.csv is missing required columns: " + ", ".join(missing)
        )

    pivot = scorecard.pivot_table(index="brand", columns="feature", values="score", aggfunc="mean")
    ideal_feature_map = _build_ideal_feature_map(scorecard, ideal_point)
    shared_columns = [column for column in pivot.columns if column in ideal_feature_map]
    if len(shared_columns) < 2:
        raise SystemExit(
            "Positioning requires at least two shared salience/valence features between positioning_scorecard.csv and ideal_point.json."
        )
    pivot = pivot[shared_columns].sort_index()
    ideal_series = pd.Series({column: ideal_feature_map[column] for column in shared_columns}, name=ideal_point["label"])
    brand_matrix = pivot.copy()
    feature_meta = _feature_meta(scorecard, shared_columns)

    coordinate_rows: list[dict[str, Any]] = []
    vector_rows: list[dict[str, Any]] = []

    if method == "factor_analysis":
        combined = pd.concat([brand_matrix, ideal_series.to_frame().T], axis=0)
        scaler = StandardScaler()
        scaled = scaler.fit_transform(combined)
        model = FactorAnalysis(n_components=2, random_state=42)
        factor_scores = model.fit_transform(scaled)
        loadings = model.components_.T

        for idx, label in enumerate(combined.index):
            point_type = "ideal" if label == ideal_point["label"] else "brand"
            coordinate_rows.append(
                {
                    "label": str(label),
                    "point_type": point_type,
                    "x": float(factor_scores[idx, 0]),
                    "y": float(factor_scores[idx, 1]),
                }
            )
        for idx, feature in enumerate(combined.columns):
            vector_rows.append(
                {
                    "label": str(feature),
                    "attribute": feature_meta[str(feature)]["attribute"],
                    "axis": feature_meta[str(feature)]["axis"],
                    "vector_type": "attribute_axis",
                    "x_start": 0.0,
                    "y_start": 0.0,
                    "x_end": float(loadings[idx, 0]),
                    "y_end": float(loadings[idx, 1]),
                    "x_loading": float(loadings[idx, 0]),
                    "y_loading": float(loadings[idx, 1]),
                }
            )
        positioning_method_used = "factor_analysis"
        attribute_vectors_not_defined = False
        perceptual_map_method = {
            "method": positioning_method_used,
            "brand_point_source": "factor scores on combined salience + valence feature matrix",
            "ideal_point_source": "factor scores on the same combined feature matrix",
            "attribute_vector_source": "factor loadings on feature-level salience/valence axes",
        }
    else:
        similarity_matrix = brands.get("similarity_matrix")
        if not similarity_matrix:
            raise SystemExit(
                "MDS requires brands.json to contain similarity_matrix for the first version."
            )
        dissimilarity = np.array(similarity_matrix, dtype=float)
        model = MDS(
            n_components=2,
            dissimilarity="precomputed",
            random_state=42,
            n_init=4,
        )
        brand_coords = model.fit_transform(dissimilarity)

        ideal_vector = ideal_series.to_numpy(dtype=float)
        brand_vectors = brand_matrix.to_numpy(dtype=float)
        weights = brand_vectors @ ideal_vector
        if float(weights.sum()) == 0.0:
            weights = np.repeat(1.0 / len(brand_coords), len(brand_coords))
        else:
            weights = weights / weights.sum()
        ideal_coord = np.average(brand_coords, axis=0, weights=weights)

        for idx, label in enumerate(brand_matrix.index):
            coordinate_rows.append(
                {
                    "label": str(label),
                    "point_type": "brand",
                    "x": float(brand_coords[idx, 0]),
                    "y": float(brand_coords[idx, 1]),
                }
            )
        coordinate_rows.append(
            {
                "label": str(ideal_point["label"]),
                "point_type": "ideal",
                "x": float(ideal_coord[0]),
                "y": float(ideal_coord[1]),
            }
        )
        positioning_method_used = "mds"
        attribute_vectors_not_defined = True
        perceptual_map_method = {
            "method": positioning_method_used,
            "brand_point_source": "mds coordinates from brand similarity matrix",
            "ideal_point_source": "weighted centroid from combined dual-axis ideal profile",
            "attribute_vector_source": "attribute_vectors_not_defined",
        }

    coordinate_frame = pd.DataFrame(coordinate_rows)
    coordinate_frame.to_csv(output_dir / "perceptual_map_coordinates.csv", index=False, encoding="utf-8")
    if vector_rows:
        pd.DataFrame(vector_rows).to_csv(
            output_dir / "perceptual_map_vectors.csv", index=False, encoding="utf-8"
        )

    figure_path = output_dir / "perceptual_map.png"
    fig, ax = plt.subplots(figsize=(8, 6))
    for row in coordinate_rows:
        if row["point_type"] == "brand":
            ax.scatter(row["x"], row["y"], color="#1f77b4", s=90)
            ax.text(row["x"] + 0.03, row["y"] + 0.03, row["label"], fontsize=9)
        else:
            ax.scatter(row["x"], row["y"], color="#d62728", marker="*", s=180)
            ax.text(row["x"] + 0.03, row["y"] + 0.03, row["label"], fontsize=10)
    for row in vector_rows:
        ax.arrow(
            0.0,
            0.0,
            row["x_end"],
            row["y_end"],
            color="#2ca02c",
            length_includes_head=True,
            head_width=0.04,
            alpha=0.85,
        )
        ax.text(row["x_end"] + 0.02, row["y_end"] + 0.02, row["label"], fontsize=8, color="#2ca02c")
    ax.axhline(0.0, color="#888888", linewidth=0.8)
    ax.axvline(0.0, color="#888888", linewidth=0.8)
    ax.set_xlabel("Factor 1" if method == "factor_analysis" else "MDS Dimension 1")
    ax.set_ylabel("Factor 2" if method == "factor_analysis" else "MDS Dimension 2")
    ax.set_title("Perceptual Map")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(figure_path, dpi=200)
    plt.close(fig)

    coordinates_by_label = {row["label"]: row for row in coordinate_rows}
    ideal_coords = coordinates_by_label[ideal_point["label"]]
    brand_distance_table = []
    for label in brand_matrix.index:
        row = coordinates_by_label[label]
        distance = math.dist((row["x"], row["y"]), (ideal_coords["x"], ideal_coords["y"]))
        brand_distance_table.append({"brand": label, "distance_to_ideal": round(distance, 4)})
    nearest = min(brand_distance_table, key=lambda item: item["distance_to_ideal"])

    feature_benchmarks: list[dict[str, Any]] = []
    for feature in shared_columns:
        scores = pivot[feature].sort_values(ascending=False)
        leader = scores.index[0]
        leader_score = float(scores.iloc[0])
        gap = float(scores.iloc[0] - scores.iloc[1]) if len(scores) > 1 else float(scores.iloc[0])
        meta = feature_meta[str(feature)]
        feature_benchmarks.append(
            {
                "attribute": meta["attribute"],
                "axis": meta["axis"],
                "feature": feature,
                "leader": str(leader),
                "leader_score": round(leader_score, 4),
                "ideal_score": round(float(ideal_series[feature]), 4),
                "gap_to_next_brand": round(gap, 4),
                "gap_to_ideal": round(float(ideal_series[feature] - leader_score), 4),
            }
        )

    pod = [item["feature"] for item in feature_benchmarks if item["gap_to_next_brand"] >= 0.4]
    pop = [
        feature
        for feature in shared_columns
        if float(pivot[feature].min()) >= float(ideal_series[feature] - 1.5)
    ]

    competition_landscape = []
    brand_labels = list(brand_matrix.index)
    for idx, brand_a in enumerate(brand_labels):
        row_a = coordinates_by_label[str(brand_a)]
        for brand_b in brand_labels[idx + 1 :]:
            row_b = coordinates_by_label[str(brand_b)]
            competition_landscape.append(
                {
                    "brand_a": str(brand_a),
                    "brand_b": str(brand_b),
                    "distance": round(
                        math.dist((row_a["x"], row_a["y"]), (row_b["x"], row_b["y"])),
                        4,
                    ),
                }
            )
    competition_landscape.sort(key=lambda item: item["distance"])

    brand_name = nearest["brand"]
    strategy_matrix = {"appeal": [], "improve": [], "change": [], "abandon": []}
    for feature in shared_columns:
        brand_score = float(pivot.loc[brand_name, feature])
        ideal_score = float(ideal_series[feature])
        gap = ideal_score - brand_score
        if gap <= 0.3:
            strategy_matrix["appeal"].append(feature)
        elif gap <= 0.8:
            strategy_matrix["improve"].append(feature)
        elif gap <= 1.4:
            strategy_matrix["change"].append(feature)
        else:
            strategy_matrix["abandon"].append(feature)

    if not attribute_vectors_not_defined and vector_rows:
        projection_summary = []
        for vector in vector_rows:
            vector_norm = math.sqrt((vector["x_end"] ** 2) + (vector["y_end"] ** 2))
            if vector_norm == 0:
                continue
            ideal_projection = (
                ideal_coords["x"] * vector["x_end"] + ideal_coords["y"] * vector["y_end"]
            ) / vector_norm
            brand_projection_rows = []
            for label in brand_matrix.index:
                row = coordinates_by_label[label]
                projection_value = (row["x"] * vector["x_end"] + row["y"] * vector["y_end"]) / vector_norm
                brand_projection_rows.append(
                    {
                        "brand": str(label),
                        "projection": round(float(projection_value), 4),
                    }
                )
            brand_projection_rows.sort(key=lambda item: item["projection"], reverse=True)
            projection_summary.append(
                {
                    "attribute": vector["attribute"],
                    "axis": vector["axis"],
                    "feature": vector["label"],
                    "ideal_projection": round(float(ideal_projection), 4),
                    "leading_brand": brand_projection_rows[0]["brand"],
                    "leading_projection": brand_projection_rows[0]["projection"],
                    "brand_rankings": brand_projection_rows,
                }
            )
        projection_summary.sort(key=lambda item: item["ideal_projection"], reverse=True)
        projection_interpretation = {
            "status": "defined",
            "method": "factor_analysis",
            "rule": (
                "Brand performance is interpreted by projecting brand points onto feature-level salience/valence "
                "vectors from the origin; ideal-point projection indicates relative importance."
            ),
            "attribute_projection_summary": projection_summary,
            "importance_interpretation": (
                "Higher ideal-point projection values imply higher relative importance for that attribute axis."
            ),
        }
    else:
        projection_interpretation = {
            "status": "not_available",
            "method": positioning_method_used,
            "reason": (
                "Attribute vectors are not defined in this MDS run because the input is similarity-based "
                "rather than feature-vector based."
            ),
            "attribute_projection_summary": [],
            "importance_interpretation": "",
        }

    score_matrix = brand_matrix.to_numpy(dtype=float)
    if score_matrix.shape[0] > 1 and score_matrix.shape[1] > 1:
        item_variances = score_matrix.var(axis=0, ddof=1)
        total_scores = score_matrix.sum(axis=1)
        total_variance = total_scores.var(ddof=1)
        if total_variance > 0:
            cronbach_alpha = (
                (score_matrix.shape[1] / (score_matrix.shape[1] - 1))
                * (1 - (item_variances.sum() / total_variance))
            )
            reliability_analysis = {
                "status": "defined",
                "method": "cronbach_alpha",
                "cronbach_alpha": round(float(cronbach_alpha), 4),
                "note": "Interpret with caution because the scorecard uses aggregated dual-axis artifact inputs.",
            }
        else:
            reliability_analysis = {
                "status": "not_available",
                "method": "cronbach_alpha",
                "cronbach_alpha": None,
                "note": "Total score variance is zero, so reliability cannot be estimated.",
            }
    else:
        reliability_analysis = {
            "status": "not_available",
            "method": "cronbach_alpha",
            "cronbach_alpha": None,
            "note": "At least two brands and two features are required for reliability estimation.",
        }

    mean_gap_to_ideal = round(
        float(sum(item["gap_to_ideal"] for item in feature_benchmarks) / len(feature_benchmarks)),
        4,
    )
    validity_analysis = {
        "status": "defined",
        "method": "ideal_point_alignment_proxy",
        "average_gap_to_ideal": mean_gap_to_ideal,
        "attribute_vector_status": "defined" if vector_rows else "not_defined",
        "note": "Lower average gap suggests the scorecard captures features that align with the segment ideal.",
    }

    highest_scoring_attributes = sorted(
        feature_benchmarks,
        key=lambda item: item["leader_score"],
        reverse=True,
    )
    lowest_scoring_attributes = sorted(
        feature_benchmarks,
        key=lambda item: item["leader_score"],
    )

    axis_contribution_summary = {
        "salience_top_features": _top_axis_features(feature_benchmarks, "salience", reverse=True),
        "valence_top_features": _top_axis_features(feature_benchmarks, "valence", reverse=True),
        "salience_low_features": _top_axis_features(feature_benchmarks, "salience", reverse=False),
        "valence_low_features": _top_axis_features(feature_benchmarks, "valence", reverse=False),
    }

    diagnostics = {
        "attribute_vectors_not_defined": attribute_vectors_not_defined,
        "key_factor_assessment": feature_benchmarks,
        "benchmark_analysis": {
            "closest_to_ideal": nearest["brand"],
            "distance_to_ideal": nearest["distance_to_ideal"],
            "attribute_leaders": feature_benchmarks,
        },
        "ideal_point_analysis": brand_distance_table,
        "competition_landscape": competition_landscape,
        "pod_pop": {"pod": pod, "pop": pop},
        "strategy_matrix": strategy_matrix,
        "projection_interpretation": projection_interpretation,
        "axis_contribution_summary": axis_contribution_summary,
    }
    interpretation = (
        f"{nearest['brand']} is closest to the ideal point on the combined salience and valence map. "
        "Distance between brand points indicates competitive crowding, while feature vectors indicate which "
        "attribute-axis combinations pull brands toward the ideal."
    )

    scorecard_rows = [
        {
            "brand": str(record["brand"]),
            "attribute": str(record["attribute"]),
            "axis": str(record["axis"]),
            "feature": str(record["feature"]),
            "score": float(record["score"]),
            "point_type": "brand",
        }
        for record in scorecard.to_dict("records")
    ]
    for feature, score in ideal_series.items():
        meta = feature_meta[str(feature)]
        scorecard_rows.append(
            {
                "brand": str(ideal_point["label"]),
                "attribute": meta["attribute"],
                "axis": meta["axis"],
                "feature": str(feature),
                "score": float(score),
                "point_type": "ideal",
            }
        )

    return {
        "positioning_scorecard": scorecard_rows,
        "dynamic_scorecard_summary": {
            "brand_count": int(len(brand_matrix)),
            "feature_count": int(len(shared_columns)),
            "highest_scoring_attributes": highest_scoring_attributes,
            "lowest_scoring_attributes": lowest_scoring_attributes,
            "ideal_point_distance_summary": brand_distance_table,
            "importance_performance_gap": feature_benchmarks,
            "reliability_analysis": reliability_analysis,
            "validity_analysis": validity_analysis,
            "axis_contribution_summary": axis_contribution_summary,
        },
        "positioning_method_used": positioning_method_used,
        "perceptual_map_figure": figure_path.name,
        "perceptual_map_coordinate_table": coordinate_rows,
        "perceptual_map_vector_table": vector_rows,
        "perceptual_map_method": perceptual_map_method,
        "perceptual_map_interpretation": interpretation,
        "projection_interpretation": projection_interpretation,
        "positioning_diagnostics": diagnostics,
        "strategy_matrix": strategy_matrix,
    }
