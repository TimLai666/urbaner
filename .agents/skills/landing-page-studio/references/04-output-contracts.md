# Output Contracts

## 1) LandingPageInput

```json
{
  "brand_theme": "沐石・湯宿：頂級溫泉飯店",
  "value_props": ["尊榮至上", "極致品味", "絕對私密"],
  "primary_cta": "立即預訂",
  "style_variant": "B",
  "output_mode": "single-file-html",
  "variant_mode": "single",
  "autonomy_mode": "multi-iteration",
  "animation_level": "high",
  "motion_preference": "respect-reduced-motion",
  "target_audience": "高端旅宿客群",
  "industry": "hospitality"
}
```

## 2) MissingDataOutput

```json
{
  "missing_fields": ["value_props"],
  "why_needed": {
    "value_props": "價值主張決定 Hero 與卡片區內容架構"
  },
  "questions_to_user": [
    "請提供 3 個核心價值主張"
  ],
  "next_step_rule": "補齊缺漏欄位後，重新執行生成"
}
```

## 3) GenerationOutput

```json
{
  "artifact_type": "single-html",
  "artifact_payload": "<!doctype html>...",
  "asset_sources": [
    {
      "provider": "unsplash",
      "url": "https://images.unsplash.com/...",
      "attribution": "Photo by ... on Unsplash"
    }
  ],
  "animation_manifest": [
    {
      "id": "hero_svg_drift",
      "category": "hero",
      "library": "animejs",
      "target": "#hero-svg",
      "trigger": "on-load",
      "fallback": "static-gradient"
    }
  ],
  "autonomy_report": {
    "mode": "multi-iteration",
    "iterations": 3,
    "candidates": [
      {
        "id": "v1",
        "scores": {
          "conversion_clarity": 8.6,
          "visual_coherence": 8.9,
          "readability": 8.4,
          "performance_risk": 7.7
        }
      }
    ],
    "selected": "v2",
    "selection_reason": "更高的 CTA 對比與較低動畫風險"
  },
  "qa_report": {
    "desktop": {"performance": 88, "accessibility": 93},
    "mobile": {"performance": 78, "accessibility": 91},
    "responsive_checks": "pass"
  }
}
```

## 4) Batch Variant Extension

當 `variant_mode=batch` 時，`GenerationOutput` 需額外包含：

- `batch_results`: array of artifacts
- `variant_diff_summary`: 每版差異（palette、typography、motion）
