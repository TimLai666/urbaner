# End-To-End Examples

## How To Read These Examples

- `評分流程輸入`: what the review scoring workflow receives from the user
- `Runnable Artifacts`: what the scripts need after the review scoring workflow has finished scoring and structuring

## Example A: Full STP From Raw Reviews

### 評分流程輸入

```json
{
  "run_mode": "full",
  "analysis_goal": "Turn raw reviews into STP outputs with evidence-backed reporting.",
  "reviews": [
    {
      "id": "R01",
      "review_text": "Delivery was fast, setup was easy, and the whole thing felt worth the money.",
      "channel": "app_store",
      "rating": 5
    },
    {
      "id": "R02",
      "review_text": "The product looks premium, but support was slower than I expected.",
      "channel": "marketplace",
      "rating": 4
    }
  ]
}
```

### 評分流程步驟

The review scoring workflow:

1. reads each review one by one
2. extracts a corpus-level attribute catalog with definitions, mention counts, and example quotes
3. freezes that attribute catalog for the scoring run
4. scores each attribute with paired `salience + valence`
5. assigns dynamic theme names plus theory annotations
6. preserves verbatim `review_text`

### Runnable Artifacts

- `review_scoring_table.csv`
- `review_foundation.json`
- `attribute_catalog.csv`
- `analysis_context.json`
- `brands.json`
- `ideal_point.json`

### Expected Outcome

- scripts emit `segmentation_variables.csv`, `targeting_dataset.csv`, and `positioning_scorecard.csv`
- the final report prints the attribute-extraction summary and representative attributes in the main body
- the final report names the statistical method and theory used in each major section
- the final report prints the dynamically inferred themes in the main body
- the final report prints theory families, subtheories, and `not_evidenced` subtheories in the main body
- each major section includes finding-level method, reproducibility steps, statistical results, and verbatim review quotes tied to `review_id`

## Example B: Full STP From A Different Dynamic Schema

### 評分流程輸入

```json
{
  "run_mode": "full",
  "analysis_goal": "Use a custom set of inferred items instead of reusing an older template.",
  "reviews": "..."
}
```

### Runnable Artifacts

- `review_scoring_table.csv`
  - contains `review_id`, `unit_id`, `brand`, `product`, `review_text`
  - contains paired columns such as `delivery_confidence_salience`, `delivery_confidence_valence`, `premium_finish_salience`, `premium_finish_valence`
- `review_foundation.json`
  - maps those columns into `dimension_catalog`
  - defines dynamic `theme_mapping`, `theory_annotations`, `attribute_extraction_summary`, and `stat_roles`
  - may include `scoring_rubric` as audit metadata, but scripts do not require it
- `attribute_catalog.csv`
  - records each attribute's definition, mention count, paired score columns, and verbatim example quote

### Expected Outcome

- scripts and validators work without assuming a fixed item count
- scripts and validators work without assuming a fixed theme count
- targeting variables come from `stat_roles`
- positioning attributes come from `stat_roles` that include `positioning`
- the report still emits the same finding-level reproducibility package even though the item names changed

## Example C: Segmentation-Only Rerun

### 評分流程輸入

```json
{
  "run_mode": "segmentation",
  "analysis_goal": "Rerun segment formation only."
}
```

### Runnable Artifacts

- `review_foundation.json`
- `segmentation_variables.csv`
- `analysis_context.json`

### Expected Outcome

- segmentation reruns independently
- cluster guardrail metadata records threshold, reruns, and final `k`

## Example D: Targeting Partial Run

### 評分流程輸入

```json
{
  "run_mode": "targeting",
  "analysis_goal": "Re-evaluate target choice using updated comparison axes.",
  "comparison_axes": ["fast_delivery", "support_trust", "value_for_money"]
}
```

### Runnable Artifacts

- `targeting_dataset.csv`
- `segment_profiles.json`
- `review_foundation.json`
- `attribute_catalog.csv`
- `analysis_context.json`

### Expected Outcome

- targeting uses the updated comparison axes
- the override base names expand into paired salience and valence columns
- output includes `priority_segments`, `secondary_segments`, and `deprioritized_segments`
- the report explains the tests in plain language

## Example E: Positioning-Only Run

### 評分流程輸入

```json
{
  "run_mode": "positioning",
  "analysis_goal": "Rebuild the perceptual map and strategic gap view."
}
```

### Runnable Artifacts

- `positioning_scorecard.csv`
- `brands.json`
- `ideal_point.json`
- `analysis_context.json`

### Expected Outcome

- default path uses `factor_analysis`
- `MDS` is allowed only when similarity input is explicitly available
- output includes ideal-point distance and pairwise `competition_landscape`
- public perceptual-map delivery is the coordinate table plus the Python-rendered figure
- factor-analysis-only vectors may appear as optional diagnostics

## Example F: Raw Reviews Sent Directly To Scripts

### Runnable Artifacts

- `reviews.json`

### Expected Outcome

- scripts do not run STP directly from raw reviews
- `MissingPrerequisiteOutput` points back to `review_scoring_table.csv` and `review_foundation.json`
- `next_step_rule` explicitly says the review scoring workflow is required first
