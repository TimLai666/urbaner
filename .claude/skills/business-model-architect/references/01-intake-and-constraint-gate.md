# Intake and Constraint Gate

## Purpose

在產出商業模式前，先完成資料齊備與限制條件盤點，避免在錯誤前提上做高成本推演。

## Required Inputs Checklist

- `product_or_service`: 產品/服務內容與核心功能
- `target_customer_context`: 客戶輪廓、場景、購買行為
- `market_context`: 市場規模、競品、替代方案
- `constraints`: 預算、時間、法規、技術、人才
- `goal_kpi`: 目標 KPI（含時間區間）
- `scope_boundary`: 提供範疇與不提供範疇
- `current_wt_state`: 現有弱勢與外部威脅（WT）狀態
- `control_levers_context`: 可調整的資源、能力、流程、合作槓桿

## MissingDataOutput Template

```json
{
  "missing_fields": [],
  "why_needed": {},
  "questions_to_user": [],
  "temporary_assumptions": [],
  "assumption_risks": []
}
```

## Questioning Rules

- 一次優先追問 1-3 個最關鍵缺口，不要散射提問。
- 問題應可用一句話回答，避免開放式長答。
- 優先問會影響「定價、通路、可行性」的欄位。
- 若缺 `scope_boundary`、`current_wt_state`、`control_levers_context`，必須優先追問。

## Quick Question Bank

- **（震央問題）** 你目前手上最強的牌是什麼：既有資源/夥伴、創新產品想法、對特定客群的深度理解，還是需要重構財務？→ 幫助選擇震央
- 產品目前最希望解決的高頻問題是什麼？
- 目標客群目前用什麼替代方案？
- 30 天內最重要的 KPI 是什麼？
- 目前最硬的限制是預算、法規，還是人力能力？
- 你明確不做的客群、場景、功能是哪些？
- 現階段最致命的弱勢與最直接的外部威脅是哪些？
- 目前可以在 30 天內調動的資源與合作槓桿有哪些？

## Temporary Assumption Rules

- 只能在缺少必要資料且任務需先推進時使用暫時假設。
- 每個假設都要附帶 `risk_if_wrong` 與驗證信號。
- 假設只能支撐暫行版，不得當作最終定案。
