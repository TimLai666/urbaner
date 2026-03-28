# Verification Scenarios

## Purpose

Use these scenarios to verify both the workflow boundary and the downstream statistical/reporting contract.

## Scenario 1: Raw Reviews, Full STP Request

- Input: only raw `reviews`
- Expected:
  - the review scoring workflow builds scored artifacts first
  - scripts do not run directly on raw review text
  - missing-prerequisite guidance points back to the review scoring workflow

## Scenario 2: Full Run From Canonical Scored Input

- Input:
  - `review_scoring_table.csv`
  - `review_foundation.json`
  - `attribute_catalog.csv`
  - `analysis_context.json`
  - `brands.json`
  - `ideal_point.json`
- Expected:
  - full STP completes
  - three intermediate statistical artifacts are emitted
  - `execution_scope` records both canonical inputs and emitted intermediates

## Scenario 3: Dynamic Item Schema

- Input: a legal `dimension_catalog` with a different set of scored item names
- Expected:
  - scripts run without assuming a fixed item count
  - scripts run without assuming a fixed theme count
  - targeting and positioning still derive their variables from `stat_roles`

## Scenario 4: Input Contract Failure

- Input: canonical artifacts missing one of the required conditions
  - missing `review_text`
  - missing `product`
  - missing `plain_language_definition`
  - missing paired `*_salience` or `*_valence` column
  - incomplete `theme_mapping`
  - empty `theme_mapping`
  - `theme_mapping` references an unknown column
  - one column is mapped to multiple themes
  - `dimension_catalog.theme` does not match `theme_mapping`
  - `salience` outside `0-7`
  - `valence` outside `0-10`
  - `salience = 0` but `valence` is present
  - `salience >= 1` but `valence` is missing
  - missing `attribute_catalog.csv`
  - fewer than `30` attributes without `shortfall_reason`
- Expected:
  - router fails early with a contract error
  - scripts do not silently continue

## Scenario 5: Scoring Rubric Metadata Is Optional

- Input: canonical scored artifacts with no `scoring_rubric`
- Expected:
  - scripts still run
  - scoring workflow remains documented in MD, not enforced by Python

## Scenario 6: Custom Scoring Rubric Metadata

- Input: canonical scored artifacts with a custom `scoring_rubric` note
- Expected:
  - scripts still run
  - validator still focuses on output contracts, not rubric prose

## Scenario 7: Segmentation Partial Rerun

- Input:
  - `review_foundation.json`
  - `segmentation_variables.csv`
- Expected:
  - segmentation reruns independently
  - cluster guardrail metadata is retained

## Scenario 8: Targeting Partial Rerun

- Input:
  - `targeting_dataset.csv`
  - `segment_profiles.json`
  - `analysis_context.json`
- Expected:
  - targeting reruns independently
  - `comparison_axes` override is preserved

## Scenario 9: Positioning Paths

- Factor-analysis path:
  - `positioning_method_used = factor_analysis`
  - `perceptual_map_coordinates.csv` and `perceptual_map.png` are present
  - optional vectors may be present as internal diagnostics
- MDS path:
  - `positioning_method_used = mds`
  - `attribute_vectors_not_defined = true`
  - `perceptual_map_coordinates.csv` and `perceptual_map.png` are present
  - no fabricated attribute-vector file is emitted

## Scenario 10: Evidence-Backed Report

- Input: canonical full run with real `review_text`
- Expected:
  - each major report section includes methods, theories, `theme_coverage_summary`, `theory_coverage_summary`, plain-language explanation, and evidence quotes
  - the report body includes the top-level attribute extraction summary with representative attributes
  - each finding includes methods, axes, theories, `themes_used`, `subtheories_used`, reproducibility steps, statistical results, and evidence quotes
  - the main `report.md` body directly lists the inferred themes plus `not_evidenced` theory subtheories
  - quotes trace back exactly to the canonical score table

## Scenario 11: Validator Guardrails

- Input: tampered output, such as:
  - missing execution-scope fields
  - altered quote text
  - missing finding reproducibility package
  - missing finding statistical-result keys
- Expected:
  - validator fails
  - failure message points to the broken contract
