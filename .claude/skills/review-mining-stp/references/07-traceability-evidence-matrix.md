# Traceability Evidence Matrix

## Purpose

This matrix ties the public skill contract to documentation, script outputs, and automated tests.

## Evidence Matrix

| Requirement | Upstream Workflow Evidence | Script / Output Evidence | Test Coverage |
| --- | --- | --- | --- |
| Raw reviews are handled by the review scoring workflow, not the scripts | `SKILL.md`, `references/01-router-and-gates.md`, `references/06-end-to-end-examples.md` | `MissingPrerequisiteOutput.next_step_rule` | `test_raw_reviews_are_rejected_until_review_scoring_workflow_creates_scored_artifacts` |
| Review scoring workflow is a workflow boundary, not an API requirement | `SKILL.md`, `references/01-router-and-gates.md` | script contract never names an API | manual doc verification |
| Scoring belongs to the review scoring workflow, not a Python-owned process | `SKILL.md`, `references/06-end-to-end-examples.md` | scripts validate only scored artifacts | `test_full_run_accepts_optional_scoring_rubric_metadata` |
| Scripts only require canonical scored artifacts plus statistical metadata | `SKILL.md`, `references/01-router-and-gates.md` | `execution_scope.upstream_artifacts_used` | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts` |
| Each review keeps verbatim `review_text` for later evidence quoting | `SKILL.md`, `references/05-output-contract-and-quality-rules.md` | `report.md`, `appendix.json` evidence quote sections | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts`, `test_validator_rejects_quote_and_axis_contract_breaks` |
| The scored table must keep dual-axis numeric inputs plus the `product` field | `SKILL.md`, `references/01-router-and-gates.md`, `references/06-end-to-end-examples.md` | canonical input validation | `test_full_run_rejects_missing_product_and_missing_pair`, `test_full_run_rejects_invalid_axis_values` |
| Full mode requires `attribute_catalog.csv` aligned to `dimension_catalog` | `SKILL.md`, `references/01-router-and-gates.md` | canonical input validation, `execution_scope.upstream_artifacts_used` | `test_full_run_requires_attribute_catalog_and_valid_attribute_contract` |
| The report body must show attribute extraction summary and representative attributes | `SKILL.md`, `references/05-output-contract-and-quality-rules.md`, `references/06-end-to-end-examples.md` | `appendix.attribute_extraction_summary`, `report.md` | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts`, `test_validator_rejects_quote_and_axis_contract_breaks` |
| Scripts do not assume a fixed item count | `SKILL.md`, `references/06-end-to-end-examples.md` | dynamic `dimension_catalog` handling | `test_full_run_supports_alternate_dynamic_schema_with_two_themes` |
| `dimension_catalog` supports dynamic themes and theory annotations | `SKILL.md`, `references/01-router-and-gates.md` | canonical input validation | `test_full_run_rejects_missing_plain_language_definition` |
| `theme_mapping` is dynamic, complete, and aligned with `dimension_catalog.theme` | `SKILL.md`, `references/01-router-and-gates.md`, `references/08-verification-scenarios.md` | dynamic `theme_mapping` validation | `test_full_run_rejects_incomplete_theme_mapping`, `test_full_run_rejects_empty_theme_mapping`, `test_full_run_rejects_theme_mapping_with_unknown_column`, `test_full_run_rejects_duplicate_theme_mapping_column`, `test_full_run_rejects_theme_mismatch_between_catalog_and_mapping` |
| Full mode emits all three intermediate statistical artifacts | `SKILL.md`, `references/05-output-contract-and-quality-rules.md` | `segmentation_variables.csv`, `targeting_dataset.csv`, `positioning_scorecard.csv`, `execution_scope.emitted_intermediate_artifacts` | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts` |
| Segmentation uses `factor_analysis -> K-means` with `>5%` guardrail metadata | `SKILL.md`, `references/02-segmentation.md` | `cluster_selection.cluster_threshold`, `reruns_performed`, `final_k` | `test_segmentation_partial_run_still_supports_direct_intermediate_artifacts` |
| Targeting respects `comparison_axes` override | `SKILL.md`, `references/03-targeting.md`, `references/06-end-to-end-examples.md` | `target_selection_decision.comparison_axes_used` | `test_targeting_partial_run_uses_comparison_axes_override` |
| Targeting emits profile significance and pairwise comparison outputs | `SKILL.md`, `references/03-targeting.md`, `references/05-output-contract-and-quality-rules.md` | `profile_significance_summary`, `pairwise_comparison_table` | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts` |
| Positioning public map delivery is coordinates plus a rendered figure | `SKILL.md`, `references/04-positioning.md`, `references/05-output-contract-and-quality-rules.md` | `perceptual_map_coordinates.csv`, `perceptual_map.png`, `perceptual_map_coordinate_table`, `perceptual_map_figure` | `test_validator_accepts_positioning_summary_without_public_vector_fields` |
| Positioning emits ideal-point and pairwise competition diagnostics | `SKILL.md`, `references/04-positioning.md`, `references/05-output-contract-and-quality-rules.md` | `positioning_scorecard`, `competition_landscape`, `dynamic_scorecard_summary` | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts` |
| `MDS` never fabricates attribute vectors | `SKILL.md`, `references/04-positioning.md` | `attribute_vectors_not_defined`, no vector table | `test_positioning_mds_does_not_fabricate_attribute_vectors` |
| Every major report section names methods, axes, theories, theme coverage, theory coverage, plain-language explanation, and evidence quotes | `SKILL.md`, `references/05-output-contract-and-quality-rules.md` | `appendix.json`, `report.md` | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts`, `test_validator_rejects_quote_and_axis_contract_breaks` |
| Every finding keeps methods, axes, theories, themes, subtheories, reproducibility, statistical results, and traceable quotes | `SKILL.md`, `references/05-output-contract-and-quality-rules.md`, `references/06-end-to-end-examples.md` | `appendix.json` finding objects, `report.md` finding sections | `test_full_run_accepts_dual_axis_inputs_and_emits_intermediate_artifacts`, `test_validator_rejects_quote_and_axis_contract_breaks` |
| Validator checks deep execution-scope and evidence contracts, not scoring prose | `references/05-output-contract-and-quality-rules.md`, `references/08-verification-scenarios.md` | validator failure paths | `test_validator_rejects_quote_and_axis_contract_breaks` |

## Audit Note

- The matrix separates upstream scoring workflow evidence from downstream statistical-output evidence.
- The goal is not only statistical correctness, but also a clean boundary between review scoring work and script work.
