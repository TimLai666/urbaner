# PCA and K-means Implementation Reference

---

## Section A — Principal Component Analysis (PCA)

### Purpose
Reduce N attributes (typically 20–40) to a smaller set of uncorrelated latent
dimensions. The PC scores matrix that results is the direct input to K-means.

### Dependencies
```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
```

### A1 — Build input matrix

```python
import json
import numpy as np

with open('/home/claude/semantic_salience.json', encoding='utf-8') as f:
    rows = json.load(f)

attr_ids = [f'{i:02d}' for i in range(1, N_ATTRS + 1)]   # e.g. ['01','02',...]
X = np.array([[r[f's{a}'] for a in attr_ids] for r in rows], dtype=float)
# shape: (n_reviews, n_attrs)
```

### A2 — Standardise

Always standardise before PCA. Salience columns have different distributions:
many zeros plus occasional high values.

```python
scaler = StandardScaler()
X_std = scaler.fit_transform(X)
```

### A3 — Choose number of components: Kaiser criterion

Run PCA on all components first to examine eigenvalues.

```python
pca_full = PCA(n_components=X.shape[1], random_state=42)
pca_full.fit(X_std)

eigenvalues = pca_full.explained_variance_
evr          = pca_full.explained_variance_ratio_
cum_evr      = np.cumsum(evr)

# Print scree data
for i, (ev, v, c) in enumerate(zip(eigenvalues, evr, cum_evr)):
    print(f"PC{i+1:02d}: eigenvalue={ev:.4f}  var={v*100:.2f}%  cumulative={c*100:.2f}%")

# Kaiser criterion: keep components with eigenvalue > 1
n_components = int((eigenvalues > 1).sum())
print(f"Kaiser: {n_components} components, cumulative variance = {cum_evr[n_components-1]*100:.2f}%")
```

Typical results for sparse salience matrices (≥ 85% zeros): 8–14 components,
cumulative variance 45–60%. This is expected and acceptable.

### A4 — Fit final PCA and compute factor loadings

```python
pca = PCA(n_components=n_components, random_state=42)
PC_scores = pca.fit_transform(X_std)   # shape: (n_reviews, n_components)

# Factor loadings = correlation of each attribute with each PC
# = eigenvectors scaled by sqrt(eigenvalues)
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
# shape: (n_attrs, n_components)
# loadings[i][j] = how strongly attribute i contributes to PC j
```

### A5 — Name each PC

For each PC, collect attributes with |loading| ≥ 0.30. Name the PC based on
the semantic cluster of its dominant positive (and negative) attributes.

```python
THRESHOLD = 0.30

for j in range(n_components):
    col = loadings[:, j]
    pos = [(attr_labels[i], col[i]) for i in range(len(attr_labels)) if col[i] >= THRESHOLD]
    neg = [(attr_labels[i], col[i]) for i in range(len(attr_labels)) if col[i] <= -THRESHOLD]
    pos.sort(key=lambda x: -x[1])
    neg.sort(key=lambda x: x[1])
    print(f"PC{j+1:02d}: pos={pos}, neg={neg}")
```

### A6 — Save outputs

```python
import json as _json

pca_result = {
    "n_components": n_components,
    "attr_ids": attr_ids,
    "attr_labels": attr_labels,
    "loadings": loadings.tolist(),          # (n_attrs, n_components)
    "eigenvalues": pca.explained_variance_.tolist(),
    "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
    "cumulative_variance": np.cumsum(pca.explained_variance_ratio_).tolist(),
    "n_reviews": len(rows),
}
with open('/home/claude/pca_results.json', 'w') as f:
    _json.dump(pca_result, f)

# Also save per-review PC scores for clustering
pc_data = []
for i, row in enumerate(rows):
    d = {"review_id": row["review_id"], "product": row["product"]}
    for j in range(n_components):
        d[f"PC{j+1:02d}"] = float(PC_scores[i, j])
    pc_data.append(d)

with open('/home/claude/pc_scores.json', 'w') as f:
    _json.dump(pc_data, f)
```

---

## Section B — K-means Customer Segmentation

### Purpose
Group reviews (= customer voices) into interpretable segments based on their
PC scores. Uses iterative pruning to eliminate noise clusters that are too small.

### Dependencies
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
```

### B1 — Load PC scores

```python
import json
import numpy as np

with open('/home/claude/pc_scores.json') as f:
    pc_data = json.load(f)

n_pcs = sum(1 for k in pc_data[0] if k.startswith('PC'))
PC = np.array([[d[f'PC{j+1:02d}'] for j in range(n_pcs)] for d in pc_data])
N_TOTAL = len(PC)
MIN_N   = int(np.ceil(N_TOTAL * 0.05))   # 5% threshold
```

### B2 — Scan K=2–9 (Elbow + Silhouette)

```python
inertias, sil_scores = [], []
for k in range(2, 10):
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = km.fit_predict(PC)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(PC, labels))
    print(f"K={k}: inertia={km.inertia_:.1f}  silhouette={sil_scores[-1]:.4f}")
