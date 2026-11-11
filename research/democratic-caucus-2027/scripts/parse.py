import re,sys,json
t=open(sys.argv[1]).read()
hdr=[]
rows=[]; buf=[]; curhdr=''
def flush():
    if buf: rows.append((curhdr,'\n'.join(buf)))
for line in t.split('\n'):
    m=re.match(r'^(=+)\s*(.*?)\s*=+\s*$',line)
    if m:
        flush(); buf=[]
        lvl=len(m.group(1)); hdr=hdr[:lvl-2]+[m.group(2)]; curhdr=' > '.join(hdr); continue
    if line.startswith('|-') or line.startswith('|}'):
        flush(); buf=[]; continue
    buf.append(line)
flush()
out=[]
for h,row in rows:
    if re.search(r'party shading/(Democratic|DFL|Independent)',row) and 'TBD (' not in row:
        m=re.search(r'\{\{sortname\|([^|}]+)\|([^|}]+)',row)
        name=(m.group(1)+' '+m.group(2)) if m else '?'
        st=re.search(r'^\s*!\s*(.*)$',row,re.M)
        state=st.group(1) if st else ''
        state=re.sub(r'\{\{ushr\|([^|}]+)\|([^|}]+)[^}]*\}\}',r'\1-\2',state)
        state=re.sub(r'\[\[[^|\]]*\|([^\]]*)\]\]',r'\1',state)
        txt=re.sub(r'<ref.*?(</ref>|/>)','',row,flags=re.S)
        txt=re.sub(r'\{\{efn\|(.*?)\}\}(?=\s*$|<br)',r'(\1)',txt,flags=re.S|re.M)
        txt=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',txt)
        txt=re.sub(r'\{\{small\|([^}]*)\}\}',r'\1',txt)
        txt=re.sub(r'\{\{party shading/\w+\}\}\s*\|','',txt)
        txt=re.sub(r'\{\{sortname\|([^|}]+)\|([^|}]+)[^}]*\}\}',r'\1 \2',txt)
        txt=re.sub(r'<br ?/?>','; ',txt,flags=re.I)
        lines=[x.strip().lstrip('|').strip() for x in txt.split('\n') if x.strip() and 'File:' not in x and not x.strip().startswith('!')]
        out.append({'section':h,'seat':state.strip(),'name':name,'cells':lines})
json.dump(out,open(sys.argv[2],'w'),indent=1)
for o in out: print(o['section'][:40],'|',o['seat'],'|',o['name'],'|',' / '.join(o['cells'][1:4])[:200])
print(len(out))
