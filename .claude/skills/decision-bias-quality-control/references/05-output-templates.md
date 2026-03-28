# Output Templates (Dual Track Mandatory)

## Template A: Standard Decision Report

```markdown
## Executive Summary
- 決策題目：{decision_statement}
- 模式：{mode}
- 決策大小：{decision_size}
- 風險等級：{risk_level}
- 建議：{go | conditional-go | no-go}

## A. 質性軌
### bias_diagnosis
- Group A（Q1-Q3）：{summary}
- Group B（Q4-Q9）：{summary}
- Group C（Q10-Q12）：{summary}

### key_risks
1. {risk_1}（證據：{evidence}）
2. {risk_2}（證據：{evidence}）
3. {risk_3}（證據：{evidence}）

### recommended_actions
1. [P1] {action}（owner: {owner}, due: {date}）
2. [P2] {action}（owner: {owner}, due: {date}）
3. [P3] {action}（owner: {owner}, due: {date}）

## B. 量化軌
### question_scores (0-2)
| Q | score | rationale | evidence |
| --- | --- | --- | --- |
| Q1 | {0-2} | {one-line reason} | {source} |
| ... | ... | ... | ... |
| Q12 | {0-2} | {one-line reason} | {source} |

### group_scores (0-100)
- Group A: {score}
- Group B: {score}
- Group C: {score}

### weighted_total_score
- {score}

### threshold_profile_used
- decision_size={Low|Medium|High}
- threshold={table_reference}

## Assumptions and Data Gaps
- {assumption_1}
- {gap_1}

## Next Validation Loop
- {48h or next meeting validation tasks}
```

## Template B: MissingDataOutput

```markdown
## MissingDataOutput
- missing_fields:
  - {field_1}
  - {field_2}
- why_needed:
  - {reason_1}
  - {reason_2}
- questions_to_user:
  1. {question_1}
  2. {question_2}
- temporary_assumption: {none | Medium decision size}
- risk_of_assumption: {impact statement}
```

## Template C: Meeting Facilitation Add-on

```markdown
## Meeting Facilitation Script
- 會議目標：{objective}
- 決策時間盒：{timebox}

### question_sequence
1. Group A: Q1 -> Q2 -> Q3
2. Group B: Q4 -> Q5 -> Q6 -> Q7 -> Q8 -> Q9
3. Group C: Q10 -> Q11 -> Q12

### facilitator_prompts
- Q1: {prompt}
- Q5: {prompt}
- Q11: {prompt}

### consensus_gaps
- {gap_1}
- {gap_2}

### close_criteria
- {what must be true for decision closure}
```

## Output Ordering Rules

- 先輸出 Executive Summary。
- 再輸出 A. 質性軌。
- 再輸出 B. 量化軌。
- 最後輸出 Assumptions 與 Next Validation Loop。
- 缺資料時，先輸出 MissingDataOutput，再提供可選暫定評分。
