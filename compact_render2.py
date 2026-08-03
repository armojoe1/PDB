import json, re, pikepdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
d=json.load(open('brief.json'))
W,H=letter
c=canvas.Canvas('/tmp/c2.pdf', pagesize=letter, pageCompression=1)
LM,RM,TM,BM=54,54,40,40
maxw=W-LM-RM; y=[H-TM]
def banner():
    c.setFont("Helvetica-Bold",6.5)
    c.drawCentredString(W/2,H-16,"TOP SECRET//NOFORN"); c.drawCentredString(W/2,12,"TOP SECRET//NOFORN")
def newpage():
    c.showPage(); banner(); y[0]=H-TM
def wrap(t,f,s):
    out=[];cur=""
    for w in t.split():
        x=(cur+" "+w).strip()
        if stringWidth(x,f,s)<=maxw: cur=x
        else: out.append(cur);cur=w
    if cur:out.append(cur)
    return out
def draw(t,f,s,l,ind=0,bul=False):
    for i,ln in enumerate(wrap(t,f,s)):
        if y[0]<BM+l: newpage()
        c.setFont(f,s)
        if bul and i==0: c.drawString(LM+3,y[0],chr(8226))
        c.drawString(LM+ind,y[0],ln); y[0]-=l
banner()
c.setFont("Helvetica-Bold",12); c.drawString(LM,y[0],"The President's Daily Brief"); y[0]-=13
c.setFont("Helvetica",8); c.drawString(LM,y[0],"For the President  -  3 August 2026"); y[0]-=6
c.line(LM,y[0],W-RM,y[0]); y[0]-=11
for a in d['articles']:
    if y[0]<BM+40: newpage()
    draw(a['headline'],"Helvetica-Bold",9,11)
    blocks=a['blocks']
    # lead para
    paras=[b for b in blocks if b['type']=='para']
    buls=[b for b in blocks if b['type']=='bullets']
    if paras: draw(re.sub('<[^>]+>','',paras[0]['text']),"Helvetica",7.8,9.3)
    if buls:
        for it in buls[0]['items'][:2]:
            draw(re.sub('<[^>]+>','',it),"Helvetica",7.8,9.3,ind=10,bul=True)
    y[0]-=6
c.showPage(); c.save()
p=pikepdf.open('/tmp/c2.pdf')
p.save('/tmp/c2p.pdf',object_stream_mode=pikepdf.ObjectStreamMode.generate,compress_streams=True,recompress_flate=True)
print("ok")
