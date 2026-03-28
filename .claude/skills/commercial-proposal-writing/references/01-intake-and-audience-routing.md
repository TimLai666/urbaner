# Intake and Audience Routing

## 1. 明確界定這份企劃要誰說 Yes

至少收斂以下資訊：

- `proposal_type`: `internal|fundraising|partnership`
- `audience`: 決策者、影響者、使用者
- `decision_goal`: 要推動什麼決策
- `ask`: 要批准的資源、金額、合作承諾或下一步
- `problem_statement`
- `target_customer`
- `available_evidence`
- `goal_kpi`
- `budget`
- `timeline`

## 2. 模式判定

- 有題目、想法、草綱，沒有完整正文 -> `generate`
- 已有稿件、要修改、要檢討 -> `review`

若是 `review`，但沒原稿或沒關鍵段落，先要求補件。

## 3. 受眾路由

### `internal`

重點看：

- 為什麼現在要做
- 要投多少資源
- ROI 與回收期
- 執行風險與 Go/No-Go

### `fundraising`

重點看：

- 市場機會
- 為什麼是現在
- 為什麼是這個團隊
- 成長敘事與資金用途

### `partnership`

重點看：

- 雙方價值交換
- 角色分工
- 合作機制
- 成功後的下一步

## 4. `tone_profile=auto`

- `internal -> executive_formal`
- `fundraising -> investor_formal`
- `partnership -> consulting_formal`

若受眾明確提到政府、標案、法遵、審議，再覆寫為 `gov_formal`。

## 5. MissingDataQueryOutput

固定輸出：

- `missing_fields`
- `why_needed`
- `questions_to_user`
- `no_data_options`
- `next_step_rule`

問題應逐題明確化，每題都要能直接回填。

## 6. A/B/C/D 無資料路徑

- A: 最快假設版
- B: 輕量訪談驗證版
- C: 小規模數據蒐集後正式版
- D: 客製方案

若使用 A，必須在正文中留下顯式假設標記，不可包裝成事實。
