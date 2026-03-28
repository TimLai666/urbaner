#!/usr/bin/env python3
"""Conjoint-style utility modeling template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run simplified conjoint utility estimation")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--target", required=True, help="Preference score or choice proxy column")
    parser.add_argument("--attributes", required=True, help="Comma-separated categorical attribute columns")
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


def run_conjoint(input_path: str, target: str, attributes: list[str]) -> dict:
    import pandas as pd
    import statsmodels.api as sm

    cols = [target] + attributes
    df = pd.read_csv(input_path)[cols].dropna()

    X = pd.get_dummies(df[attributes], drop_first=True)
    X = sm.add_constant(X)
    y = df[target]

    model = sm.OLS(y, X).fit()

    utility_rows = []
    for term, coef in model.params.items():
        if term == "const":
            continue
        utility_rows.append(
            {
                "term": term,
                "utility": float(coef),
                "p_value": float(model.pvalues[term]),
            }
        )

    top_utility = sorted(utility_rows, key=lambda x: x["utility"], reverse=True)[:5]

    return {
        "sample_size": int(len(df)),
        "target": target,
        "attributes": attributes,
        "r_squared": float(model.rsquared),
        "part_worths": utility_rows,
        "top_positive_levels": top_utility,
    }


def build_business_interpretation(analysis_result: dict) -> dict:
    top = analysis_result["top_positive_levels"]
    if top:
        top_terms = ", ".join([item["term"] for item in top[:3]])
    else:
        top_terms = "無顯著偏好水準"

    return {
        "insight": f"偏好效用較高的屬性水準包括：{top_terms}。",
        "proposal_sentence": "Conjoint 可直接支撐產品組合、價格方案與版本優先序決策。",
        "next_step": "把高效用組合轉換為 MVP 與定價實驗設計。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    attributes = [item.strip() for item in args.attributes.split(",") if item.strip()]
    analysis_result = run_conjoint(args.input, args.target, attributes)
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
