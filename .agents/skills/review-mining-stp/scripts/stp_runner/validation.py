from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate review-mining-stp outputs.")
    parser.add_argument(
        "--run-mode",
        required=True,
        choices=["full", "segmentation", "targeting", "positioning", "custom"],
    )
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def require_keys(container: dict[str, Any], keys: list[str], container_name: str) -> None:
    for key in keys:
        if key not in container:
            fail(f"{container_name} is missing {key}.")


def require_output_files(output_dir: Path, names: list[str]) -> None:
    missing = [name for name in names if not (output_dir / name).exists()]
    if missing:
        fail(f"Missing required output files: {', '.join(missing)}")


def validate_positioning(output_dir: Path) -> None:
    require_output_files(
        output_dir,
        [
            "perceptual_map.png",
            "perceptual_map_coordinates.csv",
            "positioning_diagnostics.json",
            "strategy_matrix.json",
        ],
    )
    if (output_dir / "perceptual_map.png").stat().st_size == 0:
        fail("perceptual_map.png is empty")

    diagnostics = read_json(output_dir / "positioning_diagnostics.json")
    method = read_json(output_dir / "run_metadata.json").get("positioning_method", "factor_analysis")

    with (output_dir / "perceptual_map_coordinates.csv").open(encoding="utf-8") as handle:
        coordinate_rows = list(csv.DictReader(handle))
    point_types = {row["point_type"] for row in coordinate_rows}
    if "brand" not in point_types:
        fail("Perceptual map must retain brand points.")
    if "ideal" not in point_types:
        fail("Perceptual map must retain ideal point.")

    vector_path = output_dir / "perceptual_map_vectors.csv"
    mds_without_vectors = bool(method == "mds" and diagnostics.get("attribute_vectors_not_defined"))
    if mds_without_vectors:
        if vector_path.exists():
            fail("MDS output must not fabricate attribute vectors.")
    else:
        if vector_path.exists():
            with vector_path.open(encoding="utf-8") as handle:
                vector_rows = list(csv.DictReader(handle))
            if not vector_rows:
                fail("Vector table is empty.")
            for row in vector_rows:
                if float(row["x_start"]) != 0.0 or float(row["y_start"]) != 0.0:
                    fail("Attribute vectors must start at the origin.")

    pod_pop = diagnostics.get("pod_pop", {})
    if "pod" not in pod_pop or "pop" not in pod_pop:
        fail("Positioning diagnostics must contain POD/POP.")

    projection = diagnostics.get("projection_interpretation")
    if not isinstance(projection, dict):
        fail("Positioning diagnostics must contain projection_interpretation.")
    status = projection.get("status")
    if status not in {"defined", "not_available"}:
        fail("projection_interpretation status must be defined or not_available.")
    if method == "factor_analysis":
        if status != "defined":
            fail("Factor-analysis run must provide a defined projection interpretation.")
        summary_rows = projection.get("attribute_projection_summary")
        if not isinstance(summary_rows, list) or not summary_rows:
            fail("Factor-analysis projection interpretation must include attribute projection summary.")
        if not projection.get("importance_interpretation"):
            fail("Factor-analysis projection interpretation must include importance interpretation text.")
    if mds_without_vectors:
        if status != "not_available":
            fail("MDS run without vectors must mark projection interpretation as not_available.")
        if not projection.get("reason"):
            fail("MDS projection interpretation must include an explicit not_available reason.")


