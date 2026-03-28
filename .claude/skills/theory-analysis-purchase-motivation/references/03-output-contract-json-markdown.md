# Output Contract (JSON + Markdown)

## JSON Contract

```json
{
  "theory": "purchase_motivation",
  "dimension_results": [
    {
      "dimension": "functional",
      "summary": "",
      "signal_direction": "positive|mixed|negative|insufficient",
      "evidence_count": 0,
      "evidence_item_ids": [],
      "confidence": "high|medium|low"
    }
  ],
  "evidence_quotes": [
    {
      "item_id": "",
      "dimension": "functional",
      "quote": "",
      "reason": "",
      "sentiment": "positive|neutral|negative"
    }
  ],
  "theory_annotations": [
    {
      "item_id": "",
      "family": "purchase_motivation",
      "subtheory": "functional",
      "quote": ""
    }
  ],
  "stp_mapping": {
    "attribute_group_recommendation": "attribute_function|benefit_use",
    "suggested_stat_roles": ["segmentation", "targeting"],
    "dimension_catalog_notes": []
  },
  "quality_checks": {
    "input_valid": true,
    "missing_fields": [],
    "coverage": {
      "total_items": 0,
      "coded_items": 0
    },
    "warnings": [],
    "assumptions": []
  }
}
```

## Markdown Contract

固定輸出以下章節：

1. `摘要`
2. `構面判讀`
3. `證據引文`
4. `STP 對接欄位`
5. `限制與假設`

## Consistency Rules

- `dimension_results.dimension` 只可用 `functional/security/relational`。
- `theory_annotations.family` 必須固定為 `purchase_motivation`。
- `quality_checks.input_valid = false` 時，僅輸出缺資料資訊與下一步。
