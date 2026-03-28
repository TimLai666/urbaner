# 專案背景：昆豪企業 × Urbaner 產學合作

## 計畫資訊

- **計畫名稱**：Biz Connect Taipei—2026「台北市數位產學實作計畫」
- **合作廠商**：昆豪企業股份有限公司（統編 33778451）
- **聯絡人**：林雷鈞（總經理）｜raylin@kunnexinc.com.tw
- **合作形式**：純遠端（線上）

## 品牌與市場

- **品牌**：Urbaner（旗下電動毛髮修剪器）
- **外銷市場**：美國、日本
- **外貿型態**：品牌商 + 製造商
- **電商平台**：Amazon US、Amazon JP、跨境官網
  - Amazon US：https://www.amazon.com/urbaner
  - Amazon JP：https://www.amazon.co.jp/URBANER
  - 官網：https://www.urbaner.jp/ja

## 核心任務

> **分析美國、日本 Amazon 的電剪市場**

企業提供的資料為 Amazon 平台數據，存放於 `rawdata_Urbaner/`：

| 資料集 | 路徑 | 說明 |
|--------|------|------|
| 競品評論 | `amazon_reviews/` | 各類別競品的顧客評論（xlsx） |
| 競品銷售 | `competitor_sales/` | 競品每月銷量與銷售額（xlsx） |
| 自身訂單 | `amazon_sales/US_sales/` | Urbaner 美國訂單（2024-03～） |
| 自身訂單 | `amazon_sales/JP_sales/` | Urbaner 日本訂單（2023-01～） |

## 產品類別（9 類）

```
001 Beard / Mustache Trimmers
002 Nose / Ear Trimmers
003 Body Groomers
004 Eyebrow Trimmers
005 Foil Shavers
006 Pet Electric Clippers
007 Pet Nail Clipper
008 Dog Nail Grinder
009 Baby Hair Clippers
```

## 開發環境

- **Python 環境**：uv 管理，使用 `.venv/Scripts/python` 執行
- **主要套件**：pandas、openpyxl、matplotlib
- **JP 銷售檔案編碼**：shift-jis
- **US 銷售檔案編碼**：utf-8
- **視覺化輸出**：matplotlib，font = Microsoft YaHei

## 分析腳本

- `analyze.py`：資料全覽（讀取三大資料集 + 9 張圖表）
- `urbaner_overview.png`：視覺化輸出
- `data_overview.md`：資料摘要文件
