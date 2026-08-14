"""
Script to generate PDF documents for parameter_guide.md and manual_testing_doc.md using ReportLab.
"""
import os
import re
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

BASE_DIR = os.path.dirname(__file__)

def build_pdf_from_markdown(md_file_path, pdf_output_path, doc_title):
    if not os.path.exists(md_file_path):
        print(f"Error: {md_file_path} not found.")
        return

    with open(md_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(
        pdf_output_path,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    title_s = ParagraphStyle("DocTitle", parent=styles["Title"], fontSize=20, leading=24, textColor=colors.HexColor("#1e3a5f"), spaceAfter=8, alignment=TA_LEFT)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, leading=18, textColor=colors.HexColor("#1e3a5f"), spaceBefore=14, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, leading=16, textColor=colors.HexColor("#2d6a4f"), spaceBefore=10, spaceAfter=4)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=10, leading=14, textColor=colors.HexColor("#444444"), spaceBefore=8, spaceAfter=3)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, leading=13.5, textColor=colors.HexColor("#222222"), spaceAfter=4)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=2)
    code_s = ParagraphStyle("Code", parent=body, fontName="Courier", fontSize=8.5, leading=11, backColor=colors.HexColor("#f1f5f9"), textColor=colors.HexColor("#0f172a"), leftIndent=8, rightIndent=8, spaceAfter=4)

    def parse_inline(text):
        # Convert markdown bold/italic/code to HTML
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#1e293b">\1</font>', text)
        return text

    c = []
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    for line in lines:
        line_str = line.rstrip("\n")

        # Code block toggle
        if line_str.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_text = "<br/>".join(code_lines).replace(" ", "&nbsp;")
                c.append(Paragraph(code_text, code_s))
                code_lines = []
                c.append(Spacer(1, 4))
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            safe_line = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_lines.append(safe_line)
            continue

        # Markdown Table parsing
        if "|" in line_str and not line_str.startswith("```"):
            if "---" in line_str:
                continue # Skip table delimiter line
            row = [parse_inline(cell.strip()) for cell in line_str.split("|")[1:-1]]
            if row:
                table_rows.append(row)
                in_table = True
            continue
        else:
            if in_table and table_rows:
                # Flush table
                formatted_rows = []
                for idx, r in enumerate(table_rows):
                    row_cells = []
                    for cell in r:
                        style = ParagraphStyle(f"TCell_{idx}", parent=body, fontSize=8.5, leading=11, textColor=colors.white if idx == 0 else colors.black)
                        row_cells.append(Paragraph(cell, style))
                    formatted_rows.append(row_cells)

                t = Table(formatted_rows, repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                c.append(t)
                c.append(Spacer(1, 6))
                table_rows = []
                in_table = False

        if not line_str.strip():
            c.append(Spacer(1, 3))
            continue

        # Headers
        if line_str.startswith("# "):
            c.append(Paragraph(parse_inline(line_str[2:]), title_s))
            c.append(HRFlowable(width="100%", color=colors.HexColor("#1e3a5f"), thickness=1.5, spaceAfter=8))
        elif line_str.startswith("## "):
            c.append(Paragraph(parse_inline(line_str[3:]), h1))
        elif line_str.startswith("### "):
            c.append(Paragraph(parse_inline(line_str[4:]), h2))
        elif line_str.startswith("#### "):
            c.append(Paragraph(parse_inline(line_str[5:]), h3))
        elif line_str.startswith("- ") or line_str.startswith("* "):
            c.append(Paragraph(parse_inline(line_str[2:]), bullet, bulletText="\u2022"))
        elif line_str.startswith("> "):
            quote_s = ParagraphStyle("Quote", parent=body, fontName="Helvetica-Oblique", backColor=colors.HexColor("#e2e8f0"), leftIndent=12, rightIndent=12, spaceAfter=4)
            c.append(Paragraph(parse_inline(line_str[2:]), quote_s))
        elif line_str.startswith("---"):
            c.append(HRFlowable(width="100%", color=colors.HexColor("#cbd5e1"), thickness=0.8, spaceAfter=6))
        else:
            c.append(Paragraph(parse_inline(line_str), body))

    # Flush remaining table if any
    if in_table and table_rows:
        formatted_rows = []
        for idx, r in enumerate(table_rows):
            row_cells = [Paragraph(cell, ParagraphStyle(f"TCell_{idx}", parent=body, fontSize=8.5, leading=11, textColor=colors.white if idx == 0 else colors.black)) for cell in r]
            formatted_rows.append(row_cells)

        t = Table(formatted_rows, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        c.append(t)

    doc.build(c)
    print(f"Successfully generated PDF: {pdf_output_path}")


if __name__ == "__main__":
    param_md = os.path.join(BASE_DIR, "parameter_guide.md")
    param_pdf = os.path.join(BASE_DIR, "parameter_guide.pdf")

    manual_md = os.path.join(BASE_DIR, "manual_testing_doc.md")
    manual_pdf = os.path.join(BASE_DIR, "manual_testing_doc.pdf")

    build_pdf_from_markdown(param_md, param_pdf, "AI-RCBDS Parameter Guide")
    build_pdf_from_markdown(manual_md, manual_pdf, "AI-RCBDS Manual Testing Protocol")
