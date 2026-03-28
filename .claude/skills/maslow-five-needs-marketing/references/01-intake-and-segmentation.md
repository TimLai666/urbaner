# Intake and Segmentation

以 IQ 228 顧問標準輸出：策略必須可驗證、可執行、可衡量。

## 1) Required Inputs

| field | type | required | note |
| --- | --- | --- | --- |
| product_or_service | string | yes | 產品/服務描述與核心價值 |
| target_audience | string | yes | 受眾輪廓、購買場景與痛點 |
| offer | string | yes | 價值主張與成交主體 |
| goal_kpi | string[] | yes | 成功判準與數值目標 |
| time_horizon | string | yes | 執行期間與檢核節點 |

## 2) Optional Inputs

| field | type | required | note |
| --- | --- | --- | --- |
| budget | string | no | 預算區間與限制 |
| channels | string[] | no | 可用通路清單 |
| copy_goal | enum | no | 文案目的：awareness/consideration/conversion/retention |
| copy_channel | enum | no | 文案主通路：ad/landing-page/email/social/line |
| desired_emotion | enum | no | 情緒目標：trust/belonging/status/aspiration |
| copy_constraints | string[] | no | 文案限制：字數、禁用詞、法規、語氣邊界 |
| brand_tone | string | no | 品牌語氣限制 |
| constraints | string[] | no | 法規、素材、人力限制 |
| proof_assets | string[] | no | 案例、評價、數據證據 |
| market_context | string | no | 市場趨勢與季節性 |
| competition_context | string | no | 競品動態與定位 |

## 3) Segmentation Checklist

- 人口層：年齡、職業、收入、地區。
- 行為層：購買頻率、使用情境、替代方案。
- 心理層：動機、焦慮、身份訴求、價值觀。
- 風險層：價格敏感度、信任門檻、轉換阻力。

## 4) Copy Brief Minimum (Optional but Recommended)

- 若任務含文案方向，至少補齊：`copy_goal`、`copy_channel`、`desired_emotion`。
- 若缺少這三項，可先回傳提問，不要直接生成文案成稿。
## 5) Data Sufficiency Gate

缺必要欄位時，回傳 `MissingDataOutput`，不得直接輸出完整策略。

```json
{
  "missing_fields": [],
  "why_needed": {},
  "questions_to_user": [],
  "next_step_rule": "補齊必要欄位後再輸出策略"
}
```

## 6) Non-Guessing Rule

- 不可自行捏造受眾特徵、成效數據、通路限制。
- 不確定資訊必須標記 `Assumption`，並附 `Validation Needed`。
