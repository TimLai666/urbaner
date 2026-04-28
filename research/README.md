# Urbaner 競品研究輸出（research/）

## 內容

### 1. 關鍵字
- [`keywords.md`](keywords.md) — 220+ 個英日雙語關鍵字，9 大類別 + 跨類別補充

### 2. 自家 ASIN（排除清單）
- [`own_asins.txt`](own_asins.txt) — 84 個 URBANER 已知 ASIN（從 `rawdata_Urbaner/amazon_reviews/` 推得，找競品時自動排除）

### 3. Amazon 競品評論
- [`amazon_us/`](amazon_us/) — 9 個類別 × Amazon US 競品 ASIN + 各 5-6 則最新真實評論（按 review-rank 排序）
- [`amazon_jp/`](amazon_jp/) — 9 個類別 × Amazon JP 競品 ASIN + 各 5 則最新真實評論

每個檔案結構：
```
CATEGORY: <類別>
Top competitors: ASIN + 標題 + 評論數
### ASIN - 商品名 (評論數)
評分|日期|評論內容(截斷至170字)
```

### 4. 社群媒體觀點（產品聚焦）
- [`social_us/insights.md`](social_us/insights.md) — Reddit + 美國論壇 + 部落格綜合，按 9 類別整理痛點、好評、競品偏好
- [`social_jp/insights.md`](social_jp/insights.md) — Yahoo!知恵袋 + 価格.com + マイベスト + note + 楽天みんなのレビュー 綜合

### 5. 廣義消費者情緒洞察（**主題式、非產品聚焦**）
- [`social_us/sentiment.md`](social_us/sentiment.md) — 7 大主題：刮鬍、身體除毛、鼻毛/耳毛、眉毛/臉部、寵物毛髮、寵物指甲、嬰兒理髮。每主題涵蓋核心情緒、痛點集合、願望清單、送禮場景、文化情境
- [`social_jp/sentiment.md`](social_jp/sentiment.md) — 同 7-8 大主題的日本版本，附日本特有「身嗜み」「父の日ギフト」「節約意識」文化分析

> 此兩檔回應「想了解消費者對主題的想法、心情、痛點與願望」需求 — 不限產品評論，包含日常生活情境、約會、送禮、自我形象、寵物溝通、育兒等情緒層面

---

## 蒐集方法

| 來源 | 工具 | 說明 |
|------|------|------|
| Amazon US 評論頁 | Claude in Chrome（瀏覽器自動化） | `product-reviews/<ASIN>/` 直接抓最新 5-6 則真實評論 |
| Amazon JP 評論 | 同上，但因 JP 站需登入只用 `dp/<ASIN>` 商品頁底端 8 條 top reviews | 大多數為日文真實顧客留言 |
| 社群媒體（US） | WebSearch + WebFetch | Reddit 直連被封鎖，改用搜尋引擎彙整 |
| 社群媒體（JP） | WebSearch | 直接搜知恵袋 + 価格.com + マイベスト + note |

---

## 重要說明

1. **JP 評論限制**：Amazon JP 的 `product-reviews/` URL 強制登入，本研究改抓商品頁底部前 8 則最新評論。少數 ASIN（特別是寵物用品）的評論為跨國共享，內容混合 US / CA / UK / MX。
2. **競品篩選**：所有競品 ASIN 已比對 `own_asins.txt` 排除 URBANER 自家 ASIN（如 B08LGGMP5W、B0FCYBJK6T、B07XLLBB5J、B0C2Y71YXV、B0F5VJD5DQ 等）。
3. **評論字數**：每則評論截斷至 170 字以避免工具輸出限制；保留完整字串於原始爬取流程，需 deeper analysis 可重抓。
4. **社群媒體 vs 評論的差別**：
   - 評論 = 已購買用戶的實際使用反饋（單方面）
   - 社群媒體 = 比較、討論、推薦、不滿（多方互動，常含品牌偏好遷移）

---

## 後續分析建議

1. **痛點 → 產品差異化**：從 [社群洞察]_insights.md 抽取的「痛點清單」可直接對映到 Urbaner 產品迭代方向（特別是「靜音」「LED 顯示」「USB-C」「IPX7」「LCD 電量」）。
2. **競品定位地圖**：對 9 類別 × 兩市場已有完整 top-5 競品清單（含 ASIN、標題、評論數），可直接建定位 matrix（價位 × 評分）。
3. **跨市場 Insight**：US 偏好「professional / barber-grade」品牌敘事；JP 偏好「専門家監修・医療クリニック推奨・分貝數值化」訴求。
4. **品牌策略洞察**：Panasonic 在 JP 全品類獨大；US 是 Wahl/Andis/Manscaped 三足鼎立，新興品牌靠 LCD + 顏色設計切入。

---

## 檔案位置（Windows path）
```
C:\Users\tingzhen\Documents\GitHub\urbaner\research\
├── README.md                  ← 本檔
├── keywords.md                ← 220+ 關鍵字
├── own_asins.txt              ← 自家 ASIN 排除清單
├── amazon_us/                 ← Amazon US 競品評論（9 個 .txt + 1 個 .json）
├── amazon_jp/                 ← Amazon JP 競品評論（9 個 .txt）
├── social_us/insights.md      ← 美國社群觀點彙整
└── social_jp/insights.md      ← 日本社群觀點彙整
```
