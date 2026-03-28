#!/usr/bin/env python3
"""Linear regression template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run linear regression")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--target", required=True, help="Continuous target variable")
    parser.add_argument("--features", required=True, help="Comma-separated feature columns")
    parser.add_argument("--output", help="Optional JSON output path")
    return parser.parse_args()


def ensure_dependencies() -> None:
    try:
        import pandas  # noqa: F401
        import statsmodels  # noqa: F401
    except ImportError as exc:
        print(
            "Missing dependency. Install required packages: pandas numpy scipy statsmodels scikit-learn",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def run_regression(input_path: str, target: str, features: list[str]) -> dict:
    import pandas as pd
    import statsmodels.api as sm

    cols = [target] + features
    df = pd.read_csv(input_path)[cols].dropna()

    X = sm.add_constant(df[features])
    y = df[target]

    model = sm.OLS(y, X).fit()

    coef_table = []
    for term, coef in model.params.items():
        coef_table.append(
            {
                "term": term,
                "coefficient": float(coef),
                "p_value": float(model.pvalues[term]),
            }
        )

    significant_terms = [row for row in coef_table if row["term"] != "const" and row["p_value"] < 0.05]

    return {
        "sample_size": int(len(df)),
        "target": target,
        "features": features,
        "r_squared": float(model.rsquared),
        "adj_r_squared": float(model.rsquared_adj),
        "coefficients": coef_table,
        "significant_terms": significant_terms,
    }


def build_business_interpretation(analysis_result: dict) -> dict:
    terms = analysis_result["significant_terms"]
    if terms:
        strongest = sorted(terms, key=lambda x: abs(x["coefficient"]), reverse=True)[0]
        insight = (
            f"顯著影響因子中，{strongest['term']} 的影響最大，係數為 {strongest['coefficient']:.4f}。"
        )
    else:
        insight = "目前模型未得到顯著因子，建議補充樣本或調整特徵定義。"

    return {
        "insight": insight,
        "proposal_sentence": "回歸模型提供了可量化的投入槓桿，用於支撐預算配置與 KPI 預估。",
        "next_step": "對顯著因子制定可執行動作，並設置對應監測指標。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    features = [item.strip() for item in args.features.split(",") if item.strip()]
    analysis_result = run_regression(args.input, args.target, features)
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
