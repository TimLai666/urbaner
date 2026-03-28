# External Scorer Integration

This file describes how to swap Claude's built-in semantic scoring for an
external service such as an n8n workflow, a REST API, or a batch CSV round-trip.
All patterns satisfy the same scorer contract:

**Input:** review string + attribute catalog  
**Output:** list of N integers (0–7), one per attribute, in catalog order

---

## Pattern A — n8n webhook (recommended for automation)

Set up an n8n workflow that:
1. Receives a POST request with `{ "reviews": [...], "attributes": [...] }`
2. Passes each review through your scoring logic (LLM node, code node, or hybrid)
3. Returns `{ "scores": [[int, ...], [int, ...], ...] }` — one list per review

### Python call

```python
import requests, json

N8N_WEBHOOK_URL = "https://your-n8n-instance.com/webhook/salience-scorer"

def score_batch_n8n(reviews: list[str], attrs: list[tuple]) -> list[list[int]]:
    """
    Send a batch of reviews to n8n; receive salience scores back.
    Returns list of lists: scores[i][j] = salience of review i on attribute j.
    """
    payload = {
        "reviews": reviews,
        "attributes": [{"id": a[0], "label": a[1]} for a in attrs],
    }
    resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["scores"]
```

### n8n workflow sketch

```
[Webhook trigger]
  → [Code node: parse body, build prompt per review]
  → [LLM node: score each review (loop or batch)]
  → [Code node: validate & reshape to [[int...], ...]]
  → [Respond to webhook: { "scores": ... }]
```

### Switching to n8n in the pipeline

Replace the scorer contract call in Step 3 of the main skill:

```python
# Instead of Claude scoring one by one:
# row_scores = score_one_review(review_text, ATTRS)

# Batch-call n8n:
batch_size = 20
for i in range(0, len(reviews), batch_size):
    batch = reviews[i:i + batch_size]
    batch_scores = score_batch_n8n(batch, ATTRS)
    scores[pid].extend(batch_scores)
```

---

## Pattern B — Generic REST API

Any service that accepts a review + attribute list and returns integers works.

```python
def score_batch_api(reviews, attrs, api_url, api_key=None):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "reviews": reviews,
        "attributes": [{"id": a[0], "label": a[1]} for a in attrs],
        "scale": {"min": 0, "max": 7},
    }
    resp = requests.post(api_url, json=payload, headers=headers, timeout=180)
    resp.raise_for_status()
    data = resp.json()
    # Normalise: accept either {"scores": [...]} or flat list
    return data.get("scores", data)
```

---

## Pattern C — Batch CSV round-trip

For services that accept file input (e.g. cloud ML endpoints, spreadsheet macros):

### Export

```python
import csv

with open('/tmp/to_score.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["review_id", "review_text"])
    for pid, reviews in all_reviews.items():
        for i, text in enumerate(reviews):
            writer.writerow([f"{pid}_{i+1:04d}", text])
```

### Import

After the external service fills in the score columns:

```python
import csv

scored = {}
with open('/tmp/scored.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        scored[row["review_id"]] = [int(row[f"s{a[0]}"]) for a in ATTRS]
```

---

## Validation

Regardless of the scorer used, validate before building the Excel file:

```python
def validate_scores(scores, all_reviews, attrs):
    for pid, reviews in all_reviews.items():
        assert len(scores[pid]) == len(reviews), \
            f"{pid}: expected {len(reviews)} rows, got {len(scores[pid])}"
        for i, row in enumerate(scores[pid]):
            assert len(row) == len(attrs), \
                f"{pid}[{i}]: expected {len(attrs)} scores, got {len(row)}"
            for v in row:
                assert 0 <= v <= 7, \
                    f"{pid}[{i}]: score {v} out of range 0–7"
    print("✓ All scores valid")
```

---

## Choosing a scorer

| Situation | Recommended scorer |
|-----------|-------------------|
| Ad-hoc analysis, < 200 reviews | Claude built-in (semantic reading) |
| Repeated runs on same corpus | n8n webhook (Pattern A) — cacheable, auditable |
| Large corpus (> 1000 reviews) | Batch CSV round-trip (Pattern C) — parallelisable |
| Custom ML model or fine-tuned LLM | Generic REST API (Pattern B) |
| Manual override / expert annotation | Import from CSV (Pattern C, manual fill) |
