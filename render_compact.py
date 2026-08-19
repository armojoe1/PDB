#!/usr/bin/env python3
"""Compact PDB renderer: same content/house-style, base-14 fonts only (no embedded
font subsets, no raster images) so the output PDF is small enough for a single,
integrity-verifiable upload. Cover + article furniture drawn as vectors/text."""
import json, sys
from reportlab import rl_config
rl_config.useA85 = 0  # raw binary Flate streams (no ASCII85 ~25% inflation)
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, white
from reportlab.platypus import Paragraph, Frame, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

W, H = letter
RED = Color(0.7, 0.06, 0.09)
BANNER = "TOP SECRET//NOFORN"
MARGIN = 0.9 * inch

body = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=14.5,
                      alignment=TA_LEFT, spaceAfter=7)
lead = ParagraphStyle("lead", parent=body, spaceAfter=8)
bullet = ParagraphStyle("bullet", parent=body, fontSize=10.5, leading=14, spaceAfter=5,
                        leftIndent=14, bulletIndent=2)
head = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=15, leading=18,
                      spaceAfter=10, textColor=black)
src = ParagraphStyle("src", fontName="Helvetica-Oblique", fontSize=9, leading=12,
                     textColor=Color(0.2, 0.2, 0.2), spaceBefore=8)
hdr_l = ParagraphStyle("hdr_l", fontName="Helvetica-Oblique", fontSize=10.5, leading=13)


def draw_furniture(c, date_str, first=False):
    # classification banners top & bottom
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(black)
    c.drawCentredString(W / 2, H - 0.42 * inch, BANNER)
    c.drawCentredString(W / 2, 0.34 * inch, BANNER)
    # red corner flash (top-right triangle)
    c.setFillColor(RED)
    p = c.beginPath()
    p.moveTo(W, H); p.lineTo(W - 0.55 * inch, H); p.lineTo(W, H - 0.55 * inch); p.close()
    c.drawPath(p, fill=1, stroke=0)
    if first:
        # masthead: "For the President" + date left, seal right, rule under
        y = H - 0.95 * inch
        c.setFillColor(black)
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(MARGIN, y, "For the President")
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(MARGIN, y - 15, date_str)
        # simple vector "seal" on the right (concentric rings + star) as an emblem stand-in
        cx, cy, r = W - MARGIN - 0.28 * inch, y - 6, 0.30 * inch
        c.setStrokeColor(black); c.setLineWidth(1.1); c.circle(cx, cy, r, stroke=1, fill=0)
        c.setLineWidth(0.6); c.circle(cx, cy, r - 3, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(cx, cy + r - 9, "THE WHITE HOUSE")
        c.drawCentredString(cx, cy - r + 4, "WASHINGTON")
        c.setFont("Helvetica", 12); c.drawCentredString(cx, cy - 4, "*")
        c.setLineWidth(1.0)
        c.line(MARGIN, y - 26, W - MARGIN, y - 26)
        return y - 42
    return H - 0.95 * inch


def stars_flow():
    return Paragraph('<para align="center"><font size=11>&#9733; &#9733; &#9733;</font></para>',
                     ParagraphStyle("stars", alignment=TA_CENTER, spaceBefore=6, spaceAfter=8))


def cover_page(c):
    c.setFillColor(black); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(W / 2, H - 1.4 * inch, "TOP SECRET//SCI")
    c.setFont("Helvetica", 10.5)
    lines = [
        "CONTAINS SENSITIVE COMPARTMENTED INFORMATION UP TO HCS-P/SI/TK",
        "", "THIS IS A COVER SHEET", "FOR CLASSIFIED INFORMATION", "",
        "ALL INDIVIDUALS HANDLING THIS INFORMATION ARE REQUIRED TO",
        "PROTECT IT FROM UNAUTHORIZED DISCLOSURE IN THE INTEREST OF",
        "THE NATIONAL SECURITY OF THE UNITED STATES.", "",
        "HANDLING, STORAGE, REPRODUCTION AND DISPOSITION OF THE",
        "ATTACHED DOCUMENT MUST BE IN ACCORDANCE WITH APPLICABLE",
        "EXECUTIVE ORDERS AND AGENCY DIRECTIVES.",
    ]
    y = H - 2.2 * inch
    for ln in lines:
        c.drawCentredString(W / 2, y, ln); y -= 16
    # red border
    c.setStrokeColor(RED); c.setLineWidth(3)
    c.rect(0.5 * inch, 0.5 * inch, W - inch, H - inch, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, 0.9 * inch, "TOP SECRET//SCI")
    c.showPage()


def render(data, out):
    c = canvas.Canvas(out, pagesize=letter, pageCompression=1)
    # date "19 August 2026"
    from datetime import date
    y, m, d = [int(x) for x in data["date"].split("-")]
    months = ["", "January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    date_str = f"{d} {months[m]} {y}"

    if data.get("cover", True):
        cover_page(c)

    for art in data["articles"]:
        top = draw_furniture(c, date_str, first=True)
        story = [Paragraph(art["headline"], head)]
        for b in art["blocks"]:
            t = b["type"]
            if t == "para":
                story.append(Paragraph(b["text"], lead))
            elif t == "bullets":
                items = [ListItem(Paragraph(x, bullet), leftIndent=14, value="•")
                         for x in b["items"]]
                story.append(ListFlowable(items, bulletType="bullet", start="•",
                                          leftIndent=10, spaceAfter=6))
            elif t == "stars":
                story.append(stars_flow())
        if art.get("prepared_by"):
            story.append(Paragraph("<i>%s</i>" % art["prepared_by"], src))

        # Flow the article across as many pages as needed. Frame.addFromList
        # consumes the flowables it can fit and leaves the rest in `story`.
        first_page = True
        while story:
            if first_page:
                frame_top = top
                first_page = False
            else:
                c.showPage()
                frame_top = draw_furniture(c, date_str, first=False)
                # continuation pages: no masthead, so reclaim that space
                frame_top = H - 0.95 * inch
            frame = Frame(MARGIN, 0.7 * inch, W - 2 * MARGIN, frame_top - 0.75 * inch,
                          leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
            before = len(story)
            frame.addFromList(story, c)
            if len(story) == before and story:
                # nothing fit (should not happen) — bail to avoid infinite loop
                raise RuntimeError("flowable too large to fit a page")
            if story:  # more to come -> mark continuation
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColor(black)
                c.drawRightString(W - MARGIN, 0.55 * inch, "Continued . . .")
        c.showPage()
    c.save()


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        data = json.load(f)
    render(data, sys.argv[2])
    print("wrote", sys.argv[2])
