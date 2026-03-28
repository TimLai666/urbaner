# Use Cases And Prompts

## 1) 通用行銷策略

### Use Case

當使用者想把某個 campaign、頁面或活動用 S-O-R 重新拆解時。

### Prompt

`請用 $sor-marketing-strategy 分析這個 campaign 的 Stimulus、Organism、Response，並產出可執行的策略與 KPI ladder。`

## 2) 電商轉換

### Use Case

當使用者有流量與點擊，但下單率低，想知道問題卡在價值、信任還是摩擦。

### Prompt

`我們的商品頁有流量但轉換差，請用 $sor-marketing-strategy 判斷刺激設計、心理機制與轉換阻力，並提出實驗計畫。`

### Output Focus

- `sor_map`
- `strategy_actions`
- `experiment_plan`

## 3) 會員 CRM / 回購

### Use Case

當使用者想提升會員回購、續約或再啟動。

### Prompt

`請用 $sor-marketing-strategy 幫我設計會員 CRM 策略，目標是提高回購。要同時分析被重視感與被打擾風險，並列出 KPI 與 guardrail。`

### Output Focus

- `organism` 需同時寫 relevance 與 intrusiveness
- `response` 主目標為 `repurchase`
- `guardrail` 必須含退訂或靜音風險

## 4) 品牌活動 / 聲量

### Use Case

當使用者有曝光與聲量，但不知道為什麼沒有更深層的 engagement 或 conversion。

### Prompt

`這個品牌活動有很多曝光，但沒帶動轉換。請用 $sor-marketing-strategy 拆解聲量、情緒、信任與行動之間的斷點。`

## 5) 文案前置策略

### Use Case

當使用者真正想要的是文案，但還沒想清楚心理機制、主張角度與 CTA 策略。

### Prompt

`先不要直接寫文案。請用 $sor-marketing-strategy 產出 message strategy brief，再說明哪些部分應交給 $copywriting。`

### Handoff Rule

- 先輸出：
  - `core_tension`
  - `message_angles`
  - `proof_points`
  - `cta_directions`
- 再建議用 `$copywriting` 成稿

## 6) 草稿案例模板：服飾品牌 + 網紅廣告提升點擊

### Use Case

當使用者想用 S-O-R 解析「網紅廣告是否真的提升點擊，或只是短期聲量」。

### Prompt

`以服飾品牌為例，請用 $sor-marketing-strategy 設計網紅廣告方案，目標提升點擊率。請輸出 S/O/R 三段具體措施、KPI ladder、以及低效刺激微調閉環。`

### Output Focus

- `stimulus_design_measures` 要有受眾定義、素材角度、投放位置
- `response_measurement_measures` 要有 CTR 與活動參與率
- `optimization_loop` 要點出低效刺激與下一輪測試

## 7) 草稿案例模板：互動體驗提升參與感

### Use Case

當使用者想強化「互動體驗 -> 被理解感 -> 參與行為」這條路徑。

### Prompt

`請用 $sor-marketing-strategy 以互動體驗活動為例，設計提升顧客參與感的策略。請特別輸出 organism 的 attitude_brand_affinity 變化與 response 的 activity_participation_rate。`

### Output Focus

- `organism_influence_measures` 要明確寫認知、情感、態度改變
- `response_measurement_measures` 要含活動參與率與後續轉換指標
- `optimization_loop` 要有資料回看節點與微調行動
