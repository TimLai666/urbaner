# Use Cases And Prompts

## 集團事業組合分析

```text
Use $bcg-growth-share-matrix 以繁體中文分析以下集團事業組合。請先檢查資料是否足夠，若不足先輸出 MissingDataOutput。若足夠，請計算或確認 relative market share，將各事業體分類為 Cash Cows、Stars、Question Marks、Dogs，並提出 portfolio-level 的資本配置與例外說明。
```

## 產品線組合分析

```text
Use $bcg-growth-share-matrix 分析這家公司各產品線的 BCG 位置。請不要只做分類，還要說明每條產品線的分類依據、投資姿態、停損條件，以及哪幾條線應被收割來支持成長線。
```

## 投資委員會簡報版

```text
Use $bcg-growth-share-matrix 幫我做投資委員會版本。請先給 5 點 executive summary，再給 unit classification table，最後給 Now / Next / Later 的資本重配建議。語氣要直接、可決策，不要只做教科書解釋。
```

## 缺資料追問版

```text
Use $bcg-growth-share-matrix 先做 data sufficiency gate。若沒有最大競爭者市佔或 market growth 口徑，先追問最關鍵的 3 個問題，不要直接硬分類。
```

## 保守版輸出

```text
Use $bcg-growth-share-matrix 分析以下事業組合，但對接近 cut-off 的單位請標記 borderline，並在 assumptions_and_limitations 中說明若門檻改變，結果可能如何改變。
```

## 座標與遷移路徑版

```text
Use $bcg-growth-share-matrix 以繁體中文分析以下集團。請務必輸出 matrix_plot_data（x=relative_market_share, y=market_growth_rate, points 與 quadrant_cutoffs），並在 unit classification table 為每個事業體提供 development_potential、likely_transition_path 與 transition_condition，不可只給象限名稱。
```
