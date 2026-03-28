# Scoring and Dynamic Thresholds

## 1) 題目分數

每題使用 `0|1|2`：

- `0`: 缺乏檢查或偏誤明顯未處理
- `1`: 有檢查但不完整
- `2`: 檢查完整且證據可追溯

## 2) 分組與權重

- Group A: Q1-Q3，權重 `30%`
- Group B: Q4-Q9，權重 `40%`
- Group C: Q10-Q12，權重 `30%`

## 3) 分組標準化

分組 raw 分數上限：

- Group A 上限 = `6`
- Group B 上限 = `12`
- Group C 上限 = `6`

標準化公式：

- `group_score_0_100 = (group_raw / group_max) * 100`

## 4) 加權總分

- `weighted_total_score = A*0.30 + B*0.40 + C*0.30`
- 小數點保留到 1 位。

## 5) 決策大小分級（三因子）

三因子各 1-3 分：

- `financial_impact`
- `reversibility`
- `org_blast_radius`

總分：

- `size_total = financial_impact + reversibility + org_blast_radius`

分級：

- `Low`: `3-4`
- `Medium`: `5-7`
- `High`: `8-9`

## 6) 動態風險門檻

### Low（3-4）
- `Green`: `>= 75`
- `Yellow`: `60-74`
- `Red`: `< 60`

### Medium（5-7）
- `Green`: `>= 80`
- `Yellow`: `65-79`
- `Red`: `< 65`

### High（8-9）
- `Green`: `>= 85`
- `Yellow`: `70-84`
- `Red`: `< 70`

## 7) 風險解讀

- `Green`: 可進入執行，但仍需保留監控點。
- `Yellow`: 可條件式前進，需先補齊關鍵缺口。
- `Red`: 不建議前進，先做重新評估或重設方案。

## 8) 缺資料時的暫定規則

若三因子缺漏且使用者要求先給結論：

1. 暫定 `decision_size=Medium`。
2. 明確標註 `temporary_assumption=true`。
3. 在 `recommended_actions` 第一項要求補齊三因子再重算。
