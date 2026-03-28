# Output Contract (JSON + Markdown)

## JSON Contract

```json
{
  "theory": "product_positioning",
  "dimension_results": [
    {
      "dimension": "attributes",
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
      "dimension": "attributes",
      "quote": "",
      "reason": "",
      "sentiment": "positive|neutral|negative"
    }
  ],
  "theory_annotations": [
    {
      "item_id": "",
      "family": "product_positioning",
      "subtheory": "attributes",
      "quote": ""
    }
  ],
  "stp_mapping": {
    "attribute_group_recommendation": "attribute_function|benefit_use|brand_personality|brand_image",
    "suggested_stat_roles": ["segmentation", "targeting", "positioning"],
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

- `dimension_results.dimension` 與 `theory_annotations.subtheory` 必須對齊。
- `evidence_count` 必須等於該構面被引用的 `evidence_quotes` 筆數。
- `quality_checks.input_valid = false` 時，不輸出具體結論，只輸出缺資料說明。
