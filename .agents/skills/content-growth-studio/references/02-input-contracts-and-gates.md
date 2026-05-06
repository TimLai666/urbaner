# Input Contracts And Gates

## Core Contract

Use this compact `ContentGrowthInput` shape:

```yaml
mode: auto|analyze|ideate|rewrite|package|produce|system
entry_path: auto|source-led|brief-led
topic_or_subject: string
source_artifacts:
  - type: url|transcript|article-text|existing-script|title-outline|competitor-example|channel-example|review-evidence|support-evidence|social-evidence|notes
    content: string
target_audience: string
primary_channel: article|newsletter|long-form-video|short-form-video|social|auto
goal: string
brand_or_voice: string
constraints:
  - string
```

Need at least one of:

- `topic_or_subject`
- `source_artifacts`

## Recommended Inputs By Mode

### `analyze`

- `source_artifacts`
- `target_audience`
- `primary_channel`
- `goal`

### `ideate`

- `topic_or_subject`
- `target_audience`
- `primary_channel`
- `goal`
- `brand_or_voice`

### `rewrite`

- `source_artifacts`
- `primary_channel`
- `goal`
- `brand_or_voice`

### `package`

- `topic_or_subject` or `source_artifacts`
- `primary_channel`
- `target_audience`
- `goal`

### `produce`

- `topic_or_subject` or `source_artifacts`
- `primary_channel`
- `target_audience`
- `goal`
- `brand_or_voice`

### `system`

- `goal`
- `primary_channel`
- `constraints`
- time or budget context if available

## Source Artifact Rules

Allow any combination of:

- URLs
- transcripts
- article text
- existing script
- title plus outline
- competitor or channel examples
- review, support, or social evidence
- notes pasted by the user

Normalize mixed source sets into a single working brief before generating output.

## Missing Data Gate

If enough data exists to produce a useful answer, proceed.

If the request is blocked by missing core inputs and the user did not ask for speed:

- ask concise follow-up questions
- do not fabricate a full output

If the user asks for a fast draft:

1. List `3-5` assumptions.
2. Make assumptions observable and business-relevant.
3. Continue with the requested output.

## Assumptions Rules

Allowed assumptions:

- likely audience profile
- likely channel context
- likely tone direction
- likely content goal

Do not assume:

- actual performance results
- exact competitor weaknesses unless directly observed
- facts supposedly found in inaccessible URLs
- brand constraints that materially change legal or reputational risk

## MissingDataOutput Shape

Use this shape when the task cannot safely proceed:

```json
{
  "missing_fields": [],
  "why_needed": {},
  "questions_to_user": [],
  "next_step_rule": "Provide the missing fields, then continue in the requested mode."
}
```

## Quick-Draft Rule

When the user says the equivalent of:

- 先做草稿
- 直接先出
- 快速版
- 先不要問太多

then prefer assumptions plus execution over blocking questions.
