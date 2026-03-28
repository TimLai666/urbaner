# Pressure Scenario 01: 促銷頁角度

## Purpose

驗證 skill 在常見商業需求下，是否能輸出可直接拿去寫促銷頁的策略，而不是停留在心理學解釋。

## Scenario

使用者提供一個中價位生活用品品牌，想做母親節檔期促銷頁。

已知資料：

- 產品：居家香氛禮盒
- 受眾：25-40 歲上班族女性，會買禮物給媽媽或自己
- 目標：提高檔期下單率
- channel：landing-page
- conversion_stage：warm
- proof_assets：有實拍圖、使用情境照、原價與組合價

## Baseline Without Skill

未載入 skill 時，模型常見缺點：

- 只給一般性文案建議，沒有明確 trigger stack
- 標題與 CTA 常偏空泛，像是 `立即選購`
- 會提到情感價值，但不會主動安排錨定與框架

## Pass Criteria

- 明確輸出 `strategy_summary`
- 明確輸出 `trigger_stack`
- 至少提供 3 個 `headline_options`
- 至少提供 3 個 `cta_options`
- 能正確把 `安撫 / 正當化驅動` 搭配 `錨定`
- 用繁體中文與台灣用語

## Fail Signs

- 只有散文式建議，沒有固定欄位
- 沒有 trigger stack
- CTA 過於抽象
- 完全沒用到價差或方案比較
