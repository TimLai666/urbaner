# 專案背景：昆豪企業 × Urbaner 產學合作

## 計畫資訊

- **計畫名稱**：Biz Connect Taipei—2026「台北市數位產學實作計畫」
- **合作廠商**：昆豪企業股份有限公司（統編 33778451）
- **聯絡人**：林雷鈞（總經理）｜raylin@kunnexinc.com.tw
- **合作形式**：純遠端（線上）

## 公司背景

- **創立**：1977年，創辦人林雲聲，總部新北市淡水區
- **核心理念**：Bright Idea, Great Value
- **沿革**：1977－2013 OEM代工（歐、美、日品牌）→ 2014 林雷鈞接班，轉型 OBM 自有品牌 → 2020 品牌營收正式超越代工
- **規模**：中小企業，登記資本額新台幣 1,500 萬元

## 品牌與市場

- **品牌**：URBANER 奧本（電動毛髮修剪器），2014年創立，品牌核心「品味源自細節」
- **外銷市場**：美國、日本（兼維持 OEM 代工日本、歐洲品牌）
- **外貿型態**：OBM 品牌商 + OEM 製造商雙引擎
- **銷售通路**：
  - Amazon US：<https://www.amazon.com/urbaner>
  - Amazon JP：<https://www.amazon.co.jp/URBANER>
  - 日本樂天市場（2021 年取得台灣公司直營店鋪資格，台灣廠商中稀缺優勢）
  - URBANER 跨境官網：<https://www.urbaner.jp/ja>
  - 台灣本地電商與實體通路
  - 群眾募資平台（日本市場品牌曝光）
- **拓銷策略**：先國內再海外 → 先線上再線下 → 先平台再官網

## 產品線

| 系列 | 說明 |
|------|------|
| 奧本男士系列 | 專業電動理髮剪、刮鬍刀等男性美容修剪器 |
| 奧本寵物系列 | 家用寵物電剪，主打在家享受沙龍體驗 |
| 奧本家用系列 | 多功能家庭美容修剪套組 |
| 奧本女生系列 | 女性毛髮修剪與美容相關產品 |
| 替換刀頭配件 | 各系列耗材與零件 |

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
