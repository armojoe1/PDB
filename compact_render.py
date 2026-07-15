import json, sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, HRFlowable, ListFlowable, ListItem)
from reportlab.lib.styles import ParagraphStyle

RED = HexColor("#B22222")
brief = json.load(open(sys.argv[1]))
out = sys.argv[2]
datestr = "15 July 2026"

styles = {
 'head': ParagraphStyle('head', fontName='Helvetica-Bold', fontSize=10.5, leading=12.5,
                        spaceBefore=8, spaceAfter=3, textColor=black),
 'body': ParagraphStyle('body', fontName='Helvetica', fontSize=8.4, leading=11,
                        alignment=TA_JUSTIFY, spaceAfter=3),
 'bull': ParagraphStyle('bull', fontName='Helvetica', fontSize=8.4, leading=11,
                        alignment=TA_JUSTIFY, leftIndent=10, bulletIndent=0),
 'prep': ParagraphStyle('prep', fontName='Helvetica-Oblique', fontSize=7.4, leading=9,
                        spaceBefore=2, spaceAfter=4, textColor=HexColor("#333333")),
 'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=13, leading=15,
                         alignment=TA_CENTER, spaceAfter=2),
 'sub': ParagraphStyle('sub', fontName='Helvetica', fontSize=8, leading=10,
                       alignment=TA_CENTER, textColor=HexColor("#444444"), spaceAfter=6),
 'stars': ParagraphStyle('stars', fontName='Helvetica', fontSize=8, leading=10,
                         alignment=TA_CENTER, textColor=HexColor("#777777"),
                         spaceBefore=3, spaceAfter=3),
 'banner': ParagraphStyle('banner', fontName='Helvetica-Bold', fontSize=7.5, leading=9,
                          alignment=TA_CENTER, textColor=RED),
}

def banner(c, doc):
    c.saveState()
    c.setFont('Helvetica-Bold', 7.5); c.setFillColor(RED)
    c.drawCentredString(letter[0]/2, letter[1]-0.32*inch, "TOP SECRET//NOFORN")
    c.drawCentredString(letter[0]/2, 0.28*inch, "TOP SECRET//NOFORN")
    c.setFillColor(RED); c.rect(letter[0]-0.5*inch, letter[1]-0.5*inch, 0.34*inch, 0.34*inch, fill=1, stroke=0)
    c.restoreState()

story = []
story.append(Spacer(1, 0.12*inch))
story.append(Paragraph("THE PRESIDENT&#8217;S DAILY BRIEF", styles['title']))
story.append(Paragraph("For the President&#160;&#160;&#8226;&#160;&#160;" + datestr, styles['sub']))
story.append(HRFlowable(width='100%', thickness=0.8, color=black, spaceAfter=4))

for art in brief['articles']:
    story.append(Paragraph(art['headline'], styles['head']))
    for blk in art['blocks']:
        if blk['type'] == 'para':
            story.append(Paragraph(blk['text'], styles['body']))
        elif blk['type'] == 'bullets':
            items = [ListItem(Paragraph(x, styles['bull']), leftIndent=10, value='•')
                     for x in blk['items']]
            story.append(ListFlowable(items, bulletType='bullet', start='•',
                                      leftIndent=10, bulletFontSize=7))
        elif blk['type'] == 'stars':
            story.append(Paragraph("&#9733; &#9733; &#9733;", styles['stars']))
    if art.get('prepared_by'):
        story.append(Paragraph(art['prepared_by'], styles['prep']))
    story.append(HRFlowable(width='40%', thickness=0.4, color=HexColor("#bbbbbb"),
                            spaceBefore=2, spaceAfter=2))

doc = BaseDocTemplate(out, pagesize=letter,
                      leftMargin=0.62*inch, rightMargin=0.62*inch,
                      topMargin=0.5*inch, bottomMargin=0.45*inch)
frame = Frame(doc.leftMargin, doc.bottomMargin,
              letter[0]-doc.leftMargin-doc.rightMargin,
              letter[1]-doc.topMargin-doc.bottomMargin, id='f')
doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=banner)])
doc.build(story)
print("wrote", out)
