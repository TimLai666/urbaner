#!/usr/bin/env python3
"""KMeans segmentation template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run KMeans segmentation")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--features", required=True, help="Comma-separated numeric feature columns")
    parser.add_argument("--clusters", type=int, default=3, help="Number of clusters")
    parser.add_argument("--output", help="Optional JSON output path")
    return parser.parse_args()


def ensure_dependencies() -> None:
    try:
        import pandas  # noqa: F401
        import sklearn  # noqa: F401
    except ImportError as exc:
        print(
            "Missing dependency. Install required packages: pandas numpy scipy statsmodels scikit-learn",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def run_kmeans(input_path: str, features: list[str], clusters: int) -> dict:
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    df = pd.read_csv(input_path)
    X = df[features].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(n_clusters=clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X_scaled)

    segmented = X.copy()
    segmented["cluster"] = labels

    summary = segmented.groupby("cluster")[features].mean().reset_index()
    counts = segmented["cluster"].value_counts().sort_index()

    return {
        "sample_size": int(len(segmented)),
        "clusters": int(clusters),
        "cluster_sizes": {str(int(k)): int(v) for k, v in counts.items()},
        "cluster_profile": summary.to_dict("records"),
        "inertia": float(model.inertia_),
    }


def build_business_interpretation(analysis_result: dict) -> dict:
    sizes = analysis_result["cluster_sizes"]
    largest_cluster = max(sizes, key=sizes.get)
    return {
        "insight": (
            f"共識別 {analysis_result['clusters']} 個客群，其中第 {largest_cluster} 群規模最大，"
            "建議優先設計對應的獲客與留存訊息。"
        ),
        "proposal_sentence": "分群策略將依客群價值與需求差異配置產品組合、價格與推廣預算。",
        "next_step": "將每一群對應到 STP 的 target 選擇，並設置不同 KPI。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    features = [item.strip() for item in args.features.split(",") if item.strip()]
    analysis_result = run_kmeans(args.input, features, args.clusters)
    output = {
        "analysis_result": analysis_result,
        "business_interpretation": build_business_interpretation(analysis_result),
    }

    payload = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
