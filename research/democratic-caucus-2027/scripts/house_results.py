import re,sys,json
t=open(sys.argv[1]).read()
start=t.find('==Alabama==')
t=t[start:]
rows=re.split(r"\n\|-[^\n]*\n(?=!(?:rowspan=\d+\s*\|)?\s*\{\{ushr)",t)
res=[]
def clean(s):
    s=re.sub(r'<ref[^>]*/>','',s); s=re.sub(r'<ref.*?</ref>','',s,flags=re.S)
    s=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',s); s=re.sub(r"'''","",s); return s
for r in rows:
    m=re.match(r"!(?:rowspan=\d+\s*\|)?\s*\{\{ushr\|([A-Z]{2})\|(\w+)\|X\}\}",r)
    if not m: continue
    st,d=m.group(1),m.group(2)
    r=r.split('\n|}')[0]
    inc=re.search(r'\{\{sortname\|([^|}]+)\|([^|}]+)',r)
    incname=(inc.group(1)+' '+inc.group(2)) if inc else ''
    party=re.search(r'\|\s*style="[^"]*"\s*\|\s*(Democratic|Republican|Independent|DFL|Democratic-NPL)\s*\n',r)
    lines=r.split('\n')
    status=''
    for i,l in enumerate(lines):
        if 'plainlist' in l: status=clean(lines[i-1]); break
    cands=[clean(l) for l in lines if l.startswith('*')]
    win=[c for c in cands if '{{aye}}' in c.lower() or '{{Aye}}' in c]
    def nm(c):
        c=re.sub(r'\{\{[^}]*\}\}','',c).strip(); return c
    res.append(dict(st=st,d=d,incumbent=incname,inc_party=party.group(1) if party else '',status=re.sub(r'\{\{[^}]*\}\}','',status).replace('<br>',' ').strip('| '),
        winner=nm(win[0]) if win else None,cands=[nm(c) for c in cands]))
json.dump(res,open(sys.argv[2],'w'),indent=1)
dw=[x for x in res if x['winner'] and re.search(r'\((Democratic|DFL)',x['winner'])]
unc=[x for x in res if not x['winner']]
print('districts',len(res),'dem winners',len(dw),'uncalled',len(unc))
for x in unc: print('UNCALLED',x['st'],x['d'],x['incumbent'],x['inc_party'],'|',x['status'][:80],'|',' / '.join(x['cands'])[:200])
