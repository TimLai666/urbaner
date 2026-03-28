# Validation Scenarios

## Purpose

Use these prompts to validate that the skill stops false `qual vs quant`
either-or behavior and emits a correct `MethodRoutingDecision`.

## Validation Procedure

1. Run the prompt without this skill and record whether the agent defaults to a
   single method too early.
2. Run the same prompt with `$orchestrating-mixed-methods`.
3. Verify that the response emits `MethodRoutingDecision`.
4. Verify that the route matches the expected route below.
5. Verify that the response does not claim triangulation unless both evidence
   streams exist.

## Scenario 1: Interview Themes Only

Prompt:

`Find the major themes from these user interviews and explain what they suggest about purchase hesitation.`

Expected route:

- `qualitative-only`

Expected primary need:

- `exploration` or `explanation`

Common failure without the skill:

- agent starts inventing metrics or a survey plan even though the task is pure interpretation

## Scenario 2: Cohort Difference Test

Prompt:

`Check whether cohort A differs significantly from cohort B on renewal rate.`

Expected route:

- `quantitative-only`

Expected primary need:

- `measurement` or `validation`

Common failure without the skill:

- agent adds unnecessary qualitative speculation before establishing the difference

## Scenario 3: Retention Drop With Explanation

Prompt:

`Retention dropped last month. Tell me how large the drop is and why it happened.`

Expected route:

- `mixed-quant-first`

Expected primary need:

- `explanation`

Expected downstream logic:

- quantify the drop first
- then recommend or run qualitative explanation against the anomaly

## Scenario 4: Explore Then Measure

Prompt:

`I have interview notes about how people think about AI tutoring. Help me explore the patterns first, then design a survey to measure how common each pattern is.`

Expected route:

- `mixed-qual-first`

Expected primary need:

- `validation`

Expected downstream logic:

- discover dimensions first
- then translate them into measurable constructs

## Scenario 5: Parallel Triangulation

Prompt:

`I have survey results and interview transcripts about our onboarding flow. Give me one synthesized conclusion about the main friction points.`

Expected route:

- `mixed-parallel`

Expected primary need:

- `triangulation`

Expected downstream logic:

- analyze both streams against the same onboarding-friction question
- label the result as `convergence`, `divergence`, or `expansion`

## Scenario 6: Only One Evidence Stream Available

Prompt:

`Give me a quick answer on why conversion fell. I only have the dashboard metrics right now.`

Expected behavior:

- choose the feasible primary route
- usually `mixed-quant-first` or `quantitative-only`, depending on how strongly the response keeps the qualitative follow-up alive
- explicitly name the missing complementary qualitative follow-up

Failure condition:

- agent writes a fake root-cause conclusion with no qualitative evidence

## Minimum Acceptance Criteria

The skill passes these scenarios when it consistently:

- emits `MethodRoutingDecision`
- picks the expected route
- names needed qualitative and quantitative capability classes honestly
- avoids fake triangulation
- routes broad mixed questions without forcing equal-length dual-track output
