from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .constants import ALLOWED_CUSTOM_MODULES, RUN_MODE_MODULES
from .io import (
    aggregate_review_scoring_table,
    build_missing_prereq_output,
    build_positioning_scorecard,
    build_segmentation_variables,
    build_targeting_dataset,
    find_artifact,
    load_analysis_context,
    read_json,
    validate_canonical_inputs,
    write_json,
)
from .positioning import load_positioning_inputs, run_positioning
from .reporting import (
    build_attribute_extraction_summary_contract,
    build_stage_report_contract,
    write_execution_files,
)
from .segmentation import build_segment_summary, load_segmentation_inputs, run_segmentation
from .targeting import load_targeting_inputs, run_targeting


FULL_CANONICAL_REQUIRED = [
    "review_scoring_table.csv",
    "review_foundation.json",
    "attribute_catalog.csv",
    "analysis_context.json",
    "brands.json",
    "ideal_point.json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run review-mining-stp analysis from artifacts.")
    parser.add_argument(
        "--run-mode",
        required=True,
        choices=["full", "segmentation", "targeting", "positioning", "custom"],
    )
    parser.add_argument("--requested-modules", default="", help="Comma-separated custom modules")
    parser.add_argument("--input-dir", required=True, help="Path to artifact directory")
    parser.add_argument("--output-dir", required=True, help="Path to output directory")
    parser.add_argument(
        "--upstream-artifacts-dir",
        help="Optional second artifact directory used for stage-specific runs",
    )
    parser.add_argument(
        "--positioning-method",
        choices=["factor_analysis", "mds"],
        default="factor_analysis",
    )
    parser.add_argument("--ideal-point-file", help="Optional explicit ideal point JSON path")
    parser.add_argument("--brands-file", help="Optional explicit brands JSON path")
    return parser.parse_args()


