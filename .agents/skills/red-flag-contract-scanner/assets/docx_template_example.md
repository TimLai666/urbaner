# Word 輸出範例腳本

當需要產出 Word docx 版本時,參考此範例腳本(基於 python-docx)。

實際生成時:
1. 先讀 `/mnt/skills/public/docx/SKILL.md` 取得最新最佳實踐
2. 使用 python-docx,顏色配置照下表
3. 檔名格式:`合約紅旗審閱_[文件類型]_YYYYMMDD.docx`
4. 存到 `/mnt/user-data/outputs/`

## 顏色配置

| 用途 | RGB | 說明 |
|------|-----|------|
| 紅旗標題 | (192, 0, 0) | 深紅,加粗 |
| 紅旗內文 | (0, 0, 0) | 黑色 |
| 注意條款標題 | (237, 125, 49) | 橘色,加粗 |
| 正常條款 | (127, 127, 127) | 灰色淡化 |
| 原文引用 | (89, 89, 89) | 深灰,斜體 |
| 協商建議標題 | (0, 112, 192) | 深藍,加粗 |
| 警語 | (192, 0, 0) | 深紅,加底色 |

## 範例 Python 腳本

```python
from docx import Document
from docx.shared import RGBColor, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from datetime import datetime

def create_red_flag_report(
    doc_type: str,
    risk_level: str,  # 低/中/高/極高
    red_flags: list,  # [{title, citation, plain_text, why_red, suggestion}, ...]
    yellow_flags: list,
    green_items: list,
    questions_to_ask: list,
    checklist: list,
    output_path: str,
):
    doc = Document()
    
    # 標題
    title = doc.add_heading('合約紅旗掃描報告', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 警語(紅色加底)
    warning = doc.add_paragraph()
    warning_run = warning.add_run(
        '⚠️ 此份分析僅為條款解讀協助,不構成法律意見。\n'
        '涉及高金額、長期、跨境、不動產、勞動權益等重大合約,務必諮詢專業律師。'
    )
    warning_run.bold = True
    warning_run.font.color.rgb = RGBColor(192, 0, 0)
    warning_run.font.size = Pt(10)
    
    doc.add_paragraph()
    
    # 文件基本資訊
    doc.add_heading('文件基本資訊', level=1)
    info_table = doc.add_table(rows=4, cols=2)
    info_table.style = 'Light Grid Accent 1'
    info_table.cell(0, 0).text = '文件類型'
    info_table.cell(0, 1).text = doc_type
    info_table.cell(1, 0).text = '審閱日期'
    info_table.cell(1, 1).text = datetime.now().strftime('%Y-%m-%d')
    info_table.cell(2, 0).text = '整體風險評估'
    info_table.cell(2, 1).text = risk_level
    info_table.cell(3, 0).text = '紅旗 / 注意 / 正常數量'
    info_table.cell(3, 1).text = f'{len(red_flags)} / {len(yellow_flags)} / {len(green_items)}'
    
    doc.add_paragraph()
    
    # 紅旗條款
    doc.add_heading('🚨 紅旗條款(建議拒絕或強烈協商)', level=1)
    for i, flag in enumerate(red_flags, 1):
        # 紅旗標題(深紅加粗)
        h = doc.add_heading(f'🚨 紅旗 #{i}:{flag["title"]}', level=2)
        for run in h.runs:
            run.font.color.rgb = RGBColor(192, 0, 0)
        
        # 原文位置 + 引用(深灰斜體)
        p_loc = doc.add_paragraph()
        p_loc.add_run('原文位置:').bold = True
        p_loc.add_run(flag.get('location', '未標示'))
        
        p_cite = doc.add_paragraph()
        p_cite.add_run('原文引用:').bold = True
        p_cite_text = doc.add_paragraph(flag['citation'])
        p_cite_text.paragraph_format.left_indent = Cm(1)
        for run in p_cite_text.runs:
            run.italic = True
            run.font.color.rgb = RGBColor(89, 89, 89)
        
        # 白話翻譯
        p_plain = doc.add_paragraph()
        p_plain.add_run('白話翻譯:').bold = True
        doc.add_paragraph(flag['plain_text'])
        
        # 為何是紅旗
        p_why = doc.add_paragraph()
        p_why.add_run('為何是紅旗:').bold = True
        doc.add_paragraph(flag['why_red'])
        
        # 協商建議(藍色強調)
        p_sug = doc.add_paragraph()
        sug_run = p_sug.add_run('💡 協商建議:')
        sug_run.bold = True
        sug_run.font.color.rgb = RGBColor(0, 112, 192)
        doc.add_paragraph(flag['suggestion'])
        
        doc.add_paragraph('—' * 30)
    
    # 注意條款
    if yellow_flags:
        doc.add_heading('⚠️ 注意條款', level=1)
        for i, flag in enumerate(yellow_flags, 1):
            h = doc.add_heading(f'⚠️ 注意 #{i}:{flag["title"]}', level=2)
            for run in h.runs:
                run.font.color.rgb = RGBColor(237, 125, 49)
            # 後續結構同紅旗,但顏色改橘
            # ... (相同邏輯)
    
    # 正常條款(灰色簡略)
    if green_items:
        doc.add_heading('✅ 正常或對你有利的條款', level=1)
        for item in green_items:
            p = doc.add_paragraph(f'• {item}')
            for run in p.runs:
                run.font.color.rgb = RGBColor(127, 127, 127)
    
    # 應追問的問題
    doc.add_heading('💬 你應該追問對方的問題清單', level=1)
    for q in questions_to_ask:
        doc.add_paragraph(q, style='List Number')
    
    # 簽約前檢查清單
    doc.add_heading('☑️ 簽約前檢查清單', level=1)
    for item in checklist:
        p = doc.add_paragraph(f'☐ {item}')
    
    # 頁尾警語
    doc.add_page_break()
    final = doc.add_paragraph()
    final_run = final.add_run(
        '本報告由 AI 輔助分析產出,僅供參考。\n'
        '簽署前請務必諮詢具有相關專業之律師、會計師或金融顧問。'
    )
    final_run.italic = True
    final_run.font.color.rgb = RGBColor(127, 127, 127)
    final_run.font.size = Pt(9)
    final.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.save(output_path)
    return output_path


# 使用範例
if __name__ == '__main__':
    output = create_red_flag_report(
        doc_type='公寓租約',
        risk_level='高',
        red_flags=[
            {
                'title': '不得遷入戶籍 / 不得申報',
                'location': '第 8 條第 3 項',
                'citation': '承租人不得將戶籍遷入本租賃處所,亦不得申報所得稅租金支出。',
                'plain_text': '房東禁止你把戶籍遷進來,也禁止你報所得稅扣除。',
                'why_red': '此條違反內政部「住宅租賃定型化契約不得記載事項」,屬於違法條款。對你的影響:無法申請租金補貼、無法享受所得稅扣除(每年最高 18 萬)、無法投票或辦理子女就學。房東通常是想逃稅。',
                'suggestion': '直接刪除此條。可協商「房客報稅 → 房租提高 X 元 cover 房東稅務」但不能完全剝奪你的法定權利。',
            },
            # ... 其他紅旗
        ],
        yellow_flags=[],
        green_items=['第 12 條 雙方爭議解決約定 → 業界標準'],
        questions_to_ask=[
            '是否可在簽約前完成設備清單拍照存證?',
            '若房屋發生漏水,修繕費用如何分擔?',
        ],
        checklist=[
            '已核對房東身分(地政司謄本)',
            '已確認建物用途為住宅',
            '完整設備清單已拍照存證',
            '紅旗條款已書面確認修改或刪除',
        ],
        output_path='/mnt/user-data/outputs/合約紅旗審閱_租約_20260503.docx',
    )
    print(f'報告已產出:{output}')
```

## 注意事項

- python-docx 在無顯示環境執行 OK,不需要 GUI
- 字型若需要中文標楷 / 微軟正黑等,需確認系統字體存在
- 表格樣式 'Light Grid Accent 1' 是 Word 內建,通用
- emoji 在 Word 上能顯示但顏色不會變(emoji 是字符不是字型),所以紅旗的「🚨」靠 emoji 自然紅色,標題另用顏色強調
