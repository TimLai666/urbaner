# Sequencing and Integration

## Purpose

This reference defines how the three mixed routes should be sequenced and how
their outputs should be integrated.

## `mixed-qual-first`

Use this route when the first pass must define what will later be measured.

### First pass

Qualitative outputs may include:

- theme map
- candidate dimensions
- codebook
- hypotheses
- segment logic
- instrument wording
- candidate variables

### Second pass

Quantitative outputs may include:

- prevalence
- ranking
- group differences
- effect size
- correlation
- validation of segment strength

### Integration rule

The quantitative phase validates, scales, ranks, or stress-tests the constructs
discovered in the qualitative phase.

Do not skip the qualitative discovery step when the variables are still fuzzy.

## `mixed-quant-first`

Use this route when the first pass can isolate the pattern and the second pass
must explain it.

### First pass

Quantitative outputs may include:

- trend break
- anomaly detection
- drop-off point
- unexpected cluster
- segment contrast
- conflicting metric pattern

### Second pass

Qualitative outputs may include:

- mechanism explanation
- motivation and interpretation
- contextual explanation
- process narrative
- case comparison around the anomaly

### Integration rule

The qualitative phase explains the most decision-relevant numeric pattern from
the first pass. Do not run a broad qualitative detour unrelated to the measured
anomaly.

## `mixed-parallel`

Use this route when both evidence streams already exist and both are necessary
for a credible answer.

### Parallel requirement

Both tracks must address the same research question or decision frame.

### Allowed integration labels

- `convergence`
  - both streams support the same conclusion
- `divergence`
  - the streams disagree and the contradiction matters
- `expansion`
  - one stream broadens or deepens the other without contradiction

### Integration rule

Do not merge the streams into vague synthesis language.
State which of the three integration labels applies and why.

## Conflict Handling

When mixed evidence conflicts:

- never average away disagreement
- report contradictions directly
- test likely causes:
  - sample mismatch
  - timeframe mismatch
  - construct mismatch
  - measurement artifact
  - segment heterogeneity

If the contradiction cannot be resolved, keep it visible in the conclusion and
recommend the next evidence-collection step instead of pretending consensus.

## Output Guidance

For every mixed route, `MethodRoutingDecision` should name:

- `first_pass_outputs`
- `second_pass_outputs`
- `integration_rule`

Good examples:

- `mixed-qual-first`
  - `first_pass_outputs: [theme map, candidate variables, survey wording]`
  - `second_pass_outputs: [prevalence table, segment comparison]`
  - `integration_rule: Quantitative validation of qualitatively discovered constructs`

- `mixed-quant-first`
  - `first_pass_outputs: [retention drop by cohort, anomaly summary]`
  - `second_pass_outputs: [mechanism explanation, interview-based root causes]`
  - `integration_rule: Qualitative explanation of the most decision-relevant numeric anomaly`

- `mixed-parallel`
  - `first_pass_outputs: [survey pattern summary, interview theme summary]`
  - `second_pass_outputs: [convergence or divergence memo]`
  - `integration_rule: Triangulate using convergence, divergence, or expansion`