def validate_targeting(output_dir: Path) -> None:
    require_output_files(output_dir, ["targeting_results.json", "target_selection_decision.json"])
    targeting = read_json(output_dir / "targeting_results.json")

    profile_significance = targeting.get("profile_significance_summary")
    if not isinstance(profile_significance, dict):
        fail("Targeting results must contain profile_significance_summary.")
    profile_status = profile_significance.get("status")
    if profile_status == "available":
        variables = profile_significance.get("variables")
        if not isinstance(variables, list) or not variables:
            fail("profile_significance_summary.status=available requires non-empty variables.")
        for item in variables:
            if not isinstance(item, dict):
                fail("profile_significance_summary.variables items must be objects.")
            required_keys = {"variable", "method", "p_value", "significant"}
            if not required_keys.issubset(item.keys()):
                fail("Each profile significance result must include variable/method/p_value/significant.")
    elif profile_status == "not_available":
        if not profile_significance.get("reason"):
            fail("profile_significance_summary.status=not_available requires reason.")
    else:
        fail("profile_significance_summary.status must be available or not_available.")

    pairwise_table = targeting.get("pairwise_comparison_table")
    if not isinstance(pairwise_table, list):
        fail("Targeting results must contain pairwise_comparison_table.")
    for row in pairwise_table:
        if not isinstance(row, dict):
            fail("pairwise_comparison_table entries must be objects.")
        required_keys = {"variable", "comparison", "p_value", "significant"}
        if not required_keys.issubset(row.keys()):
            fail("Each pairwise comparison row must include variable/comparison/p_value/significant.")

    significant_anova_variables = set()
    for bucket in ["current_target_market", "potential_target_market"]:
        for record in targeting.get(bucket, []):
            anova = record.get("anova")
            if not isinstance(anova, dict):
                continue
            p_value = float(anova.get("p_value", 1.0))
            if p_value < 0.05:
                significant_anova_variables.add(str(record.get("variable")))
    pairwise_variables = {str(row.get("variable")) for row in pairwise_table}
    missing_pairwise = sorted(
        variable
        for variable in significant_anova_variables
        if variable and variable not in pairwise_variables
    )
    if missing_pairwise:
        fail(
            "Missing pairwise comparisons for ANOVA-significant variables: "
            + ", ".join(missing_pairwise)
        )


def _load_review_lookup(output_dir: Path) -> dict[str, str]:
    score_table_path = output_dir / "review_scoring_table.csv"
    if not score_table_path.exists():
        return {}
    with score_table_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {
            str(row["review_id"]): str(row["review_text"])
            for row in reader
            if row.get("review_id")
        }


def _validate_described_items(
    items: Any,
    container_name: str,
    required_keys: set[str],
) -> None:
    if not isinstance(items, list) or not items:
        fail(f"{container_name} must be a non-empty list.")
    for item in items:
        if not isinstance(item, dict):
            fail(f"{container_name} entries must be objects.")
        if not required_keys.issubset(item.keys()):
            fail(
                f"{container_name} entries must include: "
                + ", ".join(sorted(required_keys))
            )


def _validate_evidence_quotes(
    summary: dict[str, Any],
    summary_name: str,
    review_lookup: dict[str, str],
    *,
    min_count_when_available: int,
    max_count_when_available: int | None = None,
) -> None:
    if "evidence_quotes" not in summary:
        fail(f"{summary_name} is missing evidence_quotes.")
    quotes = summary.get("evidence_quotes")
    if not isinstance(quotes, list):
        fail(f"{summary_name}.evidence_quotes must be a list.")
    status = summary.get("evidence_quote_status", "")
    if review_lookup:
        if len(quotes) < min_count_when_available:
            fail(
                f"{summary_name}.evidence_quotes must contain at least {min_count_when_available} traceable quotes when review evidence is available."
            )
        if max_count_when_available is not None and len(quotes) > max_count_when_available:
            fail(
                f"{summary_name}.evidence_quotes must contain no more than {max_count_when_available} traceable quotes when review evidence is available."
            )
    for quote in quotes:
        if not isinstance(quote, dict):
            fail(f"{summary_name}.evidence_quotes entries must be objects.")
        required_keys = {"review_id", "quote_text", "why_this_quote_matters", "linked_items"}
        if not required_keys.issubset(quote.keys()):
            fail(
                f"{summary_name}.evidence_quotes entries must include: "
                + ", ".join(sorted(required_keys))
            )
        if not isinstance(quote.get("linked_items"), list) or not quote["linked_items"]:
            fail(f"{summary_name}.evidence_quotes.linked_items must be a non-empty list.")
        if review_lookup:
            review_id = str(quote["review_id"])
            if review_id not in review_lookup:
                fail(f"{summary_name} evidence quote review_id '{review_id}' does not exist in review_scoring_table.csv.")
            if str(quote["quote_text"]) != review_lookup[review_id]:
                fail(f"{summary_name} evidence quote text for review_id '{review_id}' does not match review_scoring_table.csv.")
    if review_lookup and status != "available":
        fail(f"{summary_name}.evidence_quote_status must be available when review evidence exists.")
    if not review_lookup and quotes:
        fail(f"{summary_name}.evidence_quotes must be empty when review evidence is not available.")


