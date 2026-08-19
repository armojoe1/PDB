#!/usr/bin/env python3
"""Ultra-compact PDB: minimal PDF so the base64 payload is small enough for a
single reliable upload. Banners top/bottom every page, masthead on p1, bold
headlines, bullets, *** dividers, italic source lines. Helvetica base-14 only."""
import json, sys
from reportlab import rl_config
rl_config.useA85 = 0
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.platypus import Paragraph, Frame, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

W, H = letter
M = 0.7 * inch
BAN = "TOP SECRET//NOFORN"
body = ParagraphStyle("b", fontName="Helvetica", fontSize=9, leading=11.6, spaceAfter=5)
lead = ParagraphStyle("l", parent=body, spaceAfter=6)
bl = ParagraphStyle("bl", parent=body, leftIndent=12, spaceAfter=3)
hd = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=12, leading=14, spaceBefore=8, spaceAfter=5)
sr = ParagraphStyle("s", fontName="Helvetica-Oblique", fontSize=8, leading=10, spaceAfter=4)
st = ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER, spaceBefore=3, spaceAfter=5)


def furn(c, ds, first):
    c.setFont("Helvetica-Bold", 8); c.setFillColor(black)
    c.drawCentredString(W/2, H-0.4*inch, BAN)
    c.drawCentredString(W/2, 0.32*inch, BAN)
    if first:
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(M, H-0.72*inch, "For the President")
        c.drawRightString(W-M, H-0.72*inch, ds)
        c.setLineWidth(0.8); c.line(M, H-0.78*inch, W-M, H-0.78*inch)
        return H-0.9*inch
    return H-0.6*inch


def build(data, out):
    c = canvas.Canvas(out, pagesize=letter, pageCompression=1)
    y_, m_, d_ = [int(x) for x in data["date"].split("-")]
    months = ["", "January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    ds = f"{d_} {months[m_]} {y_}"
    story = []
    for art in data["articles"]:
        story.append(Paragraph(art["headline"], hd))
        for b in art["blocks"]:
            if b["type"] == "para":
                story.append(Paragraph(b["text"], lead))
            elif b["type"] == "bullets":
                story.append(ListFlowable(
                    [ListItem(Paragraph(x, bl), value="•") for x in b["items"]],
                    bulletType="bullet", start="•", leftIndent=10, spaceAfter=4))
            elif b["type"] == "stars":
                story.append(Paragraph("* * *", st))
        if art.get("prepared_by"):
            story.append(Paragraph("<i>%s</i>" % art["prepared_by"], sr))

    first = True
    while story:
        top = furn(c, ds, first); first = False
        fr = Frame(M, 0.55*inch, W-2*M, top-0.6*inch, 0, 0, 0, 0)
        before = len(story)
        fr.addFromList(story, c)
        if len(story) == before and story:
            raise RuntimeError("overflow")
        c.showPage()
    c.save()


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
    print("ok")
