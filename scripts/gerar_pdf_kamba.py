from pathlib import Path
import re
import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Preformatted, ListFlowable, ListItem, HRFlowable, KeepTogether
)
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "descricao-tecnica-projeto-kamba.md"
OUTPUT = ROOT / "docs" / "descricao-tecnica-projeto-kamba.pdf"

raw = SOURCE.read_text(encoding="utf-8")
html = markdown.markdown(raw, extensions=["tables", "fenced_code", "sane_lists"])
soup = BeautifulSoup(html, "html.parser")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="DocTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                          fontSize=21, leading=26, textColor=colors.HexColor("#17365D"),
                          alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name="H1Custom", parent=styles["Heading1"], fontName="Helvetica-Bold",
                          fontSize=15, leading=19, textColor=colors.HexColor("#17365D"),
                          spaceBefore=14, spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle(name="H2Custom", parent=styles["Heading2"], fontName="Helvetica-Bold",
                          fontSize=12, leading=15, textColor=colors.HexColor("#24527A"),
                          spaceBefore=10, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="H3Custom", parent=styles["Heading3"], fontName="Helvetica-Bold",
                          fontSize=10.5, leading=13, spaceBefore=7, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica",
                          fontSize=9.2, leading=13.2, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="SmallCustom", parent=styles["BodyText"], fontName="Helvetica",
                          fontSize=8, leading=10, textColor=colors.HexColor("#444444")))
styles.add(ParagraphStyle(name="CodeCustom", parent=styles["Code"], fontName="Courier",
                          fontSize=7.4, leading=9, backColor=colors.HexColor("#F3F5F7"),
                          borderPadding=6, spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle(name="QuoteCustom", parent=styles["BodyText"], fontName="Helvetica-Oblique",
                          fontSize=9, leading=13, leftIndent=12, textColor=colors.HexColor("#555555"),
                          spaceBefore=4, spaceAfter=8))

def inline_markup(node):
    if isinstance(node, NavigableString):
        return escape(str(node)).replace("\n", " ")
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    inner = "".join(inline_markup(child) for child in node.children)
    if name in ("strong", "b"):
        return f"<b>{inner}</b>"
    if name in ("em", "i"):
        return f"<i>{inner}</i>"
    if name == "code":
        return f'<font name="Courier" size="8">{inner}</font>'
    if name == "a":
        href = node.get("href", "")
        return f'<link href="{escape(href, {chr(34): "&quot;"})}" color="#24527A">{inner}</link>' if href else inner
    if name == "br":
        return "<br/>"
    return inner

def paragraph_text(tag):
    return "".join(inline_markup(child) for child in tag.children).strip()

def render_list(tag, ordered=False):
    items = []
    for li in tag.find_all("li", recursive=False):
        parts = []
        for child in li.children:
            if isinstance(child, Tag) and child.name in ("ul", "ol"):
                continue
            if isinstance(child, Tag) and child.name == "p":
                parts.append(Paragraph(paragraph_text(child), styles["BodyCustom"]))
            elif isinstance(child, NavigableString) and str(child).strip():
                parts.append(Paragraph(escape(str(child).strip()), styles["BodyCustom"]))
            elif isinstance(child, Tag):
                parts.append(Paragraph(paragraph_text(child), styles["BodyCustom"]))
        if not parts:
            parts = [Paragraph("", styles["BodyCustom"])]
        items.append(ListItem(parts, leftIndent=10))
    return ListFlowable(items, bulletType="1" if ordered else "bullet",
                        start="1", leftIndent=18, bulletFontName="Helvetica",
                        bulletFontSize=8, spaceAfter=6)

def render_table(tag):
    rows = []
    for tr in tag.find_all("tr"):
        cells = []
        for cell in tr.find_all(["th", "td"], recursive=False):
            cells.append(Paragraph(paragraph_text(cell), styles["SmallCustom"]))
        if cells:
            rows.append(cells)
    if not rows:
        return None
    cols = max(len(row) for row in rows)
    for row in rows:
        row.extend([""] * (cols - len(row)))
    available = A4[0] - 36*mm
    widths = [available / cols] * cols
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C7D0DA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table

story = []
first_h1 = True
for element in soup.contents:
    if isinstance(element, NavigableString) or not isinstance(element, Tag):
        continue
    name = element.name.lower()
    if name == "h1":
        story.append(Paragraph(paragraph_text(element), styles["DocTitle"] if first_h1 else styles["H1Custom"]))
        first_h1 = False
    elif name == "h2":
        story.append(Paragraph(paragraph_text(element), styles["H2Custom"]))
    elif name == "h3":
        story.append(Paragraph(paragraph_text(element), styles["H3Custom"]))
    elif name in ("h4", "h5", "h6"):
        story.append(Paragraph(f"<b>{paragraph_text(element)}</b>", styles["BodyCustom"]))
    elif name == "p":
        story.append(Paragraph(paragraph_text(element), styles["BodyCustom"]))
    elif name in ("ul", "ol"):
        story.append(render_list(element, ordered=(name == "ol")))
    elif name == "pre":
        code = element.get_text().rstrip()
        story.append(Preformatted(code, styles["CodeCustom"], maxLineLength=100))
    elif name == "blockquote":
        story.append(Paragraph(paragraph_text(element), styles["QuoteCustom"]))
    elif name == "table":
        table = render_table(element)
        if table:
            story.extend([Spacer(1, 4), table, Spacer(1, 8)])
    elif name == "hr":
        story.extend([Spacer(1, 5), HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#C7D0DA")), Spacer(1, 7)])

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(18*mm, 12*mm, "Kamba — Descrição Técnica do Projeto")
    canvas.drawRightString(A4[0] - 18*mm, 12*mm, f"Página {doc.page}")
    canvas.restoreState()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                        topMargin=18*mm, bottomMargin=20*mm,
                        title="Descrição Técnica do Projeto Kamba",
                        author="Kamba")
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"PDF criado: {OUTPUT}")
