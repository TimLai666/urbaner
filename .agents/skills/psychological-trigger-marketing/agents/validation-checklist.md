# Validation Checklist

## RED: Baseline Findings

- 未載入 skill 時，輸出容易停在抽象行銷建議
- 常見缺 trigger stack、headline 結構與 CTA 結構
- 容易把 FOMO 直接寫成假限量或假倒數
- 容易忽略台灣在地語感，寫成泛中文案
- 容易只講品牌故事，不處理轉換節奏與價格比較

## GREEN: Structure Checks

- `SKILL.md` frontmatter 只有 `name` 與 `description`
- description 只描述觸發條件，不摘要 workflow
- `SKILL.md` 明確包含：
  - `Overview`
  - `When to Use`
  - `Input Contract`
  - `Data Sufficiency Gate`
  - `Trigger Engine`
  - `Trigger Selection Rules`
  - `Output Contract`
  - `Hard Rules`
  - `Suggested Prompts`
- `references/01-trigger-playbook.md` 包含六種 trigger
- `references/02-application-matrix.md` 包含 channel 與目標的套用表
- `agents/` 包含三個 pressure scenario 與一份 checklist

## GREEN: Behavioral Checks

- 產出固定欄位：
  - `strategy_summary`
  - `trigger_stack`
  - `message_angles`
  - `headline_options`
  - `cta_options`
  - `risk_flags`
  - `assumptions_used`
- 缺必要資料時，會先輸出 `MissingDataOutput`
- 預設使用繁體中文與台灣用語
- 保留雙軌命名：
  - `嚇唬 / 失落驅動`
  - `安撫 / 正當化驅動`
  - `引誘 / 渴望驅動`
- 不會一次把六種 trigger 全開

## REFACTOR: Guardrail Checks

- 不得捏造數據、見證、原價、限量或倒數
- 使用稀缺或限時說法時，必須在 `risk_flags` 中能追溯到真實條件
- 沒有 `proof_assets` 時，會降低強刺激 FOMO 的使用強度
- 不把在地、公益、友善、永續當成空洞裝飾詞
- CTA 不應只有空泛動詞

## Acceptance Gate

視為可交付前，至少要通過：

- `quick_validate.py` 通過
- `agents/openai.yaml` 與 `SKILL.md` 對齊
- 三個 pressure scenario 都能用這份 skill 的結構檢查
