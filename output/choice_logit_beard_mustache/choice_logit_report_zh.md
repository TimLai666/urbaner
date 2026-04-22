# Amazon 顧客評論聯合分析（Choice / Logit）完整報告

## 一、研究目的

本報告的目標，是把 Amazon 評論資料轉成可估計的選擇行為資料（choice data），用聯合分析思路估計消費者對各屬性的部分效用（part-worth utility），進而回答三個問題：

1. 什麼屬性會顯著提升產品被選擇機率？
2. 哪些屬性組合最值得優先投入開發？
3. 產品定位與定價訊息要先打哪幾個賣點？

## 二、資料範圍與模型設定

- 產品類別：Beard / Mustache Trimmers
- 產品數：40
- 評論數：7,118
- 選擇集合大小（alternatives per set）：40
- long-format 列數：284,720
- 模型估計樣本：2,500 則評論（固定隨機抽樣）
- 模型：Conditional Logit（低階水準作為參照組）

## 三、聯合分析流程（完整版）

### Step 1：評論資料標準化

先整合標題、內文、星等、語言、國家欄位，並排除過短或資訊不足的評論，確保後續屬性評分穩定。

### Step 2：評論屬性評分

依據 attribute catalog 關鍵詞規則，對每篇評論計算屬性分數，形成 review-level attribute profile。

### Step 3：聚合為產品層級特徵

將評論層級分數彙整為產品層級平均值，得到 product-level attribute vector。

### Step 4：屬性分層（low / mid / high）

把連續分數切為 low / mid / high。當唯一值不足時採穩健替代切分，避免 dummy 編碼失真。

### Step 5：Dummy 編碼

每個屬性轉為 mid/high 兩個 dummy（low 為參照組），後續係數即為相對於 low 的效用差。

### Step 6：建構 long-format choice data

每一筆評論都展開成 40 筆候選產品資料：

- 實際評論產品：`choice = 1`
- 其餘 39 款替代品：`choice = 0`

### Step 7：Conditional Logit 估計

以 BFGS 迭代求解，輸出每個屬性水準的係數、標準誤、z 值、p 值與 odds ratio。

### Step 8：效用轉決策

將係數解讀為部分效用，並連結到產品組合排序與定位訊息，形成實際策略建議。

## 四、核心屬性中英對照（含中文備註）

| 屬性代碼 | 英文屬性 | 中文備註 |
|---|---|---|
| rechargeable_design | Rechargeable Design | 充電式設計 |
| blade_sharpness | Blade Sharpness | 刀片鋒利度 |
| blade_hair_pulling | Blade Hair Pulling / Snagging | 刀片拉毛問題 |
| motor_power_rpm | Motor Power / Speed | 馬達功率轉速 |
| waterproof_rating_ipx8 | IPX8 Waterproof Rating | IPX8防水等級 |
| adjustable_comb_settings | Adjustable Comb Length Settings | 可調式導梳長度設定 |
| price_value_ratio | Price-to-Value Ratio | 性價比 |
| ease_of_use_overall | Ease of Use (Overall) | 整體易用性 |

## 五、模型表現摘要

| 指標 | 數值 |
|---|---:|
| Log-likelihood | -8,589.749 |
| Null log-likelihood | -26,257.444 |
| McFadden pseudo R² | 0.6729 |
| Top-1 hit rate | 0.0701 |

解讀重點：

- McFadden pseudo R² 達 0.6729，代表相對於隨機基準有強解釋力。
- Top-1 hit rate 在大 choice set 下通常偏低，應與 pseudo R²、係數顯著性一起解讀。

## 六、係數結果與管理意涵

### 1) 正向驅動屬性

- `ease_of_use_overall_tier_high`（整體易用性高階）係數最高：2.0320
- `price_value_ratio_tier_high`（性價比高階）係數：1.2132
- `blade_sharpness_tier_high`（刀片鋒利度高階）係數：0.8915
- `waterproof_rating_ipx8_tier_mid`（IPX8 防水中階）係數：0.8938

管理含意：優先強化「好上手、值得買、夠鋒利、可防水」會最直接提升選擇機率。

### 2) 負向風險屬性

- `adjustable_comb_settings_tier_high` 係數：-3.4765
- `adjustable_comb_settings_tier_mid` 係數：-0.9470
- `blade_hair_pulling_tier_high` 係數：-1.4617

管理含意：過度複雜的導梳設定與拉毛體驗會明顯削弱轉換，應優先簡化操作並降低卡毛風險。

### 3) 屬性效用差（high - low）

| 屬性 | high - low |
|---|---:|
| ease_of_use_overall | 2.0320 |
| price_value_ratio | 1.2132 |
| blade_sharpness | 0.8915 |
| motor_power_rpm | 0.5415 |
| waterproof_rating_ipx8 | 0.3365 |
| rechargeable_design | 0.2828 |
| blade_hair_pulling | -1.4617 |
| adjustable_comb_settings | -3.4765 |

## 七、WTP（願付價格）換算方式

若後續模型加入真實價格係數 $\beta_{price}$，可用下式換算：

$$
WTP = -\frac{\beta_{attribute}}{\beta_{price}}
$$

比較兩個水準時：

$$
WTP(high\ vs.\ low) = -\frac{\beta_{high}-\beta_{low}}{\beta_{price}}
$$

本次 `price_value_ratio` 為感知價值，不是實際售價，因此目前結果建議做「相對效用」解讀，不直接轉美元金額。

## 八、圖表建議與逐圖說明（可直接放簡報）

1. 係數條圖（`logit_coefficients_bar.png`）
說明：比較各屬性水準對效用的正負與強弱。
口頭解讀：正向越長代表越能拉升選擇機率；負向越長代表應優先排除的設計風險。

2. 前五名組合機率圖（`top5_choice_probabilities.png`）
說明：顯示前五組產品組合的 raw 與 normalized 機率。
口頭解讀：可用來決定新品先後上架順序與資源分配。

3. 選擇資料流程圖（建議新增）
說明：從評論清理、屬性評分、dummy 編碼到 logit 估計。
口頭解讀：讓非技術部門理解模型如何連到實際決策。

## 九、可直接採用的結論

1. 核心勝出邏輯不是功能越多越好，而是「使用感知價值」越清晰越好。
2. 優先投資屬性順序建議：整體易用性 → 性價比 → 刀片鋒利度 → 防水便利性。
3. 產品開發需避免複雜度失控，導梳設計與卡毛問題是目前最明確的負向訊號。

## 十、附註

本次估計使用 2,500 筆評論樣本進行模型 fit，以兼顧收斂穩定與運算效率。完整資料與係數輸出已存於同資料夾，後續可延伸至全樣本估計或加入真實價格變數。 