def _validate_reproducibility_package(package: Any, container_name: str) -> None:
    required_keys = {
        "input_artifacts",
        "input_columns",
        "filters",
        "preprocessing",
        "analysis_steps",
        "decision_rule",
    }
    if not isinstance(package, dict):
        fail(f"{container_name} must be an object.")
    if set(package.keys()) != required_keys:
        fail(f"{container_name} must contain exactly: " + ", ".join(sorted(required_keys)))
    if not isinstance(package["input_artifacts"], list) or not package["input_artifacts"]:
        fail(f"{container_name}.input_artifacts must be a non-empty list.")
    if not isinstance(package["input_columns"], list) or not package["input_columns"]:
        fail(f"{container_name}.input_columns must be a non-empty list.")
    for key in ["filters", "preprocessing", "analysis_steps"]:
        if not isinstance(package[key], list):
            fail(f"{container_name}.{key} must be a list.")
    if not package["analysis_steps"]:
        fail(f"{container_name}.analysis_steps must be non-empty.")
    if not str(package["decision_rule"]).strip():
        fail(f"{container_name}.decision_rule must be non-empty.")


def _validate_statistical_results(package: Any, container_name: str) -> None:
    required_keys = {
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
        "axis_breakdown",
    }
    if not isinstance(package, dict):
        fail(f"{container_name} must be an object.")
    if set(package.keys()) != required_keys:
        fail(f"{container_name} must contain exactly: " + ", ".join(sorted(required_keys)))
    if not str(package["method_family"]).strip():
        fail(f"{container_name}.method_family must be non-empty.")
    if not str(package["test_or_model"]).strip():
        fail(f"{container_name}.test_or_model must be non-empty.")
    if package["sample_size"] is None:
        fail(f"{container_name}.sample_size must not be null.")
    if not str(package["result_direction"]).strip():
        fail(f"{container_name}.result_direction must be non-empty.")
    axis_breakdown = package["axis_breakdown"]
    if not isinstance(axis_breakdown, dict):
        fail(f"{container_name}.axis_breakdown must be an object.")
    if set(axis_breakdown.keys()) != {"salience", "valence"}:
        fail(f"{container_name}.axis_breakdown must contain salience and valence.")
    for axis_name, axis_payload in axis_breakdown.items():
        if axis_payload is None:
            continue
        if not isinstance(axis_payload, dict):
            fail(f"{container_name}.axis_breakdown.{axis_name} must be an object or null.")
        nested = dict(axis_payload)
        nested.setdefault("axis_breakdown", {"salience": None, "valence": None})
        _validate_statistical_results(nested, f"{container_name}.axis_breakdown.{axis_name}")


def _validate_themes_used(items: Any, container_name: str) -> None:
    if not isinstance(items, list) or not items:
        fail(f"{container_name} must be a non-empty list.")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"{container_name}[{index}] must be an object.")
        require_keys(item, ["theme", "supporting_items"], f"{container_name}[{index}]")
        if not str(item["theme"]).strip():
            fail(f"{container_name}[{index}].theme must be non-empty.")
        if not isinstance(item["supporting_items"], list) or not item["supporting_items"]:
            fail(f"{container_name}[{index}].supporting_items must be a non-empty list.")


