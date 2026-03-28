# 建議補充的資料清單

> 現有資料缺乏流量與轉換指標，建議請廠商從 Amazon Seller Central 後台補充以下報告。

---

## 優先級高（影響核心分析）

| 報告名稱 | 後台路徑 | 可取得的欄位 | 用途 |
|----------|----------|-------------|------|
| Detail Page Sales and Traffic by ASIN | Reports → Business Reports → By ASIN | Sessions、Page Views、Buy Box %、Units Ordered、Unit Session %（轉換率） | 計算 Urbaner 各 SKU 真實轉換率 |
| Search Term Report | Advertising → Reports → Search Term | Impressions、Clicks、CTR、Spend、Sales、ACOS、CVR | 廣告關鍵字效益、點擊轉換分析 |

---

## 優先級中（補強分析深度）

| 報告名稱 | 後台路徑 | 可取得的欄位 | 用途 |
|----------|----------|-------------|------|
| Inventory Ledger | Reports → Fulfillment → Inventory Ledger | 每日庫存水位、進貨量、出貨量、調整量 | 庫存周轉分析、斷貨風險評估 |
| Returns Report | Reports → Fulfillment → Returns | 退貨原因、退貨率、ASIN | 品質問題識別 |
| Campaign Performance Report | Advertising → Reports → Campaign | CPC、展示次數、點擊數、廣告銷售額 | 廣告投報率分析 |

---

## 優先級低（選擇性補充）

| 報告名稱 | 後台路徑 | 可取得的欄位 | 用途 |
|----------|----------|-------------|------|
| FBA Reimbursements | Reports → Payments → Reimbursements | 退款金額、原因 | 損耗成本估算 |
| Date Range Transaction Report | Reports → Payments | 費用明細（FBA 費、廣告費、平台抽成） | 毛利率推算 |

---

## 補充說明

- 報告請分別匯出 **US（amazon.com）** 與 **JP（amazon.co.jp）** 兩個站點
- 時間範圍建議與現有訂單資料對齊：**US 從 2024-03、JP 從 2023-01**
- 格式：CSV 或 TSV 均可，放入 `rawdata_Urbaner/` 下對應子資料夾
