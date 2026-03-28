#!/usr/bin/env python3
"""One-way/Two-way ANOVA template for proposal analytics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ANOVA with one or two factors")
    parser.add_argument("--input", required=True, help="Path to CSV file")
    parser.add_argument("--dependent", required=True, help="Continuous dependent variable")
    parser.add_argument("--group", required=True, help="Primary grouping factor")
    parser.add_argument("--second-group", help="Optional second grouping factor")
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


def run_anova(input_path: str, dependent: str, group: str, second_group: str | None) -> dict:
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

    cols = [dependent, group] + ([second_group] if second_group else [])
    df = pd.read_csv(input_path)[cols].dropna()

    if second_group:
        formula = f"{dependent} ~ C({group}) + C({second_group}) + C({group}):C({second_group})"
        model_type = "two_way"
    else:
        formula = f"{dependent} ~ C({group})"
        model_type = "one_way"

    model = ols(formula, data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    anova_records = anova_table.reset_index().rename(columns={"index": "term"}).to_dict("records")

    significant_terms = [
        row["term"]
        for row in anova_records
        if isinstance(row.get("PR(>F)"), float) and row["PR(>F)"] < 0.05
    ]

    return {
        "sample_size": int(len(df)),
        "model_type": model_type,
        "formula": formula,
        "anova_table": anova_records,
        "significant_terms": significant_terms,
    }


def build_business_interpretation(analysis_result: dict) -> dict:
    terms = analysis_result["significant_terms"]
    if terms:
        insight = f"顯著因子包含：{', '.join(terms)}。"
    else:
        insight = "未觀察到顯著群組差異，建議先檢查樣本與分組定義。"

    return {
        "insight": insight,
        "proposal_sentence": "ANOVA 結果可用於決定資源是否應按客群或通路差異化分配。",
        "next_step": "對顯著組別做事後比較，擬定優先投入群組。",
    }


def main() -> None:
    args = parse_args()
    ensure_dependencies()

    analysis_result = run_anova(args.input, args.dependent, args.group, args.second_group)
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