def _validate_subtheories_used(items: Any, container_name: str) -> None:
    if not isinstance(items, list) or not items:
        fail(f"{container_name} must be a non-empty list.")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"{container_name}[{index}] must be an object.")
        require_keys(
            item,
            ["family", "subtheory", "label", "source", "supporting_item"],
            f"{container_name}[{index}]",
        )
        for key in ["family", "subtheory", "label", "source", "supporting_item"]:
            if not str(item[key]).strip():
                fail(f"{container_name}[{index}].{key} must be non-empty.")


def _validate_theme_coverage_summary(items: Any, container_name: str) -> None:
    if not isinstance(items, list) or not items:
        fail(f"{container_name} must be a non-empty list.")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"{container_name}[{index}] must be an object.")
        require_keys(
            item,
            ["theme", "supporting_items", "related_findings", "evidence_status"],
            f"{container_name}[{index}]",
        )
        if not str(item["theme"]).strip():
            fail(f"{container_name}[{index}].theme must be non-empty.")
        if not isinstance(item["supporting_items"], list) or not item["supporting_items"]:
            fail(f"{container_name}[{index}].supporting_items must be a non-empty list.")
        if not isinstance(item["related_findings"], list):
            fail(f"{container_name}[{index}].related_findings must be a list.")
        if str(item["evidence_status"]) not in {"covered", "not_evidenced"}:
            fail(f"{container_name}[{index}].evidence_status must be covered or not_evidenced.")


def _validate_theory_coverage_summary(items: Any, container_name: str) -> None:
    if not isinstance(items, list) or not items:
        fail(f"{container_name} must be a non-empty list.")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"{container_name}[{index}] must be an object.")
        require_keys(
            item,
            [
                "theory_family",
                "covered_subtheories",
                "not_evidenced_subtheories",
                "supporting_items",
                "evidence_status",
            ],
            f"{container_name}[{index}]",
        )
        if not str(item["theory_family"]).strip():
            fail(f"{container_name}[{index}].theory_family must be non-empty.")
        for key in ["covered_subtheories", "not_evidenced_subtheories", "supporting_items"]:
            if not isinstance(item[key], list):
                fail(f"{container_name}[{index}].{key} must be a list.")
        if str(item["evidence_status"]) not in {"covered", "not_evidenced", "legacy_inferred", "mixed"}:
            fail(
                f"{container_name}[{index}].evidence_status must be covered, not_evidenced, legacy_inferred, or mixed."
            )


def _validate_findings(
    findings: Any,
    container_name: str,
    review_lookup: dict[str, str],
) -> None:
    required_keys = {
        "finding_id",
        "finding_statement",
        "business_implication",
        "methods_used",
        "theories_used",
        "axes_used",
        "themes_used",
        "subtheories_used",
        "reproducibility",
        "statistical_results",
        "plain_language_explanation",
        "evidence_quotes",
    }
    if not isinstance(findings, list) or not findings:
        fail(f"{container_name} must be a non-empty list.")
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            fail(f"{container_name}[{index}] must be an object.")
        if not required_keys.issubset(finding.keys()):
            fail(
                f"{container_name}[{index}] is missing keys: "
                + ", ".join(sorted(required_keys - set(finding.keys())))
            )
        for text_key in ["finding_id", "finding_statement", "business_implication", "plain_language_explanation"]:
            if not str(finding[text_key]).strip():
                fail(f"{container_name}[{index}].{text_key} must be non-empty.")
        if str(finding.get("axes_used")) not in {"salience", "valence", "mixed"}:
            fail(f"{container_name}[{index}].axes_used must be salience, valence, or mixed.")
        _validate_described_items(
            finding.get("methods_used"),
            f"{container_name}[{index}].methods_used",
            {"name", "description"},
        )
        _validate_described_items(
            finding.get("theories_used"),
            f"{container_name}[{index}].theories_used",
            {"name", "description"},
        )
        _validate_themes_used(
            finding.get("themes_used"),
            f"{container_name}[{index}].themes_used",
        )
        _validate_subtheories_used(
            finding.get("subtheories_used"),
            f"{container_name}[{index}].subtheories_used",
        )
        _validate_reproducibility_package(
            finding.get("reproducibility"),
            f"{container_name}[{index}].reproducibility",
        )
        _validate_statistical_results(
            finding.get("statistical_results"),
            f"{container_name}[{index}].statistical_results",
        )
        _validate_evidence_quotes(
            {"evidence_quotes": finding.get("evidence_quotes"), "evidence_quote_status": "available" if review_lookup else "not_available"},
            f"{container_name}[{index}]",
            review_lookup,
            min_count_when_available=1,
        )


