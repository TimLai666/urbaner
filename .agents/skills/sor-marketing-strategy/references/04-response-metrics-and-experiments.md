# Response Metrics And Experiments

## Purpose

把 response 從「有沒有成交」擴大成可分階段觀察的指標系統，並把 S-O-R 假設轉成可測試的實驗。

## Response Ladder

| Response Level | 常見指標 | 前導訊號 | 典型風險 |
| --- | --- | --- | --- |
| attention | impression CTR, view rate, 停留 | 首屏停留、滑動、開信 | 只買到注意，沒買到意義 |
| engagement | click depth, add-to-cart, 收藏, 回覆 | 二次互動、內容展開 | 互動高但意圖弱 |
| conversion | signup, order, booking, lead | checkout start, form start | 壓榨短期轉換傷害信任 |
| repurchase | repeat order, renewal, upgrade | 回訪、再瀏覽、再開信 | 促銷依賴過高 |
| advocacy | referral, review, share, UGC | NPS、收藏、轉傳 | 聲量和推薦品質脫鉤 |

## KPI Ladder Rules

- 每份策略至少定義：
  - 1 個 primary outcome metric
  - 2-3 個 leading indicators
  - 1-2 個 guardrail metrics
- 若目標是 `conversion`，guardrail 常見是：
  - bounce rate
  - refund rate
  - lead quality
- 若目標是 `repurchase`，guardrail 常見是：
  - unsubscribe rate
  - notification mute
  - complaint/support rate

## Activity Participation Rate

對應草稿中的「活動參與率」，在這個 skill 中統一命名為 `activity_participation_rate`。

定義：
- 在指定期間內，完成指定活動行為的人數占可參與人數的比例。

計算口徑：

```text
activity_participation_rate
= unique_users_completed_activity / unique_users_eligible_for_activity
```

適用場景：
- 品牌活動、直播互動、社群任務、會員任務、門市體驗活動。
- S-O-R 中常用來衡量 `engagement` 層級的 response。

使用注意：
- 需要明確定義 `eligible`，避免把無法參與的人算進分母。
- 若活動分多步驟，另補 step-level participation，避免只看總參與率。
- 建議與 `conversion` 或 `repurchase` 一起觀察，避免只優化活動熱度。

## Experiment Mapping

把 S-O-R 假設寫成：

```text
Because [current organism problem],
we believe changing [stimulus]
will shift [desired organism state]
and increase [target response]
for [audience].
We'll measure this through [leading metrics] and [result metric].
```

## Good Experiment Targets

- 一次只驗證一個主要 stimulus change
- 先測最接近瓶頸的 stimulus
- 先選 impact 高、實作成本低、倫理風險低的測試

## Example Patterns

### 落地頁

- 問題：有流量，註冊低
- 假設：不是 CTA 顏色問題，而是 trust/risk 沒建好
- 可測 stimulus：
  - 將 social proof 與 guarantee 前移
  - 簡化 hero 訊息
- leading metrics：
  - CTA click-through rate
  - pricing section view
- result metric：
  - signup completed

### CRM / 回購

- 問題：推播有開，但回購低
- 假設：訊息有 attention，沒有 relevance 或 trust
- 可測 stimulus：
  - 促銷導向 vs 使用情境導向
  - generic offer vs 分群 offer
- leading metrics：
  - open rate
  - click-to-product rate
- result metric：
  - repeat purchase rate
- guardrail：
  - unsubscribe
  - block/mute rate

## Handoff Notes

- 需要正式 sample size、檢定方法、test duration 時，轉交 `$ab-test-setup`。
- 需要事件、參數、GA4/GTM 實作時，轉交 `$analytics-tracking`。

## Minimum Output For Experiment Plan

每次至少列出：
- `hypothesis`
- `control`
- `variant`
- `primary_metric`
- `leading_metrics`
- `guardrails`
- `decision_rule`
