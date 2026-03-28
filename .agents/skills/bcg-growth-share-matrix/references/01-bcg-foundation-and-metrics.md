# BCG Foundation And Metrics

## Purpose

提供 BCG 成長佔有率矩陣的核心定義、常用計算規則與門檻預設，避免分類時混用不同口徑。

## Core Logic

- BCG 矩陣用兩個 proxy 看組合配置：
  - `relative market share` 代表競爭力
  - `market growth rate` 代表市場吸引力
- 經典邏輯是：
  - 高 share 代表較高規模、經驗曲線與成本優勢機率
  - 高 growth 代表市場仍在擴張，未來資源投入可能有更高回報

## Relative Market Share

優先規則：
- 若輸入已提供 `relative_market_share`，直接採用
- 若未提供，且有 `market_share` 與 `largest_competitor_share`，則計算：

```text
relative_market_share = market_share / largest_competitor_share
```

判讀規則：
- `>= 1.0`：預設視為高 share
- `< 1.0`：預設視為低 share
- 若使用者提供產業 cut-off，以使用者版本優先

例子：
- 你的事業體市佔 24%，最大競爭者 12% -> `relative_market_share = 2.0`
- 你的事業體市佔 15%，最大競爭者 30% -> `relative_market_share = 0.5`

## Market Growth Rate

預設規則：
- `> 10%`：高 growth
- `<= 10%`：低 growth

注意：
- `10%` 只是常見教學與實務預設，不是跨產業固定法律
- 若產業本身成熟且平均成長很低，應改用產業情境 cut-off
- 若市場極新、極波動，單一年度成長率可能失真，優先看 2-3 年趨勢或 forward CAGR

## Borderline Rule

若使用者未另設，預設：
- `borderline_band = 2.0`

判讀方式：
- 若 `market_growth_rate` 距 cut-off 只差 2 個百分點內，標記為 `borderline growth`
- 若 `relative_market_share` 接近 1.0 且資料來源粗估，標記為 `borderline share`
- `borderline` 不改變分類規則，但會降低語氣確定性，並要求補資料或做敏感度說明

## Quadrant Definitions

- `Stars`: 高 share + 高 growth
- `Cash Cows`: 高 share + 低 growth
- `Question Marks`: 低 share + 高 growth
- `Dogs`: 低 share + 低 growth

## Coordinate Output Specification

每次分析都應附 `matrix_plot_data`，至少包含：

```json
{
  "x_axis": "relative_market_share",
  "y_axis": "market_growth_rate",
  "quadrant_cutoffs": {
    "relative_market_share_cutoff": 1.0,
    "market_growth_cutoff": 10.0
  },
  "points": [
    {
      "name": "Business A",
      "x": 1.2,
      "y": 12.5,
      "quadrant": "Stars",
      "borderline": false
    }
  ]
}
```

座標映射規則：
- `x >= relative_market_share_cutoff` 且 `y > market_growth_cutoff` -> `Stars`
- `x >= relative_market_share_cutoff` 且 `y <= market_growth_cutoff` -> `Cash Cows`
- `x < relative_market_share_cutoff` 且 `y > market_growth_cutoff` -> `Question Marks`
- `x < relative_market_share_cutoff` 且 `y <= market_growth_cutoff` -> `Dogs`

## Interpretation Guardrails

- 高 share 不是永遠等於長期優勢，只代表經典 BCG 邏輯下的競爭力 proxy
- 高 growth 也不等於必然值得投資，仍要看單位經濟、現金需求與勝率
- BCG 最適合拿來做資本配置優先序，不適合單獨代替完整戰略審查

## Source Notes

- BCG 官方 revisited 文章重申：原始矩陣用 `relative market share` 看 competitiveness，用 `growth rate` 看 market attractiveness，並指出今日市場中 share 與持久優勢的關聯已下降  
  https://www.bcg.com/publications/2014/growth-share-matrix-bcg-classics-revisited
- CFI 提供常見實務 cut-off：市場成長率常用 `10%` 作高低分界，並把四象限定義為 question marks, stars, dogs, cash cows  
  https://corporatefinanceinstitute.com/resources/management/boston-consulting-group-bcg-matrix/
