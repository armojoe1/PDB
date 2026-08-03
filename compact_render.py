import json, pikepdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

d=json.load(open('brief.json'))
W,H=letter
c=canvas.Canvas('/tmp/compact.pdf', pagesize=letter, pageCompression=1)
LM,RM,TM,BM=54,54,54,54
maxw=W-LM-RM
y=[H-TM]

def banner():
    c.setFont("Helvetica-Bold",7)
    c.drawCentredString(W/2,H-20,"TOP SECRET//NOFORN")
    c.drawCentredString(W/2,14,"TOP SECRET//NOFORN")

def newpage():
    c.showPage(); banner(); y[0]=H-TM

def wrap(text,font,size):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if stringWidth(t,font,size)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

def draw(text,font,size,lead,indent=0,bullet=False):
    for i,ln in enumerate(wrap(text,font,size)):
        if y[0]<BM+lead: newpage()
        c.setFont(font,size)
        x=LM+indent
        if bullet and i==0:
            c.drawString(LM+4,y[0],chr(8226)); 
        c.drawString(x,y[0],ln); y[0]-=lead

banner()
c.setFont("Helvetica-Bold",13); c.drawString(LM,y[0],"The President's Daily Brief"); y[0]-=16
c.setFont("Helvetica",9); c.drawString(LM,y[0],"For the President  -  3 August 2026"); y[0]-=8
c.setLineWidth(0.5); c.line(LM,y[0],W-RM,y[0]); y[0]-=14

for a in d['articles']:
    if y[0]<BM+60: newpage()
    draw(a['headline'],"Helvetica-Bold",10.5,13)
    y[0]-=2
    for b in a['blocks']:
        if b['type']=='para':
            import re
            txt=re.sub('<[^>]+>','',b['text'])
            draw(txt,"Helvetica",8.5,10.5)
        elif b['type']=='bullets':
            for it in b['items']:
                import re
                draw(re.sub('<[^>]+>','',it),"Helvetica",8.5,10.5,indent=12,bullet=True)
        elif b['type']=='stars':
            if y[0]<BM+12: newpage()
            c.setFont("Helvetica",8); c.drawCentredString(W/2,y[0],"* * *"); y[0]-=11
        y[0]-=2
    if a.get('prepared_by'):
        draw(a['prepared_by'],"Helvetica-Oblique",7.5,9.5)
    y[0]-=8

c.showPage(); c.save()

pdf=pikepdf.open('/tmp/compact.pdf')
pdf.save('/tmp/compact_packed.pdf',
         object_stream_mode=pikepdf.ObjectStreamMode.generate,
         compress_streams=True, recompress_flate=True)
print("done")
