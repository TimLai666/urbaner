# Segmentation

## Purpose

本文件定義評論資料如何轉換為市場區隔輸出。

## Core Lens

`Segmentation` 階段以人／貨／場為主軸：

- `人`：消費者特質、需求、動機、輪廓線索
- `貨`：產品特色、購買觸發、定位基礎
- `場`：使用情境、消費情境、場景線索

## Product Trigger Classification Rule

`貨` 類訊號必須標記主要判斷系統：

- `System 1`：直覺、情感、形象、氣氛、犒賞、衝動、分享感
- `System 2`：價格、品質、功能、效率、成分、比較、理性計算

## Maslow Keyword Requirement

Segmentation 輸出必須列出五需求層級與對應評論關鍵字：

- 生理需求
- 安全需求
- 社交需求
- 尊重需求
- 自我實現需求

## Segmentation Variable Taxonomy

### 地理統計

- 國家別
- 地區別
- 城市大小
- 氣候
- 人口密度

### 人口統計

- 年齡
- 生命週期階段
- 生命階段
- 性別
- 所得
- 世代
- 職業
- 教育
- 家庭生命週期
- 社會階層

### 心理統計

- 生活型態
- 人格特質
- 個性
- 動機

### 行為變數

- 場合
- 追求的利益
- 使用者狀態
- 產品使用頻率
- 品牌忠誠度
- 消費情境
- 購買準備階段
- 態度

## Clustering Method Rule

- 分群前須整理區隔變數或動機因子。
- 優先方法：`factor analysis -> K-means`
- `k` 可由 2 起試。
- 任一群體占比 `< 5%` 時，不得保留該解；需降低群數並重新執行。
- 最終結果所有群體占比均須 `> 5%`。

## Required Outputs

- `Segmentation Summary`
- `Segment Variable Table`
- `Cluster Share Table`
- `Segment Profile Cards`
- `Consumer Portrait Narrative`
