from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .io import write_json


THEORY_DETAILS = {
    "product_positioning": {
        "name": "Product Positioning Theory",
        "description": "Used to explain how attributes shape brand meaning and perceived differentiation.",
    },
    "purchase_motivation": {
        "name": "Purchase Motivation Theory",
        "description": "Used to explain which needs and decision drivers are pushing the purchase.",
    },
    "wom_motivation": {
        "name": "Word-of-Mouth Motivation Theory",
        "description": "Used to interpret why reviewers share experiences and recommendations.",
    },
    "dual_process": {
        "name": "System 1 / System 2",
        "description": "Used to separate intuitive reactions from deliberate evaluation.",
    },
    "maslow": {
        "name": "Maslow's Hierarchy of Needs",
        "description": "Used to interpret whether reviews reflect safety, social belonging, esteem, or other need layers.",
    },
}
THEORY_TAXONOMY = {
    "product_positioning": [
        "attributes",
        "functions",
        "benefits",
        "usage_context_service_experience",
    ],
    "purchase_motivation": [
        "functional",
        "security",
        "relational",
    ],
    "wom_motivation": [
        "altruistic",
        "social_identity",
        "self_enhancement",
        "emotional_expression",
    ],
    "dual_process": [
        "system1",
        "system2",
    ],
    "maslow": [
        "physiological",
        "safety",
        "social",
        "esteem",
        "self_actualization",
    ],
}
LEGACY_TAG_MAP = {
    "product_positioning": [("product_positioning", "benefits")],
    "purchase_motivation": [("purchase_motivation", "functional")],
    "wom_motivation": [("wom_motivation", "social_identity")],
    "system1": [("dual_process", "system1")],
    "system2": [("dual_process", "system2")],
    "physiological": [("maslow", "physiological")],
    "safety": [("maslow", "safety")],
    "social": [("maslow", "social")],
    "belonging": [("maslow", "social")],
    "esteem": [("maslow", "esteem")],
    "self_actualization": [("maslow", "self_actualization")],
}


def _catalog_lookup(foundation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("column")): item
        for item in foundation.get("dimension_catalog", [])
        if isinstance(item, dict) and item.get("column")
    }