def _validate_stage_report_contract(
    summary: dict[str, Any],
    summary_name: str,
    review_lookup: dict[str, str],
) -> None:
    require_keys(
        summary,
        [
            "what_this_section_is_doing",
            "axis_modeling_summary",
            "methods_used",
            "theories_used",
            "theme_coverage_summary",
            "theory_coverage_summary",
            "plain_language_explanation",
            "evidence_quote_status",
            "evidence_quote_reason",
            "evidence_quotes",
            "findings",
        ],
        summary_name,
    )
    if not summary.get("what_this_section_is_doing"):
        fail(f"{summary_name}.what_this_section_is_doing must be non-empty.")
    if not summary.get("plain_language_explanation"):
        fail(f"{summary_name}.plain_language_explanation must be non-empty.")
    axis_modeling_summary = summary.get("axis_modeling_summary")
    if not isinstance(axis_modeling_summary, dict):
        fail(f"{summary_name}.axis_modeling_summary must be an object.")
    require_keys(
        axis_modeling_summary,
        [
            "axes_mode",
            "salience_columns_used",
            "valence_columns_used",
            "modeling_rule",
            "plain_language_explanation",
        ],
        f"{summary_name}.axis_modeling_summary",
    )
    if str(axis_modeling_summary["axes_mode"]) not in {"salience", "valence", "mixed"}:
        fail(f"{summary_name}.axis_modeling_summary.axes_mode must be salience, valence, or mixed.")
    for key in ["salience_columns_used", "valence_columns_used"]:
        if not isinstance(axis_modeling_summary[key], list):
            fail(f"{summary_name}.axis_modeling_summary.{key} must be a list.")
    for key in ["modeling_rule", "plain_language_explanation"]:
        if not str(axis_modeling_summary[key]).strip():
            fail(f"{summary_name}.axis_modeling_summary.{key} must be non-empty.")
    _validate_described_items(summary.get("methods_used"), f"{summary_name}.methods_used", {"name", "description"})
    _validate_described_items(summary.get("theories_used"), f"{summary_name}.theories_used", {"name", "description"})
    _validate_theme_coverage_summary(
        summary.get("theme_coverage_summary"),
        f"{summary_name}.theme_coverage_summary",
    )
    _validate_theory_coverage_summary(
        summary.get("theory_coverage_summary"),
        f"{summary_name}.theory_coverage_summary",
    )
    _validate_evidence_quotes(summary, summary_name, review_lookup, min_count_when_available=2, max_count_when_available=3)
    _validate_findings(summary.get("findings"), f"{summary_name}.findings", review_lookup)


