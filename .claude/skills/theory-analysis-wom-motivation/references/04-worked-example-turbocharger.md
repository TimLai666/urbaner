# Worked Example (Turbocharger Reviews)

## Example Input

```json
{
  "analysis_goal": "辨識證據提供者分享渦輪增壓器經驗背後的口碑動機",
  "evidence_items": [
    {
      "item_id": "i1",
      "content": "訪談摘要：寫這段是給想自己改裝的人參考，少走一些冤枉路。",
      "content_type": "text",
      "source_type": "interview_note",
      "source_ref": "intv-2026-03"
    },
    {
      "item_id": "i2",
      "content": "社群貼文：我研究很久才找到這顆，裝完真的有差，分享給同好。",
      "content_type": "text",
      "source_type": "social_post",
      "source_ref": "post-233"
    },
    {
      "item_id": "i3",
      "content": "客服工單紀要：物流拖超久，真的很火大。",
      "content_type": "text",
      "source_type": "support_ticket",
      "source_ref": "ticket-8912"
    }
  ]
}
```

## Example JSON (Excerpt)

```json
{
  "theory": "wom_motivation",
  "theory_annotations": [
    {
      "item_id": "i1",
      "family": "wom_motivation",
      "subtheory": "altruistic",
      "quote": "給想自己改裝的人參考"
    },
    {
      "item_id": "i2",
      "family": "wom_motivation",
      "subtheory": "self_enhancement",
      "quote": "我研究很久才找到這顆"
    },
    {
      "item_id": "i2",
      "family": "wom_motivation",
      "subtheory": "social_identity",
      "quote": "分享給同好"
    },
    {
      "item_id": "i3",
      "family": "wom_motivation",
      "subtheory": "emotional_expression",
      "quote": "真的很火大"
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
