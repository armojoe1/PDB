#!/usr/bin/env python3
"""Compact PDB renderer: same content/house-voice styling as render_pdb.py but
with efficient (Platypus) text streams so the PDF stays small. Uses base-14
Helvetica (not embedded). Reproduces TOP SECRET//NOFORN banners, the
"For the President / date" masthead with rule, bold headlines, bullet
sub-judgments, star dividers and the italic 'Prepared by' source line.
"""
import sys, json, datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                Paragraph, Spacer, PageBreak)

RED = HexColor("#8B0000")

def fmt_date(d):
    try:
        dt = datetime.datetime.strptime(d, "%Y-%m-%d")
        return dt.strftime("%-d %B %Y")
    except Exception:
        return d

def build(brief, out):
    date_h = fmt_date(brief.get("date", ""))
    cls = brief.get("classification", "TOP SECRET//NOFORN")

    styles = {
        "toc_title": ParagraphStyle("toc_title", fontName="Helvetica-Bold",
            fontSize=15, leading=19, spaceAfter=10),
        "toc": ParagraphStyle("toc", fontName="Helvetica", fontSize=10.5,
            leading=15, spaceAfter=5),
        "headline": ParagraphStyle("headline", fontName="Helvetica-Bold",
            fontSize=15, leading=18, spaceAfter=9),
        "para": ParagraphStyle("para", fontName="Helvetica", fontSize=10.5,
            leading=14.5, spaceAfter=8),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10.5,
            leading=14.5, leftIndent=16,
            bulletIndent=4, spaceAfter=6),
        "stars": ParagraphStyle("stars", fontName="Helvetica-Bold", fontSize=11,
            leading=16, alignment=TA_CENTER, textColor=RED, spaceBefore=4,
            spaceAfter=8),
        "prep": ParagraphStyle("prep", fontName="Helvetica-Oblique", fontSize=9,
            leading=12, textColor=HexColor("#333333"), spaceBefore=10),
    }

    def page_furniture(canvas, doc):
        canvas.saveState()
        w, h = letter
        # classification banners
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(black)
        canvas.drawCentredString(w/2, h-30, cls)
        canvas.drawCentredString(w/2, 22, cls)
        # red corner flash
        canvas.setFillColor(RED)
        canvas.rect(w-42, h-42, 24, 24, stroke=0, fill=1)
        # masthead: "For the President" left, date right, rule under
        canvas.setFillColor(black)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(54, h-70, "For the President")
        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(w-54, h-70, date_h)
        canvas.setLineWidth(0.8)
        canvas.line(54, h-76, w-54, h-76)
        canvas.restoreState()

    frame = Frame(54, 40, letter[0]-108, letter[1]-40-96, id="body")
    doc = BaseDocTemplate(out, pagesize=letter,
        leftMargin=54, rightMargin=54, topMargin=96, bottomMargin=40,
        title="President's Daily Brief", author="ODNI")
    doc.addPageTemplates([PageTemplate(id="pdb", frames=[frame],
        onPage=page_furniture)])

    story = []
    toc = brief.get("toc")
    if toc:
        story.append(Paragraph("Today&rsquo;s Brief", styles["toc_title"]))
        for e in toc:
            tag = (e.get("tag", "") or "").upper()
            story.append(Paragraph("<b>%s:</b> %s" % (tag, e.get("summary", "")),
                styles["toc"]))
        story.append(PageBreak())

    arts = brief.get("articles", [])
    for i, art in enumerate(arts):
        story.append(Paragraph(art.get("headline", ""), styles["headline"]))
        for blk in art.get("blocks", []):
            t = blk.get("type")
            if t == "para":
                story.append(Paragraph(blk.get("text", ""), styles["para"]))
            elif t == "bullets":
                for it in blk.get("items", []):
                    story.append(Paragraph(it, styles["bullet"],
                        bulletText="•"))
            elif t == "stars":
                story.append(Paragraph("* * *", styles["stars"]))
        if art.get("prepared_by"):
            story.append(Paragraph("<i>%s</i>" % art["prepared_by"], styles["prep"]))
        if i != len(arts) - 1:
            story.append(PageBreak())

    doc.build(story)

def main():
    if len(sys.argv) < 3:
        print("usage: render_compact.py brief.json out.pdf"); sys.exit(1)
    brief = json.load(open(sys.argv[1]))
    build(brief, sys.argv[2])
    print("Wrote", sys.argv[2])

if __name__ == "__main__":
    main()
