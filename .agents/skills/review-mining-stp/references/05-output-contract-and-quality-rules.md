# Output Contract And Quality Rules

## Default Output Shape

Every completed run should produce:

1. `Execution Scope Summary`
2. `Attribute Extraction Summary`
3. `Risks / Bias / Confidence Notes`
4. `Appendix (JSON)`

When the corresponding stage runs, also produce:

5. `Segmentation Summary`
6. `Targeting Summary`
7. `Positioning Summary`
8. `Integrated STP Actions`

## Top-Level Attribute Extraction Contract

`attribute_extraction_summary` must include:

- `target_minimum`
- `actual_count`
- `shortfall_reason`
- `themes_discovered`
- `attribute_group_summary`
- `representative_attributes`

Each `attribute_group_summary` row must include:

- `attribute_group`
- `attribute_count`

Each `representative_attributes` row must include:

- `attribute_key`
- `label`
- `theme`
- `attribute_group`
- `mention_count`
- `example_review_id`
- `example_quote`

## Stage-Level Report Contract

Each major summary section must contain:

- `what_this_section_is_doing`
- `axis_modeling_summary`
- `methods_used`
- `theories_used`
- `theme_coverage_summary`
- `theory_coverage_summary`
- `plain_language_explanation`
- `evidence_quote_status`
- `evidence_quote_reason`
- `evidence_quotes`
- `findings`

### `methods_used`

Must be a non-empty list of objects with:

- `name`
- `description`

### `axis_modeling_summary`

Must be an object with:

- `axes_mode`
- `salience_columns_used`
- `valence_columns_used`
- `modeling_rule`
- `plain_language_explanation`

### `theories_used`

Must be a non-empty list of objects with:

- `name`
- `description`

### `theme_coverage_summary`

Must be a non-empty list of objects with:

- `theme`
- `supporting_items`
- `related_findings`
- `evidence_status`

Theme names are dynamic. The contract never assumes a fixed theme count or fixed theme labels.

### `theory_coverage_summary`

Must be a non-empty list of objects with:

- `theory_family`
- `covered_subtheories`
- `not_evidenced_subtheories`
- `supporting_items`
- `evidence_status`

### `evidence_quotes`

Each quote object must include:

- `review_id`
- `quote_text`
- `why_this_quote_matters`
- `linked_items`

When canonical review evidence is available:

- each major section should contain 2-3 quotes
- `quote_text` must exactly match `review_scoring_table.csv.review_text`
- `review_id` must exist in the canonical score table

The report contract is a script-layer responsibility. The scoring process itself is not.

### `findings`

Must be a non-empty list of objects.

Each finding must include:

- `finding_id`
- `finding_statement`
- `business_implication`
- `axes_used`
- `methods_used`
- `theories_used`
- `themes_used`
- `subtheories_used`
- `reproducibility`
- `statistical_results`
- `plain_language_explanation`
- `evidence_quotes`

### `themes_used`

Each finding-level theme object must include:

- `theme`
- `supporting_items`

### `subtheories_used`

Each finding-level subtheory object must include:

- `family`
- `subtheory`
- `label`
- `source`
- `supporting_item`

### `reproducibility`

Each finding-level reproducibility package must include:

- `input_artifacts`
- `input_columns`
- `filters`
- `preprocessing`
- `analysis_steps`
- `decision_rule`

### `statistical_results`

Each finding-level statistical result package must include:

- `method_family`
- `test_or_model`
- `sample_size`
- `statistic`
- `degrees_of_freedom`
- `p_value`
- `effect_size`
- `coefficient`
- `confidence_interval`
- `result_direction`
- `axis_breakdown`

## Stage-Specific Fields

### Segmentation Summary

Must retain:

- `people_insights`
- `product_triggers`
- `context_scenarios`
- `system1_system2_split`
- `maslow_keywords`
- `segment_variable_table`
- `cluster_share_table`
- `segment_profiles`
- `consumer_portrait_narrative`

`cluster_selection` must retain:

- `cluster_threshold`
- `reruns_performed`
- `final_k`

### Targeting Summary

Must retain:

- `current_target_market`
- `potential_target_market`
- `method_selection`
- `profile_significance_summary`
- `pairwise_comparison_table`
- `target_selection_decision`
- `target_selection_rationale`

`target_selection_decision` must retain:

- `priority_segments`
- `secondary_segments`
- `deprioritized_segments`
- `comparison_axes_used`

### Positioning Summary

Must retain:

- `positioning_scorecard`
- `dynamic_scorecard_summary`
- `positioning_method_used`
- `perceptual_map_figure`
- `perceptual_map_coordinate_table`
- `perceptual_map_method`
- `perceptual_map_interpretation`
- `positioning_diagnostics`
- `strategy_matrix`

Optional factor-analysis diagnostics may retain:

- `perceptual_map_vector_table`
- `projection_interpretation`

`dynamic_scorecard_summary` must retain:

- `highest_scoring_attributes`
- `lowest_scoring_attributes`
- `ideal_point_distance_summary`
- `importance_performance_gap`
- `reliability_analysis`
- `validity_analysis`

`positioning_diagnostics.competition_landscape` rows must include:

- `brand_a`
- `brand_b`
- `distance`

## Appendix Minimum Schema

```json
{
  "execution_scope": {},
  "attribute_extraction_summary": {},
  "segmentation_summary": {},
  "targeting_summary": {},
  "positioning_summary": {},
  "integrated_stp_actions": [],
  "proactive_marketing_notes": [],
  "usp_translation_candidates": [],
  "risks_bias_confidence_notes": [],
  "evidence": []
}
```

## Quality Checklist

- Full runs must list canonical input files in `execution_scope.upstream_artifacts_used`.
- Full runs must include `attribute_catalog.csv` and `attribute_extraction_summary`.
- Full runs must list all three emitted statistical intermediates in `execution_scope.emitted_intermediate_artifacts`.
- Partial and custom runs must retain accurate prerequisite traces.
- Full runs must preserve the dual-axis contract: `salience 0-7`, `valence 0-10`, `salience=0 -> valence empty`, `salience>=1 -> valence present`.
- Segmentation must keep `System 1 / System 2`, Maslow, and the `>5%` cluster guardrail metadata.
- Targeting must keep current-market and potential-market outputs plus pairwise comparisons where required.
- Positioning must keep ideal-point logic, pairwise competition distance, and no fabricated vectors in `MDS`.
- Reports must explain the method and theory used in language that non-specialists can understand.
- Reports must explain how `salience` and `valence` were modeled.
- Reports must show dynamic theme coverage in the report body, not only in appendix-style JSON.
- Reports must show theory families, subtheories, and `not_evidenced` subtheories in the report body.
- Reports must show attribute-extraction summary plus representative attributes in the report body.
- Reports must explain every major finding with a reproducibility package and a fixed-shape statistical-results package.
- Evidence quotes must be verbatim and traceable.
- Validators must not hardcode a fixed item count.
- Validators must not hardcode a fixed theme count.
- Validators must not enforce the wording of the scoring workflow.
