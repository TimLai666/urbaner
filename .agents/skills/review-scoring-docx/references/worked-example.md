# Worked Example — Safety Eyewear (Amazon, 8 products, 923 reviews)

This file illustrates what one complete run of the skill looks like. Nothing here
is prescriptive for other product categories. The attribute labels, Maslow
assignments, and scores are all specific to this corpus; a different category
(e.g. headphones, skincare, kitchen appliances) will yield different attributes.

Use this file to:
- Calibrate what a well-formed attribute catalog looks like
- Anchor your scoring intuition against real reference scores
- See which attribute discovery heuristics surfaced the most signal

---

## Corpus summary

| Product ID | Description | Valid reviews | Languages |
|-----------|-------------|--------------|-----------|
| B00080FKIO | Wiley X Saber Advanced | 115 | EN, FR, ES, IT, DE |
| B007W7X1UK | Bollé Safety | 46 | EN, ES |
| B00X69LVKK | ESS Crossbow | 37 | EN, ES |
| B016KZ2APQ | 3M Solus | 249 | EN, FR, ES |
| B07GB8Y11G | NoCry (v1) | 194 | EN, ES |
| B08GKPC599 | NoCry (v2) | 208 | EN, DE |
| B0B15BXZ94 | Impactable Pickleball | 42 | EN |
| B0BQHBHNQF | Lab/Science glasses | 32 | EN, FR, ES |

Key finding: products with the most reviews (249 / 208 / 194) showed the largest
divergence between early and full-corpus scores — sampling would have materially
changed the rankings.

---

## Attribute catalog (30 attributes)

### Tier 1 — Physiological (attributes 01–06)

| id | label | dimension | tier |
|----|-------|-----------|------|
| 01 | 光學清晰度 | Whether vision through the lens is free of distortion, blur, or unwanted magnification | 生理 |
| 02 | 防霧性能 | How quickly fog forms on the lens and whether the anti-fog claim holds under real use conditions | 生理 |
| 03 | 視野廣度 | How much of the peripheral visual field the frame and lens cover without obstruction | 生理 |
| 04 | 抗UV／眩光 | Whether the lens filters UV radiation and reduces glare in bright conditions | 生理 |
| 05 | 鏡片透明度持久性 | How long the lens stays optically clear before hazing, yellowing, or coating delamination | 生理 |
| 06 | 貼臉密封性 | How well the frame seals against the face to prevent debris, wind, or splash entry | 生理 |

### Tier 2 — Safety (attributes 07–12)

| id | label | dimension | tier |
|----|-------|-----------|------|
| 07 | 抗衝擊／彈道防護 | Whether the lens and frame meet Z87 / ballistic standards and hold up in impact tests | 安全 |
| 08 | 鏡片耐刮性 | How quickly the lens surface accumulates scratches under normal handling and cleaning | 安全 |
| 09 | 鏡框耐用性 | How often hinges, arms, or frame-to-lens joints break under everyday stress | 安全 |
| 10 | 長時間佩戴穩定性 | Whether the glasses stay in position during activity without sliding or requiring constant adjustment | 安全 |
| 11 | 鼻墊可靠性 | Whether the nose pad stays attached and correctly positioned over extended use | 安全 |
| 12 | 與耳罩相容性 | Whether the frame allows hearing protection to seal properly and whether a strap system is available | 安全 |

### Tier 3 — Belonging (attributes 13–17)

| id | label | dimension | tier |
|----|-------|-----------|------|
| 13 | 職業／社群認同感 | Whether reviewers cite the product as a marker of professional or community membership (military, medical, sport) | 社交 |
| 14 | 禮物適切性 | Whether the product was purchased as a gift and whether the recipient responded positively | 社交 |
| 15 | 口碑推薦意願 | How strongly reviewers state they have recommended or will recommend the product to others | 社交 |
| 16 | 回購忠誠度 | Whether reviewers have bought multiple units over time and intend to continue | 社交 |
| 17 | 同事共用適性 | Whether the product was bought for team or workplace use and how that experience was received | 社交 |

### Tier 4 — Esteem (attributes 18–22)

| id | label | dimension | tier |
|----|-------|-----------|------|
| 18 | 外觀造型吸引力 | Whether reviewers comment positively on the visual design and how the product looks when worn | 自尊 |
| 19 | 品牌聲望感知 | How much the brand name raises reviewer confidence and perceived product status | 自尊 |
| 20 | 廣告／描述誠信度 | Whether the product delivered on all claims in the listing (anti-fog, lens count, scratch resistance, etc.) | 自尊 |
| 21 | 客服與售後支援 | How responsive and effective the brand was when reviewers raised problems | 自尊 |
| 22 | 相對競品價值感 | How reviewers rate the product's value when explicitly comparing it to premium or budget alternatives | 自尊 |

### Tier 5 — Self-actualisation (attributes 23–30)

| id | label | dimension | tier |
|----|-------|-----------|------|
| 23 | 全天佩戴舒適度 | Whether extended wear (hours to full shift) causes pressure discomfort at ears, nose, or temples | 自我實現 |
| 24 | 輕量化 | Whether the weight of the glasses is low enough to feel unobtrusive during activity | 自我實現 |
| 25 | 活動場景適應廣度 | How many distinct use contexts (shooting, sport, lab, medical, outdoor work) reviewers report using the product in | 自我實現 |
| 26 | 鏡片互換／配件擴充 | Whether the product supports lens swapping, elastic strap replacement, or a parts ecosystem | 自我實現 |
| 27 | 適配頭型多樣性 | Whether the product fits a wide range of head shapes, nose types, and over-glasses use cases | 自我實現 |
| 28 | C/P 值 | Whether reviewers judge the price to be justified by the quality and durability they actually experienced | 自我實現 |
| 29 | 包裝完整性 | Whether the delivered product matched the listing (contents, condition, quantity) | 自我實現 |
| 30 | 創新解決痛點 | Whether the product solves a problem that competing products consistently fail at (e.g. fogging with mask, earmuff interference) | 自我實現 |

