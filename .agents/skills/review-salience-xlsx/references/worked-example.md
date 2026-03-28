# Worked Example — Safety Eyewear (923 reviews, 30 attributes, 4 clusters)

Use this file to calibrate scoring intuition and verify PCA / K-means outputs.
All results are from a full semantic reading pass + downstream analysis on
Amazon safety-eyewear reviews spanning English, French, Spanish, Italian, German.

---

## Corpus

8 products, 923 valid reviews (body length > 15 chars), no language filtering.

| Product | Count | Key use context |
|---------|-------|----------------|
| B00080FKIO | 115 | Shooting, airsoft, military (EN/FR/ES/IT/DE) |
| B007W7X1UK | 46 | Machine shop, OR, COVID PPE |
| B00X69LVKK | 37 | Military, tactical, everyday |
| B016KZ2APQ | 249 | Pickleball, factory, healthcare |
| B07GB8Y11G | 194 | Outdoor, sport, pickleball |
| B08GKPC599 | 208 | Healthcare, lab, pickleball |
| B0B15BXZ94 | 42 | Pickleball (sport-specific) |
| B0BQHBHNQF | 32 | Welding class, dental lab, pickleball |

---

## Scoring calibration examples

### Score = 0 (not mentioned)

> "Great for every day wear, been wearing these everyday for at least a year and I'm on my second pair"

- `s07` (impact protection) = 0 — no mention of ballistic or impact testing
- `s12` (ear-muff compatibility) = 0 — no hearing protection context
- `s13` (community identity) = 0 — no professional/military language

### Score = 3–4 (indirect or ambiguous)

> "Fogs up playing airsoft"

- `s02` (anti-fog) = 6 — clear complaint, single-sentence but unambiguous
- `s25` (scene adaptability) = 4 — airsoft is implied context, not elaborated

> "Die Brille passt, sitz bequem, der Preis ist ok."  
> (DE: The glasses fit, sit comfortably, the price is ok.)

- `s23` (all-day comfort) = 5 — "bequem" (comfortable) is clear
- `s28` (price-value) = 4 — "Preis ist ok" is neutral, not praising or criticising

### Score = 5–6 (clearly mentioned)

> "I work in an operating room and i am scrubbed in for 6+ hours a day. These glasses are comfy and looked and functioned great for the first 3 weeks. However i bought two pairs and the protective coating started to wear off of them after only 3 weeks of use. Some of the coating flaked off into my eye."

- `s05` (lens clarity durability) = 7 — coating failure is the central complaint, described vividly
- `s17` (team/workplace use) = 5 — bought two pairs, workplace context
- `s23` (all-day comfort) = 6 — "6+ hours a day" is explicit
- `s25` (scene adaptability) = 5 — OR context stated

### Score = 7 (strongly emphasised)

> "Buyer beware! You will only receive 1 color of lense. I give 3 stars and not 5 because of the fact that the product is deceptively advertised to make you think you are getting 3 sets."

- `s20` (ad honesty) = 7 — "deceptively advertised" is the entire purpose of the review

> "LITERALLY SCRATCHED WHEN I RECEIVED THEM!! This was probably my worst purchase ever."

- `s08` (scratch resistance) = 7 — capitalised emphasis, strongest possible negative signal

---

## Score distribution from this corpus

| Score | Count | % of all cells |
|-------|-------|---------------|
| 0 | 25,287 | 91.3% |
| 1 | 0 | 0.0% |
| 2 | 29 | 0.1% |
| 3 | 41 | 0.1% |
| 4 | 340 | 1.2% |
| 5 | 1,668 | 6.0% |
| 6 | 264 | 1.0% |
| 7 | 61 | 0.2% |

**Key observation:** 91 % of cells are 0. Most reviews mention only 2–5
attributes. Scores of 1 are nearly absent because reviews rarely make partial
references — they either say something clearly (5+) or don't say it (0).
Score 4 appears for ambiguous statements like "price is ok" or implied context.

---

## Average attributes mentioned per review

| Product | Mean non-zero attrs/review |
|---------|--------------------------|
| B0B15BXZ94 (pickleball-specific) | 4.4 |
| B00080FKIO (Wiley X, multi-context) | 3.5 |
| B0BQHBHNQF (lab/dental) | 3.3 |
| B007W7X1UK (Bollé) | 2.9 |
| B08GKPC599 (NoCry healthcare) | 2.7 |
| B07GB8Y11G (NoCry general) | 2.2 |
| B016KZ2APQ (3M) | 1.9 |

Short, complaint-focused reviews (3M corpus) produce lower attribute density
than detailed sport-use reviews (Impactable pickleball corpus).

---

## Cross-language scoring notes

- **Italian** "poco resistenti ai graffi" → `s08` = 6 (scratch resistance, clearly negative)
- **Spanish** "no se empañan" → `s02` = 5 (no fogging, clearly positive)
- **French** "ne bue pas au début (une semaine) et après rien à faire, on y voit plus rien" → `s02` = 7 (fog resistance collapses after one week — vivid, emphasis-worthy)
- **German** "beschlägt kaum" → `s02` = 4 (barely fogs — mild positive, not strong enough for 5)

Treat all languages identically. Do not assign lower confidence to non-English
reviews when scoring.

---

## PCA results

