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

- `analysis_goal` 與 `evidence_items` 不可缺。
- `content` 若全為空白或只有符號，視為不可用。
- 若證據僅有評分無可分析內容，需回傳缺資料而非猜測動機。
- `content` 應為可分析文字（原文、逐字稿、摘要皆可）。

## Missing Data Output

```json
{
  "missing_fields": ["analysis_goal", "evidence_items.content"],
  "why_needed": {
    "analysis_goal": "Needed to limit interpretation scope for WOM motive coding.",
    "evidence_items.content": "Needed to infer sharing intent with auditable quotes."
  },
  "questions_to_user": [
    "What sharing behavior decision should this analysis support?",
    "Can you provide evidence items with stable item_id values and analyzable content?"
  ],
  "next_step_rule": "Do not infer WOM motives until required input is complete."
}
```

## Coverage Rule

- 至少 70% 證據項目需有可辨識動機或明確 `insufficient` 判斷。
- 若大量證據只有功能描述但無分享意圖，需在限制章節說明。
