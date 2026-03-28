# Excel Output Format

## Workbook structure

```
salience_matrix.xlsx
├── Sheet 1: 評論×屬性 顯著度矩陣   (full review-level matrix)
└── Sheet 2: 產品×屬性 平均顯著度    (product-level summary)
```

---

## Sheet 1 — Full matrix

### Column layout

| Col | Name | Content |
|-----|------|---------|
| A | `review_id` | `{PRODUCT_ID}_{zero-padded-index}`, e.g. `B016KZ2APQ_0001` |
| B | `product` | Product identifier string |
| C | `salience_sum` | Excel formula: `=SUM(E{row}:{last_attr_col}{row})` |
| D | `review_text` | First 120–300 chars of the review body |
| E … | `s01`, `s02` … `sN` | Integer salience scores 0–7 |

### Header rows

**Row 1 — Maslow tier group headers** (merged across attribute columns)  
Each tier's columns are merged and labelled (e.g. `生理需求`, `安全需求`).  
Fixed metadata columns (A–D) each span rows 1–2 (merged).

**Row 2 — Attribute headers**  
Each cell contains `{id}\n{label}` (e.g. `01\n光學清晰度`), wrap_text=True, height ≈ 42pt.

### Tier colour map

Apply these fills to both the tier header row and each attribute column header:

| Tier | Header fill | Separator row fill |
|------|------------|-------------------|
| 生理 | `E2EFDA` | `C6E0B4` |
| 安全 | `FCE4D6` | `F4B183` |
| 社交 | `DDEBF7` | `9DC3E6` |
| 自尊 | `FFF2CC` | `FFD966` |
| 自我實現 | `EAE0F5` | `C9B1E0` |

### Score cell conditional formatting

Apply a three-colour scale to the range `E3:{last_col}{last_row}`:

```python
from openpyxl.formatting.rule import ColorScaleRule

ws.conditional_formatting.add(data_range, ColorScaleRule(
    start_type="num", start_value=0, start_color="FFFFFF",   # white  = 0
    mid_type="num",   mid_value=3,   mid_color="FFD966",     # yellow = mid
    end_type="num",   end_value=7,   end_color="E85D24",     # orange = 7
))
```

### Product colour map (column B)

Assign a distinct pastel fill per product so rows are visually grouped:

```python
PROD_COLORS = {
    "product_1": "E2EFDA",  # light green
    "product_2": "DDEBF7",  # light blue
    "product_3": "FFF2CC",  # light yellow
    "product_4": "FCE4D6",  # light orange
    # ... continue cycling through light pastels
}
```

### Freeze panes and dimensions

```python
ws.freeze_panes = "E3"          # freeze metadata cols + header rows
ws.column_dimensions["A"].width = 18
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 9
ws.column_dimensions["D"].width = 45
# Score columns:
for score_col in score_columns:
    ws.column_dimensions[score_col].width = 7
ws.row_dimensions[2].height = 42  # attr header row, needs wrap
```

---

## Sheet 2 — Product summary

### Layout

- Row 1: Maslow tier group headers (same merge + colour logic as Sheet 1)
- Row 2: Attribute labels (same as Sheet 1)
- Rows 3+: One row per product, labelled `{PRODUCT_ID}\n(n={review_count})`
- Column A frozen; header rows frozen

### Cell values

Each cell is the **mean salience** across all reviews for that product-attribute pair, rounded to 2 decimal places.

```python
mean_val = round(sum(scores_list) / len(scores_list), 2)
```

### Conditional formatting

Apply a three-colour scale on the data range (adjust mid-value for mean scale):

```python
ColorScaleRule(
    start_type="num", start_value=0, start_color="FFFFFF",
    mid_type="num",   mid_value=2,   mid_color="FFD966",
    end_type="num",   end_value=5,   end_color="E85D24",
)
```

---

## openpyxl quick reference

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

wb = Workbook()
ws = wb.active
ws.title = "評論×屬性 顯著度矩陣"

# Cell styling
c = ws.cell(row=r, column=col, value=value)
c.fill = PatternFill("solid", fgColor="E2EFDA")
c.font = Font(name="Arial", bold=True, size=10)
c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

thin = Side(style="thin", color="CCCCCC")
c.border = Border(left=thin, right=thin, top=thin, bottom=thin)

# Merge cells
ws.merge_cells(start_row=1, start_column=5, end_row=1, end_column=10)

# Column width
ws.column_dimensions[get_column_letter(col)].width = 7

# Row height
ws.row_dimensions[2].height = 42

# Freeze panes
ws.freeze_panes = "E3"

# Save
wb.save("/home/claude/salience_matrix.xlsx")
```

### Recalculate formulas after saving

```bash
python scripts/recalc.py /home/claude/salience_matrix.xlsx 60
```

Check that the returned JSON shows `"status": "success"` and `"total_errors": 0`.