- **n_components chosen:** 11 (Kaiser criterion, eigenvalue > 1)
- **Cumulative variance explained:** 53.78%
- **Matrix shape:** 923 reviews × 30 attributes → 923 × 11 PC scores

### PC names (from dominant loadings |≥ 0.30|)

| PC | Name | Key positive attrs | Key negative attrs |
|----|------|-------------------|-------------------|
| PC01 | 整體使用價值感 | 長時間佩戴穩定性(+0.54), 全天佩戴舒適度(+0.49), 抗衝擊彈道防護(+0.48) | — |
| PC02 | 戰術品牌信任感 | 品牌聲望感知(+0.48), 鏡片互換配件擴充(+0.37) | 貼臉密封性(−0.42), 視野廣度(−0.40) |
| PC03 | 場景創新適應力 | 創新解決痛點(+0.71), 與耳罩相容性(+0.55), 防霧性能(+0.50) | 鏡框耐用性(−0.34) |
| PC04 | CP值vs社群認同 | CP值(+0.53), 相對競品價值感(+0.41) | 職業社群認同感(−0.36), 回購忠誠度(−0.34) |
| PC05 | 鏡片耐久性 | 鏡片耐刮性(+0.60), 鏡片透明度持久性(+0.51) | — |
| PC06 | 誠信與配件完整性 | 包裝完整性(+0.45), 鏡片互換配件擴充(+0.41), 廣告描述誠信度(+0.36) | — |
| PC07 | 廣告誠信vs霧化 | 廣告描述誠信度(+0.44), 防霧性能(+0.40) | 鏡片透明度持久性(−0.36), 全天佩戴舒適度(−0.35) |
| PC08 | 客服與推薦動機 | 客服售後支援(+0.50), 口碑推薦意願(+0.31) | — |
| PC09 | 密封vs輕量衝突 | 貼臉密封性(+0.33) | 輕量化(−0.31) |
| PC10 | 客服vs社交場合 | 客服售後支援(+0.46), 鼻墊可靠性(+0.32) | 同事共用適性(−0.35) |
| PC11 | 零件可靠性綜合 | 鼻墊可靠性(+0.41), 包裝完整性(+0.34), 客服售後支援(+0.34) | — |

---

## K-means results

### Scan K=2–9

| K | Inertia | Silhouette |
|---|---------|-----------|
| 2 | 13244.4 | **0.3700** ← highest |
| 3 | 12268.5 | 0.3229 |
| 4 | 11473.7 | 0.1845 |
| 5 | 10575.5 | 0.2052 ← starting K chosen |
| 6 | 9855.6 | 0.2125 |
| 7 | 9381.8 | 0.1933 |

K=2 wins silhouette but is too coarse. K=5 chosen as starting point for interpretability.

### Iterative pruning history

| Iter | K | Active | Silhouette | Cluster sizes | Action |
|------|---|--------|-----------|--------------|--------|
| 1 | 5 | 923 | 0.2052 | {0:52, 1:**45**, 2:564, 3:132, 4:130} | C1=45<47 (4.9%) → remove, K→4 |
| 2 | 4 | 878 | 0.2199 | {0:114, 1:52, 2:601, 3:111} | ✓ all ≥ 47 → converged |

### Re-assign all 923 reviews (`km.predict(PC_all)`)

The 45 pruned reviews are re-assigned to nearest centroid:
- 20 → Cluster 0 (体驗達人)
- 23 → Cluster 2 (沉默大眾)
- 1 → Cluster 1 (場景創新派)
- 1 → Cluster 3 (耐刮耐用派)

**Final cluster sizes (all 923 reviews):**

| Cluster | Name | n | % | PC centroid highlights |
|---------|------|---|---|----------------------|
| C0 | 體驗達人 | 134 | 14.5% | PC01=+2.71, PC02=−1.18 |
| C1 | 場景創新派 | 53 | 5.7% | PC03=+3.80, PC09=+0.87, PC06=+0.93 |
| C2 | 沉默大眾 | 624 | 67.6% | PC01=−0.46 (near zero on all PCs) |
| C3 | 耐刮耐用派 | 112 | 12.1% | PC05=+2.04, PC07=−0.85 |

Final silhouette (all 923): **0.1923** (slightly lower than 0.2199 due to re-assigned borderline reviews — expected)

### Cluster interpretation notes

- **C0 體驗達人:** Extremely high PC1 = overall satisfaction. Strong negative PC2 = not brand-driven. Top attrs: 活動場景適應廣度(3.29), 全天佩戴舒適度(2.95). Products: evenly spread; B08GKPC599 and B0B15BXZ94 slightly over-represented.
- **C1 場景創新派:** PC3 dominant (+3.80). Top attrs: 創新解決痛點(4.25), 防霧性能(3.60). B00080FKIO and B016KZ2APQ each ≈31% of this cluster (military/pickleball scenario language).
- **C2 沉默大眾:** All PCs near zero. Short, content-sparse reviews. Top attr by mean is 防霧性能(1.29) — even in the silent majority, fog is the #1 topic. B016KZ2APQ alone = 31% of this cluster.
- **C3 耐刮耐用派:** PC5=+2.04 dominant. Top attrs: 鏡片耐刮性(4.63), 鏡片透明度持久性(1.63). Negative PC7 = disappointed by anti-fog claims. This is the primary negative-signal cluster for product quality. B07GB8Y11G (36 reviews) and B016KZ2APQ (27) most frequent.