---

## Score reference table

Full-corpus scores (all valid reviews, no truncation). Use these to calibrate your
scoring intuition — not to copy scores into a new analysis.

| # | Attribute | B00080FKIO | B007W7X1UK | B00X69LVKK | B016KZ2APQ | B07GB8Y11G | B08GKPC599 | B0B15BXZ94 | B0BQHBHNQF |
|---|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| 01 | 光學清晰度 | 7 | 7 | 8 | 5 | 6 | 6 | 7 | 7 |
| 02 | 防霧性能 | 4 | 3 | 6 | 4 | 5 | 4 | 7 | 5 |
| 03 | 視野廣度 | 8 | 7 | 8 | 7 | 7 | 6 | 8 | 7 |
| 04 | 抗UV／眩光 | 8 | 7 | 8 | 5 | 5 | 4 | 7 | 6 |
| 05 | 鏡片透明度持久性 | 6 | 4 | 5 | 4 | 3 | 3 | 6 | 4 |
| 06 | 貼臉密封性 | 8 | 6 | 8 | 6 | 7 | 6 | 7 | 7 |
| 07 | 抗衝擊／彈道防護 | 9 | 6 | 9 | 6 | 6 | 5 | 8 | 7 |
| 08 | 鏡片耐刮性 | 5 | 4 | 4 | 3 | 3 | 3 | 6 | 4 |
| 09 | 鏡框耐用性 | 7 | 6 | 7 | 3 | 4 | 4 | 4 | 7 |
| 10 | 長時間佩戴穩定性 | 7 | 8 | 8 | 6 | 7 | 6 | 8 | 7 |
| 11 | 鼻墊可靠性 | 5 | 6 | 5 | 3 | 4 | 5 | 5 | 5 |
| 12 | 與耳罩相容性 | 9 | 5 | 7 | 5 | 5 | 4 | 5 | 5 |
| 13 | 職業／社群認同感 | 9 | 4 | 9 | 5 | 4 | 4 | 5 | 5 |
| 14 | 禮物適切性 | 7 | 6 | 7 | 5 | 5 | 6 | 6 | 7 |
| 15 | 口碑推薦意願 | 7 | 6 | 8 | 5 | 5 | 5 | 8 | 7 |
| 16 | 回購忠誠度 | 7 | 8 | 8 | 4 | 4 | 5 | 7 | 7 |
| 17 | 同事共用適性 | 7 | 7 | 7 | 6 | 5 | 6 | 6 | 7 |
| 18 | 外觀造型吸引力 | 8 | 6 | 8 | 5 | 6 | 5 | 7 | 8 |
| 19 | 品牌聲望感知 | 9 | 7 | 9 | 5 | 5 | 5 | 6 | 6 |
| 20 | 廣告／描述誠信度 | 4 | 3 | 7 | 2 | 3 | 3 | 7 | 7 |
| 21 | 客服與售後支援 | 8 | 5 | 6 | 3 | 7 | 8 | 5 | 6 |
| 22 | 相對競品價值感 | 7 | 7 | 7 | 5 | 5 | 5 | 7 | 7 |
| 23 | 全天佩戴舒適度 | 8 | 8 | 8 | 5 | 6 | 6 | 8 | 8 |
| 24 | 輕量化 | 7 | 8 | 8 | 7 | 7 | 8 | 8 | 7 |
| 25 | 活動場景適應廣度 | 8 | 7 | 8 | 6 | 7 | 6 | 6 | 7 |
| 26 | 鏡片互換／配件擴充 | 8 | 5 | 6 | 4 | 5 | 4 | 5 | 5 |
| 27 | 適配頭型多樣性 | 6 | 6 | 6 | 4 | 5 | 4 | 5 | 6 |
| 28 | C/P 值 | 7 | 7 | 6 | 5 | 5 | 5 | 7 | 7 |
| 29 | 包裝完整性 | 5 | 7 | 7 | 4 | 4 | 5 | 6 | 7 |
| 30 | 創新解決痛點 | 8 | 5 | 7 | 5 | 5 | 5 | 7 | 7 |
| — | **Product avg** | **7.10** | **6.03** | **7.17** | **4.73** | **5.17** | **5.03** | **6.47** | **6.40** |

---

## Key observations from this corpus

These are observations about this specific dataset, not universal rules.

**Attribute with widest variance:** 廣告／描述誠信度 (attribute 20) — scores ranged from 2 (3M, systematic anti-fog failure + missing items) to 7 (ESS, Impactable, Lab glasses). Ad-honesty gaps are consistently diagnostic in e-commerce reviews.

**Attribute most correlated with overall rank:** 鏡框耐用性 (09) and 鏡片耐刮性 (08) — the products that ranked lowest all shared severe structural fragility complaints.

**Tier most often under-counted in first pass:** Tier 3 (Belonging). Military/professional identity language and gifting cues are easy to miss when scanning quickly.

**Sampling risk:** B016KZ2APQ (3M) scored a naive 7.0 on a first-100-review pass, but dropped to 4.73 when all 249 reviews were read. The later reviews contained a concentration of durability failures that tipped the balance.
