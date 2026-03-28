# Urbaner Amazon 資料全覽摘要

> 資料來源：`rawdata_Urbaner/`｜分析日期：2026-03-28

---

## 資料結構（共 176 個檔案）

| 資料集 | 格式 | 檔案數 | 說明 |
|--------|------|--------|------|
| `amazon_reviews/` | xlsx | 84 | 競品顧客評論，按類別 / ASIN 分檔 |
| `competitor_sales/` | xlsx | 30 | 競品每月銷售量 & 金額 |
| `amazon_sales/US_sales/` | txt (TSV) | 26 | Urbaner 美國訂單（2024-03 ～ 2026-02） |
| `amazon_sales/JP_sales/` | txt (TSV) | 36 | Urbaner 日本訂單（2023-01 ～ 2026-02） |

---

## 類別清單（9 個）

| ID | 類別名稱 |
|----|---------|
| 001 | Beard / Mustache Trimmers |
| 002 | Nose / Ear Trimmers |
| 003 | Body Groomers |
| 004 | Eyebrow Trimmers |
| 005 | Foil Shavers |
| 006 | Pet Electric Clippers |
| 007 | Pet Nail Clipper |
| 008 | Dog Nail Grinder |
| 009 | Baby Hair Clippers |

> 目前 `amazon_reviews` 與 `competitor_sales` 只有 001 / 002 / 003 三個類別有實際資料。

---

## 關鍵數字（KPI）

| 指標 | 數值 |
|------|------|
| 競品評論總數 | **11,799** 筆 |
| 競品產品數（ASIN） | **50** 個 |
| 競品市場累計銷售額 | **¥1,282.4M** |
| Urbaner US 累計出貨量 | **4,184** 件 |
| Urbaner JP 累計出貨量 | **16,744** 件 |
| 競品平均評分 | **4.42 ★** |

---

## amazon_reviews 欄位結構

| 欄位 | 說明 |
|------|------|
| ASIN | 產品編號 |
| 标题 | 評論標題 |
| 内容 | 評論內文 |
| VP评论 | 是否為 Verified Purchase |
| Vine Voice评论 | 是否為 Vine 評論 |
| 型号 | 型號 / 規格 |
| 星级 | 星級（1–5） |
| 赞同数 | Helpful 數量 |
| 图片数量 / 图片地址 | 評論圖片 |
| 是否有视频 / 视频地址 | 評論影片 |
| 评论人 | 評論者名稱 |
| 所属国家 | 評論者國家 |
| 评论时间 | 評論日期 |

各類別評論數量：
- **001 Beard**：~7,700 筆（最多）
- **002 Nose/Ear**：~3,100 筆
- **003 Body**：~980 筆

星級分佈呈 J 形（5 星壓倒多數），平均 **4.42 ★**。

---

## competitor_sales 欄位結構

| 欄位 | 說明 |
|------|------|
| 站点 | 市場（JP） |
| 最近几月 | 月份（YYYY-MM） |
| ASIN | 產品編號 |
| 商品 | 產品名稱 |
| 所属类目 | 類目 |
| 月销量 | 月出貨件數 |
| 月销售额(￥) | 月銷售金額（日圓） |
| 平均单价(￥) | 平均售價（日圓） |

- 目前僅 **001 Beard/Mustache Trimmers** 有競品銷售資料（30 個 ASIN）
- Top 品牌：**Wahl、Panasonic**，單品月銷最高近 **40,000 件**
- 市場有明顯季節性，年末銷售額飆升至 **¥450M+**

---

## amazon_sales 欄位結構（US & JP 共通）

| 欄位 | 說明 |
|------|------|
| amazon-order-id | 訂單編號 |
| purchase-date | 購買時間 |
| order-status | 狀態（Shipped / Cancelled） |
| product-name | 產品名稱 |
| sku | SKU 編號 |
| asin | ASIN |
| quantity | 數量 |
| currency | 貨幣（USD / JPY） |
| item-price | 商品售價 |
| ship-country | 出貨國家 |

Urbaner Top SKU（JP 市場）：
1. `MB-042/FBA`：Mustache Trimmer（最暢銷）
2. `MB-980/FBA`
3. `CT-20/FBA`：Pet Nail Clipper

JP 出貨量約為 US 的 **4 倍**，JP 高峰達 1,000+ 件/月。

---

## 視覺化

完整圖表見 [`urbaner_overview.png`](urbaner_overview.png)，涵蓋：
1. 各類別評論數量
2. 評論星級分佈
3. 各類別平均星級
4. 競品月銷量 Top 15
5. 競品市場月總銷售額趨勢
6. Urbaner 月出貨量趨勢（US vs JP）
7. Urbaner SKU 出貨量排行
8. 競品評論月新增趨勢
