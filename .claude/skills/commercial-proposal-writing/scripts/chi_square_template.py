#!/usr/bin/env python3
"""Chi-square test template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run chi-square test on two categorical columns")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--x-col", required=True, help="First categorical column")
    parser.add_argument("--y-col", required=True, help="Second categorical column")
    parser.add_argument("--output", help="Optional JSON output path")
    return parser.parse_args()


def ensure_dependencies() -> None:
    try:
        import pandas  # noqa: F401
        import scipy  # noqa: F401
    except ImportError as exc:
        print(
            "Missing dependency. Install required packages: pandas numpy scipy statsmodels scikit-learn",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def run_chi_square(input_path: str, x_col: str, y_col: str) -> dict:
    import pandas as pd
    from scipy.stats import chi2_contingency

    df = pd.read_csv(input_path)
    sub = df[[x_col, y_col]].dropna()

    contingency = pd.crosstab(sub[x_col], sub[y_col])
    chi2, p_value, dof, expected = chi2_contingency(contingency)

    return {
        "sample_size": int(len(sub)),
        "x_col": x_col,
        "y_col": y_col,
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        "is_significant_0_05": bool(p_value < 0.05),
        "contingency_table": contingency.reset_index().to_dict("records"),
        "expected_frequency_shape": [int(expected.shape[0]), int(expected.shape[1])],
    }


def build_business_interpretation(analysis_result: dict) -> dict:
    significant = analysis_result["is_significant_0_05"]
    message = "存在顯著關聯，需分眾策略。" if significant else "未達顯著，先採共通策略再補資料驗證。"
    return {
        "insight": (
            f"{analysis_result['x_col']} 與 {analysis_result['y_col']} 的卡方檢定 p 值為 "
            f"{analysis_result['p_value']:.4f}，{message}"
        ),
        "proposal_sentence": "此檢定結果可作為是否拆分客群訊息與資源配置的依據。",
        "next_step": "若顯著，針對主要關聯格位設計專屬行銷動作與 KPI。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    analysis_result = run_chi_square(args.input, args.x_col, args.y_col)
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
