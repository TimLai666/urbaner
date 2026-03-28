# Positioning

## Purpose

Positioning turns scored review attributes into a brand-versus-ideal view, a perceptual map, and a practical gap analysis.

The scripts do not infer new attributes from raw review text. They only analyze the scored positioning inputs that already exist in artifacts.

## Inputs

Required script inputs:

- `positioning_scorecard.csv`
- `brands.json`
- `ideal_point.json`

`positioning_scorecard.csv` must contain:

- `brand`
- `attribute`
- `score`

The attribute set is dynamic. It comes from `dimension_catalog.stat_roles` containing `positioning`, not from a fixed template.

## Method Rules

- default positioning method: `factor_analysis`
- optional similarity-driven method: `mds`
- always record the final method in `positioning_method_used`
- always produce a two-dimensional coordinate table and a Python-generated perceptual-map figure
- always compute ideal-point distance and pairwise brand distance
- never fabricate attribute vectors in `mds`

## Public Output Contract

The public perceptual-map contract is:

- `perceptual_map_figure`
- `perceptual_map_coordinate_table`
- `perceptual_map_method`
- `perceptual_map_interpretation`

The public contract is intentionally centered on the coordinate table and the rendered figure.

## Optional Internal Diagnostics

When the method is `factor_analysis`, the scripts may also retain:

- `perceptual_map_vector_table`
- `projection_interpretation`

These are internal diagnostics, not public required outputs.

When the method is `mds`:

- `attribute_vectors_not_defined` must be `true`
- `projection_interpretation` may be omitted from the public summary
- if internal diagnostics are emitted, they must explicitly say vectors are not defined

## Coordinate Table Schema

`perceptual_map_coordinate_table` rows must include:

- `label`
- `point_type = brand | ideal`
- `x`
- `y`

If `perceptual_map_vector_table` is emitted for diagnostics, rows must include:

- `label`
- `vector_type = attribute`
- `x_start = 0`
- `y_start = 0`
- `x_end`
- `y_end`
- `x_loading`
- `y_loading`

## Required Positioning Outputs

- `positioning_scorecard`
- `dynamic_scorecard_summary`
- `positioning_method_used`
- `perceptual_map_figure`
- `perceptual_map_coordinate_table`
- `perceptual_map_method`
- `perceptual_map_interpretation`
- `positioning_diagnostics`
- `strategy_matrix`

## Required Diagnostics

`dynamic_scorecard_summary` must retain:

- `highest_scoring_attributes`
- `lowest_scoring_attributes`
- `ideal_point_distance_summary`
- `importance_performance_gap`
- `reliability_analysis`
- `validity_analysis`

`positioning_diagnostics` must retain:

- `benchmark_analysis`
- `ideal_point_analysis`
- `competition_landscape`
- `pod_pop`
- `strategy_matrix`

`competition_landscape` must be based on pairwise brand distances, not distance-to-ideal.
