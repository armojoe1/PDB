#!/usr/bin/env python3
"""Render a byte-compact PDB PDF (same content/voice as the skill brief) small
enough that its base64 can be transmitted reliably. Flows all entries across
pages with TOP SECRET//NOFORN banners, a 'For the President' masthead, bold
headlines, bullets, star dividers and italic source lines."""
import json, sys, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, HRFlowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import black, HexColor

brief = json.load(open(sys.argv[1]))
out = sys.argv[2]
date_h = "11 August 2026"

INK = HexColor("#1a1a1a")
styles = {
    "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=11.5,
                        leading=14, spaceBefore=8, spaceAfter=5, textColor=INK),
    "b": ParagraphStyle("b", fontName="Helvetica", fontSize=9, leading=12.2,
                        spaceAfter=5, textColor=INK, alignment=TA_LEFT),
    "li": ParagraphStyle("li", fontName="Helvetica", fontSize=9, leading=12.2,
                        spaceAfter=3, leftIndent=12, bulletIndent=2, textColor=INK),
    "src": ParagraphStyle("src", fontName="Helvetica-Oblique", fontSize=8,
                        leading=10.5, spaceBefore=4, spaceAfter=8, textColor=INK),
}

def banner(c, doc):
    c.saveState()
    c.setFont("Helvetica-Bold", 8)
    for y in (770, 18):
        c.drawCentredString(letter[0] / 2, y, "TOP SECRET//NOFORN")
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(54, 752, "For the President")
    c.drawRightString(letter[0] - 54, 752, date_h)
    c.setLineWidth(0.7)
    c.line(54, 747, letter[0] - 54, 747)
    c.setFont("Helvetica", 7)
    c.drawCentredString(letter[0] / 2, 30, "Prepared by ODNI  ·  mock brief, open-source reporting")
    c.restoreState()

doc = BaseDocTemplate(out, pagesize=letter, topMargin=58, bottomMargin=46,
                      leftMargin=54, rightMargin=54, title="The President's Daily Brief")
frame = Frame(54, 46, letter[0] - 108, 690, leftPadding=0, rightPadding=0,
              topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="pt", frames=[frame], onPage=banner)])

flow = []
flow.append(Paragraph("The President’s Daily Brief", styles["h"]))
flow.append(Paragraph(date_h, styles["b"]))
flow.append(HRFlowable(width="100%", thickness=0.6, color=black, spaceAfter=4))

def clean(t):
    return t  # reportlab mini-html already valid in source

for art in brief["articles"]:
    flow.append(Paragraph(clean(art["headline"]), styles["h"]))
    for blk in art["blocks"]:
        if blk["type"] == "para":
            flow.append(Paragraph(clean(blk["text"]), styles["b"]))
        elif blk["type"] == "bullets":
            for it in blk["items"]:
                flow.append(Paragraph(clean(it), styles["li"], bulletText="•"))
        elif blk["type"] == "stars":
            flow.append(Paragraph("★ ★ ★", ParagraphStyle(
                "st", parent=styles["b"], alignment=1, spaceBefore=3, spaceAfter=3)))
    if art.get("prepared_by"):
        flow.append(Paragraph(clean(art["prepared_by"]), styles["src"]))

doc.build(flow)
print("wrote", out)
