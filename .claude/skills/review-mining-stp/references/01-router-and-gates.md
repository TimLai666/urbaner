# Router And Gates

## Purpose

This reference defines what belongs to the review scoring workflow, what belongs to the scripts, and which artifacts each run mode requires.

## Workflow Boundary

### Review Scoring Workflow

The review scoring workflow handles:

- raw `reviews` or `review_text`
- extracting or curating the corpus-level attribute catalog
- freezing that catalog before formal scoring starts
- inferring scored items from the full corpus
- applying paired `salience` and `valence` scoring to every inferred attribute for every review
- assigning dynamic `theme` names inferred from the corpus
- assigning `theory_annotations` and `stat_roles`
- preserving verbatim review text for later evidence quoting

The review scoring workflow emits the scored artifacts that the scripts need.
It is a workflow boundary, not a requirement to use a specific API.

### Scripts

The scripts accept scored artifacts only.

Canonical input:

- `review_scoring_table.csv`
- `review_foundation.json`
- `attribute_catalog.csv`
- `analysis_context.json`
- `brands.json`
- `ideal_point.json`

The scripts may emit:

- `segmentation_variables.csv`
- `targeting_dataset.csv`
- `positioning_scorecard.csv`

They do not accept raw reviews and they do not define the scoring workflow.
They also do not modify the frozen attribute catalog while statistics are running.

## Canonical Input Rules

### `review_scoring_table.csv`

Must be per-review and must include:

- `review_id`
- `unit_id`
- `brand`
- `product`
- `review_text`

All scored attributes must:

- exist in `dimension_catalog`
- exist as paired `*_salience` and `*_valence` columns
- keep `*_salience` as numeric integers inside `0-7`
- keep `*_valence` as numeric integers inside `0-10`
- keep `*_valence` empty when `*_salience = 0`
- keep `*_valence` present when `*_salience >= 1`

The scored item count is dynamic. The contract never assumes a fixed item count.

### `review_foundation.json`

Must include:

- `dimension_catalog`
- `theme_mapping`
- `attribute_extraction_summary`

It may also include audit-only metadata such as:

- `scoring_rubric`

Each `dimension_catalog` item must include:

- `column`
- `label`
- `theme`
- `attribute_group`
- `salience_column`
- `valence_column`
- `stat_roles`
- `plain_language_definition`
- `theory_annotations`

Legacy compatibility is allowed through:

- `theory_tags`

`theme_mapping` must:

- contain at least one theme
- keep a non-empty column list for each theme
- reference only columns present in `dimension_catalog`
- cover every `dimension_catalog` column exactly once
- match the `theme` value stored on each `dimension_catalog` item

### `attribute_catalog.csv`

Must include:

- `attribute_key`
- `label`
- `theme`
- `attribute_group`
- `definition`
- `source_type`
- `mention_count`
- `salience_column`
- `valence_column`
- `example_review_id`
- `example_quote`

Rules:

- it must align one-to-one with `dimension_catalog`
- `example_quote` must stay verbatim so downstream evidence is auditable
- if fewer than `30` attributes are extracted, `attribute_extraction_summary.shortfall_reason` must explain why

## Run Modes

- `full`
  - starts from canonical scored input
  - emits all three statistical intermediates
- `segmentation`
  - requires `review_foundation.json + segmentation_variables.csv`
- `targeting`
  - requires `targeting_dataset.csv + segment_profiles.json`
- `positioning`
  - requires `positioning_scorecard.csv + brands.json + ideal_point.json`
- `custom`
  - runs only requested downstream modules

## Missing Outputs

### `MissingDataOutput`

Review-scoring-workflow artifact used when the user has not provided enough upstream context to build scored artifacts.

### `MissingPrerequisiteOutput`

Script artifact used when required scored artifacts or intermediate statistical artifacts are missing.

Expected shape:

```json
{
  "requested_stage": "",
  "requested_modules": [],
  "missing_prerequisites": [],
  "acceptable_upstream_artifacts": [],
  "available_artifacts": [],
  "auto_backfill_allowed": false,
  "next_step_rule": "Scripts accept scored artifacts only; run the review scoring workflow to build the missing files before rerunning."
}
```

Rules:

- `missing_prerequisites` must list only truly missing files
- `acceptable_upstream_artifacts` should mirror the missing files
- `auto_backfill_allowed` must stay `false`
- when canonical scored input is missing, `next_step_rule` must point back to the review scoring workflow

## Execution Scope Summary

Every completed run must record:

- `run_mode`
- `requested_modules`
- `modules_executed`
- `auto_backfilled_modules`
- `upstream_artifacts_used`
- `emitted_intermediate_artifacts`
- `comparison_axes`
- `brands`
- `positioning_method_used`
- `cluster_threshold`
- `reruns_performed`
- `final_k`
- `scope_limits`

## Reporting Gate

Each stage summary must keep:

- top-level `attribute_extraction_summary` for full runs
- section-level `axis_modeling_summary`, `methods_used`, `theories_used`, `plain_language_explanation`, and `evidence_quotes`
- section-level `theme_coverage_summary` and `theory_coverage_summary`
- a non-empty `findings` list

Each finding must keep:

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

The scripts are responsible for assembling this reporting structure from scored artifacts. The review scoring workflow is responsible for the upstream scoring work only.
