# Review Mining Reference

How to extract demand-side signal from consumer review text. Used in Phase I (data acquisition) to feed the triangulation step in Phase II (attribute filtering).

## Why this matters

Product page data tells you what attributes *exist*. Review data tells you what attributes *matter to consumers*. An attribute must score on both before it enters the model — that's the triangulation principle.

Skipping this step typically results in:
- Including attributes that look important on the spec sheet but no one cares about (e.g., RoHS certification on glasses).
- Excluding attributes that drive purchase decisions but aren't prominently advertised (e.g., "fits over my prescription glasses without slipping").

## The mining workflow

### Step 1: Collect reviews

Sources, in rough order of preference:

| Source | Pros | Cons |
|---|---|---|
| Direct platform scraping | Most reviews, structured | Often against ToS |
| Third-party aggregators (e.g., Sellerly, Helium 10, "賣家精靈") | Pre-cleaned, ToS-compliant | Subscription cost |
| Public review sites (Yelp, Trustpilot) | Free, broad | Smaller volume per product |
| Forum / Reddit discussions | Detailed, contextual | Unstructured, hard to volumize |

Aim for at least 20 reviews per product, 100+ total across the sample.

### Step 2: Clean

```python
import re

def clean_review(text):
    text = re.sub(r'http\S+', '', text)              # URLs
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text) # punctuation, keep CJK
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()  # English; skip lower() for CJK
```

Filter out reviews shorter than ~30 characters — they rarely contain attribute mentions.

### Step 3: Extract themes

Three approaches, choose by available tooling:

#### A. LLM-based theme extraction (recommended default)

Send batches of 20–50 reviews to an LLM with a structured prompt:

```
You are analyzing consumer reviews of [product category].
For each review, identify which product attributes the consumer mentions
and what sentiment they express (positive/negative/neutral).

Return a structured list:
- attribute: <name>
- mention_count: <number of reviews discussing this>
- sentiment_distribution: {positive: X, negative: Y, neutral: Z}
- representative_quotes: [up to 3 short quotes]

Reviews:
[paste reviews]
```

Aggregate results across batches. This is fast and works well for any language including Traditional Chinese.

#### B. BERTopic / topic modeling

For larger corpora (500+ reviews), use BERTopic for unsupervised clustering:

```python
from bertopic import BERTopic
topic_model = BERTopic(language='multilingual')
topics, probs = topic_model.fit_transform(reviews)
print(topic_model.get_topic_info())
```

Examine the top 10 topics, manually map each to a product attribute. This requires more interpretation work but reveals attributes you might not have anticipated.

#### C. Keyword frequency (simplest)

Build a candidate attribute list from the product page first. Then count mentions in reviews:

```python
from collections import Counter

attribute_keywords = {
    'fit': ['fit', 'size', 'comfortable', '尺寸', '合適'],
    'lens_clarity': ['clear', 'blurry', '清晰', '模糊'],
    'durability': ['scratch', 'break', 'durable', '耐用', '刮痕'],
    # ...
}

def count_mentions(reviews, keywords):
    counts = Counter()
    for r in reviews:
        for attr, kws in keywords.items():
            if any(kw in r for kw in kws):
                counts[attr] += 1
    return counts
```

Crude but transparent and reproducible.

### Step 4: Optional — apply an interpretive framework

The case study used **Maslow's Hierarchy of Needs** to categorize themes (basic safety, social, esteem, self-actualization). This is useful when:

- The user wants a narrative structure for the report.
- Reviews show varied need levels (some about price/safety, others about styling/identity).

Skip the framework if reviews are highly task-focused (e.g., B2B industrial supplies). For consumer products with emotional dimensions, frameworks like Maslow, JTBD (Jobs-To-Be-Done), or Kano model add interpretive depth.

### Step 5: Output

Produce a frequency-ranked attribute table:

| Theme | Mention count | % of reviews | Sentiment skew |
|---|---|---|---|
| Frame size compatibility | 87 | 43% | Mixed (positive when fits, very negative when doesn't) |
| Anti-fog | 64 | 32% | Mostly positive |
| Anti-scratch | 51 | 26% | Positive |
| Tinting / clarity | 22 | 11% | Mixed |

This table is the input to the triangulation step in Phase II — cross-check against the supply-side universality table.

## Common pitfalls

### Counting product feature names as themes

If "anti-scratch" is a feature listed on the product page, every review that copies that phrase will count. Filter out exact matches of marketing copy if possible — focus on user-generated phrasing.

### Confounding sentiment with importance

A theme can be heavily mentioned because everyone hates it OR loves it. Always report sentiment alongside frequency. The former is a problem signal; the latter is a delight signal — both indicate the attribute matters, but the implications differ.

### Translating across languages

For Chinese-language reviews of products, do **not** translate before mining. Mine in original language using a multilingual model. Translation distorts attribute terminology.

### Over-fitting to vocal minority

A small subset of reviewers are highly verbose and can dominate keyword counts. Cap each reviewer's contribution at 1–2 mentions per theme.
