# Quality Gates

## Performance and Accessibility Thresholds

最低門檻：

1. Desktop
- Performance >= 85
- Accessibility >= 90

2. Mobile
- Performance >= 75
- Accessibility >= 90

## Responsive Gate

必須檢查以下斷點至少一次：

- 390x844 (mobile)
- 768x1024 (tablet)
- 1440x900 (desktop)

要求：

- Hero 文字不可溢出
- CTA 必須在首屏可見（或可快速抵達）
- Navbar 不可遮蔽主內容

## Readability Gate

1. 主標與背景對比需可讀
2. 內文 line length 建議 45-85 字元
3. 重要 CTA 對比需明顯高於次要按鈕

## Motion Gate

1. reduced-motion 模式必須可正常使用
2. 動畫不可阻塞互動
3. 可視狀態切換需在 300-900ms 合理範圍

## Autonomy QA Loop

多輪模式下，每輪至少檢查：

- conversion clarity
- visual coherence
- readability
- performance risk

若最低項目 < 7.5，必須啟動下一輪修正（最多 3 輪）。

## Failure Handling

若任一硬性門檻未達：

1. 回報未達項目
2. 降低動畫強度與背景層複雜度
3. 再輸出修正版與前後差異
