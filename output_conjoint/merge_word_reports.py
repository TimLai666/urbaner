"""
Merge four URBANER conjoint Word reports into one master document.

Order (logical flow of analysis):
  1. URBANER_聯合分析報告.docx        — 基礎聯合分析（屬性 part-worth 與重要性）
  2. URBANER_產品組合購買機率.docx    — 產品卡組合購買機率（套用係數至設計卡）
  3. URBANER_市場競爭力分析.docx      — 市場競爭力 MNL 分析（含競品選擇情境）
  4. URBANER_延伸分析報告.docx        — 延伸分析（深入洞察與圖表）

All content is preserved verbatim — no truncation.
"""
from pathlib import Path
from docx import Document
from docxcompose.composer import Composer

HERE = Path(__file__).resolve().parent

ORDERED_FILES = [
    "URBANER_聯合分析報告.docx",
    "URBANER_產品組合購買機率.docx",
    "URBANER_市場競爭力分析.docx",
    "URBANER_延伸分析報告.docx",
]

OUTPUT = HERE / "URBANER_完整分析報告.docx"


def main():
    paths = [HERE / f for f in ORDERED_FILES]
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(p)

    master = Document(str(paths[0]))
    composer = Composer(master)

    for p in paths[1:]:
        sub = Document(str(p))
        composer.append(sub)

    composer.save(str(OUTPUT))
    print(f"Merged {len(paths)} documents -> {OUTPUT}")


if __name__ == "__main__":
    main()
