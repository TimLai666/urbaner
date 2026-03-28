# Worked Example (Turbocharger Reviews)

## Example Input

```json
{
  "analysis_goal": "理解消費者如何評價渦輪增壓器的市場定位與實際價值",
  "evidence_items": [
    {
      "item_id": "i1",
      "content": "訪談摘錄：尺寸吻合，裝上去一次就成功，增壓反應比原廠件快。",
      "content_type": "text",
      "source_type": "interview_note",
      "source_ref": "intv-2026-01"
    },
    {
      "item_id": "i2",
      "content": "客服工單摘要：包裝完整但客服回覆偏慢，功能上跑高速時很穩。",
      "content_type": "text",
      "source_type": "support_ticket",
      "source_ref": "ticket-8831"
    },
    {
      "item_id": "i3",
      "content": "社群貼文：安裝教學不難，但一開始擔心和車型不合。",
      "content_type": "text",
      "source_type": "social_post",
      "source_ref": "post-177"
    }
  ]
}
```

## Example JSON (Excerpt)

```json
{
  "theory": "product_positioning",
  "theory_annotations": [
    {
      "item_id": "i1",
      "family": "product_positioning",
      "subtheory": "attributes",
      "quote": "尺寸吻合"
    },
    {
      "item_id": "i1",
      "family": "product_positioning",
      "subtheory": "functions",
      "quote": "增壓反應比原廠件快"
    },
    {
      "item_id": "i2",
      "family": "product_positioning",
      "subtheory": "usage_context_service_experience",
      "quote": "客服回覆偏慢"
    }
  ]
}
```

## Example Markdown (Section Names)

- 摘要
- 構面判讀
- 證據引文
- STP 對接欄位
- 限制與假設
