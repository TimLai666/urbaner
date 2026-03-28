from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_DIMENSION_KEYS = {
    "column",
    "label",
    "theme",
    "attribute_group",
    "salience_column",
    "valence_column",
    "stat_roles",
    "plain_language_definition",
}
REQUIRED_ATTRIBUTE_CATALOG_COLUMNS = {
    "attribute_key",
    "label",
    "theme",
    "attribute_group",
    "definition",
    "source_type",
    "mention_count",
    "salience_column",
    "valence_column",
    "example_review_id",
    "example_quote",
}
ATTRIBUTE_GROUPS = {
    "attribute_function",
    "benefit_use",
    "brand_personality",
    "brand_image",
}
EMPTY_SENTINELS = {"", "n/a", "na", "null", "none"}

THEORY_TAXONOMY = {
    "product_positioning": {
        "attributes",
        "functions",
        "benefits",
        "usage_context_service_experience",
    },
    "purchase_motivation": {
        "functional",
        "security",
        "relational",
    },
    "wom_motivation": {
        "altruistic",
        "social_identity",
        "self_enhancement",
        "emotional_expression",
    },
    "dual_process": {
        "system1",
        "system2",
    },
    "maslow": {
        "physiological",
        "safety",
        "social",
        "esteem",
        "self_actualization",
    },
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def find_artifact(paths: list[Path], name: str) -> Path | None:
    for root in paths:
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def resolve_required_files(
    artifact_paths: list[Path],
    files: list[str],
) -> tuple[dict[str, Path], list[str]]:
    located: dict[str, Path] = {}
    missing: list[str] = []
    for filename in files:
        path = find_artifact(artifact_paths, filename)
        if path is None:
            missing.append(filename)
        else:
            located[filename] = path
    return located, missing


def require_files(artifact_paths: list[Path], files: list[str]) -> dict[str, Path] | None:
    located, missing = resolve_required_files(artifact_paths, files)
    if missing:
        return None
    return located


def list_available_artifacts(paths: list[Path]) -> list[str]:
    artifact_names: set[str] = set()
    for root in paths:
        if not root.exists():
            continue
        for candidate in root.iterdir():
            if candidate.is_file():
                artifact_names.add(candidate.name)
    return sorted(artifact_names)


def load_analysis_context(artifact_paths: list[Path]) -> dict[str, Any]:
    path = find_artifact(artifact_paths, "analysis_context.json")
    if path is None:
        return {"analysis_goal": "", "comparison_axes": [], "scope_limits": []}
    payload = read_json(path)
    payload.setdefault("analysis_goal", "")
    payload.setdefault("comparison_axes", [])
    payload.setdefault("scope_limits", [])
    return payload


def _fail_contract(message: str) -> None:
    raise SystemExit(message)


def _validate_theory_metadata(column: str, item: dict[str, Any]) -> None:
    theory_annotations = item.get("theory_annotations")
    theory_tags = item.get("theory_tags")
    if theory_annotations is None and theory_tags is None:
        _fail_contract(
            f"dimension_catalog column '{column}' must define theory_annotations or theory_tags."
        )

    if theory_annotations is not None:
        if not isinstance(theory_annotations, dict) or not theory_annotations:
            _fail_contract(
                f"dimension_catalog column '{column}' must define theory_annotations as a non-empty object."
            )
        for family, subtheories in theory_annotations.items():
            family_name = str(family)
            if family_name not in THEORY_TAXONOMY:
                _fail_contract(
                    f"dimension_catalog column '{column}' uses unsupported theory family '{family_name}'."
                )
            if not isinstance(subtheories, list) or not subtheories:
                _fail_contract(
                    f"dimension_catalog column '{column}' must define theory_annotations.{family_name} as a non-empty list."
                )
            invalid_subtheories = sorted(
                str(subtheory)
                for subtheory in subtheories
                if str(subtheory) not in THEORY_TAXONOMY[family_name]
            )
            if invalid_subtheories:
                _fail_contract(
                    f"dimension_catalog column '{column}' uses unsupported subtheories in theory_annotations.{family_name}: "
                    + ", ".join(invalid_subtheories)
                )

    if theory_tags is not None and (not isinstance(theory_tags, list) or not theory_tags):
        _fail_contract(
            f"dimension_catalog column '{column}' must define theory_tags as a non-empty list when present."
        )


def _normalize_optional_axis_values(series: Any, column: str, *, max_score: int) -> Any:
    import pandas as pd

    normalized = series.copy()
    normalized = normalized.apply(lambda value: pd.NA if str(value).strip().lower() in EMPTY_SENTINELS else value)
    numeric = pd.to_numeric(normalized, errors="coerce")
    invalid_mask = normalized.notna() & numeric.isna()
    if invalid_mask.any():
        _fail_contract(
            f"review_scoring_table.csv column '{column}' must contain integers or empty values."
        )
    present_values = numeric.dropna()
    if ((present_values < 0) | (present_values > max_score)).any():
        _fail_contract(
            f"review_scoring_table.csv column '{column}' must keep every score inside the 0-{max_score} range."
        )
    if not ((present_values % 1) == 0).all():
        _fail_contract(
            f"review_scoring_table.csv column '{column}' must use integer scores."
        )
    return numeric.astype("Int64")


def _expand_attribute_tokens(
    requested: list[str],
    pair_columns_by_base: dict[str, dict[str, str]],
    axis_column_to_base: dict[str, str],
    available_columns: set[str],
) -> list[str]:
    expanded: list[str] = []
    for token in requested:
        token_name = str(token)
        if token_name in pair_columns_by_base:
            pair = pair_columns_by_base[token_name]
            for axis in ["salience", "valence"]:
                column = pair[axis]
                if column in available_columns:
                    expanded.append(column)
        elif token_name in axis_column_to_base and token_name in available_columns:
            expanded.append(token_name)
        elif token_name in available_columns:
            expanded.append(token_name)
    return list(dict.fromkeys(expanded))


def _validate_attribute_catalog(
    attribute_catalog: Any,
    score_table: Any,
    catalog_by_column: dict[str, dict[str, Any]],
    extraction_summary: dict[str, Any],
) -> dict[str, Any]:
    import pandas as pd

    if attribute_catalog is None:
        _fail_contract("attribute_catalog.csv is required for the dual-axis canonical full input.")

    missing_columns = sorted(REQUIRED_ATTRIBUTE_CATALOG_COLUMNS - set(attribute_catalog.columns))
    if missing_columns:
        _fail_contract(
            "attribute_catalog.csv is missing required columns: " + ", ".join(missing_columns)
        )

    if attribute_catalog["attribute_key"].duplicated().any():
        _fail_contract("attribute_catalog.csv must not contain duplicate attribute_key values.")

    review_lookup = {
        str(row["review_id"]): str(row["review_text"])
        for row in score_table[["review_id", "review_text"]].to_dict("records")
    }

    attribute_keys = [str(value) for value in attribute_catalog["attribute_key"].tolist()]
    missing_attributes = sorted(column for column in catalog_by_column if column not in attribute_keys)
    extra_attributes = sorted(attribute for attribute in attribute_keys if attribute not in catalog_by_column)
    if missing_attributes or extra_attributes:
        messages: list[str] = []
        if missing_attributes:
            messages.append("missing from attribute_catalog.csv: " + ", ".join(missing_attributes))
        if extra_attributes:
            messages.append("unknown in attribute_catalog.csv: " + ", ".join(extra_attributes))
        _fail_contract("attribute_catalog.csv must align 1:1 with dimension_catalog. " + "; ".join(messages))

    for row in attribute_catalog.to_dict("records"):
        attribute_key = str(row["attribute_key"])
        item = catalog_by_column[attribute_key]
        if str(row["theme"]).strip() != str(item["theme"]).strip():
            _fail_contract(
                f"attribute_catalog.csv theme for '{attribute_key}' must match dimension_catalog."
            )
        if str(row["attribute_group"]).strip() != str(item["attribute_group"]).strip():
            _fail_contract(
                f"attribute_catalog.csv attribute_group for '{attribute_key}' must match dimension_catalog."
            )
        if str(row["salience_column"]).strip() != str(item["salience_column"]).strip():
            _fail_contract(
                f"attribute_catalog.csv salience_column for '{attribute_key}' must match dimension_catalog."
            )
        if str(row["valence_column"]).strip() != str(item["valence_column"]).strip():
            _fail_contract(
                f"attribute_catalog.csv valence_column for '{attribute_key}' must match dimension_catalog."
            )
        for field in ["label", "definition", "source_type", "example_review_id", "example_quote"]:
            if not str(row[field]).strip():
                _fail_contract(
                    f"attribute_catalog.csv '{attribute_key}' must define non-empty {field}."
                )
        mention_count = pd.to_numeric(pd.Series([row["mention_count"]]), errors="coerce").iloc[0]
        if pd.isna(mention_count) or float(mention_count) < 0:
            _fail_contract(
                f"attribute_catalog.csv '{attribute_key}' must define mention_count as a non-negative number."
            )
        review_id = str(row["example_review_id"])
        if review_id not in review_lookup:
            _fail_contract(
                f"attribute_catalog.csv '{attribute_key}' example_review_id '{review_id}' does not exist in review_scoring_table.csv."
            )
        if str(row["example_quote"]) != review_lookup[review_id]:
            _fail_contract(
                f"attribute_catalog.csv '{attribute_key}' example_quote must exactly match review_scoring_table.csv review_text."
            )

    target_minimum = int(extraction_summary.get("target_minimum", 30))
    actual_count = int(extraction_summary.get("actual_count", len(attribute_catalog)))
    shortfall_reason = str(extraction_summary.get("shortfall_reason", "") or "").strip()
    if actual_count != len(attribute_catalog):
        _fail_contract(
            "review_foundation.json attribute_extraction_summary.actual_count must match attribute_catalog.csv row count."
        )
    if actual_count < target_minimum and not shortfall_reason:
        _fail_contract(
            "attribute_extraction_summary.shortfall_reason is required when fewer than 30 attributes are extracted."
        )

    return {
        "target_minimum": target_minimum,
        "actual_count": actual_count,
        "shortfall_reason": shortfall_reason,
    }


def validate_canonical_inputs(
    score_table: Any,
    foundation: dict[str, Any],
    attribute_catalog: Any | None = None,
) -> dict[str, Any]:
    import pandas as pd

    unit_id_defaulted = False
    if "unit_id" not in score_table.columns and "review_id" in score_table.columns:
        score_table["unit_id"] = score_table["review_id"]
        unit_id_defaulted = True

    required_columns = {"review_id", "unit_id", "brand", "product", "review_text"}
    missing_columns = sorted(required_columns - set(score_table.columns))
    if missing_columns:
        _fail_contract(
            "review_scoring_table.csv is missing required columns: " + ", ".join(missing_columns)
        )

    review_text = score_table["review_text"].fillna("").astype(str).str.strip()
    if (review_text == "").any():
        _fail_contract("review_scoring_table.csv must contain non-empty review_text for every row.")

    dimension_catalog = foundation.get("dimension_catalog")
    if not isinstance(dimension_catalog, list) or not dimension_catalog:
        _fail_contract("review_foundation.json must contain a non-empty dimension_catalog.")

    theme_mapping = foundation.get("theme_mapping")
    if not isinstance(theme_mapping, dict) or not theme_mapping:
        _fail_contract("review_foundation.json must contain theme_mapping as a non-empty object.")

    extraction_summary = foundation.get("attribute_extraction_summary", {})
    if not isinstance(extraction_summary, dict):
        _fail_contract("review_foundation.json attribute_extraction_summary must be an object.")
    extraction_summary.setdefault("target_minimum", 30)
    extraction_summary.setdefault("actual_count", len(dimension_catalog))
    extraction_summary.setdefault("shortfall_reason", "")

    dimension_columns: list[str] = []
    role_map: dict[str, list[str]] = {}
    expanded_role_map: dict[str, list[str]] = {}
    catalog_by_column: dict[str, dict[str, Any]] = {}
    pair_columns_by_base: dict[str, dict[str, str]] = {}
    axis_column_to_base: dict[str, str] = {}

    for item in dimension_catalog:
        if not isinstance(item, dict):
            _fail_contract("dimension_catalog entries must be objects.")
        missing_keys = sorted(REQUIRED_DIMENSION_KEYS - set(item.keys()))
        if missing_keys:
            _fail_contract("dimension_catalog entries are missing keys: " + ", ".join(missing_keys))

        column = str(item["column"]).strip()
        if not column:
            _fail_contract("dimension_catalog column must be non-empty.")
        if column in catalog_by_column:
            _fail_contract(f"dimension_catalog contains duplicate column '{column}'.")

        theme = str(item["theme"]).strip()
        if not theme:
            _fail_contract(f"dimension_catalog column '{column}' must define a non-empty theme.")

        attribute_group = str(item["attribute_group"]).strip()
        if attribute_group not in ATTRIBUTE_GROUPS:
            _fail_contract(
                f"dimension_catalog column '{column}' must use one of: "
                + ", ".join(sorted(ATTRIBUTE_GROUPS))
            )

        salience_column = str(item["salience_column"]).strip()
        valence_column = str(item["valence_column"]).strip()
        if not salience_column or not valence_column:
            _fail_contract(
                f"dimension_catalog column '{column}' must define both salience_column and valence_column."
            )
        if salience_column == valence_column:
            _fail_contract(
                f"dimension_catalog column '{column}' must use distinct salience_column and valence_column values."
            )

        stat_roles = item.get("stat_roles")
        plain_language_definition = str(item.get("plain_language_definition", "")).strip()
        if not isinstance(stat_roles, list) or not stat_roles:
            _fail_contract(f"dimension_catalog column '{column}' must define stat_roles.")
        if not plain_language_definition:
            _fail_contract(f"dimension_catalog column '{column}' must define plain_language_definition.")

        _validate_theory_metadata(column, item)

        catalog_by_column[column] = item
        dimension_columns.append(column)
        pair_columns_by_base[column] = {
            "salience": salience_column,
            "valence": valence_column,
        }
        axis_column_to_base[salience_column] = column
        axis_column_to_base[valence_column] = column
        for role in stat_roles:
            role_name = str(role)
            role_map.setdefault(role_name, []).append(column)
            expanded_role_map.setdefault(role_name, []).extend([salience_column, valence_column])

    missing_axis_columns = sorted(
        column
        for pair in pair_columns_by_base.values()
        for column in pair.values()
        if column not in score_table.columns
    )
    if missing_axis_columns:
        _fail_contract(
            "review_scoring_table.csv is missing paired salience/valence columns declared in dimension_catalog: "
            + ", ".join(missing_axis_columns)
        )

    salience_columns: list[str] = []
    valence_columns: list[str] = []
    numeric_feature_columns: list[str] = []
    for base_column in dimension_columns:
        salience_column = pair_columns_by_base[base_column]["salience"]
        valence_column = pair_columns_by_base[base_column]["valence"]

        salience_values = pd.to_numeric(score_table[salience_column], errors="coerce")
        if salience_values.isna().any():
            _fail_contract(
                f"review_scoring_table.csv column '{salience_column}' must contain numeric salience scores for every review."
            )
        if ((salience_values < 0) | (salience_values > 7)).any():
            _fail_contract(
                f"review_scoring_table.csv column '{salience_column}' must keep every score inside the 0-7 range."
            )
        if not ((salience_values % 1) == 0).all():
            _fail_contract(
                f"review_scoring_table.csv column '{salience_column}' must use integer scores that follow the 0-7 scale."
            )
        score_table[salience_column] = salience_values.astype(int)

        valence_values = _normalize_optional_axis_values(
            score_table[valence_column],
            valence_column,
            max_score=10,
        )
        invalid_present = (score_table[salience_column] == 0) & valence_values.notna()
        if invalid_present.any():
            _fail_contract(
                f"review_scoring_table.csv column '{valence_column}' must be empty when '{salience_column}' is 0."
            )
        invalid_missing = (score_table[salience_column] >= 1) & valence_values.isna()
        if invalid_missing.any():
            _fail_contract(
                f"review_scoring_table.csv column '{valence_column}' must be present when '{salience_column}' is at least 1."
            )
        score_table[valence_column] = valence_values

        salience_columns.append(salience_column)
        valence_columns.append(valence_column)
        numeric_feature_columns.extend([salience_column, valence_column])

    if len(dimension_columns) < 3:
        _fail_contract(
            "review_scoring_table.csv must provide at least 3 scored attributes from dimension_catalog."
        )

    normalized_theme_mapping: dict[str, list[str]] = {}
    column_to_theme: dict[str, str] = {}
    for theme, columns in theme_mapping.items():
        theme_name = str(theme).strip()
        if not theme_name:
            _fail_contract("theme_mapping keys must be non-empty strings.")
        if not isinstance(columns, list) or not columns:
            _fail_contract(f"theme_mapping.{theme_name} must be a non-empty list.")
        normalized_columns = [str(column) for column in columns]
        invalid_columns = sorted(column for column in normalized_columns if column not in catalog_by_column)
        if invalid_columns:
            _fail_contract(
                f"theme_mapping.{theme_name} references columns not present in dimension_catalog: "
                + ", ".join(invalid_columns)
            )
        normalized_theme_mapping[theme_name] = normalized_columns
        for column in normalized_columns:
            if column in column_to_theme:
                _fail_contract(
                    f"theme_mapping maps column '{column}' to multiple themes: "
                    f"{column_to_theme[column]}, {theme_name}."
                )
            column_to_theme[column] = theme_name

    missing_theme_columns = sorted(column for column in dimension_columns if column not in column_to_theme)
    if missing_theme_columns:
        _fail_contract(
            "theme_mapping must cover every dimension_catalog column. Missing columns: "
            + ", ".join(missing_theme_columns)
        )

    mismatched_columns = sorted(
        column
        for column, item in catalog_by_column.items()
        if str(item.get("theme", "")).strip() != column_to_theme.get(column, "")
    )
    if mismatched_columns:
        _fail_contract(
            "theme_mapping must match dimension_catalog.theme for every column. Mismatched columns: "
            + ", ".join(mismatched_columns)
        )

    validated_extraction_summary = _validate_attribute_catalog(
        attribute_catalog,
        score_table,
        catalog_by_column,
        extraction_summary,
    )

    return {
        "dimension_catalog": dimension_catalog,
        "catalog_by_column": catalog_by_column,
        "dimension_columns": dimension_columns,
        "salience_columns": salience_columns,
        "valence_columns": valence_columns,
        "numeric_feature_columns": numeric_feature_columns,
        "pair_columns_by_base": pair_columns_by_base,
        "axis_column_to_base": axis_column_to_base,
        "role_map": {role: list(dict.fromkeys(columns)) for role, columns in role_map.items()},
        "expanded_role_map": {
            role: list(dict.fromkeys(columns)) for role, columns in expanded_role_map.items()
        },
        "theme_mapping": normalized_theme_mapping,
        "unit_id_defaulted": unit_id_defaulted,
        "attribute_extraction_summary": validated_extraction_summary,
    }


def aggregate_review_scoring_table(score_table: Any, contract: dict[str, Any]) -> Any:
    import pandas as pd

    pair_columns_by_base = contract["pair_columns_by_base"]
    paired_columns = {
        column
        for pair in pair_columns_by_base.values()
        for column in pair.values()
    }
    metadata_columns = [
        column
        for column in score_table.columns
        if column not in {"review_id", "review_text"} | paired_columns
    ]
    rows: list[dict[str, Any]] = []
    for unit_id, group in score_table.groupby("unit_id", sort=False):
        row: dict[str, Any] = {"unit_id": unit_id}
        row["brand"] = str(group["brand"].mode().iloc[0])
        row["product"] = str(group["product"].mode().iloc[0])
        row["review_count"] = int(len(group))
        for base_column, pair in pair_columns_by_base.items():
            salience_column = pair["salience"]
            valence_column = pair["valence"]
            salience_mean = round(float(pd.to_numeric(group[salience_column]).mean()), 4)
            mentioned = group.loc[group[salience_column] >= 1, valence_column]
            mentioned_numeric = pd.to_numeric(mentioned, errors="coerce").dropna()
            valence_mean = round(float(mentioned_numeric.mean()), 4) if not mentioned_numeric.empty else 0.0
            row[salience_column] = salience_mean
            row[valence_column] = valence_mean
        for column in metadata_columns:
            if column in {"unit_id", "brand", "product"}:
                continue
            series = group[column].dropna()
            if series.empty:
                continue
            if pd.api.types.is_numeric_dtype(group[column]):
                row[column] = round(float(pd.to_numeric(series).mean()), 4)
            else:
                mode = series.mode()
                row[column] = str(mode.iloc[0]) if not mode.empty else str(series.iloc[0])
        rows.append(row)
    return pd.DataFrame(rows)


def build_segmentation_variables(unit_table: Any, contract: dict[str, Any]) -> Any:
    segmentation_columns = [
        column
        for column in contract["expanded_role_map"].get("segmentation", [])
        if column in unit_table.columns
    ]
    if len(segmentation_columns) < 6:
        for column in contract["numeric_feature_columns"]:
            if column not in segmentation_columns and column in unit_table.columns:
                segmentation_columns.append(column)
            if len(segmentation_columns) >= 6:
                break
    profile_columns = [column for column in unit_table.columns if column.startswith("profile_")]
    passthrough_columns = [
        column
        for column in ["unit_id", "product", *profile_columns, "rating", "brand"]
        if column in unit_table.columns
    ]
    selected_columns = list(dict.fromkeys(passthrough_columns + segmentation_columns))
    return unit_table[selected_columns].copy()


def build_targeting_dataset(
    unit_table: Any,
    segment_assignments: Any,
    contract: dict[str, Any],
    comparison_axes: list[str],
) -> Any:
    targeting_columns = [
        column
        for column in contract["expanded_role_map"].get("current_target", [])
        + contract["expanded_role_map"].get("potential_target", [])
        if column in unit_table.columns
    ]
    targeting_columns.extend(
        _expand_attribute_tokens(
            comparison_axes,
            contract["pair_columns_by_base"],
            contract["axis_column_to_base"],
            set(unit_table.columns),
        )
    )
    if not targeting_columns:
        targeting_columns.extend(contract["numeric_feature_columns"])
    profile_columns = [column for column in unit_table.columns if column.startswith("profile_")]
    extra_columns = [
        column for column in ["unit_id", "brand", "product", *profile_columns] if column in unit_table.columns
    ]
    selected_columns = list(dict.fromkeys(extra_columns + targeting_columns))
    frame = unit_table[selected_columns].copy()
    assignments = segment_assignments.copy()
    if "unit_id" not in assignments.columns or "cluster" not in assignments.columns:
        raise SystemExit("Segmentation assignments must contain unit_id and cluster.")
    merged = frame.merge(assignments[["unit_id", "cluster"]], on="unit_id", how="left")
    if merged["cluster"].isna().any():
        raise SystemExit("Targeting dataset could not align all unit_id rows to segmentation clusters.")
    cluster = merged.pop("cluster")
    merged.insert(0, "cluster", cluster)
    return merged


def build_positioning_scorecard(score_table: Any, contract: dict[str, Any]) -> Any:
    import pandas as pd

    positioning_attributes = contract["role_map"].get("positioning", [])
    if len(positioning_attributes) < 2:
        positioning_attributes = list(contract["dimension_columns"])
    rows: list[dict[str, Any]] = []
    for brand, group in score_table.groupby("brand", sort=True):
        for attribute in positioning_attributes:
            pair = contract["pair_columns_by_base"][attribute]
            salience_column = pair["salience"]
            valence_column = pair["valence"]
            salience_score = round(float(pd.to_numeric(group[salience_column]).mean()), 4)
            mentioned = group.loc[group[salience_column] >= 1, valence_column]
            valence_numeric = pd.to_numeric(mentioned, errors="coerce").dropna()
            valence_score = round(float(valence_numeric.mean()), 4) if not valence_numeric.empty else 0.0
            rows.append(
                {
                    "brand": str(brand),
                    "attribute": attribute,
                    "axis": "salience",
                    "feature": salience_column,
                    "score": salience_score,
                }
            )
            rows.append(
                {
                    "brand": str(brand),
                    "attribute": attribute,
                    "axis": "valence",
                    "feature": valence_column,
                    "score": valence_score,
                }
            )
    return pd.DataFrame(rows)


def derive_role_columns(foundation: dict[str, Any]) -> dict[str, list[str]]:
    role_map: dict[str, list[str]] = {}
    for item in foundation.get("dimension_catalog", []):
        if not isinstance(item, dict):
            continue
        salience_column = str(item.get("salience_column", ""))
        valence_column = str(item.get("valence_column", ""))
        fallback_column = str(item.get("column", ""))
        expanded = [column for column in [salience_column, valence_column] if column] or [fallback_column]
        for role in item.get("stat_roles", []):
            role_name = str(role)
            role_map.setdefault(role_name, []).extend(expanded)
    return {role: list(dict.fromkeys(columns)) for role, columns in role_map.items()}


def build_missing_prereq_output(
    output_dir: Path,
    run_mode: str,
    requested_modules: list[str],
    artifact_paths: list[Path],
    required: list[str],
) -> None:
    _, missing = resolve_required_files(artifact_paths, required)
    next_step_rule = "Provide the missing upstream artifacts before rerunning this stage."
    if {
        "review_scoring_table.csv",
        "review_foundation.json",
        "attribute_catalog.csv",
    } & set(missing):
        next_step_rule = (
            "Scripts accept scored artifacts only; run the review scoring workflow to convert raw reviews "
            "into review_scoring_table.csv, review_foundation.json, and attribute_catalog.csv before rerunning."
        )
    payload = {
        "requested_stage": run_mode,
        "requested_modules": requested_modules,
        "missing_prerequisites": missing,
        "acceptable_upstream_artifacts": missing,
        "available_artifacts": list_available_artifacts(artifact_paths),
        "auto_backfill_allowed": False,
        "next_step_rule": next_step_rule,
    }
    write_json(output_dir / "MissingPrerequisiteOutput.json", payload)
