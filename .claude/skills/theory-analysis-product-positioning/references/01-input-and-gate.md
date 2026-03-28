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

- `analysis_goal` 不可為空字串。
- `evidence_items` 至少要有 1 筆。
- 每筆證據至少要有可用的 `content`。
- 若 `item_id` 重複，保留原值但在 `quality_checks.warnings` 註記重複風險。
- `content` 應為可分析文字（原文、逐字稿、摘要皆可）。

## Missing Data Output

缺資料時，輸出：

```json
{
  "missing_fields": ["analysis_goal", "evidence_items.content"],
  "why_needed": {
    "analysis_goal": "Needed to bound coding focus and prevent random interpretation.",
    "evidence_items.content": "Needed to produce auditable evidence quotes."
  },
  "questions_to_user": [
    "What decision should this coding support?",
    "Can you provide evidence items with stable item_id values and analyzable content?"
  ],
  "next_step_rule": "Do not code until required input is complete."
}
```

## Coverage Rule

- 至少 80% 的證據項目需被至少一個定位構面標註。
- 未達門檻時，`quality_checks.warnings` 必須說明原因，例如語料太短或噪音過高。
