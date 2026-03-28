# Intake and Mode Selection

## 1) Required Inputs

| field | type | required | note |
| --- | --- | --- | --- |
| brand_theme | string | yes | 品牌名稱與主題描述 |
| value_props | string[3] | yes | 三個核心價值主張 |
| primary_cta | string | yes | 主 CTA 文案 |
| style_variant | string | yes | A-L 或 custom |
| output_mode | string | yes | single-file-html / react-project |
| variant_mode | string | no | single (default) / batch |
| autonomy_mode | string | no | multi-iteration (default) / single-pass |
| animation_level | string | no | high (default) / medium / low |
| motion_preference | string | no | respect-reduced-motion |
| target_audience | string | no | 受眾描述 |
| industry | string | no | 產業背景 |
| react_stack | string | no | React 模式使用 |

## 2) Data Sufficiency Gate

缺少以下欄位任一時，不可生成頁面：

- `brand_theme`
- `value_props`
- `primary_cta`
- `style_variant`
- `output_mode`

且 `value_props` 長度必須為 3。

## 3) MissingDataOutput Format

```json
{
  "missing_fields": ["..."],
  "why_needed": {
    "field": "reason"
  },
  "questions_to_user": ["..."],
  "next_step_rule": "補齊欄位後再生成"
}
```

## 4) Mode Selection

- 僅需快速交付：`single-file-html`
- 需元件化與延展：`react-project`

## 5) React Stack Choice Rule

當 `output_mode=react-project` 且未提供 `react_stack` 時，先返回三種選項與優缺點：

1. `vite-react-tailwind-framer`
- 優點：啟動快、生成效率高、適合高頻迭代
- 缺點：內建 SEO 能力較弱

2. `nextjs-app-router`
- 優點：SEO 與路由能力完整、產品化好延伸
- 缺點：結構較重、開發成本較高

3. `react-css-modules`
- 優點：依賴少、可控性高
- 缺點：特效整合成本較高

## 6) Variant Mode

- `single`：預設單版
- `batch`：一次產多版，必附差異摘要
