from __future__ import annotations

from typing import Any

from .io import read_json, require_files


def load_segmentation_inputs(artifact_paths: list) -> tuple[dict[str, Any], Any] | None:
    import pandas as pd

    located = require_files(artifact_paths, ["review_foundation.json", "segmentation_variables.csv"])
    if located is None:
        return None
    foundation = read_json(located["review_foundation.json"])
    frame = pd.read_csv(located["segmentation_variables.csv"])
    return foundation, frame


def _classify_segment_variables(columns: list[str], foundation: dict[str, Any]) -> dict[str, list[str]]:
    catalog_columns = {
        str(item.get("column"))
        for item in foundation.get("dimension_catalog", [])
        if isinstance(item, dict) and item.get("column")
    }
    taxonomy = {
        "geographic": [],
        "demographic": [],
        "psychographic": [],
        "behavioral": [],
    }
    for column in columns:
        lowered = column.lower()
        if lowered in {"unit_id", "customer_id"}:
            continue
        if column in catalog_columns:
            taxonomy["psychographic"].append(column)
        elif any(token in lowered for token in ["region", "country", "city", "market", "geo"]):
            taxonomy["geographic"].append(column)
        elif any(token in lowered for token in ["age", "gender", "income", "occupation", "family"]):
            taxonomy["demographic"].append(column)
        else:
            taxonomy["behavioral"].append(column)
    return taxonomy


def _pick_identifier_column(frame: Any) -> str | None:
    for candidate in ["unit_id", "customer_id"]:
        if candidate in frame.columns:
            return candidate
    for column in frame.columns:
        if column.endswith("_id"):
            return column
    return None


