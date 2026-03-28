# Input And Gate

## Required Input

- `analysis_goal: string`
- `evidence_items: array<object>`
  - `item_id: string`
  - `content: string`
  - `content_type: string`

Optional:

- `source_type: string`
- `source_ref: string`
- `context_tags: string[]`

## Validation Rules

- `analysis_goal` 不可空白。
- `evidence_items` 至少 1 筆，且每筆應有可用 `content`。
- 若證據內容過短或只有單字評價，需在 `quality_checks.warnings` 註記低訊號。
- `content` 應為可分析文字（原文、逐字稿、摘要皆可）。

## Missing Data Output

```json
{
  "missing_fields": ["analysis_goal", "evidence_items.content"],
  "why_needed": {
    "analysis_goal": "Needed to bound decision context for motivation coding.",
    "evidence_items.content": "Needed to produce auditable motivation evidence."
  },
  "questions_to_user": [
    "What purchase decision should these evidence items support?",
    "Can you provide evidence items with stable item_id values and analyzable content?"
  ],
  "next_step_rule": "Do not infer purchase motivations until required input is complete."
}
```

## Coverage Rule

- 至少 80% 證據項目需被標註到 `functional/security/relational` 其中之一。
- 未達門檻時，摘要要明確說資料限制，不輸出過度結論。
