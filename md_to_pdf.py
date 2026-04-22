"""Convert Markdown to PDF using fpdf2, supporting Traditional/Simplified Chinese."""
import re
import sys
from fpdf import FPDF

# ── fonts ──────────────────────────────────────────────────────────────────
# Use 標楷體 when available on Windows
FONT_REGULAR = r"C:\Windows\Fonts\kaiu.ttf"   # DFKai-SB / 標楷體
FONT_BOLD    = r"C:\Windows\Fonts\kaiu.ttf"
FALLBACK_REGULAR = r"C:\Windows\Fonts\simsun.ttc"
FALLBACK_BOLD    = r"C:\Windows\Fonts\simhei.ttf"

import os
if not os.path.exists(FONT_REGULAR):
    FONT_REGULAR = FALLBACK_REGULAR
    FONT_BOLD    = FALLBACK_BOLD


class MdPDF(FPDF):
    def header(self): pass
    def footer(self):
        self.set_y(-12)
        self.set_font("reg", size=8)
        self.set_text_color(150)
        self.cell(0, 10, f"{self.page_no()}", align="C")
        self.set_text_color(0)


def strip_inline(text):
    """Remove bold/italic markers, backticks, links for plain rendering."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*',     r'\1', text)
    text = re.sub(r'`(.*?)`',       r'\1', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    return text


def has_bold(text):
    return bool(re.search(r'\*\*(.*?)\*\*', text))


def render_inline(pdf, text, base_size, line_height, indent=0):
    """Render a line with possible bold segments."""
    # Split on **bold** markers
    parts = re.split(r'(\*\*.*?\*\*)', text)
    if indent:
        pdf.set_x(pdf.l_margin + indent)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            content = part[2:-2]
            pdf.set_font("bold", size=base_size)
        else:
            content = re.sub(r'\*(.*?)\*', r'\1', part)
            content = re.sub(r'`(.*?)`',   r'\1', content)
            content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
            pdf.set_font("reg", size=base_size)
        if content:
            pdf.write(line_height, content)


def convert(md_path, pdf_path):
    pdf = MdPDF(format="A4")
    pdf.add_font("reg",  fname=FONT_REGULAR)
    pdf.add_font("bold", fname=FONT_BOLD)
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(True, margin=18)
    pdf.add_page()

    LH = 6.5  # line height mm

    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    in_table = False
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        pdf.set_font("reg", size=9)
        # filter separator rows
        rows = [r for r in table_rows if not re.match(r'^[\s|:\-]+$', ''.join(r))]
        if not rows:
            table_rows = []
            return

        col_n = max(len(r) for r in rows)
        col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / col_n

        for ri, row in enumerate(rows):
            is_header = ri == 0
            pdf.set_font("bold" if is_header else "reg", size=9)
            fill = is_header
            pdf.set_fill_color(60, 60, 60) if is_header else pdf.set_fill_color(249, 249, 249)
            pdf.set_text_color(255 if is_header else 0)
            for ci, cell in enumerate(row):
                text = strip_inline(cell.strip())
                pdf.multi_cell(col_w, LH, text, border=1,
                               fill=fill if (is_header or ri % 2 == 0) else False,
                               new_x="RIGHT" if ci < len(row)-1 else "LMARGIN",
                               new_y="TOP"   if ci < len(row)-1 else "NEXT",
                               max_line_height=LH)
            pdf.set_text_color(0)
        pdf.ln(2)
        table_rows = []

    for raw in lines:
        line = raw.rstrip('\n')

        # ── table detection ─────────────────────────────────────────
        if '|' in line:
            cells = [c for c in line.split('|')]
            # remove empty first/last from leading/trailing |
            if cells and cells[0].strip() == '':
                cells = cells[1:]
            if cells and cells[-1].strip() == '':
                cells = cells[:-1]
            # separator row?
            if all(re.match(r'^[\s:\-]+$', c) for c in cells):
                in_table = True
                continue
            in_table = True
            table_rows.append(cells)
            continue
        else:
            if in_table:
                flush_table()
                in_table = False

        stripped = line.strip()

        # ── headings ────────────────────────────────────────────────
        h_match = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if h_match:
            level = len(h_match.group(1))
            text  = strip_inline(h_match.group(2))
            sizes   = {1: 18, 2: 14, 3: 11, 4: 10}
            margins = {1: 6,  2: 4,  3: 3,  4: 2}
            sz = sizes.get(level, 10)
            pdf.ln(margins.get(level, 2))
            pdf.set_font("bold", size=sz)
            if level == 1:
                pdf.set_fill_color(30, 30, 30)
                pdf.set_text_color(255)
                pdf.cell(0, sz * 0.5 + 4, f"  {text}", fill=True, new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0)
            elif level == 2:
                pdf.set_draw_color(80, 80, 80)
                pdf.cell(0, sz * 0.5 + 3, text, border="B", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, sz * 0.5 + 3, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            continue

        # ── blockquote ──────────────────────────────────────────────
        bq = re.match(r'^>\s*(.*)', stripped)
        if bq:
            pdf.set_fill_color(245, 245, 245)
            pdf.set_draw_color(150, 150, 150)
            pdf.set_font("reg", size=9)
            pdf.set_text_color(80)
            pdf.set_x(pdf.l_margin + 4)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 4,
                           LH, strip_inline(bq.group(1)), border="L", fill=True,
                           new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0)
            continue

        # ── horizontal rule ─────────────────────────────────────────
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            pdf.ln(2)
            pdf.set_draw_color(180)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(3)
            continue

        # ── list items ──────────────────────────────────────────────
        li = re.match(r'^(\s*)[-*]\s+(.*)', line)
        if li:
            indent_mm = len(li.group(1)) * 2 + 4
            content   = li.group(2)
            bullet    = "\u2022 "
            pdf.set_font("reg", size=10)
            pdf.set_x(pdf.l_margin + indent_mm)
            full = bullet + strip_inline(content)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - indent_mm,
                           LH, full, new_x="LMARGIN", new_y="NEXT")
            continue

        # ── numbered list ───────────────────────────────────────────
        oli = re.match(r'^(\s*)(\d+)\.\s+(.*)', line)
        if oli:
            indent_mm = len(oli.group(1)) * 2 + 4
            num       = oli.group(2)
            content   = oli.group(3)
            pdf.set_font("reg", size=10)
            pdf.set_x(pdf.l_margin + indent_mm)
            full = f"{num}. {strip_inline(content)}"
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - indent_mm,
                           LH, full, new_x="LMARGIN", new_y="NEXT")
            continue

        # ── blank line ──────────────────────────────────────────────
        if stripped == '':
            pdf.ln(2)
            continue

        # ── normal paragraph ────────────────────────────────────────
        pdf.set_font("reg", size=10)
        pdf.multi_cell(0, LH, strip_inline(stripped), new_x="LMARGIN", new_y="NEXT")

    if in_table:
        flush_table()

    pdf.output(pdf_path)
    print(f"PDF saved: {pdf_path}")


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