def ensure_dependencies() -> None:
    try:
        import matplotlib  # noqa: F401
        import numpy  # noqa: F401
        import pandas  # noqa: F401
        import scipy  # noqa: F401
        import sklearn  # noqa: F401
        import statsmodels  # noqa: F401
    except ImportError as exc:
        print(
            "Missing dependency. Install required packages from requirements.txt before running.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def parse_requested_modules(args: argparse.Namespace) -> list[str]:
    if args.run_mode != "custom":
        return list(RUN_MODE_MODULES[args.run_mode])
    modules = [item.strip() for item in args.requested_modules.split(",") if item.strip()]
    if not modules:
        raise SystemExit("--requested-modules is required when --run-mode custom.")
    unknown = [item for item in modules if item not in ALLOWED_CUSTOM_MODULES]
    if unknown:
        raise SystemExit(f"Unsupported custom modules: {', '.join(sorted(unknown))}")
    return modules


def build_recommended_extensions(
    targeting_summary: dict[str, Any] | None,
    positioning_summary: dict[str, Any] | None,
) -> tuple[list[str], list[dict[str, Any]]]:
    proactive_marketing_notes: list[str] = []
    usp_translation_candidates: list[dict[str, Any]] = []

    if targeting_summary:
        decision = targeting_summary.get("target_selection_decision", {})
        selected_cluster = decision.get("selected_cluster", "selected segment")
        proactive_marketing_notes.append(
            f"Prioritize demand-shaping messages for {selected_cluster} instead of only reactive conversion tactics."
        )

    if positioning_summary:
        pod = positioning_summary.get("positioning_diagnostics", {}).get("pod_pop", {}).get("pod", [])
        if pod:
            proactive_marketing_notes.append(
                "Use strongest POD attributes to define category meaning, not just compare with current competitors."
            )
        projection = positioning_summary.get("projection_interpretation", {})
        if projection.get("status") == "defined":
            proactive_marketing_notes.append(
                "Focus creative direction on attributes with the highest ideal-point projection scores."
            )

    if targeting_summary and positioning_summary:
        decision = targeting_summary.get("target_selection_decision", {})
        persona = decision.get("persona", "")
        selected_cluster = decision.get("selected_cluster", "selected segment")
        pod = positioning_summary.get("positioning_diagnostics", {}).get("pod_pop", {}).get("pod", [])
        for attribute in pod[:3]:
            usp_translation_candidates.append(
                {
                    "target_cluster": selected_cluster,
                    "usp_attribute": attribute,
                    "usp_statement": f"For {selected_cluster}, lead with {attribute} as the primary differentiation claim.",
                    "persona_anchor": persona,
                }
            )

    return proactive_marketing_notes, usp_translation_candidates


def _maybe_prepare_canonical_inputs(artifact_paths: list[Path]) -> dict[str, Any] | None:
    import pandas as pd

    score_path = find_artifact(artifact_paths, "review_scoring_table.csv")
    foundation_path = find_artifact(artifact_paths, "review_foundation.json")
    attribute_catalog_path = find_artifact(artifact_paths, "attribute_catalog.csv")
    if score_path is None or foundation_path is None or attribute_catalog_path is None:
        return None

    score_table = pd.read_csv(score_path)
    foundation = read_json(foundation_path)
    attribute_catalog = pd.read_csv(attribute_catalog_path)
    contract = validate_canonical_inputs(score_table, foundation, attribute_catalog)
    unit_table = aggregate_review_scoring_table(score_table, contract)
    segmentation_frame = build_segmentation_variables(unit_table, contract)
    positioning_scorecard = build_positioning_scorecard(score_table, contract)
    return {
        "score_table": score_table,
        "foundation": foundation,
        "attribute_catalog": attribute_catalog,
        "contract": contract,
        "unit_table": unit_table,
        "segmentation_frame": segmentation_frame,
        "positioning_scorecard": positioning_scorecard,
    }


def _write_frame(path: Path, frame: Any) -> None:
    frame.to_csv(path, index=False, encoding="utf-8")


def _load_reporting_foundation(
    artifact_paths: list[Path],
    canonical_inputs: dict[str, Any] | None,
    generated_segmentation: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if canonical_inputs:
        return canonical_inputs["foundation"]
    foundation_path = find_artifact(artifact_paths, "review_foundation.json")
    if foundation_path is not None:
        return read_json(foundation_path)
    if generated_segmentation and isinstance(generated_segmentation.get("review_foundation"), dict):
        return generated_segmentation["review_foundation"]
    return None


def _load_reporting_attribute_catalog(
    artifact_paths: list[Path],
    canonical_inputs: dict[str, Any] | None,
) -> Any | None:
    if canonical_inputs:
        return canonical_inputs["attribute_catalog"]
    attribute_catalog_path = find_artifact(artifact_paths, "attribute_catalog.csv")
    if attribute_catalog_path is None:
        return None
    import pandas as pd

    return pd.read_csv(attribute_catalog_path)


def _build_unit_cluster_map(generated_segmentation: dict[str, Any] | None) -> dict[str, str]:
    if not generated_segmentation:
        return {}
    mappings: dict[str, str] = {}
    for item in generated_segmentation.get("segment_assignments", []):
        if not isinstance(item, dict):
            continue
        cluster = item.get("cluster")
        if not cluster:
            continue
        identifier = None
        if "unit_id" in item:
            identifier = item["unit_id"]
        else:
            for key, value in item.items():
                if key != "cluster" and key.endswith("_id"):
                    identifier = value
                    break
        if identifier is not None:
            mappings[str(identifier)] = str(cluster)
    return mappings


def main() -> None:
    ensure_dependencies()
    args = parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths = [Path(args.input_dir)]
    if args.upstream_artifacts_dir:
        artifact_paths.append(Path(args.upstream_artifacts_dir))

    requested_modules = parse_requested_modules(args)
    analysis_context = load_analysis_context(artifact_paths)
    canonical_inputs = _maybe_prepare_canonical_inputs(artifact_paths)

    if args.run_mode == "full":
        missing = [name for name in FULL_CANONICAL_REQUIRED if find_artifact(artifact_paths, name) is None]
        if missing:
            build_missing_prereq_output(
                output_dir,
                args.run_mode,
                requested_modules,
                artifact_paths,
                FULL_CANONICAL_REQUIRED,
            )
            return
        if canonical_inputs is None:
            raise SystemExit("Full run requires valid review_scoring_table.csv and review_foundation.json.")

    upstream_artifacts_used: list[str] = []
    modules_executed: list[str] = []
    emitted_intermediate_artifacts: list[str] = []

    brands: list[str] = []
    brands_path = Path(args.brands_file) if args.brands_file else find_artifact(artifact_paths, "brands.json")
    if brands_path and brands_path.exists():
        brands = list(read_json(brands_path).get("brands", []))
    ideal_path = Path(args.ideal_point_file) if args.ideal_point_file else find_artifact(artifact_paths, "ideal_point.json")

    if args.run_mode == "full" and canonical_inputs:
        _write_frame(output_dir / "review_scoring_table.csv", canonical_inputs["score_table"])
        write_json(output_dir / "review_foundation.json", canonical_inputs["foundation"])
        _write_frame(output_dir / "attribute_catalog.csv", canonical_inputs["attribute_catalog"])
        write_json(output_dir / "analysis_context.json", analysis_context)
        if brands_path and brands_path.exists():
            write_json(output_dir / "brands.json", read_json(brands_path))
        if ideal_path and ideal_path.exists():
            write_json(output_dir / "ideal_point.json", read_json(ideal_path))

    appendix: dict[str, Any] = {
        "execution_scope": {
            "run_mode": args.run_mode,
            "requested_modules": requested_modules,
            "modules_executed": [],
            "auto_backfilled_modules": [],
            "upstream_artifacts_used": [],
            "emitted_intermediate_artifacts": [],
            "comparison_axes": list(analysis_context.get("comparison_axes", [])),
            "brands": brands,
            "positioning_method_used": args.positioning_method,
            "cluster_threshold": 0.05,
            "reruns_performed": 0,
            "final_k": None,
            "scope_limits": list(analysis_context.get("scope_limits", [])),
        },
        "attribute_extraction_summary": None,
        "segmentation_summary": None,
        "targeting_summary": None,
        "positioning_summary": None,
        "integrated_stp_actions": [],
        "proactive_marketing_notes": [],
        "usp_translation_candidates": [],
        "risks_bias_confidence_notes": [
            "Upstream scored artifacts are assumed to be generated by the review scoring workflow.",
            "Statistical outputs are decision support, not causal proof.",
        ],
        "evidence": [],
    }

    generated_segmentation: dict[str, Any] | None = None
    prepared_targeting_dataset = None

    segmentation_needed = any(
        module in requested_modules
        for module in ["review-foundation", "segmentation-variables", "segment-clustering", "segment-profiles"]
    ) or args.run_mode == "full"
    targeting_needed = any(
        module in requested_modules
        for module in ["current-target-market", "potential-target-market", "target-selection"]
    ) or args.run_mode == "full"
    positioning_needed = any(
        module in requested_modules
        for module in ["positioning-scorecard", "perceptual-map", "positioning-diagnostics", "strategy-matrix"]
    ) or args.run_mode == "full"

    if canonical_inputs and args.run_mode in {"full", "segmentation"} and segmentation_needed:
        _write_frame(output_dir / "segmentation_variables.csv", canonical_inputs["segmentation_frame"])
        emitted_intermediate_artifacts.append("segmentation_variables.csv")

    if canonical_inputs and args.run_mode in {"full", "positioning"} and positioning_needed:
        _write_frame(output_dir / "positioning_scorecard.csv", canonical_inputs["positioning_scorecard"])
        emitted_intermediate_artifacts.append("positioning_scorecard.csv")

    if segmentation_needed:
        segmentation_inputs = None
        if canonical_inputs and args.run_mode in {"full", "segmentation"}:
            segmentation_inputs = (
                canonical_inputs["foundation"],
                canonical_inputs["segmentation_frame"],
            )
            for artifact_name in ["review_scoring_table.csv", "review_foundation.json", "attribute_catalog.csv", "analysis_context.json"]:
                if find_artifact(artifact_paths, artifact_name):
                    upstream_artifacts_used.append(artifact_name)
        else:
            segmentation_inputs = load_segmentation_inputs(artifact_paths)

        if segmentation_inputs is None:
            build_missing_prereq_output(
                output_dir,
                args.run_mode,
                requested_modules,
                artifact_paths,
                ["review_foundation.json", "segmentation_variables.csv"],
            )
            return

        generated_segmentation = run_segmentation(*segmentation_inputs)
        write_json(output_dir / "segment_profiles.json", generated_segmentation)
        (output_dir / "segment_summary.md").write_text(
            build_segment_summary(generated_segmentation),
            encoding="utf-8",
        )
        appendix["segmentation_summary"] = generated_segmentation
        modules_executed.extend(
            ["review-foundation", "segmentation-variables", "segment-clustering", "segment-profiles"]
        )
        if not canonical_inputs or args.run_mode not in {"full", "segmentation"}:
            for artifact_name in ["review_foundation.json", "segmentation_variables.csv", "analysis_context.json"]:
                if find_artifact(artifact_paths, artifact_name):
                    upstream_artifacts_used.append(artifact_name)

    if targeting_needed:
        targeting_inputs = None
        role_columns = None
        if args.run_mode == "full" and canonical_inputs and generated_segmentation:
            import pandas as pd

            prepared_targeting_dataset = build_targeting_dataset(
                canonical_inputs["unit_table"],
                pd.DataFrame(generated_segmentation.get("segment_assignments", [])),
                canonical_inputs["contract"],
                list(analysis_context.get("comparison_axes", [])),
            )
            _write_frame(output_dir / "targeting_dataset.csv", prepared_targeting_dataset)
            emitted_intermediate_artifacts.append("targeting_dataset.csv")
            targeting_inputs = (
                prepared_targeting_dataset,
                generated_segmentation,
                canonical_inputs["contract"]["expanded_role_map"],
            )
            for artifact_name in ["review_scoring_table.csv", "review_foundation.json", "attribute_catalog.csv", "analysis_context.json"]:
                if find_artifact(artifact_paths, artifact_name):
                    upstream_artifacts_used.append(artifact_name)
        else:
            targeting_inputs = load_targeting_inputs(artifact_paths, generated_segmentation)

        if targeting_inputs is None:
            build_missing_prereq_output(
                output_dir,
                args.run_mode,
                requested_modules,
                artifact_paths,
                ["segment_profiles.json", "targeting_dataset.csv"],
            )
            return

        dataset, segmentation_payload, role_columns = targeting_inputs
        targeting = run_targeting(
            dataset,
            segmentation_payload,
            list(analysis_context.get("comparison_axes", [])),
            role_columns,
        )
        write_json(output_dir / "targeting_results.json", targeting)
        write_json(output_dir / "target_selection_decision.json", targeting["target_selection_decision"])
        appendix["targeting_summary"] = targeting
        appendix["integrated_stp_actions"].append(
            {
                "stage": "targeting",
                "selected_cluster": targeting["target_selection_decision"]["selected_cluster"],
                "rationale": targeting["target_selection_rationale"],
            }
        )
        modules_executed.extend(["current-target-market", "potential-target-market", "target-selection"])
        if not (args.run_mode == "full" and canonical_inputs):
            for artifact_name in ["targeting_dataset.csv", "segment_profiles.json", "analysis_context.json"]:
                if find_artifact(artifact_paths, artifact_name):
                    upstream_artifacts_used.append(artifact_name)

    if positioning_needed:
        positioning_inputs = None
        if canonical_inputs and args.run_mode in {"full", "positioning"}:
            brands_local_path = brands_path
            if ideal_path is None or brands_local_path is None or not ideal_path.exists() or not brands_local_path.exists():
                build_missing_prereq_output(
                    output_dir,
                    args.run_mode,
                    requested_modules,
                    artifact_paths,
                    ["positioning_scorecard.csv", "brands.json", "ideal_point.json"],
                )
                return
            positioning_inputs = (
                canonical_inputs["positioning_scorecard"],
                read_json(brands_local_path),
                read_json(ideal_path),
            )
            for artifact_name in ["review_scoring_table.csv", "review_foundation.json", "attribute_catalog.csv", "brands.json", "ideal_point.json", "analysis_context.json"]:
                if find_artifact(artifact_paths, artifact_name) or (
                    artifact_name == "brands.json" and args.brands_file
                ) or (artifact_name == "ideal_point.json" and args.ideal_point_file):
                    upstream_artifacts_used.append(artifact_name)
        else:
            positioning_inputs = load_positioning_inputs(
                artifact_paths,
                args.ideal_point_file,
                args.brands_file,
            )

        if positioning_inputs is None:
            build_missing_prereq_output(
                output_dir,
                args.run_mode,
                requested_modules,
                artifact_paths,
                ["positioning_scorecard.csv", "brands.json", "ideal_point.json"],
            )
            return

        positioning = run_positioning(*positioning_inputs, args.positioning_method, output_dir)
        write_json(output_dir / "positioning_diagnostics.json", positioning["positioning_diagnostics"])
        write_json(output_dir / "strategy_matrix.json", positioning["strategy_matrix"])
        appendix["positioning_summary"] = positioning
        appendix["integrated_stp_actions"].append(
            {
                "stage": "positioning",
                "method": positioning["positioning_method_used"],
                "pod": positioning["positioning_diagnostics"]["pod_pop"]["pod"],
                "pop": positioning["positioning_diagnostics"]["pod_pop"]["pop"],
            }
        )
        modules_executed.extend(
            ["positioning-scorecard", "perceptual-map", "positioning-diagnostics", "strategy-matrix"]
        )
        appendix["execution_scope"]["positioning_method_used"] = positioning["positioning_method_used"]
        if not (canonical_inputs and args.run_mode in {"full", "positioning"}):
            for artifact_name in ["positioning_scorecard.csv", "brands.json", "ideal_point.json", "analysis_context.json"]:
                if find_artifact(artifact_paths, artifact_name) or (
                    artifact_name == "brands.json" and args.brands_file
                ) or (artifact_name == "ideal_point.json" and args.ideal_point_file):
                    upstream_artifacts_used.append(artifact_name)

    proactive_marketing_notes, usp_translation_candidates = build_recommended_extensions(
        appendix.get("targeting_summary"),
        appendix.get("positioning_summary"),
    )
    appendix["proactive_marketing_notes"] = proactive_marketing_notes
    appendix["usp_translation_candidates"] = usp_translation_candidates

    reporting_foundation = _load_reporting_foundation(
        artifact_paths,
        canonical_inputs,
        generated_segmentation,
    )
    reporting_attribute_catalog = _load_reporting_attribute_catalog(
        artifact_paths,
        canonical_inputs,
    )
    score_table_for_reporting = canonical_inputs["score_table"] if canonical_inputs else None
    unit_cluster_map = _build_unit_cluster_map(generated_segmentation)
    appendix["attribute_extraction_summary"] = build_attribute_extraction_summary_contract(
        reporting_foundation,
        reporting_attribute_catalog,
    )
    appendix["segmentation_summary"] = build_stage_report_contract(
        "segmentation",
        appendix.get("segmentation_summary"),
        reporting_foundation,
        score_table_for_reporting,
        positioning_method=args.positioning_method,
        unit_cluster_map=unit_cluster_map,
    )
    appendix["targeting_summary"] = build_stage_report_contract(
        "targeting",
        appendix.get("targeting_summary"),
        reporting_foundation,
        score_table_for_reporting,
        positioning_method=args.positioning_method,
        unit_cluster_map=unit_cluster_map,
    )
    appendix["positioning_summary"] = build_stage_report_contract(
        "positioning",
        appendix.get("positioning_summary"),
        reporting_foundation,
        score_table_for_reporting,
        positioning_method=args.positioning_method,
        unit_cluster_map=unit_cluster_map,
    )

    evidence: list[dict[str, Any]] = []
    for stage_name, summary_key in [
        ("segmentation", "segmentation_summary"),
        ("targeting", "targeting_summary"),
        ("positioning", "positioning_summary"),
    ]:
        summary = appendix.get(summary_key)
        if not isinstance(summary, dict):
            continue
        for quote in summary.get("evidence_quotes", []):
            evidence.append({"stage": stage_name, **quote})
        for finding in summary.get("findings", []):
            if not isinstance(finding, dict):
                continue
            finding_id = finding.get("finding_id", "")
            for quote in finding.get("evidence_quotes", []):
                evidence.append({"stage": stage_name, "finding_id": finding_id, **quote})
    appendix["evidence"] = evidence

    if canonical_inputs and canonical_inputs["contract"].get("unit_id_defaulted"):
        appendix["risks_bias_confidence_notes"].append(
            "unit_id was defaulted from review_id, so aggregation stayed at per-review granularity."
        )

    appendix["execution_scope"]["modules_executed"] = list(dict.fromkeys(modules_executed))
    appendix["execution_scope"]["upstream_artifacts_used"] = list(dict.fromkeys(upstream_artifacts_used))
    appendix["execution_scope"]["emitted_intermediate_artifacts"] = sorted(
        set(emitted_intermediate_artifacts)
    )
    if generated_segmentation:
        cluster_selection = generated_segmentation.get("cluster_selection", {})
        appendix["execution_scope"]["reruns_performed"] = cluster_selection.get("reruns_performed", 0)
        appendix["execution_scope"]["final_k"] = cluster_selection.get("final_k")
        appendix["execution_scope"]["cluster_threshold"] = cluster_selection.get(
            "cluster_threshold",
            0.05,
        )

    write_execution_files(output_dir, args.run_mode, requested_modules, appendix, args.positioning_method)