def _base_column_lookup(foundation: dict[str, Any]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for item in foundation.get("dimension_catalog", []):
        if not isinstance(item, dict):
            continue
        column = str(item.get("column", ""))
        if not column:
            continue
        lookup[column] = column
        salience_column = str(item.get("salience_column", ""))
        valence_column = str(item.get("valence_column", ""))
        if salience_column:
            lookup[salience_column] = column
        if valence_column:
            lookup[valence_column] = column
    return lookup


def _axis_for_column(foundation: dict[str, Any], column: str) -> str:
    for item in foundation.get("dimension_catalog", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("salience_column", "")) == str(column):
            return "salience"
        if str(item.get("valence_column", "")) == str(column):
            return "valence"
    if str(column).endswith("_salience"):
        return "salience"
    if str(column).endswith("_valence"):
        return "valence"
    return "mixed"


def _normalize_to_base_columns(foundation: dict[str, Any], columns: list[str]) -> list[str]:
    lookup = _base_column_lookup(foundation)
    normalized = [lookup.get(str(column), str(column)) for column in columns]
    return list(dict.fromkeys(normalized))


def _item_bundle(*items: tuple[str, str]) -> list[dict[str, str]]:
    return [{"name": name, "description": description} for name, description in items]


def _titleize(token: str) -> str:
    return str(token).replace("_", " ").title()


def _subtheory_label(family: str, subtheory: str) -> str:
    family_labels = {
        "product_positioning": "Product Positioning",
        "purchase_motivation": "Purchase Motivation",
        "wom_motivation": "WOM Motivation",
        "dual_process": "Dual Process",
        "maslow": "Maslow",
    }
    return f"{family_labels.get(family, _titleize(family))} > {_titleize(subtheory)}"


def _dedupe_named_rows(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        identity = tuple(str(row.get(key, "")) for key in keys)
        if identity in seen:
            continue
        seen.add(identity)
        deduped.append(row)
    return deduped


def _theory_entries_for_item(item: dict[str, Any], supporting_label: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    theory_annotations = item.get("theory_annotations", {})
    if isinstance(theory_annotations, dict) and theory_annotations:
        for family, subtheories in theory_annotations.items():
            family_name = str(family)
            if not isinstance(subtheories, list):
                continue
            for subtheory in subtheories:
                subtheory_name = str(subtheory)
                entries.append(
                    {
                        "family": family_name,
                        "subtheory": subtheory_name,
                        "label": _subtheory_label(family_name, subtheory_name),
                        "source": "annotated",
                        "supporting_item": supporting_label,
                    }
                )
    elif isinstance(item.get("theory_tags"), list):
        for tag in item.get("theory_tags", []):
            for family_name, subtheory_name in LEGACY_TAG_MAP.get(str(tag), []):
                entries.append(
                    {
                        "family": family_name,
                        "subtheory": subtheory_name,
                        "label": _subtheory_label(family_name, subtheory_name),
                        "source": "legacy_inference",
                        "supporting_item": supporting_label,
                    }
                )
    return _dedupe_named_rows(entries, ("family", "subtheory", "source", "supporting_item"))


def _overlay_theory_entries(foundation: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    system_split = foundation.get("system1_system2_split", {})
    if isinstance(system_split, dict):
        for subtheory in ["system1", "system2"]:
            values = system_split.get(subtheory)
            if isinstance(values, list) and values:
                entries.append(
                    {
                        "family": "dual_process",
                        "subtheory": subtheory,
                        "label": _subtheory_label("dual_process", subtheory),
                        "source": "overlay",
                        "supporting_item": "system1_system2_split",
                    }
                )
    maslow_keywords = foundation.get("maslow_keywords", {})
    if isinstance(maslow_keywords, dict):
        for key, values in maslow_keywords.items():
            subtheory = "social" if str(key) == "belonging" else str(key)
            if subtheory in THEORY_TAXONOMY["maslow"] and isinstance(values, list) and values:
                entries.append(
                    {
                        "family": "maslow",
                        "subtheory": subtheory,
                        "label": _subtheory_label("maslow", subtheory),
                        "source": "overlay",
                        "supporting_item": "maslow_keywords",
                    }
                )
    return _dedupe_named_rows(entries, ("family", "subtheory", "source", "supporting_item"))


def _theory_entries_for_columns(
    foundation: dict[str, Any],
    columns: list[str],
    include_segmentation_overlays: bool = False,
) -> list[dict[str, str]]:
    catalog = _catalog_lookup(foundation)
    entries: list[dict[str, str]] = []
    for column in _normalize_to_base_columns(foundation, columns):
        item = catalog.get(column)
        if not isinstance(item, dict):
            continue
        entries.extend(_theory_entries_for_item(item, _format_label(column, catalog)))
    if include_segmentation_overlays:
        entries.extend(_overlay_theory_entries(foundation))
    return _dedupe_named_rows(entries, ("family", "subtheory", "source", "supporting_item"))


def _family_status(entries: list[dict[str, str]], covered_subtheories: list[str]) -> str:
    if not covered_subtheories:
        return "not_evidenced"
    sources = {str(entry.get("source", "")) for entry in entries}
    if sources == {"legacy_inference"}:
        return "legacy_inferred"
    if "legacy_inference" in sources:
        return "mixed"
    return "covered"


def build_attribute_extraction_summary_contract(
    foundation: dict[str, Any] | None,
    attribute_catalog: Any | None,
) -> dict[str, Any] | None:
    if not isinstance(foundation, dict):
        return None
    rows: list[dict[str, Any]] = []
    if hasattr(attribute_catalog, "to_dict"):
        rows = attribute_catalog.to_dict("records")
    elif isinstance(attribute_catalog, list):
        rows = [row for row in attribute_catalog if isinstance(row, dict)]

    extraction_summary = foundation.get("attribute_extraction_summary", {})
    if not isinstance(extraction_summary, dict):
        extraction_summary = {}

    theme_counter: dict[str, int] = {}
    group_counter: dict[str, int] = {}
    representative_attributes: list[dict[str, Any]] = []
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            -int(float(row.get("mention_count", 0) or 0)),
            str(row.get("label", "")),
        ),
    )
    for row in rows:
        theme = str(row.get("theme", "")).strip()
        if theme:
            theme_counter[theme] = theme_counter.get(theme, 0) + 1
        attribute_group = str(row.get("attribute_group", "")).strip()
        if attribute_group:
            group_counter[attribute_group] = group_counter.get(attribute_group, 0) + 1
    for row in sorted_rows[:5]:
        representative_attributes.append(
            {
                "attribute_key": str(row.get("attribute_key", "")),
                "label": str(row.get("label", "")),
                "theme": str(row.get("theme", "")),
                "attribute_group": str(row.get("attribute_group", "")),
                "mention_count": int(float(row.get("mention_count", 0) or 0)),
                "example_review_id": str(row.get("example_review_id", "")),
                "example_quote": str(row.get("example_quote", "")),
            }
        )
    actual_count = int(extraction_summary.get("actual_count", len(rows) or len(foundation.get("dimension_catalog", []))))
    return {
        "target_minimum": int(extraction_summary.get("target_minimum", 30)),
        "actual_count": actual_count,
        "shortfall_reason": str(extraction_summary.get("shortfall_reason", "")),
        "themes_discovered": sorted(theme_counter.keys()),
        "attribute_group_summary": [
            {"attribute_group": group, "attribute_count": count}
            for group, count in sorted(group_counter.items())
        ],
        "representative_attributes": representative_attributes,
    }


def _themes_for_columns(
    foundation: dict[str, Any],
    columns: list[str],
) -> list[dict[str, Any]]:
    catalog = _catalog_lookup(foundation)
    by_theme: dict[str, list[str]] = {}
    for column in _normalize_to_base_columns(foundation, columns):
        item = catalog.get(column)
        if not isinstance(item, dict):
            continue
        theme = str(item.get("theme", "")).strip()
        if not theme:
            continue
        by_theme.setdefault(theme, []).append(_format_label(column, catalog))
    return [
        {
            "theme": theme,
            "supporting_items": list(dict.fromkeys(labels)),
        }
        for theme, labels in by_theme.items()
    ]


def _theory_coverage_summary(
    foundation: dict[str, Any],
    columns: list[str],
    *,
    include_segmentation_overlays: bool = False,
) -> list[dict[str, Any]]:
    entries = _theory_entries_for_columns(
        foundation,
        columns,
        include_segmentation_overlays=include_segmentation_overlays,
    )
    summary: list[dict[str, Any]] = []
    for family, subtheories in THEORY_TAXONOMY.items():
        family_entries = [entry for entry in entries if entry.get("family") == family]
        covered = list(
            dict.fromkeys(str(entry.get("subtheory", "")) for entry in family_entries if entry.get("subtheory"))
        )
        supporting_items = list(
            dict.fromkeys(str(entry.get("supporting_item", "")) for entry in family_entries if entry.get("supporting_item"))
        )
        summary.append(
            {
                "theory_family": THEORY_DETAILS[family]["name"],
                "covered_subtheories": [_subtheory_label(family, subtheory) for subtheory in covered],
                "not_evidenced_subtheories": [
                    _subtheory_label(family, subtheory)
                    for subtheory in subtheories
                    if subtheory not in covered
                ],
                "supporting_items": supporting_items,
                "evidence_status": _family_status(family_entries, covered),
            }
        )
    return summary


def _theme_coverage_summary(
    foundation: dict[str, Any],
    findings: list[dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    finding_ids_by_theme: dict[str, list[str]] = {}
    for finding in findings:
        for theme_entry in finding.get("themes_used", []):
            theme_name = str(theme_entry.get("theme", ""))
            if not theme_name:
                continue
            finding_ids_by_theme.setdefault(theme_name, []).append(str(finding.get("finding_id", "")))

    summary: list[dict[str, Any]] = []
    for theme_name, columns in foundation.get("theme_mapping", {}).items():
        labels = [_format_label(str(column), catalog) for column in columns]
        related_findings = list(dict.fromkeys(finding_ids_by_theme.get(str(theme_name), [])))
        summary.append(
            {
                "theme": str(theme_name),
                "supporting_items": labels,
                "related_findings": related_findings,
                "evidence_status": "covered" if related_findings else "not_evidenced",
            }
        )
    return summary


def _columns_for_stage(
    foundation: dict[str, Any],
    stage: str,
    stage_summary: dict[str, Any],
) -> list[str]:
    role_map: dict[str, list[str]] = {}
    for item in foundation.get("dimension_catalog", []):
        if not isinstance(item, dict):
            continue
        salience_column = str(item.get("salience_column", ""))
        valence_column = str(item.get("valence_column", ""))
        expanded_columns = [column for column in [salience_column, valence_column] if column]
        if not expanded_columns:
            column = str(item.get("column", ""))
            expanded_columns = [column] if column else []
        for role in item.get("stat_roles", []):
            role_map.setdefault(str(role), []).extend(expanded_columns)

    if stage == "segmentation":
        return list(dict.fromkeys(role_map.get("segmentation", [])))
    if stage == "targeting":
        return list(
            dict.fromkeys(
                role_map.get("current_target", [])
                + role_map.get("potential_target", [])
                + role_map.get("comparison_axis", [])
            )
        )
    if stage == "positioning":
        columns = [
            str(row.get("feature") or row.get("attribute"))
            for row in stage_summary.get("positioning_scorecard", [])
            if row.get("point_type") == "brand" and (row.get("feature") or row.get("attribute"))
        ]
        if columns:
            return list(dict.fromkeys(columns))
        return list(dict.fromkeys(role_map.get("positioning", [])))
    return []


def _theories_for_columns(
    foundation: dict[str, Any],
    columns: list[str],
    include_segmentation_overlays: bool = False,
) -> list[dict[str, str]]:
    entries = _theory_entries_for_columns(
        foundation,
        columns,
        include_segmentation_overlays=include_segmentation_overlays,
    )
    unique_keys = list(
        dict.fromkeys(str(entry.get("family", "")) for entry in entries if entry.get("family"))
    )
    return [THEORY_DETAILS[key] for key in unique_keys if key in THEORY_DETAILS]


def _fallback_theories(stage: str) -> list[dict[str, str]]:
    labels = {
        "segmentation": "Segmentation Theory Metadata",
        "targeting": "Targeting Theory Metadata",
        "positioning": "Positioning Theory Metadata",
    }
    return [
        {
            "name": labels[stage],
            "description": "Theory tags were not available for this rerun, so only the statistical method could be resolved from the artifacts.",
        }
    ]


def _quote_candidates(
    score_table: Any,
    relevant_columns: list[str],
    catalog: dict[str, dict[str, Any]],
    foundation: dict[str, Any],
    unit_cluster_map: dict[str, str] | None = None,
    selected_cluster: str | None = None,
    selected_brand: str | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    import pandas as pd

    if score_table is None or score_table.empty:
        return []
    relevant_columns = [column for column in relevant_columns if column in score_table.columns]
    if not relevant_columns:
        return []
    base_lookup = _base_column_lookup(foundation)

    frame = score_table.copy()
    if unit_cluster_map:
        frame["cluster"] = frame["unit_id"].astype(str).map(unit_cluster_map)
    if selected_cluster:
        cluster_series = frame.get("cluster")
        if cluster_series is not None:
            filtered = frame[cluster_series == selected_cluster]
            if not filtered.empty:
                frame = filtered
    if selected_brand and "brand" in frame.columns:
        filtered = frame[frame["brand"].astype(str) == selected_brand]
        if not filtered.empty:
            frame = filtered

    score_matrix = frame[relevant_columns].apply(pd.to_numeric, errors="coerce")
    frame = frame.assign(_relevance=score_matrix.mean(axis=1))
    frame = frame.sort_values("_relevance", ascending=False)

    quotes: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        review_text = str(row.get("review_text", "")).strip()
        if not review_text:
            continue
        linked_columns = []
        for column in relevant_columns:
            value = row.get(column)
            if value is None:
                continue
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue
            if numeric_value >= 5:
                linked_columns.append(column)
        if not linked_columns:
            def _score_for_sort(current: str) -> float:
                try:
                    value = row.get(current)
                    if value is None:
                        return 0.0
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0

            top_columns = sorted(
                relevant_columns,
                key=_score_for_sort,
                reverse=True,
            )
            linked_columns = top_columns[:2]
        linked_items = []
        for column in linked_columns:
            base_column = base_lookup.get(column, column)
            label = str(catalog.get(base_column, {}).get("label", base_column))
            axis = _axis_for_column(foundation, column)
            linked_items.append(f"{label} ({_titleize(axis)})" if axis != "mixed" else label)
        if not linked_items:
            normalized_relevant = [
                base_lookup.get(column, column)
                for column in relevant_columns[:2]
            ]
            linked_items = [
                str(catalog.get(column, {}).get("label", column))
                for column in normalized_relevant
            ] or ["review evidence"]
        quotes.append(
            {
                "review_id": str(row["review_id"]),
                "quote_text": review_text,
                "why_this_quote_matters": "This review strongly reflects " + ", ".join(linked_items) + ".",
                "linked_items": linked_items,
            }
        )
        if len(quotes) >= limit:
            break
    return quotes[:limit]


def _merge_quotes(*quote_lists: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for quote_list in quote_lists:
        for quote in quote_list:
            review_id = str(quote.get("review_id", ""))
            if review_id and review_id not in seen:
                seen.add(review_id)
                merged.append(quote)
    return merged


def _stage_methods(stage: str, positioning_method: str | None = None) -> list[dict[str, str]]:
    if stage == "segmentation":
        return [
            {"name": "Factor Analysis", "description": "Reduces many scored items into a smaller set of shared patterns."},
            {"name": "K-Means Clustering", "description": "Groups similar reviewers or units into segments based on those patterns."},
            {"name": "Cluster Size Guardrail", "description": "Re-runs clustering if any segment is too small to trust."},
        ]
    if stage == "targeting":
        return [
            {"name": "ANOVA / Regression", "description": "Tests whether clusters differ on continuous outcomes and how strongly cluster membership explains them."},
            {"name": "Chi-Square / Logistic Regression", "description": "Tests whether clusters differ on binary outcomes or conversion-like behaviors."},
            {"name": "Tukey HSD", "description": "Shows which specific clusters differ when the overall ANOVA is significant."},
        ]
    method_name = "Factor Analysis" if positioning_method != "mds" else "Multidimensional Scaling"
    method_description = (
        "Maps brand and ideal-point relationships using attribute structure."
        if positioning_method != "mds"
        else "Maps brand similarity distances when only similarity structure is available."
    )
    return [
        {"name": method_name, "description": method_description},
        {"name": "Ideal-Point Distance", "description": "Shows which brand is closest to the desired market ideal."},
        {"name": "Reliability / Validity Checks", "description": "Checks whether the scorecard behaves coherently as an analytical tool."},
    ]


def _what_this_section_is_doing(stage: str) -> str:
    messages = {
        "segmentation": "Finding distinct reviewer or customer groups based on shared score patterns.",
        "targeting": "Comparing segments to decide which audience should be prioritized, watched, or deprioritized.",
        "positioning": "Comparing brands against ideal expectations to clarify competitive position and strategic gaps.",
    }
    return messages[stage]


def _plain_language_explanation(stage: str, stage_summary: dict[str, Any]) -> str:
    if stage == "segmentation":
        return "This section groups similar review patterns together so you can see different customer mindsets instead of one average customer."
    if stage == "targeting":
        selected_cluster = stage_summary.get("target_selection_decision", {}).get("selected_cluster", "the top segment")
        return f"This section checks which segment is most attractive to prioritize. Right now {selected_cluster} stands out on the most important scoring dimensions."
    closest_brand = stage_summary.get("positioning_diagnostics", {}).get("benchmark_analysis", {}).get("closest_to_ideal", "the leading brand")
    return f"This section shows how close each brand is to the ideal customer expectation. Right now {closest_brand} is nearest to that ideal."


def _format_label(column: str, catalog: dict[str, dict[str, Any]]) -> str:
    return str(catalog.get(column, {}).get("label", column))


def _format_feature_label(
    foundation: dict[str, Any],
    column: str,
    catalog: dict[str, dict[str, Any]],
) -> str:
    base_column = _base_column_lookup(foundation).get(str(column), str(column))
    label = _format_label(base_column, catalog)
    axis = _axis_for_column(foundation, column)
    return f"{label} ({_titleize(axis)})" if axis != "mixed" else label


def _format_maslow_name(name: str) -> str:
    return str(name).replace("_", " ")


def _stage_input_artifacts(stage: str) -> list[str]:
    if stage == "segmentation":
        return ["review_foundation.json", "attribute_catalog.csv", "segmentation_variables.csv"]
    if stage == "targeting":
        return ["review_foundation.json", "attribute_catalog.csv", "targeting_dataset.csv", "segment_profiles.json", "analysis_context.json"]
    return ["review_foundation.json", "attribute_catalog.csv", "positioning_scorecard.csv", "brands.json", "ideal_point.json"]


def _build_reproducibility(
    input_artifacts: list[str],
    input_columns: list[str],
    filters: list[str],
    preprocessing: list[str],
    analysis_steps: list[str],
    decision_rule: str,
) -> dict[str, Any]:
    return {
        "input_artifacts": input_artifacts,
        "input_columns": input_columns,
        "filters": filters,
        "preprocessing": preprocessing,
        "analysis_steps": analysis_steps,
        "decision_rule": decision_rule,
    }


def _build_statistical_results(
    method_family: str,
    test_or_model: str,
    sample_size: Any,
    statistic: Any,
    result_direction: str,
    degrees_of_freedom: Any = None,
    p_value: Any = None,
    effect_size: Any = None,
    coefficient: Any = None,
    confidence_interval: Any = None,
    axis_breakdown: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "method_family": method_family,
        "test_or_model": test_or_model,
        "sample_size": sample_size,
        "statistic": statistic,
        "degrees_of_freedom": degrees_of_freedom,
        "p_value": p_value,
        "effect_size": effect_size,
        "coefficient": coefficient,
        "confidence_interval": confidence_interval,
        "result_direction": result_direction,
        "axis_breakdown": axis_breakdown or {"salience": None, "valence": None},
    }


def _build_finding(
    finding_id: str,
    finding_statement: str,
    business_implication: str,
    methods_used: list[dict[str, str]],
    theories_used: list[dict[str, str]],
    reproducibility: dict[str, Any],
    statistical_results: dict[str, Any],
    plain_language_explanation: str,
    evidence_quotes: list[dict[str, Any]],
    axes_used: str = "mixed",
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "finding_statement": finding_statement,
        "business_implication": business_implication,
        "methods_used": methods_used,
        "theories_used": theories_used,
        "axes_used": axes_used,
        "reproducibility": reproducibility,
        "statistical_results": statistical_results,
        "plain_language_explanation": plain_language_explanation,
        "evidence_quotes": evidence_quotes,
    }


def _axes_used_for_columns(foundation: dict[str, Any], columns: list[str]) -> str:
    axes = {
        _axis_for_column(foundation, column)
        for column in columns
        if _axis_for_column(foundation, column) in {"salience", "valence"}
    }
    if axes == {"salience"}:
        return "salience"
    if axes == {"valence"}:
        return "valence"
    return "mixed"


def _axis_modeling_summary(
    foundation: dict[str, Any],
    stage: str,
    relevant_columns: list[str],
    positioning_method: str | None,
) -> dict[str, Any]:
    salience_columns = [column for column in relevant_columns if _axis_for_column(foundation, column) == "salience"]
    valence_columns = [column for column in relevant_columns if _axis_for_column(foundation, column) == "valence"]
    if stage == "segmentation":
        modeling_rule = "Salience and valence columns are standardized separately, then modeled together through factor analysis before K-means clustering."
    elif stage == "targeting":
        modeling_rule = "Salience and valence columns are both tested as candidate drivers; continuous variables flow into ANOVA/regression, and binary variables flow into chi-square/logistic models."
    else:
        map_method = "factor analysis" if positioning_method != "mds" else "MDS"
        modeling_rule = f"Salience and valence columns are combined into one feature matrix for the {map_method} perceptual map and ideal-point distance analysis."
    return {
        "axes_mode": _axes_used_for_columns(foundation, relevant_columns),
        "salience_columns_used": salience_columns,
        "valence_columns_used": valence_columns,
        "modeling_rule": modeling_rule,
        "plain_language_explanation": "Salience captures how much an attribute is mentioned; valence captures how positively or negatively that attribute is evaluated.",
    }


def _axis_breakdown_from_result(
    statistical_results: dict[str, Any],
    axes_used: str,
) -> dict[str, Any]:
    payload = {
        key: value
        for key, value in statistical_results.items()
        if key != "axis_breakdown"
    }
    if axes_used == "salience":
        return {"salience": payload, "valence": None}
    if axes_used == "valence":
        return {"salience": None, "valence": payload}
    return {"salience": payload, "valence": payload}


def _segmentation_sample_size(stage_summary: dict[str, Any], score_table: Any) -> int | None:
    cluster_share_table = stage_summary.get("cluster_share_table", [])
    if cluster_share_table:
        return int(sum(int(row.get("sample_size", 0)) for row in cluster_share_table if isinstance(row, dict)))
    if score_table is not None and "unit_id" in score_table.columns:
        return int(score_table["unit_id"].nunique())
    return None


def _targeting_sample_size(score_table: Any, unit_cluster_map: dict[str, str] | None, stage_summary: dict[str, Any]) -> int | None:
    if unit_cluster_map:
        return len(unit_cluster_map)
    if score_table is not None and "unit_id" in score_table.columns:
        return int(score_table["unit_id"].nunique())
    cluster_table = stage_summary.get("cluster_score_table", [])
    return len(cluster_table) if cluster_table else None


def _positioning_sample_size(stage_summary: dict[str, Any], score_table: Any) -> int | None:
    dynamic_summary = stage_summary.get("dynamic_scorecard_summary", {})
    brand_count = dynamic_summary.get("brand_count")
    if brand_count is not None:
        return int(brand_count)
    if score_table is not None and "brand" in score_table.columns:
        return int(score_table["brand"].nunique())
    return None


def _segmentation_columns_from_summary(stage_summary: dict[str, Any], fallback_columns: list[str]) -> list[str]:
    segment_variable_table = stage_summary.get("segment_variable_table", {})
    columns: list[str] = []
    if isinstance(segment_variable_table, dict):
        for values in segment_variable_table.values():
            if isinstance(values, list):
                columns.extend(str(value) for value in values)
    filtered = [column for column in columns if column and not column.endswith("_id")]
    return list(dict.fromkeys(filtered)) or fallback_columns


def _segmentation_findings(
    stage_summary: dict[str, Any],
    foundation: dict[str, Any],
    score_table: Any,
    catalog: dict[str, dict[str, Any]],
    relevant_columns: list[str],
    unit_cluster_map: dict[str, str] | None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    relevant_columns = _segmentation_columns_from_summary(stage_summary, relevant_columns)
    cluster_share_table = [
        row for row in stage_summary.get("cluster_share_table", []) if isinstance(row, dict)
    ]
    cluster_share_table.sort(key=lambda row: float(row.get("share", 0.0)), reverse=True)
    if not cluster_share_table:
        return findings

    profiles = {
        str(profile.get("cluster")): profile
        for profile in stage_summary.get("segment_profiles", [])
        if isinstance(profile, dict) and profile.get("cluster")
    }
    sample_size = _segmentation_sample_size(stage_summary, score_table)
    cluster_selection = stage_summary.get("cluster_selection", {})
    segment_count = int(cluster_selection.get("final_k") or len(cluster_share_table))
    reruns = int(cluster_selection.get("reruns_performed", 0))
    lead_segment = cluster_share_table[0]
    lead_cluster = str(lead_segment.get("cluster"))
    lead_share = float(lead_segment.get("share", 0.0))

    findings.append(
        _build_finding(
            finding_id="segmentation-cluster-structure",
            finding_statement=f"The review base separates into {segment_count} segments, with {lead_cluster} the largest at {lead_share:.1%} share.",
            business_implication="Do not treat the market as one average audience. Use segment-specific messaging, offers, and channel priorities.",
            methods_used=_item_bundle(
                ("Factor Analysis", "Reduce the scored items into shared latent patterns before clustering."),
                ("K-Means Clustering", "Assign each unit to the nearest segment center in the reduced factor space."),
                ("Cluster Size Guardrail", "Only accept a solution when every segment stays above the 5% minimum share threshold."),
            ),
            theories_used=_theories_for_columns(foundation, relevant_columns, include_segmentation_overlays=True) or _fallback_theories("segmentation"),
            reproducibility=_build_reproducibility(
                input_artifacts=_stage_input_artifacts("segmentation"),
                input_columns=relevant_columns,
                filters=[],
                preprocessing=[
                    "Scale numeric segmentation inputs.",
                    "One-hot encode categorical segmentation inputs when present.",
                    "Reduce encoded variables into factor scores before clustering.",
                ],
                analysis_steps=[
                    "Build factor scores from segmentation_variables.csv.",
                    "Run K-means from the initial k downward until every cluster is above the 5% threshold.",
                    "Assign each unit to the final cluster and compute the cluster share table.",
                ],
                decision_rule="Accept the highest-k solution where every segment share is greater than 5%; otherwise rerun with fewer clusters.",
            ),
            statistical_results=_build_statistical_results(
                method_family="unsupervised_clustering",
                test_or_model="factor_analysis -> kmeans",
                sample_size=sample_size,
                statistic=segment_count,
                effect_size=round(lead_share, 4),
                result_direction=f"{lead_cluster} is the largest segment and the final solution required {reruns} reruns.",
            ),
            plain_language_explanation="There is more than one kind of customer in the review base. The largest group is important, but it should not define the entire market by itself.",
            evidence_quotes=_quote_candidates(
                score_table,
                relevant_columns,
                catalog,
                foundation,
                unit_cluster_map=unit_cluster_map,
                selected_cluster=lead_cluster,
                limit=2,
            ),
        )
    )

    driver_column = ""
    driver_high_cluster = lead_cluster
    driver_low_cluster = lead_cluster
    driver_high_value = 0.0
    driver_low_value = 0.0
    driver_spread = -1.0
    for column in relevant_columns:
        column_values: list[tuple[str, float]] = []
        for cluster_name, profile in profiles.items():
            numeric_summary = profile.get("numeric_summary", {})
            if isinstance(numeric_summary, dict) and column in numeric_summary:
                column_values.append((cluster_name, float(numeric_summary[column])))
        if len(column_values) < 2:
            continue
        highest = max(column_values, key=lambda item: item[1])
        lowest = min(column_values, key=lambda item: item[1])
        spread = highest[1] - lowest[1]
        if spread > driver_spread:
            driver_column = column
            driver_high_cluster = highest[0]
            driver_low_cluster = lowest[0]
            driver_high_value = highest[1]
            driver_low_value = lowest[1]
            driver_spread = spread

    if driver_column:
        driver_label = _format_feature_label(foundation, driver_column, catalog)
        findings.append(
            _build_finding(
                finding_id="segmentation-key-driver",
                finding_statement=f"{driver_label} is the clearest segmentation driver: {driver_high_cluster} scores {driver_high_value:.2f} versus {driver_low_cluster} at {driver_low_value:.2f}.",
                business_implication=f"Use {driver_label} as a primary split in messaging, offer framing, and creative testing.",
                methods_used=_item_bundle(
                    ("Cluster Profile Comparison", "Compare cluster-level mean scores to identify the variables with the widest spread between segments."),
                    ("K-Means Clustering", "Use the final cluster assignments as the basis for profile comparison."),
                ),
                theories_used=_theories_for_columns(foundation, [driver_column]) or _fallback_theories("segmentation"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("segmentation"),
                    input_columns=[driver_column],
                    filters=[],
                    preprocessing=[
                        "Aggregate scored review items to the unit level before clustering.",
                        "Carry the final cluster assignment into cluster-level profile means.",
                    ],
                    analysis_steps=[
                        "Read numeric_summary values from each segment profile.",
                        "Compute the max-minus-min spread for each scored item across clusters.",
                        "Choose the item with the largest spread as the strongest segmentation driver.",
                    ],
                    decision_rule="Treat the scored item with the largest between-cluster spread as the strongest practical segmentation driver.",
                ),
                statistical_results=_build_statistical_results(
                    method_family="cluster_profile_comparison",
                    test_or_model="cluster_mean_spread",
                    sample_size=sample_size,
                    statistic=round(driver_spread, 4),
                    effect_size=round(driver_spread, 4),
                    result_direction=f"{driver_high_cluster} is highest and {driver_low_cluster} is lowest on {driver_label}.",
                ),
                plain_language_explanation=f"This is the item that most clearly separates one segment from another, so it is a strong candidate for differentiation in strategy.",
                evidence_quotes=_quote_candidates(
                    score_table,
                    [driver_column],
                    catalog,
                    foundation,
                    unit_cluster_map=unit_cluster_map,
                    selected_cluster=driver_high_cluster,
                    limit=1,
                ),
            )
        )

    lead_profile = profiles.get(lead_cluster, {})
    lead_numeric_summary = lead_profile.get("numeric_summary", {}) if isinstance(lead_profile, dict) else {}
    top_columns = [
        column
        for column, _ in sorted(
            (
                (str(column), float(value))
                for column, value in lead_numeric_summary.items()
                if str(column) in catalog
            ),
            key=lambda item: item[1],
            reverse=True,
        )[:2]
    ]
    if not top_columns:
        top_columns = relevant_columns[:2]
    theory_entries = _theory_entries_for_columns(
        foundation,
        top_columns,
        include_segmentation_overlays=True,
    )
    process_labels = [
        _titleize(str(entry.get("subtheory", "")))
        for entry in theory_entries
        if entry.get("family") == "dual_process"
    ]
    need_labels = [
        _titleize(str(entry.get("subtheory", "")))
        for entry in theory_entries
        if entry.get("family") == "maslow"
    ]
    if not process_labels:
        process_labels.append("mixed decision processing")
    if not need_labels:
        need_labels.append("multiple need states")

    findings.append(
        _build_finding(
            finding_id="segmentation-psychology-overlay",
            finding_statement=f"{lead_cluster} is most associated with {', '.join(process_labels)} cues and {', '.join(need_labels)} needs, anchored by {', '.join(_format_feature_label(foundation, column, catalog) for column in top_columns)}.",
            business_implication="Use motive-based positioning for the lead segment, not only descriptive demographics or channel tags.",
            methods_used=_item_bundle(
                ("Cluster Profile Aggregation", "Identify the highest-scoring items inside the lead segment after clustering."),
                ("Theory Overlay", "Map those items back to annotated theory families and subtheories from dimension_catalog to interpret the segment psychologically."),
            ),
            theories_used=_theories_for_columns(foundation, top_columns, include_segmentation_overlays=True) or _fallback_theories("segmentation"),
            reproducibility=_build_reproducibility(
                input_artifacts=_stage_input_artifacts("segmentation"),
                input_columns=top_columns,
                filters=[f"cluster = {lead_cluster}"],
                preprocessing=[
                    "Use the final segment assignments to isolate the lead segment.",
                    "Sort the lead segment's scored items by cluster-level mean.",
                ],
                analysis_steps=[
                    "Take the largest segment from cluster_share_table.",
                    "Read the lead segment's top scored items from numeric_summary.",
                    "Overlay the items' theory annotations to interpret System 1 / System 2 and Maslow signals.",
                ],
                decision_rule="Explain the segment using the highest-scoring items and their mapped theory annotations, rather than free-form interpretation.",
            ),
            statistical_results=_build_statistical_results(
                method_family="descriptive_profile_overlay",
                test_or_model="top_item_theory_overlay",
                sample_size=int(lead_segment.get("sample_size", 0)),
                statistic={"top_columns": top_columns},
        result_direction=f"{lead_cluster} concentrates on {', '.join(_format_feature_label(foundation, column, catalog) for column in top_columns)}.",
            ),
            plain_language_explanation="This finding explains what kind of motive sits underneath the lead segment, so strategy can speak to the real need instead of just the observable behavior.",
            evidence_quotes=_quote_candidates(
                score_table,
                top_columns,
                catalog,
                foundation,
                unit_cluster_map=unit_cluster_map,
                selected_cluster=lead_cluster,
                limit=1,
            ),
        )
    )
    return findings


def _best_record(results: list[dict[str, Any]], key_name: str) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_p = float("inf")
    for record in results:
        if not isinstance(record, dict):
            continue
        bucket = record.get(key_name, {})
        if not isinstance(bucket, dict):
            continue
        p_value = float(bucket.get("p_value", 1.0))
        if p_value < best_p:
            best = record
            best_p = p_value
    return best


def _first_significant_pairwise(pairwise_table: list[dict[str, Any]], variable: str) -> dict[str, Any] | None:
    for row in pairwise_table:
        if str(row.get("variable")) == variable and bool(row.get("significant")):
            return row
    return None


def _targeting_findings(
    stage_summary: dict[str, Any],
    foundation: dict[str, Any],
    score_table: Any,
    catalog: dict[str, dict[str, Any]],
    relevant_columns: list[str],
    unit_cluster_map: dict[str, str] | None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    sample_size = _targeting_sample_size(score_table, unit_cluster_map, stage_summary)
    decision = stage_summary.get("target_selection_decision", {})
    cluster_table = [row for row in stage_summary.get("cluster_score_table", []) if isinstance(row, dict)]
    cluster_table.sort(key=lambda row: int(row.get("rank", 9999)))
    selected_cluster = str(decision.get("selected_cluster", ""))
    selected_score = float(decision.get("score", 0.0))
    comparison_axes = [str(column) for column in decision.get("comparison_axes_used", []) if column]
    runner_up_gap = None
    if len(cluster_table) > 1:
        runner_up_gap = round(selected_score - float(cluster_table[1].get("score", 0.0)), 4)

    if selected_cluster:
        findings.append(
            _build_finding(
                finding_id="targeting-priority-segment",
                finding_statement=f"{selected_cluster} is the priority segment because it ranks highest across the selected comparison axes.",
                business_implication="Prioritize messaging, lifecycle interventions, and budget allocation for this segment before scaling to secondary audiences.",
                methods_used=_item_bundle(
                    ("Comparison-Axis Normalization", "Scale cluster mean scores to a common 0-1 range before averaging them into a segment ranking score."),
                    ("Segment Ranking", "Order clusters by the averaged normalized score to identify priority, secondary, and deprioritized audiences."),
                ),
                theories_used=_theories_for_columns(foundation, comparison_axes) or _fallback_theories("targeting"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("targeting"),
                    input_columns=comparison_axes or relevant_columns,
                    filters=[],
                    preprocessing=[
                        "Aggregate scored reviews to the unit level before targeting.",
                        "Compute cluster means for the chosen comparison axes.",
                        "Min-max normalize the cluster means by axis.",
                    ],
                    analysis_steps=[
                        "Read comparison_axes_used from target_selection_decision.",
                        "Average the normalized comparison-axis scores within each cluster.",
                        "Rank clusters from highest to lowest average score.",
                    ],
                    decision_rule="Choose the highest-scoring cluster as priority, keep middle-ranked clusters as secondary, and place the lowest-ranked cluster in deprioritized.",
                ),
                statistical_results=_build_statistical_results(
                    method_family="segment_ranking",
                    test_or_model="comparison_axis_normalization",
                    sample_size=sample_size,
                    statistic=round(selected_score, 4),
                    effect_size=runner_up_gap,
                    result_direction=f"{selected_cluster} ranks first on {', '.join(_format_feature_label(foundation, column, catalog) for column in comparison_axes) or 'the selected axes'}.",
                ),
                plain_language_explanation="This finding turns multiple target-selection inputs into one ranking, so you can see which segment deserves the first move.",
                evidence_quotes=_quote_candidates(
                    score_table,
                    comparison_axes or relevant_columns,
                    catalog,
                    foundation,
                    unit_cluster_map=unit_cluster_map,
                    selected_cluster=selected_cluster,
                    limit=1,
                ),
            )
        )

    pairwise_table = [row for row in stage_summary.get("pairwise_comparison_table", []) if isinstance(row, dict)]
    current_best = _best_record(stage_summary.get("current_target_market", []), "anova")
    if current_best:
        variable = str(current_best.get("variable"))
        variable_label = _format_feature_label(foundation, variable, catalog)
        anova = current_best.get("anova", {})
        pairwise = _first_significant_pairwise(pairwise_table, variable)
        findings.append(
            _build_finding(
                finding_id="targeting-current-market-driver",
                finding_statement=f"{variable_label} is the strongest current-market differentiator across clusters.",
                business_implication=f"Use {variable_label} to shape immediate conversion and retention messaging because it most strongly separates current segment performance.",
                methods_used=_item_bundle(
                    ("ANOVA", "Test whether cluster means differ on the continuous targeting variable."),
                    ("OLS Regression", "Estimate how much cluster membership explains variance in the variable."),
                    ("Tukey HSD", "Inspect which specific cluster pairs differ when the overall ANOVA is significant."),
                ),
                theories_used=_theories_for_columns(foundation, [variable]) or _fallback_theories("targeting"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("targeting"),
                    input_columns=["cluster", variable],
                    filters=[],
                    preprocessing=[
                        "Keep non-null rows for the selected targeting variable.",
                        "Encode cluster membership as regression dummies for OLS.",
                    ],
                    analysis_steps=[
                        "Run one-way ANOVA for the variable across clusters.",
                        "Fit an OLS model with cluster dummies to estimate explained variance.",
                        "Review Tukey HSD pairwise results when the ANOVA is significant.",
                    ],
                    decision_rule="Treat the variable with the smallest ANOVA p-value as the strongest continuous current-market differentiator.",
                ),
                statistical_results=_build_statistical_results(
                    method_family="continuous_targeting",
                    test_or_model="anova_regression",
                    sample_size=sample_size,
                    statistic=round(float(anova.get("f_stat", 0.0)), 4),
                    p_value=round(float(anova.get("p_value", 1.0)), 6),
                    effect_size=round(float(current_best.get("regression_r2", 0.0)), 4),
                    confidence_interval=[pairwise.get("lower"), pairwise.get("upper")] if pairwise else None,
                    result_direction=f"{variable_label} shows the strongest cluster-level difference among current-market measures.",
                ),
                plain_language_explanation=f"This variable most clearly separates how the segments already perform today, so it is a practical lever for near-term targeting.",
                evidence_quotes=_quote_candidates(
                    score_table,
                    [variable],
                    catalog,
                    foundation,
                    unit_cluster_map=unit_cluster_map,
                    selected_cluster=selected_cluster or None,
                    limit=1,
                ),
            )
        )

    potential_results = stage_summary.get("potential_target_market", [])
    best_potential = None
    best_potential_p = float("inf")
    for record in potential_results:
        if not isinstance(record, dict):
            continue
        if record.get("method") == "chi_square_logistic_regression":
            p_value = float(record.get("chi_square", {}).get("p_value", 1.0))
        else:
            p_value = float(record.get("anova", {}).get("p_value", 1.0))
        if p_value < best_potential_p:
            best_potential = record
            best_potential_p = p_value

    if best_potential:
        variable = str(best_potential.get("variable"))
        variable_label = _format_feature_label(foundation, variable, catalog)
        if best_potential.get("method") == "chi_square_logistic_regression":
            chi_square = best_potential.get("chi_square", {})
            statistical_results = _build_statistical_results(
                method_family="binary_targeting",
                test_or_model="chi_square_logistic_regression",
                sample_size=sample_size,
                statistic=round(float(chi_square.get("chi2", 0.0)), 4),
                p_value=round(float(chi_square.get("p_value", 1.0)), 6),
                coefficient=best_potential.get("coefficients"),
                result_direction=f"{variable_label} is the strongest binary potential-market separator across clusters.",
            )
            methods_used = _item_bundle(
                ("Chi-Square Test", "Check whether the binary outcome is distributed differently across clusters."),
                ("Logistic Regression", "Estimate cluster-specific directional coefficients for the binary outcome."),
            )
        else:
            anova = best_potential.get("anova", {})
            statistical_results = _build_statistical_results(
                method_family="continuous_targeting",
                test_or_model="anova",
                sample_size=sample_size,
                statistic=round(float(anova.get("f_stat", 0.0)), 4),
                p_value=round(float(anova.get("p_value", 1.0)), 6),
                result_direction=f"{variable_label} is the strongest continuous potential-market separator across clusters.",
            )
            methods_used = _item_bundle(
                ("ANOVA", "Check whether the potential-market outcome differs across clusters."),
                ("Cluster Comparison", "Interpret the variable as a directional growth signal when it separates clusters."),
            )
        findings.append(
            _build_finding(
                finding_id="targeting-potential-market-driver",
                finding_statement=f"{variable_label} is the strongest potential-market signal in the targeting model.",
                business_implication=f"Use {variable_label} as a growth-screening variable when deciding where to expand after the priority segment.",
                methods_used=methods_used,
                theories_used=_theories_for_columns(foundation, [variable]) or _fallback_theories("targeting"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("targeting"),
                    input_columns=["cluster", variable],
                    filters=[],
                    preprocessing=["Keep rows with valid cluster labels and non-null values for the potential-market variable."],
                    analysis_steps=[
                        "Run the matching inferential test for the variable type.",
                        "Sort potential-market variables by ascending p-value.",
                        "Treat the variable with the lowest p-value as the strongest practical growth discriminator.",
                    ],
                    decision_rule="Use the smallest p-value among potential-market variables to choose the clearest growth signal for segment expansion.",
                ),
                statistical_results=statistical_results,
                plain_language_explanation="This finding points to the variable that best explains where future growth is most likely to differ between segments.",
                evidence_quotes=_quote_candidates(
                    score_table,
                    [variable],
                    catalog,
                    foundation,
                    unit_cluster_map=unit_cluster_map,
                    selected_cluster=selected_cluster or None,
                    limit=1,
                ),
            )
        )
    return findings


def _positioning_score_lookup(stage_summary: dict[str, Any]) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, Any]], dict[str, float]]:
    brand_scores: dict[str, dict[str, float]] = {}
    feature_meta: dict[str, dict[str, Any]] = {}
    ideal_scores: dict[str, float] = {}
    for row in stage_summary.get("positioning_scorecard", []):
        if not isinstance(row, dict):
            continue
        brand = str(row.get("brand", ""))
        attribute = str(row.get("attribute", ""))
        feature = str(row.get("feature") or attribute)
        axis = str(row.get("axis", "mixed"))
        score = float(row.get("score", 0.0))
        if not brand or not feature:
            continue
        feature_meta[feature] = {"attribute": attribute, "axis": axis}
        if str(row.get("point_type")) == "ideal":
            ideal_scores[feature] = score
        else:
            brand_scores.setdefault(brand, {})[feature] = score
    return brand_scores, feature_meta, ideal_scores


def _positioning_findings(
    stage_summary: dict[str, Any],
    foundation: dict[str, Any],
    score_table: Any,
    catalog: dict[str, dict[str, Any]],
    relevant_columns: list[str],
    positioning_method: str | None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    sample_size = _positioning_sample_size(stage_summary, score_table)
    diagnostics = stage_summary.get("positioning_diagnostics", {})
    benchmark = diagnostics.get("benchmark_analysis", {})
    closest_brand = str(benchmark.get("closest_to_ideal", ""))
    closest_distance = float(benchmark.get("distance_to_ideal", 0.0))
    distance_table = [
        row for row in stage_summary.get("dynamic_scorecard_summary", {}).get("ideal_point_distance_summary", [])
        if isinstance(row, dict)
    ]
    distance_table.sort(key=lambda row: float(row.get("distance_to_ideal", 9999.0)))
    gap_to_second = None
    if len(distance_table) > 1:
        gap_to_second = round(float(distance_table[1].get("distance_to_ideal", 0.0)) - closest_distance, 4)

    method_name = "Factor Analysis" if positioning_method != "mds" else "Multidimensional Scaling"
    method_model = "factor_analysis" if positioning_method != "mds" else "mds"
    if closest_brand:
        findings.append(
            _build_finding(
                finding_id="positioning-closest-to-ideal",
                finding_statement=f"{closest_brand} is closest to the ideal point on the perceptual map.",
                business_implication=f"Use {closest_brand} as the benchmark for what the market ideal currently rewards, then decide whether to defend or outflank that position.",
                methods_used=_item_bundle(
                    (method_name, "Build the two-dimensional perceptual map used for brand comparison."),
                    ("Ideal-Point Distance", "Measure each brand's Euclidean distance from the desired market ideal."),
                ),
                theories_used=_theories_for_columns(foundation, relevant_columns) or _fallback_theories("positioning"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("positioning"),
                    input_columns=relevant_columns,
                    filters=[f"brand = {closest_brand}"],
                    preprocessing=[
                        "Aggregate per-review scores into a brand-attribute scorecard.",
                        f"Project brand points into two dimensions with {method_name}.",
                    ],
                    analysis_steps=[
                        "Build the brand-attribute matrix from positioning_scorecard.csv.",
                        "Add the ideal point profile.",
                        f"Compute two-dimensional coordinates using {method_name}.",
                        "Calculate each brand's Euclidean distance to the ideal point.",
                    ],
                    decision_rule="Treat the smallest distance_to_ideal as the closest strategic fit to the desired market ideal.",
                ),
                statistical_results=_build_statistical_results(
                    method_family="perceptual_map_distance",
                    test_or_model=method_model,
                    sample_size=sample_size,
                    statistic=round(closest_distance, 4),
                    effect_size=gap_to_second,
                    result_direction=f"{closest_brand} is nearest to the ideal point.",
                ),
                plain_language_explanation="This finding tells you which brand currently sits nearest to what the market ideally wants, based on the scored attribute structure.",
                evidence_quotes=_quote_candidates(
                    score_table,
                    relevant_columns,
                    catalog,
                    foundation,
                    selected_brand=closest_brand,
                    limit=1,
                ),
            )
        )

    attribute_benchmarks = [
        row for row in diagnostics.get("benchmark_analysis", {}).get("attribute_leaders", [])
        if isinstance(row, dict)
    ]
    strongest_attribute = None
    if attribute_benchmarks:
        strongest_attribute = max(attribute_benchmarks, key=lambda row: float(row.get("gap_to_next_brand", 0.0)))
    if strongest_attribute:
        attribute = str(strongest_attribute.get("attribute"))
        feature = str(strongest_attribute.get("feature") or attribute)
        leader = str(strongest_attribute.get("leader"))
        gap_to_next = float(strongest_attribute.get("gap_to_next_brand", 0.0))
        leader_score = float(strongest_attribute.get("leader_score", 0.0))
        attribute_label = _format_feature_label(foundation, feature, catalog)
        findings.append(
            _build_finding(
                finding_id="positioning-strongest-advantage",
                finding_statement=f"{leader} owns the clearest attribute advantage on {attribute_label}.",
                business_implication=f"Use {attribute_label} as a lead proof point when explaining why {leader} is meaningfully different.",
                methods_used=_item_bundle(
                    ("Brand-Attribute Scorecard", "Compare mean brand scores on each positioning attribute."),
                    ("Attribute Gap Analysis", "Measure the leading brand's gap to the next-best competitor on each attribute."),
                ),
                theories_used=_theories_for_columns(foundation, [feature]) or _fallback_theories("positioning"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("positioning"),
                    input_columns=[feature],
                    filters=[f"leader brand = {leader}"],
                    preprocessing=["Aggregate attribute scores by brand before comparing attribute leaders."],
                    analysis_steps=[
                        "Rank brands by score for each positioning attribute.",
                        "Compute the score gap between the top brand and the next-best brand.",
                        "Choose the attribute with the largest positive gap as the clearest owned advantage.",
                    ],
                    decision_rule="Treat the largest positive gap_to_next_brand as the clearest practical attribute advantage.",
                ),
                statistical_results=_build_statistical_results(
                    method_family="attribute_gap_analysis",
                    test_or_model="brand_attribute_leader_gap",
                    sample_size=sample_size,
                    statistic=round(gap_to_next, 4),
                    effect_size=round(gap_to_next, 4),
                    coefficient=round(leader_score, 4),
                    result_direction=f"{leader} leads {attribute_label} by {gap_to_next:.4f} points over the next brand.",
                ),
                plain_language_explanation="This is the attribute where one brand most clearly owns a distinctive edge, making it a strong candidate for competitive messaging.",
                evidence_quotes=_quote_candidates(
                    score_table,
                    [feature],
                    catalog,
                    foundation,
                    selected_brand=leader,
                    limit=1,
                ),
            )
        )

    brand_scores, feature_meta, ideal_scores = _positioning_score_lookup(stage_summary)
    gap_attribute = ""
    gap_value = -1.0
    gap_brand_score = 0.0
    gap_ideal_score = 0.0
    if closest_brand and closest_brand in brand_scores:
        for attribute, brand_score in brand_scores[closest_brand].items():
            ideal_score = float(ideal_scores.get(attribute, brand_score))
            gap = ideal_score - float(brand_score)
            if gap > gap_value:
                gap_attribute = attribute
                gap_value = gap
                gap_brand_score = float(brand_score)
                gap_ideal_score = ideal_score
    if gap_attribute:
        gap_label = _format_feature_label(foundation, gap_attribute, catalog)
        findings.append(
            _build_finding(
                finding_id="positioning-main-gap",
                finding_statement=f"{closest_brand}'s biggest ideal-point gap is {gap_label}.",
                business_implication=f"Improve {gap_label} before expanding awareness, otherwise traffic growth will amplify an avoidable positioning weakness.",
                methods_used=_item_bundle(
                    ("Brand-Attribute Scorecard", "Compare the brand's current attribute score with the ideal profile score."),
                    ("Ideal-Point Gap Analysis", "Measure the distance between the brand and ideal score for each attribute."),
                ),
                theories_used=_theories_for_columns(foundation, [gap_attribute]) or _fallback_theories("positioning"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("positioning"),
                    input_columns=[gap_attribute],
                    filters=[f"brand = {closest_brand}"],
                    preprocessing=["Join the nearest brand's scorecard row to the ideal profile row for the same attribute."],
                    analysis_steps=[
                        "Identify the brand closest to the ideal point.",
                        "Compare that brand's score against the ideal score for each attribute.",
                        "Select the attribute with the largest positive ideal-minus-brand gap.",
                    ],
                    decision_rule="Treat the largest positive ideal-minus-brand gap as the main positioning weakness for the closest brand.",
                ),
                statistical_results=_build_statistical_results(
                    method_family="importance_performance_gap",
                    test_or_model="ideal_point_gap",
                    sample_size=sample_size,
                    statistic=round(gap_value, 4),
                    coefficient={"brand_score": round(gap_brand_score, 4), "ideal_score": round(gap_ideal_score, 4)},
                    result_direction=f"{closest_brand} trails the ideal most strongly on {gap_label}.",
                ),
                plain_language_explanation="Even the brand nearest to the ideal still has a weakest link. This shows where the next product or messaging improvement would matter most.",
                evidence_quotes=_quote_candidates(
                    score_table,
                    [gap_attribute],
                    catalog,
                    foundation,
                    selected_brand=closest_brand,
                    limit=1,
                ),
            )
        )

    competition_landscape = [
        row for row in diagnostics.get("competition_landscape", [])
        if isinstance(row, dict)
    ]
    competition_landscape.sort(key=lambda row: float(row.get("distance", 9999.0)))
    if competition_landscape:
        crowded_pair = competition_landscape[0]
        brand_a = str(crowded_pair.get("brand_a"))
        brand_b = str(crowded_pair.get("brand_b"))
        crowded_distance = float(crowded_pair.get("distance", 0.0))
        findings.append(
            _build_finding(
                finding_id="positioning-competitive-crowding",
                finding_statement=f"{brand_a} and {brand_b} are the most crowded pair on the perceptual map.",
                business_implication="Avoid me-too positioning against this nearest rival pair. Create separation on a specific attribute or need state instead.",
                methods_used=_item_bundle(
                    (method_name, "Use the perceptual map coordinates as the basis for pairwise competitive spacing."),
                    ("Pairwise Competition Distance", "Compute the Euclidean distance between every pair of brand points and find the smallest distance."),
                ),
                theories_used=_theories_for_columns(foundation, relevant_columns) or _fallback_theories("positioning"),
                reproducibility=_build_reproducibility(
                    input_artifacts=_stage_input_artifacts("positioning"),
                    input_columns=relevant_columns,
                    filters=[f"brands = {brand_a}, {brand_b}"],
                    preprocessing=[f"Map all brands into the same two-dimensional space with {method_name}."],
                    analysis_steps=[
                        "Read the perceptual map coordinate table.",
                        "Compute pairwise Euclidean distance between every brand pair.",
                        "Treat the smallest distance as the most crowded competitive pair.",
                    ],
                    decision_rule="Smaller inter-brand distance indicates stronger competitive crowding on the current map.",
                ),
                statistical_results=_build_statistical_results(
                    method_family="pairwise_brand_distance",
                    test_or_model=method_model,
                    sample_size=sample_size,
                    statistic=round(crowded_distance, 4),
                    result_direction=f"{brand_a} and {brand_b} are closer to each other than any other brand pair.",
                ),
                plain_language_explanation="These two brands look most similar on the map, so the market may struggle to see why one should win over the other.",
                evidence_quotes=_merge_quotes(
                    _quote_candidates(score_table, relevant_columns, catalog, foundation, selected_brand=brand_a, limit=1),
                    _quote_candidates(score_table, relevant_columns, catalog, foundation, selected_brand=brand_b, limit=1),
                ),
            )
        )
    return findings


def _stage_findings(
    stage: str,
    stage_summary: dict[str, Any],
    foundation: dict[str, Any],
    score_table: Any,
    catalog: dict[str, dict[str, Any]],
    relevant_columns: list[str],
    positioning_method: str | None,
    unit_cluster_map: dict[str, str] | None,
) -> list[dict[str, Any]]:
    if stage == "segmentation":
        return _segmentation_findings(stage_summary, foundation, score_table, catalog, relevant_columns, unit_cluster_map)
    if stage == "targeting":
        return _targeting_findings(stage_summary, foundation, score_table, catalog, relevant_columns, unit_cluster_map)
    return _positioning_findings(stage_summary, foundation, score_table, catalog, relevant_columns, positioning_method)


def _augment_findings_with_theme_and_theory_details(
    findings: list[dict[str, Any]],
    foundation: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    fallback_columns: list[str],
    *,
    include_segmentation_overlays: bool = False,
) -> list[dict[str, Any]]:
    augmented: list[dict[str, Any]] = []
    for finding in findings:
        reproducibility = finding.get("reproducibility", {})
        finding_columns = [
            str(column)
            for column in reproducibility.get("input_columns", [])
            if str(column)
        ]
        if not finding_columns:
            finding_columns = list(fallback_columns)
        base_columns = _normalize_to_base_columns(foundation, finding_columns)
        fallback_base_columns = _normalize_to_base_columns(foundation, list(fallback_columns))
        updated = dict(finding)
        axes_used = _axes_used_for_columns(foundation, finding_columns)
        updated["axes_used"] = axes_used
        themes_used = _themes_for_columns(foundation, base_columns)
        if not themes_used:
            themes_used = _themes_for_columns(foundation, fallback_base_columns)
        updated["themes_used"] = themes_used
        subtheories_used = _theory_entries_for_columns(
            foundation,
            base_columns,
            include_segmentation_overlays=include_segmentation_overlays,
        )
        if not subtheories_used:
            subtheories_used = _theory_entries_for_columns(
                foundation,
                fallback_base_columns,
                include_segmentation_overlays=include_segmentation_overlays,
            )
        updated["subtheories_used"] = subtheories_used
        statistical_results = dict(updated.get("statistical_results", {}))
        statistical_results["axis_breakdown"] = _axis_breakdown_from_result(
            statistical_results,
            axes_used,
        )
        updated["statistical_results"] = statistical_results
        augmented.append(updated)
    return augmented


def build_stage_report_contract(
    stage: str,
    stage_summary: dict[str, Any] | None,
    foundation: dict[str, Any] | None,
    score_table: Any | None,
    positioning_method: str | None = None,
    unit_cluster_map: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(stage_summary, dict):
        return stage_summary
    foundation = foundation or {}

    catalog = _catalog_lookup(foundation)
    relevant_columns = _columns_for_stage(foundation, stage, stage_summary)
    include_segmentation_overlays = stage == "segmentation"
    selected_cluster = None
    selected_brand = None
    if stage == "targeting":
        selected_cluster = stage_summary.get("target_selection_decision", {}).get("selected_cluster")
    if stage == "positioning":
        selected_brand = stage_summary.get("positioning_diagnostics", {}).get("benchmark_analysis", {}).get("closest_to_ideal")

    evidence_quotes = _quote_candidates(
        score_table,
        relevant_columns,
        catalog,
        foundation,
        unit_cluster_map=unit_cluster_map,
        selected_cluster=selected_cluster,
        selected_brand=selected_brand,
    )
    evidence_status = "available" if evidence_quotes else "not_available"
    evidence_reason = "" if evidence_quotes else "Canonical per-review scoring evidence was not provided for this run."

    enriched = dict(stage_summary)
    enriched["what_this_section_is_doing"] = _what_this_section_is_doing(stage)
    enriched["methods_used"] = _stage_methods(stage, positioning_method)
    enriched["axis_modeling_summary"] = _axis_modeling_summary(
        foundation,
        stage,
        relevant_columns,
        positioning_method,
    )
    theories_used = _theories_for_columns(
        foundation,
        relevant_columns,
        include_segmentation_overlays=include_segmentation_overlays,
    )
    enriched["theories_used"] = theories_used or _fallback_theories(stage)
    enriched["plain_language_explanation"] = _plain_language_explanation(stage, stage_summary)
    enriched["evidence_quote_status"] = evidence_status
    enriched["evidence_quote_reason"] = evidence_reason
    enriched["evidence_quotes"] = evidence_quotes
    findings = _stage_findings(
        stage,
        stage_summary,
        foundation,
        score_table,
        catalog,
        relevant_columns,
        positioning_method,
        unit_cluster_map,
    )
    enriched["findings"] = _augment_findings_with_theme_and_theory_details(
        findings,
        foundation,
        catalog,
        relevant_columns,
        include_segmentation_overlays=include_segmentation_overlays,
    )
    enriched["theme_coverage_summary"] = _theme_coverage_summary(
        foundation,
        enriched["findings"],
        catalog,
    )
    enriched["theory_coverage_summary"] = _theory_coverage_summary(
        foundation,
        relevant_columns,
        include_segmentation_overlays=include_segmentation_overlays,
    )
    return enriched


def _render_described_items(items: list[dict[str, Any]], indent: str = "") -> list[str]:
    lines: list[str] = []
    for item in items:
        lines.append(f"{indent}- {item.get('name')}: {item.get('description')}")
    return lines


def _stringify(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _render_quotes(quotes: list[dict[str, Any]], empty_reason: str, indent: str = "") -> list[str]:
    if not quotes:
        return [f"{indent}- not available: {empty_reason}"]
    lines: list[str] = []
    for quote in quotes:
        lines.append(f"{indent}- [{quote.get('review_id')}] \"{quote.get('quote_text')}\"")
        lines.append(f"{indent}  Why it matters: {quote.get('why_this_quote_matters')}")
        lines.append(f"{indent}  Linked items: {', '.join(quote.get('linked_items', [])) or 'none'}")
    return lines


def _render_theme_coverage(summary: list[dict[str, Any]], indent: str = "") -> list[str]:
    lines: list[str] = []
    for row in summary:
        lines.append(
            f"{indent}- {row.get('theme')}: status={row.get('evidence_status')}; "
            f"supporting_items={', '.join(row.get('supporting_items', [])) or 'none'}; "
            f"related_findings={', '.join(row.get('related_findings', [])) or 'none'}"
        )
    return lines


def _render_theory_coverage(summary: list[dict[str, Any]], indent: str = "") -> list[str]:
    lines: list[str] = []
    for row in summary:
        lines.append(
            f"{indent}- {row.get('theory_family')}: status={row.get('evidence_status')}; "
            f"covered={', '.join(row.get('covered_subtheories', [])) or 'none'}; "
            f"not_evidenced={', '.join(row.get('not_evidenced_subtheories', [])) or 'none'}; "
            f"supporting_items={', '.join(row.get('supporting_items', [])) or 'none'}"
        )
    return lines


def _render_themes_used(items: list[dict[str, Any]], indent: str = "") -> list[str]:
    lines: list[str] = []
    for item in items:
        lines.append(
            f"{indent}- {item.get('theme')}: {', '.join(item.get('supporting_items', [])) or 'none'}"
        )
    return lines


def _render_subtheories_used(items: list[dict[str, Any]], indent: str = "") -> list[str]:
    lines: list[str] = []
    for item in items:
        lines.append(
            f"{indent}- {item.get('label')}: source={item.get('source')}; "
            f"supporting_item={item.get('supporting_item')}"
        )
    return lines


def _render_axis_modeling(summary: dict[str, Any], indent: str = "") -> list[str]:
    return [
        f"{indent}- axes_mode: {summary.get('axes_mode', 'n/a')}",
        f"{indent}- salience_columns_used: {', '.join(summary.get('salience_columns_used', [])) or 'none'}",
        f"{indent}- valence_columns_used: {', '.join(summary.get('valence_columns_used', [])) or 'none'}",
        f"{indent}- modeling_rule: {summary.get('modeling_rule', 'n/a')}",
        f"{indent}- plain_language_explanation: {summary.get('plain_language_explanation', 'n/a')}",
    ]


def _render_axis_breakdown(axis_breakdown: dict[str, Any], indent: str = "") -> list[str]:
    lines: list[str] = []
    for axis in ["salience", "valence"]:
        payload = axis_breakdown.get(axis)
        if payload is None:
            lines.append(f"{indent}- {axis}: null")
            continue
        lines.append(
            f"{indent}- {axis}: test_or_model={payload.get('test_or_model')}; "
            f"statistic={_stringify(payload.get('statistic'))}; "
            f"p_value={_stringify(payload.get('p_value'))}; "
            f"result_direction={payload.get('result_direction')}"
        )
    return lines


def _render_attribute_extraction_summary(summary: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## Attribute Extraction Summary",
        f"- target_minimum: {summary.get('target_minimum', 'n/a')}",
        f"- actual_count: {summary.get('actual_count', 'n/a')}",
        f"- shortfall_reason: {summary.get('shortfall_reason') or 'none'}",
        f"- themes_discovered: {', '.join(summary.get('themes_discovered', [])) or 'none'}",
        "- Attribute groups:",
    ]
    for row in summary.get("attribute_group_summary", []):
        lines.append(
            f"  - {row.get('attribute_group')}: {row.get('attribute_count')} attributes"
        )
    if not summary.get("attribute_group_summary"):
        lines.append("  - none")
    lines.append("- Representative attributes:")
    for row in summary.get("representative_attributes", []):
        lines.append(
            "  - "
            f"{row.get('label')} [{row.get('theme')} / {row.get('attribute_group')}]: "
            f"mention_count={row.get('mention_count')}; "
            f"example=[{row.get('example_review_id')}] \"{row.get('example_quote')}\""
        )
    if not summary.get("representative_attributes"):
        lines.append("  - none")
    return lines


def _render_finding(finding: dict[str, Any]) -> list[str]:
    reproducibility = finding.get("reproducibility", {})
    statistical_results = finding.get("statistical_results", {})
    lines = [
        "",
        f"### Finding {finding.get('finding_id')}",
        f"- Finding statement: {finding.get('finding_statement', 'n/a')}",
        f"- Business implication: {finding.get('business_implication', 'n/a')}",
        f"- Axes used: {finding.get('axes_used', 'n/a')}",
        "- Statistical methods used:",
    ]
    lines.extend(_render_described_items(finding.get("methods_used", []), indent="  "))
    lines.append("- Theories used:")
    lines.extend(_render_described_items(finding.get("theories_used", []), indent="  "))
    lines.append("- Themes used:")
    lines.extend(_render_themes_used(finding.get("themes_used", []), indent="  "))
    lines.append("- Subtheories used:")
    lines.extend(_render_subtheories_used(finding.get("subtheories_used", []), indent="  "))
    lines.append("- Reproducibility:")
    lines.append(f"  - input_artifacts: {', '.join(reproducibility.get('input_artifacts', [])) or 'none'}")
    lines.append(f"  - input_columns: {', '.join(reproducibility.get('input_columns', [])) or 'none'}")
    lines.append(f"  - filters: {', '.join(reproducibility.get('filters', [])) or 'none'}")
    lines.append(f"  - preprocessing: {'; '.join(reproducibility.get('preprocessing', [])) or 'none'}")
    lines.append(f"  - analysis_steps: {'; '.join(reproducibility.get('analysis_steps', [])) or 'none'}")
    lines.append(f"  - decision_rule: {reproducibility.get('decision_rule', 'n/a')}")
    lines.append("- Statistical results:")
    for key in [
        "method_family",
        "test_or_model",
        "sample_size",
        "statistic",
        "degrees_of_freedom",
        "p_value",
        "effect_size",
        "coefficient",
        "confidence_interval",
        "result_direction",
    ]:
        lines.append(f"  - {key}: {_stringify(statistical_results.get(key))}")
    lines.append("  - axis_breakdown:")
    lines.extend(_render_axis_breakdown(statistical_results.get("axis_breakdown", {}), indent="    "))
    lines.append(f"- Plain-language explanation: {finding.get('plain_language_explanation', 'n/a')}")
    lines.append("- Evidence quotes:")
    lines.extend(_render_quotes(finding.get("evidence_quotes", []), "No evidence quotes were attached to this finding.", indent="  "))
    return lines


def _render_report_section(title: str, section: dict[str, Any]) -> list[str]:
    lines = [
        "",
        f"## {title}",
        f"- What this section is doing: {section.get('what_this_section_is_doing', 'n/a')}",
        "- Axis modeling summary:",
    ]
    lines.extend(_render_axis_modeling(section.get("axis_modeling_summary", {}), indent="  "))
    lines.extend([
        "- Statistical methods used:",
    ])
    lines.extend(_render_described_items(section.get("methods_used", []), indent="  "))
    lines.append("- Theories used:")
    lines.extend(_render_described_items(section.get("theories_used", []), indent="  "))
    lines.append("- Theme coverage:")
    lines.extend(_render_theme_coverage(section.get("theme_coverage_summary", []), indent="  "))
    lines.append("- Theory coverage:")
    lines.extend(_render_theory_coverage(section.get("theory_coverage_summary", []), indent="  "))
    lines.append(f"- Plain-language explanation: {section.get('plain_language_explanation', 'n/a')}")
    lines.append("- Section-level evidence quotes:")
    lines.extend(
        _render_quotes(
            section.get("evidence_quotes", []),
            section.get("evidence_quote_reason", "No evidence quotes were attached."),
            indent="  ",
        )
    )
    if section.get("findings"):
        lines.append("")
        lines.append("### Findings")
        for finding in section["findings"]:
            lines.extend(_render_finding(finding))
    return lines


def write_report(output_dir: Path, run_mode: str, appendix: dict[str, Any]) -> None:
    execution_scope = appendix.get("execution_scope", {})
    lines = [
        "# Review Mining STP Report",
        "",
        "## Execution Scope Summary",
        f"- run_mode: {run_mode}",
        f"- requested modules: {', '.join(execution_scope.get('requested_modules', [])) or 'none'}",
        f"- executed modules: {', '.join(execution_scope.get('modules_executed', [])) or 'none'}",
        f"- upstream artifacts used: {', '.join(execution_scope.get('upstream_artifacts_used', [])) or 'none'}",
        f"- emitted intermediates: {', '.join(execution_scope.get('emitted_intermediate_artifacts', [])) or 'none'}",
        f"- comparison axes: {', '.join(execution_scope.get('comparison_axes', [])) or 'none'}",
        f"- brands: {', '.join(execution_scope.get('brands', [])) or 'none'}",
        f"- positioning method: {execution_scope.get('positioning_method_used', 'unknown')}",
        f"- cluster threshold: {execution_scope.get('cluster_threshold', 'n/a')}",
        f"- reruns performed: {execution_scope.get('reruns_performed', 0)}",
        f"- final_k: {execution_scope.get('final_k', 'n/a')}",
        f"- scope limits: {'; '.join(execution_scope.get('scope_limits', [])) or 'none'}",
        "",
        "## Risks / Bias / Confidence Notes",
        "- Output quality depends on the quality of upstream scored artifacts.",
        "- Statistical outputs are directional; validate with domain review before decisions.",
    ]
    attribute_extraction_summary = appendix.get("attribute_extraction_summary")
    if isinstance(attribute_extraction_summary, dict):
        lines.extend(_render_attribute_extraction_summary(attribute_extraction_summary))

    section_map = [
        ("Segmentation Summary", appendix.get("segmentation_summary")),
        ("Targeting Summary", appendix.get("targeting_summary")),
        ("Positioning Summary", appendix.get("positioning_summary")),
    ]
    for title, section in section_map:
        if section:
            lines.extend(_render_report_section(title, section))

    proactive_notes = appendix.get("proactive_marketing_notes", [])
    usp_candidates = appendix.get("usp_translation_candidates", [])
    if proactive_notes or usp_candidates:
        lines.extend(["", "## Strategy Extensions (Recommended)"])
        if proactive_notes:
            lines.extend([f"- proactive note: {item}" for item in proactive_notes])
        if usp_candidates:
            for candidate in usp_candidates:
                lines.append(
                    "- usp candidate: "
                    f"{candidate.get('usp_attribute')} -> {candidate.get('usp_statement')}"
                )

    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_execution_files(
    output_dir: Path,
    run_mode: str,
    requested_modules: list[str],
    appendix: dict[str, Any],
    positioning_method: str,
) -> None:
    write_json(
        output_dir / "run_metadata.json",
        {
            "run_mode": run_mode,
            "requested_modules": requested_modules,
            "positioning_method": positioning_method,
        },
    )
    write_json(output_dir / "appendix.json", appendix)
    write_report(output_dir, run_mode, appendix)
