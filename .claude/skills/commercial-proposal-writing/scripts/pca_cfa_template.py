#!/usr/bin/env python3
"""PCA/CFA template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PCA (and optional CFA note) on survey/features data")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--features", required=True, help="Comma-separated numeric feature columns")
    parser.add_argument("--components", type=int, default=2, help="Number of PCA components")
    parser.add_argument("--run-cfa", action="store_true", help="Add CFA guidance note")
    parser.add_argument("--output", help="Optional JSON output path")
    return parser.parse_args()


def ensure_dependencies() -> None:
    try:
        import pandas  # noqa: F401
        import numpy  # noqa: F401
        import sklearn  # noqa: F401
    except ImportError as exc:
        print(
            "Missing dependency. Install required packages: pandas numpy scipy statsmodels scikit-learn",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def run_pca(input_path: str, features: list[str], n_components: int, run_cfa: bool) -> dict:
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    df = pd.read_csv(input_path)
    X = df[features].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=n_components)
    pcs = pca.fit_transform(X_scaled)

    loadings = pd.DataFrame(
        pca.components_.T,
        index=features,
        columns=[f"PC{i + 1}" for i in range(n_components)],
    )

    result = {
        "sample_size": int(X.shape[0]),
        "features": features,
        "explained_variance_ratio": [float(v) for v in pca.explained_variance_ratio_],
        "cumulative_explained_variance": float(np.sum(pca.explained_variance_ratio_)),
        "component_loadings": loadings.reset_index().rename(columns={"index": "feature"}).to_dict("records"),
        "score_preview": [
            {f"PC{i + 1}": float(row[i]) for i in range(n_components)}
            for row in pcs[: min(5, len(pcs))]
        ],
    }
    if run_cfa:
        result["cfa_note"] = (
            "CFA requires a predefined latent structure and specialized packages (e.g., semopy). "
            "Use PCA output to propose latent constructs before CFA confirmation."
        )
    return result


def build_business_interpretation(analysis_result: dict) -> dict:
    ratio = analysis_result["explained_variance_ratio"]
    top_ratio = ratio[0] if ratio else 0.0
    return {
        "insight": (
            f"第一主成分解釋度為 {top_ratio:.2%}，可用於描述主要需求構面，"
            "適合後續市場區隔與訊息分眾。"
        ),
        "proposal_sentence": (
            "我們將高維度需求資料萃取為少數核心構面，並以此作為目標客群分群與產品優先級設定的基礎。"
        ),
        "next_step": "以主成分分數搭配 KMeans 分群，建立可操作的客群策略。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    features = [item.strip() for item in args.features.split(",") if item.strip()]
    analysis_result = run_pca(args.input, features, args.components, args.run_cfa)
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
