#!/usr/bin/env python3
"""MDS positioning template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MDS for product/brand positioning")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--id-col", required=True, help="Product/brand identifier column")
    parser.add_argument("--features", required=True, help="Comma-separated numeric feature columns")
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


def run_mds(input_path: str, id_col: str, features: list[str]) -> dict:
    import pandas as pd
    from sklearn.manifold import MDS
    from sklearn.metrics import pairwise_distances

    cols = [id_col] + features
    df = pd.read_csv(input_path)[cols].dropna()

    profile = df.groupby(id_col)[features].mean()
    distance = pairwise_distances(profile.values, metric="euclidean")
    model = MDS(n_components=2, random_state=42, n_init=4, init="random", metric="precomputed")
    coords = model.fit_transform(distance)

    position_rows = []
    index = list(profile.index)
    for i, name in enumerate(index):
        position_rows.append(
            {
                "id": str(name),
                "x": float(coords[i, 0]),
                "y": float(coords[i, 1]),
            }
        )

    return {
        "entities": len(index),
        "id_col": id_col,
        "features": features,
        "positions": position_rows,
        "stress": float(model.stress_),
    }


def build_business_interpretation(analysis_result: dict) -> dict:
    return {
        "insight": (
            f"MDS 完成 {analysis_result['entities']} 個對象的定位映射，可視覺化競爭接近度與差異化空間。"
        ),
        "proposal_sentence": "定位圖可直接用於說明我們與主要競品在關鍵維度上的相對位置。",
        "next_step": "基於定位空位調整產品訊息，並設計下一輪品牌溝通測試。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    features = [item.strip() for item in args.features.split(",") if item.strip()]
    analysis_result = run_mds(args.input, args.id_col, features)
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
