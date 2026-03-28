# Worked Example (Turbocharger Reviews)

## Example Input

```json
{
  "analysis_goal": "理解消費者購買渦輪增壓器時的主要決策驅動",
  "evidence_items": [
    {
      "item_id": "i1",
      "content": "訪談摘要：跟車型很合，安裝順利，價格也合理。",
      "content_type": "text",
      "source_type": "interview_note",
      "source_ref": "intv-2026-02"
    },
    {
      "item_id": "i2",
      "content": "客服工單：包裝完整但物流有點慢，客服有回但要等一天。",
      "content_type": "text",
      "source_type": "support_ticket",
      "source_ref": "ticket-8890"
    },
    {
      "item_id": "i3",
      "content": "社群貼文：看了幾篇比較文後才下單，重點還是怕買到不合規格。",
      "content_type": "text",
      "source_type": "social_post",
      "source_ref": "post-210"
    }
  ]
}
```

## Example JSON (Excerpt)

```json
{
  "theory": "purchase_motivation",
  "theory_annotations": [
    {
      "item_id": "i1",
      "family": "purchase_motivation",
      "subtheory": "functional",
      "quote": "跟車型很合，安裝順利"
    },
    {
      "item_id": "i2",
      "family": "purchase_motivation",
      "subtheory": "security",
      "quote": "包裝完整但物流有點慢"
    },
    {
      "item_id": "i2",
      "family": "purchase_motivation",
      "subtheory": "relational",
      "quote": "客服有回但要等一天"
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