def _validate_attribute_extraction_summary(
    summary: dict[str, Any],
    review_lookup: dict[str, str],
) -> None:
    require_keys(
        summary,
        [
            "target_minimum",
            "actual_count",
            "shortfall_reason",
            "themes_discovered",
            "attribute_group_summary",
            "representative_attributes",
        ],
        "attribute_extraction_summary",
    )
    if not isinstance(summary["themes_discovered"], list):
        fail("attribute_extraction_summary.themes_discovered must be a list.")
    if not isinstance(summary["attribute_group_summary"], list):
        fail("attribute_extraction_summary.attribute_group_summary must be a list.")
    if not isinstance(summary["representative_attributes"], list):
        fail("attribute_extraction_summary.representative_attributes must be a list.")
    for index, row in enumerate(summary["attribute_group_summary"]):
        if not isinstance(row, dict):
            fail(f"attribute_extraction_summary.attribute_group_summary[{index}] must be an object.")
        require_keys(
            row,
            ["attribute_group", "attribute_count"],
            f"attribute_extraction_summary.attribute_group_summary[{index}]",
        )
    for index, row in enumerate(summary["representative_attributes"]):
        if not isinstance(row, dict):
            fail(f"attribute_extraction_summary.representative_attributes[{index}] must be an object.")
        require_keys(
            row,
            [
                "attribute_key",
                "label",
                "theme",
                "attribute_group",
                "mention_count",
                "example_review_id",
                "example_quote",
            ],
            f"attribute_extraction_summary.representative_attributes[{index}]",
        )
        if review_lookup:
            review_id = str(row["example_review_id"])
            if review_id not in review_lookup:
                fail(
                    "attribute_extraction_summary representative attribute example_review_id "
                    f"'{review_id}' does not exist in review_scoring_table.csv."
                )
            if str(row["example_quote"]) != review_lookup[review_id]:
                fail(
                    "attribute_extraction_summary representative attribute example_quote must "
                    "exactly match review_scoring_table.csv review_text."
                )


