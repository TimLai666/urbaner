#!/usr/bin/env python3
"""Validate and normalize LandingPageInput for landing-page-studio skill."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

REQUIRED_FIELDS = [
    "brand_theme",
    "value_props",
    "primary_cta",
    "style_variant",
    "output_mode",
]

ALLOWED_STYLES = set(list("ABCDEFGHIJKL") + ["custom"])
ALLOWED_OUTPUT_MODES = {"single-file-html", "react-project"}
ALLOWED_VARIANT_MODES = {"single", "batch"}
ALLOWED_AUTONOMY_MODES = {"single-pass", "multi-iteration"}
ALLOWED_ANIMATION_LEVELS = {"low", "medium", "high"}

DEFAULTS: Dict[str, Any] = {
    "variant_mode": "single",
    "autonomy_mode": "multi-iteration",
    "animation_level": "high",
    "motion_preference": "respect-reduced-motion",
}

REACT_STACK_OPTIONS = [
    {
        "id": "vite-react-tailwind-framer",
        "pros": ["啟動快", "生成效率高", "動畫整合快"],
        "cons": ["SEO 能力需額外配置"],
    },
    {
        "id": "nextjs-app-router",
        "pros": ["SEO 友好", "路由與部署成熟"],
        "cons": ["結構較重", "學習與維護成本較高"],
    },
    {
        "id": "react-css-modules",
        "pros": ["依賴少", "樣式可控"],
        "cons": ["動效整合與速度通常較慢"],
    },
]


def _load_input(args: argparse.Namespace) -> Dict[str, Any]:
    if args.input_json:
        return json.loads(args.input_json)
    if args.file:
        with open(args.file, "r", encoding="utf-8-sig") as f:
            return json.load(f)

    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("No input provided. Use --input-json, --file, or stdin JSON.")
    return json.loads(raw)


def _missing_output(missing: List[str], extra_reasons: Dict[str, str]) -> Dict[str, Any]:
    why_needed = {
        "brand_theme": "決定視覺語言與文案語氣",
        "value_props": "決定核心轉換訊息與三卡區塊內容",
        "primary_cta": "決定行動路徑與按鈕文案",
        "style_variant": "決定色彩、字體與動畫策略",
        "output_mode": "決定輸出格式與專案結構",
    }
    why_needed.update(extra_reasons)

    return {
        "type": "MissingDataOutput",
        "missing_fields": missing,
        "why_needed": {k: why_needed.get(k, "此欄位為必要輸入") for k in missing},
        "questions_to_user": [f"請提供 `{field}`" for field in missing],
        "next_step_rule": "補齊缺失欄位後重新執行生成。",
    }


def validate_intake(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = {**DEFAULTS, **payload}

    missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] in (None, "", [])]
    reasons: Dict[str, str] = {}

    if "value_props" in data and not (isinstance(data["value_props"], list) and len(data["value_props"]) == 3):
        if "value_props" not in missing:
            missing.append("value_props")
        reasons["value_props"] = "`value_props` 必須是長度 3 的字串陣列。"

    if missing:
        return _missing_output(missing, reasons)

    style = str(data["style_variant"])
    if style not in ALLOWED_STYLES:
        return _missing_output(
            ["style_variant"],
            {"style_variant": "style_variant 必須是 A-L 或 custom。"},
        )

    output_mode = data["output_mode"]
    if output_mode not in ALLOWED_OUTPUT_MODES:
        return _missing_output(
            ["output_mode"],
            {"output_mode": "output_mode 必須是 single-file-html 或 react-project。"},
        )

    variant_mode = data.get("variant_mode", DEFAULTS["variant_mode"])
    if variant_mode not in ALLOWED_VARIANT_MODES:
        data["variant_mode"] = DEFAULTS["variant_mode"]

    autonomy_mode = data.get("autonomy_mode", DEFAULTS["autonomy_mode"])
    if autonomy_mode not in ALLOWED_AUTONOMY_MODES:
        data["autonomy_mode"] = DEFAULTS["autonomy_mode"]

    animation_level = data.get("animation_level", DEFAULTS["animation_level"])
    if animation_level not in ALLOWED_ANIMATION_LEVELS:
        data["animation_level"] = DEFAULTS["animation_level"]

    framework_choice_required = output_mode == "react-project" and not data.get("react_stack")

    return {
        "type": "LandingPageInputNormalized",
        "valid": True,
        "framework_choice_required": framework_choice_required,
        "react_stack_options": REACT_STACK_OPTIONS if framework_choice_required else [],
        "normalized_input": data,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate landing-page-studio intake payload")
    parser.add_argument("--input-json", help="Input JSON string")
    parser.add_argument("--file", help="Path to JSON file")
    args = parser.parse_args()

    try:
        payload = _load_input(args)
        result = validate_intake(payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        error = {"type": "error", "message": str(exc)}
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