```

Choose starting K: prefer interpretability over peak silhouette if the top-K
produces trivially few segments. For most review corpora K=5 is a good starting
point even when K=2 has the highest silhouette.

### B3 — Iterative pruning

Remove clusters smaller than 5% of the corpus. Decrement K and refit on the
remaining reviews. Repeat until all clusters are ≥ 5%.

```python
def iterative_prune(PC, k_start, min_n, seed=42):
    """
    Returns: (converged KMeans object, active_mask, history)
    active_mask: bool array, True for reviews used in final fit
    """
    history = []
    active_mask = np.ones(len(PC), dtype=bool)
    k = k_start

    while True:
        km = KMeans(n_clusters=k, random_state=seed, n_init=20)
        labels = km.fit_predict(PC[active_mask])

        unique, counts = np.unique(labels, return_counts=True)
        sizes = dict(zip(unique.tolist(), counts.tolist()))
        small = [c for c, n in sizes.items() if n < min_n]
        sil = silhouette_score(PC[active_mask], labels) if k > 1 else 0.0

        history.append({
            "k": k, "n_active": int(active_mask.sum()),
            "cluster_sizes": sizes, "silhouette": round(sil, 4),
            "pruned_clusters": small, "pruned_n": sum(sizes[c] for c in small),
        })

        if not small:
            return km, active_mask, history  # converged

        # Mark small-cluster reviews as inactive
        labels_full = np.full(len(PC), -1)
        labels_full[active_mask] = labels
        active_mask &= ~np.isin(labels_full, small)
        k -= len(small)

        if k < 2:
            return km, active_mask, history  # forced stop

# Run
km_final, active_mask, history = iterative_prune(PC, k_start=5, min_n=MIN_N)

for h in history:
    print(f"K={h['k']}: active={h['n_active']}, sil={h['silhouette']:.4f}, "
          f"sizes={h['cluster_sizes']}, pruned={h['pruned_clusters']}")
```

### B4 — Assign ALL reviews (critical)

After convergence, use `predict()` on the **full** PC matrix — not just the
active subset. This assigns every review, including those removed during pruning,
to the nearest final centroid. No review is discarded.

```python
# Assign all N_TOTAL reviews to nearest final centroid
labels_all = km_final.predict(PC)   # shape: (N_TOTAL,)

# Verify: previously pruned reviews are now assigned
n_previously_pruned = (~active_mask).sum()
print(f"Previously pruned: {n_previously_pruned} — now all re-assigned via predict()")

# Final cluster sizes (all reviews included)
unique, counts = np.unique(labels_all, return_counts=True)
sil_final = silhouette_score(PC, labels_all)
for c, n in zip(unique, counts):
    print(f"Cluster {c}: n={n} ({n/N_TOTAL*100:.1f}%)")
print(f"Final silhouette: {sil_final:.4f}")
```

**Why silhouette drops slightly after re-assignment:** the pruned reviews were
borderline cases (hence they formed a small, diffuse cluster). Assigning them
to the nearest centroid is correct but slightly reduces the average within-cluster
cohesion. This is expected and acceptable.

### B5 — Profile each cluster

Compute PC centroids and attribute means per cluster.

```python
with open('/home/claude/semantic_salience.json') as f:
    sal_rows = json.load(f)
X_raw = np.array([[r[f's{a}'] for a in attr_ids] for r in sal_rows], dtype=float)

pc_centroids   = []
attr_centroids = []

for c in sorted(set(labels_all)):
    mask = labels_all == c
    pc_centroids.append(PC[mask].mean(axis=0).tolist())
    attr_centroids.append(X_raw[mask].mean(axis=0).tolist())

    # Top 5 attributes
    top5 = sorted(enumerate(attr_centroids[-1]), key=lambda x: -x[1])[:5]
    print(f"Cluster {c} (n={mask.sum()}) top attrs: "
          f"{[(attr_labels[i], round(v,2)) for i,v in top5]}")
```

### B6 — Name clusters

For each cluster, look at:
1. PC centroids: which PCs are strongly positive (> +1.0) or negative (< −1.0)
2. Top attribute means: what are reviewers actually talking about
3. Product composition: which products dominate

Combine into a short label (e.g. "體驗達人", "沉默大眾", "耐刮耐用派").

### B7 — Save enriched results

```python
result = {
    "n_total": int(N_TOTAL),
    "min_pct": 0.05,
    "min_n": int(MIN_N),
    "method": "iterative pruning → centroids → predict() all reviews",
    "history": history,
    "final_k": len(set(labels_all)),
    "final_silhouette": round(float(sil_final), 4),
    "cluster_sizes": {int(c): int(n) for c, n in zip(unique, counts)},
    "final_labels": labels_all.tolist(),
    "pc_centroids": pc_centroids,
    "attr_centroids": attr_centroids,
    "attr_labels": attr_labels,
    "review_ids": [r['review_id'] for r in sal_rows],
    "products": [r['product'] for r in sal_rows],
}
with open('/home/claude/kmeans_enriched.json', 'w') as f:
    json.dump(result, f)
```

---

## Common pitfalls

| Pitfall | Correct approach |
|---------|-----------------|
| Discarding pruned reviews | Always use `km.predict(ALL)` after convergence |
| Using raw salience as K-means input | Always use PC scores, not raw salience |
| Forgetting to standardise before PCA | `StandardScaler` is mandatory |
| Choosing K solely by silhouette | K=2 often wins silhouette but is too coarse; balance with interpretability |
| Treating silhouette drop post-reassignment as an error | It is expected and correct |
| Naming PCs without reading loadings | Always inspect all attributes with \|loading\| ≥ 0.30 |

---

## Typical output summary to include in Word / report

For each cluster state:
- Cluster name and size (n and %)
- Dominant PC centroids (> ±1.0)
- Top 3–5 attribute means
- Product distribution highlights
- One-sentence interpretation of who these reviewers are
