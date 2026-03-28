# Intake And Data Sufficiency

## Purpose

先確認資料是否足以支撐 BCG 分類，避免在錯誤市場邊界或缺失數據上做資本配置建議。

## Required Inputs Checklist

- `group_context`
- `business_units[]`
- 每個單位至少一筆可用於競爭力判定的資料：
  - `relative_market_share`
  - 或 `market_share + largest_competitor_share`
- 每個單位至少一筆可用於市場吸引力判定的資料：
  - `market_growth_rate`

## Recommended Inputs Checklist

- `revenue_size`
- `cash_generation`
- `strategic_synergy`
- `competitive_moat`
- `capex_intensity`
- `time_horizon`
- `thresholds`

## MissingDataOutput Template

```json
{
  "missing_fields": [],
  "why_needed": {},
  "questions_to_user": [],
  "temporary_assumptions": [],
  "assumption_risks": [],
  "next_step_rule": "若缺口會改變象限或資本動作，先補資料。"
}
```

## Questioning Rules

- 一次追問 1-3 個最影響分類的缺口
- 優先追問：
  - 最大競爭者市佔
  - 市場成長率口徑
  - 市場邊界定義
  - 現金生成能力
- 問句應短，能一兩句回答

## Quick Question Bank

- 這些事業體是否都放在同一個可比較的市場定義下？
- 各事業體的最大競爭者是誰，其市佔率是多少？
- `market_growth_rate` 是歷史 YoY、3 年 CAGR，還是前瞻預估？
- 哪些事業體目前是集團現金來源，哪些仍在吃現金？
- 是否有即使低 share 也必須保留的事業，原因是協同、防禦或牌照？

## Temporary Assumption Rules

- 只有在使用者要先推進分析、且缺口不會讓結果完全失真時，才允許暫時假設
- 每個暫時假設都要列：
  - `assumption`
  - `why_used`
  - `risk_if_wrong`
  - `what_to_collect_next`

## Data Hierarchy

優先順序：
1. 使用者提供的明確數值
2. 使用者提供的可計算數值
3. 具名來源的估算數值
4. 暫時假設

禁止：
- 用模糊詞如「領先」、「成長快」直接當作數值
- 把不同市場口徑的 share 放在同一張矩陣比較
- 把單年異常波動直接當成長期 growth 趨勢

## Exception Triggers

若出現以下訊號，即使象限已能判出，也必須加例外說明：
- `strategic_synergy` 很高
- 法規牌照、分銷入口、關鍵供應能力難替代
- 平台或生態位勢高於短期市佔
- 事業體是其他高價值單位的必要前置條件
