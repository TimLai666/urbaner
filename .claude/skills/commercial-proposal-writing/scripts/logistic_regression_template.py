#!/usr/bin/env python3
"""Logistic regression template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run logistic regression for binary outcomes")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--target", required=True, help="Binary target column")
    parser.add_argument("--features", required=True, help="Comma-separated feature columns")
    parser.add_argument("--output", help="Optional JSON output path")
    return parser.parse_args()


def ensure_dependencies() -> None:
    try:
        import pandas  # noqa: F401
        import sklearn  # noqa: F401
        import numpy  # noqa: F401
    except ImportError as exc:
        print(
            "Missing dependency. Install required packages: pandas numpy scipy statsmodels scikit-learn",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def run_logistic(input_path: str, target: str, features: list[str]) -> dict:
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    cols = [target] + features
    df = pd.read_csv(input_path)[cols].dropna()

    X = df[features]
    y = df[target]

    if y.nunique() != 2:
        raise ValueError("Target must contain exactly two classes for logistic regression.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    odds_ratios = np.exp(model.coef_[0])

    coef_table = [
        {
            "feature": features[i],
            "coefficient": float(model.coef_[0][i]),
            "odds_ratio": float(odds_ratios[i]),
        }
        for i in range(len(features))
    ]

    return {
        "sample_size": int(len(df)),
        "target": target,
        "features": features,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "coefficients": coef_table,
    }


def build_business_interpretation(analysis_result: dict) -> dict:
    strongest = sorted(
        analysis_result["coefficients"], key=lambda item: abs(item["coefficient"]), reverse=True
    )[0]
    return {
        "insight": (
            f"影響二元結果最強的因子是 {strongest['feature']}，"
            f"勝算比為 {strongest['odds_ratio']:.3f}。"
        ),
        "proposal_sentence": "Logistic 結果可用於定義高機率轉換客群與高風險流失客群的差異化行動。",
        "next_step": "將高影響因子轉成可執行規則，並建立週期性監控。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    features = [item.strip() for item in args.features.split(",") if item.strip()]
    analysis_result = run_logistic(args.input, args.target, features)
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
