# Targeting

## Purpose

本文件定義市場區隔資料如何轉換為目標市場選擇。

## Required Inputs

- `segment_profiles`
- `comparison_axes`
- 至少一種反應變數

可用反應變數例：

- 忠誠度
- 活躍度
- 消費額
- 使用頻率
- 曾購與否
- 轉換意圖
- 潛力分數

## Required Paths

### Current Target Market

分析對象：

- 現有高價值顧客
- 忠誠顧客
- 活躍顧客
- 重度消費顧客

### Potential Target Market

分析對象：

- 曾購品牌與否
- 初次採用潛力
- 轉單可能性
- 未來可爭取客群

## Method Rule

| Response Type | Example | Preferred Method |
| --- | --- | --- |
| Continuous / interval-like | loyalty score, spending, activity score | `ANOVA`, `post-hoc`, `regression` |
| Binary | purchased_or_not, convert_or_not | `chi-square`, `logistic regression` |

Pairwise default:

- 若 `ANOVA p<0.05`，預設輸出 `Tukey HSD (alpha=0.05)` 成對比較結果。

## Output Rule

- 不得只停留於顯著差異。
- 必須輸出：
  - 優先目標市場
  - 次優先市場
  - 暫不投入市場
- 每項結論均需附統計依據、市場規模 / 占比與品牌適配理由。

### Hard Rule (Must)

- 若存在 `profile_*` 欄位，必須輸出 `profile_significance_summary`（chi-square）。
- 若不存在可用輪廓欄位，仍須輸出 `profile_significance_summary.status=not_available` 與原因。
- 所有 `ANOVA p<0.05` 的變數，必須在 `pairwise_comparison_table` 中存在對應比較列。

### Recommendation

- 補充 `proactive_marketing_notes`，說明如何把目標市場結論轉為需求塑造策略。
- 補充 `usp_translation_candidates`，把目標客群洞察轉為可執行訴求句型。

## Required Outputs

- `Current Target Market Summary`
- `Potential Target Market Summary`
- `Target Selection Decision`
- `Target Selection Rationale`
- `Targeting Risks And Tradeoffs`
- `profile_significance_summary`
- `pairwise_comparison_table`