def validate_appendix(output_dir: Path, run_mode: str) -> None:
    require_output_files(output_dir, ["appendix.json", "report.md", "run_metadata.json"])
    appendix = read_json(output_dir / "appendix.json")
    review_lookup = _load_review_lookup(output_dir)
    if "execution_scope" not in appendix:
        fail("Appendix is missing execution_scope.")
    execution_scope = appendix["execution_scope"]
    if not isinstance(execution_scope, dict):
        fail("execution_scope must be an object.")
    require_keys(
        execution_scope,
        [
            "run_mode",
            "requested_modules",
            "modules_executed",
            "auto_backfilled_modules",
            "upstream_artifacts_used",
            "emitted_intermediate_artifacts",
            "comparison_axes",
            "brands",
            "positioning_method_used",
            "cluster_threshold",
            "reruns_performed",
            "final_k",
            "scope_limits",
        ],
        "execution_scope",
    )
    if run_mode == "full":
        for artifact_name in [
            "review_scoring_table.csv",
            "review_foundation.json",
            "attribute_catalog.csv",
            "analysis_context.json",
            "brands.json",
            "ideal_point.json",
        ]:
            if artifact_name not in execution_scope["upstream_artifacts_used"]:
                fail(f"execution_scope.upstream_artifacts_used must include {artifact_name}.")
        expected_emitted = {
            "segmentation_variables.csv",
            "targeting_dataset.csv",
            "positioning_scorecard.csv",
        }
        if set(execution_scope.get("emitted_intermediate_artifacts", [])) != expected_emitted:
            fail("Full run must record emitted_intermediate_artifacts for all three generated statistical artifacts.")

    if run_mode in {"full", "segmentation"} and not appendix.get("segmentation_summary"):
        fail("Appendix is missing segmentation_summary.")
    if run_mode in {"full", "targeting"} and not appendix.get("targeting_summary"):
        fail("Appendix is missing targeting_summary.")
    if run_mode in {"full", "positioning"} and not appendix.get("positioning_summary"):
        fail("Appendix is missing positioning_summary.")
    if run_mode == "full" and not appendix.get("attribute_extraction_summary"):
        fail("Appendix is missing attribute_extraction_summary.")

    attribute_extraction_summary = appendix.get("attribute_extraction_summary")
    if isinstance(attribute_extraction_summary, dict):
        _validate_attribute_extraction_summary(attribute_extraction_summary, review_lookup)

    segmentation_summary = appendix.get("segmentation_summary")
    if isinstance(segmentation_summary, dict):
        _validate_stage_report_contract(segmentation_summary, "segmentation_summary", review_lookup)
        require_keys(
            segmentation_summary,
            [
                "people_insights",
                "product_triggers",
                "context_scenarios",
                "system1_system2_split",
                "maslow_keywords",
                "segment_variable_table",
                "cluster_share_table",
                "segment_profiles",
                "consumer_portrait_narrative",
            ],
            "segmentation_summary",
        )
        cluster_selection = segmentation_summary.get("cluster_selection", {})
        if isinstance(cluster_selection, dict):
            require_keys(
                cluster_selection,
                ["cluster_threshold", "reruns_performed", "final_k"],
                "segmentation_summary.cluster_selection",
            )

    targeting_summary = appendix.get("targeting_summary")
    if isinstance(targeting_summary, dict):
        _validate_stage_report_contract(targeting_summary, "targeting_summary", review_lookup)
        require_keys(
            targeting_summary,
            [
                "profile_significance_summary",
                "pairwise_comparison_table",
                "target_selection_decision",
                "target_selection_rationale",
            ],
            "targeting_summary",
        )
        decision = targeting_summary.get("target_selection_decision", {})
        if isinstance(decision, dict):
            require_keys(
                decision,
                [
                    "priority_segments",
                    "secondary_segments",
                    "deprioritized_segments",
                    "comparison_axes_used",
                ],
                "targeting_summary.target_selection_decision",
            )

    positioning_summary = appendix.get("positioning_summary")
    if isinstance(positioning_summary, dict):
        _validate_stage_report_contract(positioning_summary, "positioning_summary", review_lookup)
        require_keys(
            positioning_summary,
            [
                "perceptual_map_figure",
                "perceptual_map_coordinate_table",
                "perceptual_map_method",
                "perceptual_map_interpretation",
                "dynamic_scorecard_summary",
            ],
            "positioning_summary",
        )
        dynamic_summary = positioning_summary.get("dynamic_scorecard_summary", {})
        if isinstance(dynamic_summary, dict):
            require_keys(
                dynamic_summary,
                [
                    "highest_scoring_attributes",
                    "lowest_scoring_attributes",
                    "ideal_point_distance_summary",
                    "importance_performance_gap",
                    "reliability_analysis",
                    "validity_analysis",
                ],
                "positioning_summary.dynamic_scorecard_summary",
            )
        diagnostics = positioning_summary.get("positioning_diagnostics", {})
        if isinstance(diagnostics, dict):
            competition_landscape = diagnostics.get("competition_landscape", [])
            for row in competition_landscape:
                if not {"brand_a", "brand_b", "distance"}.issubset(row.keys()):
                    fail("competition_landscape rows must include brand_a/brand_b/distance.")

    for optional_key in ["proactive_marketing_notes", "usp_translation_candidates"]:
        if optional_key in appendix and not isinstance(appendix[optional_key], list):
            fail(f"{optional_key} must be a list when present.")
    if "evidence" in appendix and not isinstance(appendix["evidence"], list):
        fail("evidence must be a list when present.")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)

    if (output_dir / "MissingPrerequisiteOutput.json").exists():
        print("Validation skipped because output is a MissingPrerequisiteOutput artifact.")
        return

    require_output_files(output_dir, ["report.md", "appendix.json", "run_metadata.json"])

    if args.run_mode == "full":
        require_output_files(
            output_dir,
            [
                "review_scoring_table.csv",
                "review_foundation.json",
                "attribute_catalog.csv",
                "analysis_context.json",
                "brands.json",
                "ideal_point.json",
                "segment_profiles.json",
                "segment_summary.md",
                "targeting_results.json",
                "target_selection_decision.json",
                "segmentation_variables.csv",
                "targeting_dataset.csv",
                "positioning_scorecard.csv",
            ],
        )
        validate_targeting(output_dir)
        validate_positioning(output_dir)
    elif args.run_mode == "segmentation":
        require_output_files(output_dir, ["segment_profiles.json", "segment_summary.md"])
    elif args.run_mode == "targeting":
        validate_targeting(output_dir)
    elif args.run_mode == "positioning":
        validate_positioning(output_dir)

    validate_appendix(output_dir, args.run_mode)
    print("Validation passed.")