def run_segmentation(foundation: dict[str, Any], frame: Any) -> dict[str, Any]:
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.compose import ColumnTransformer
    from sklearn.decomposition import FactorAnalysis
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    identifier_column = _pick_identifier_column(frame)
    excluded_columns = {identifier_column} if identifier_column else set()
    feature_columns = [column for column in frame.columns if column not in excluded_columns]
    numeric_columns = frame[feature_columns].select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = [column for column in feature_columns if column not in numeric_columns]

    transformers = []
    if numeric_columns:
        transformers.append(("numeric", StandardScaler(), numeric_columns))
    if categorical_columns:
        transformers.append(
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_columns)
        )
    if not transformers:
        raise SystemExit("segmentation_variables.csv must contain at least one usable feature column.")

    transformer = ColumnTransformer(transformers=transformers)
    encoded = transformer.fit_transform(frame[feature_columns])
    if hasattr(encoded, "toarray"):
        encoded = encoded.toarray()

    if encoded.shape[1] > 1 and len(frame) > 2:
        n_components = max(1, min(2, encoded.shape[1], len(frame) - 1))
        factor_scores = FactorAnalysis(n_components=n_components, random_state=42).fit_transform(encoded)
    else:
        factor_scores = encoded

    cluster_threshold = 0.05
    initial_k = min(6, max(2, len(frame) // 12))
    best_labels = None
    selected_k = initial_k
    reruns_performed = 0

    for clusters in range(initial_k, 1, -1):
        model = KMeans(n_clusters=clusters, random_state=42, n_init=10)
        labels = model.fit_predict(factor_scores)
        counts = pd.Series(labels).value_counts(normalize=True)
        if bool((counts > cluster_threshold).all()):
            best_labels = labels
            selected_k = clusters
            break
        reruns_performed += 1
        if best_labels is None:
            best_labels = labels
            selected_k = clusters

    if best_labels is None:
        raise SystemExit("Segmentation could not produce cluster labels.")

    segmented = frame.copy()
    segmented["cluster"] = [f"segment_{int(label)}" for label in best_labels]
    counts = segmented["cluster"].value_counts().sort_index()
    shares = (counts / counts.sum()).to_dict()

    segment_profiles: list[dict[str, Any]] = []
    for cluster in counts.index:
        subset = segmented[segmented["cluster"] == cluster]
        numeric_summary = {
            column: round(float(pd.to_numeric(subset[column]).mean()), 4)
            for column in numeric_columns
        }
        categorical_summary = {}
        for column in categorical_columns:
            mode = subset[column].mode()
            categorical_summary[column] = str(mode.iloc[0]) if not mode.empty else ""
        top_numeric = sorted(numeric_summary.items(), key=lambda item: item[1], reverse=True)[:2]
        dominant_context = next(iter(categorical_summary.values()), "mixed")
        persona = (
            f"{dominant_context or 'mixed'} users prioritize "
            f"{', '.join(name for name, _ in top_numeric) or 'multiple factors'}."
        )
        segment_profiles.append(
            {
                "cluster": cluster,
                "sample_size": int(len(subset)),
                "share": round(float(shares[cluster]), 4),
                "numeric_summary": numeric_summary,
                "categorical_summary": categorical_summary,
                "persona": persona,
            }
        )

    cluster_share_table = [
        {"cluster": profile["cluster"], "sample_size": profile["sample_size"], "share": profile["share"]}
        for profile in segment_profiles
    ]
    consumer_portrait_narrative = "; ".join(
        f"{profile['cluster']} reflects {profile['persona']}" for profile in segment_profiles
    )

    segment_assignments = []
    if identifier_column:
        segment_assignments = [
            {identifier_column: row[identifier_column], "cluster": row["cluster"]}
            for row in segmented[[identifier_column, "cluster"]].to_dict("records")
        ]

    return {
        "cluster_selection": {
            "initial_k": int(initial_k),
            "selected_k": int(selected_k),
            "final_k": int(selected_k),
            "cluster_threshold": cluster_threshold,
            "reruns_performed": int(reruns_performed),
            "method": "factor_analysis -> kmeans",
            "all_clusters_above_threshold": bool(all(item["share"] > 0.05 for item in segment_profiles)),
        },
        "segment_profiles": segment_profiles,
        "segment_variable_table": _classify_segment_variables(feature_columns, foundation),
        "cluster_share_table": cluster_share_table,
        "consumer_portrait_narrative": consumer_portrait_narrative,
        "segment_assignments": segment_assignments,
        "people_insights": foundation.get("people_insights", []),
        "product_triggers": foundation.get("product_triggers", []),
        "context_scenarios": foundation.get("context_scenarios", []),
        "system1_system2_split": foundation.get("system1_system2_split", {}),
        "maslow_keywords": foundation.get("maslow_keywords", {}),
        "review_foundation": foundation,
    }


def build_segment_summary(segmentation: dict[str, Any]) -> str:
    lines = [
        "# Segmentation Summary",
        "",
        "## Review Foundation",
        f"- People insights: {', '.join(segmentation.get('people_insights', [])) or 'none'}",
        f"- Product triggers: {', '.join(segmentation.get('product_triggers', [])) or 'none'}",
        f"- Context scenarios: {', '.join(segmentation.get('context_scenarios', [])) or 'none'}",
        (
            "- System 1 triggers: "
            + ", ".join(segmentation.get("system1_system2_split", {}).get("system1", []))
        ),
        (
            "- System 2 triggers: "
            + ", ".join(segmentation.get("system1_system2_split", {}).get("system2", []))
        ),
        (
            "- Maslow keywords: "
            + ", ".join(
                f"{need}={'/'.join(words)}"
                for need, words in segmentation.get("maslow_keywords", {}).items()
            )
        ),
        "",
        "## Cluster Share Table",
    ]
    for row in segmentation["cluster_share_table"]:
        lines.append(f"- {row['cluster']}: {row['sample_size']} units, share={row['share']:.2%}")
    lines.extend(["", "## Segment Variable Table"])
    for category, variables in segmentation["segment_variable_table"].items():
        lines.append(f"- {category}: {', '.join(variables) if variables else 'none'}")
    lines.extend(["", "## Segment Personas"])
    for profile in segmentation["segment_profiles"]:
        lines.append(f"- {profile['cluster']}: {profile['persona']}")
    lines.extend(["", "## Consumer Portrait Narrative", f"- {segmentation['consumer_portrait_narrative']}"])
    return "\n".join(lines) + "\n"
