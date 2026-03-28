# Routing Rules

## Purpose

This reference defines the route-selection logic for:

- `qualitative-only`
- `quantitative-only`
- `mixed-qual-first`
- `mixed-quant-first`
- `mixed-parallel`

The goal is to choose the smallest method path that answers the user's actual
question without collapsing mixed-method needs into a false binary.

## Step 1: Respect Explicit Constraints

Check explicit user constraints first.

- If the user asks for `qualitative only`, `interview-based`, `thematic`, or
  `non-statistical`, prefer `qualitative-only`.
- If the user asks for `quantitative only`, `statistical`, `significance`,
  `forecast`, or `metric-based`, prefer `quantitative-only`.
- Override that preference only when the same request clearly asks for both:
  - scale or magnitude
  - explanation, mechanism, or context

Example:

- `Run a significance test between cohorts` -> `quantitative-only`
- `Explain why the cohorts differ and whether the difference is large` -> mixed route

## Step 2: Score the Five Dimensions

Read the task against these dimensions:

1. `meaning-context-mechanism`
   - high when the task asks why something happened, how users interpret it,
     what a pattern means, or which mechanism explains the result
2. `magnitude-comparison-significance`
   - high when the task asks how much, how many, whether A differs from B,
     whether a change is significant, or how large an effect is
3. `construct-stability`
   - stable when the variables, categories, codebook, or constructs already
     exist
   - exploratory when the categories still need to be discovered or defined
4. `evidence-shape`
   - text-heavy, numbers-heavy, or dual-evidence
5. `decision-goal`
   - exploration, explanation, measurement, estimation, validation,
     triangulation, or design

Do not route from a single keyword. Route from the combined profile.

## Step 3: Route by the Smallest Valid Path

### `qualitative-only`

Choose this route when most of the following are true:

- the task is exploratory or interpretive
- constructs are unstable or undefined
- evidence is mostly interviews, notes, observations, open-ended text, or cases
- the main output is themes, mechanisms, frames, hypotheses, or explanations

Common triggers:

- interview synthesis
- open coding
- concept discovery
- case comparison
- mechanism building
- interpreting a customer journey or decision process

### `quantitative-only`

Choose this route when most of the following are true:

- the task is comparative, estimative, or inferential
- constructs are already defined
- evidence is structured numeric data
- the main output is prevalence, rank, effect size, confidence, trend, or forecast

Common triggers:

- significance testing
- cohort comparison
- descriptive statistics
- experiment analysis
- forecasting
- scoring and ranking

### `mixed-qual-first`

Choose this route when:

- the end goal includes measurement or validation
- but the constructs are still fuzzy, user-defined, or underspecified
- the first pass must discover dimensions before the second pass can measure them

Common triggers:

- turn interviews into a survey instrument
- discover themes, then test how common they are
- build a codebook, then score a larger dataset
- derive candidate segments, then validate them quantitatively

### `mixed-quant-first`

Choose this route when:

- structured metrics already exist
- the first pass can isolate anomalies, gaps, segments, or outliers
- the second pass is needed to explain why those numeric patterns happened

Common triggers:

- explain a retention drop after seeing the metrics
- explain unexpected segment behavior
- interpret a KPI anomaly using follow-up interviews or cases
- explain why two cohorts differ after the difference is established

### `mixed-parallel`

Choose this route when:

- both narrative and numeric evidence already exist
- both streams address the same research question
- credibility depends on triangulation rather than simple sequencing

Common triggers:

- survey + interview synthesis
- metrics + ticket or review synthesis
- concurrent evaluation of observed behavior and reported perception

## Tie-Breakers

If two routes seem plausible, use these tie-breakers in order:

1. pick the route that answers the user's core question with fewer method passes
2. if measurement is impossible until constructs are defined, use `mixed-qual-first`
3. if explanation is impossible until a pattern is established, use `mixed-quant-first`
4. if both evidence streams already exist and neither is obviously primary, use `mixed-parallel`
5. if the task can be fully answered with one method, do not upgrade it to mixed

## Missing Evidence Rule

If the research question is mixed but only one evidence stream is available:

- route to the feasible primary method
- keep the route honest about the missing complementary stream
- recommend the follow-up method explicitly

Do not claim a completed mixed-methods result when one side is still absent.

## Recommended Primary Need Labels

Use these `primary_need` values consistently:

- `exploration`
  - open discovery and framing
- `explanation`
  - interpretive and mechanism-seeking work
- `measurement`
  - counting, ranking, prevalence, and descriptive comparison
- `estimation`
  - effect size, projection, trend, or forecast
- `validation`
  - testing whether a pattern or construct holds more broadly
- `triangulation`
  - reconciling parallel evidence streams
