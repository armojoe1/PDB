import json,re,sys
S=sys.argv[1]
d=json.load(open(f'{S}/bulk/full_roster_raw.json'))
cur=[c for c in d['cur'] if c['party'] in ('Democrat','Independent')]
spec={'Congressional_Progressive_Caucus':(r'== Membership ==',r'\n== (?!Membership)'),
      'New_Democrat_Coalition':(r'=== Current members ===',r'\n===? (?!Current)'),
      'Blue_Dog_Coalition':(r'=== Current members ===',r'\n===? (?!Current)'),
      'Problem_Solvers_Caucus':(r'== Membership ==',r'=== Former members ===')}
out={}
for f,(a,b) in spec.items():
    t=open(f'{S}/bulk/caucus/{f}.wiki').read()
    i=re.search(a,t).start(); rest=t[i+5:]; m=re.search(b,rest); sec=rest[:m.start()] if m else rest
    links=set(x.strip().replace('_',' ') for x in re.findall(r'\[\[([^|\]#]+)',sec))
    sortn=set(f"{x[0].strip()} {x[1].strip()}" for x in re.findall(r'\{\{sortname\|([^|}]+)\|([^|}]+)',sec))
    pairs=[(x[0].strip().lower(),x[1].strip().lower()) for x in re.findall(r'\{\{sortname\|([^|}]+)\|([^|}]+)',sec)]
    dabs=set(x.strip() for x in re.findall(r'\{\{sortname\|[^|}]+\|[^|}]+\|([^|}=]+)\}\}',sec))
    mem=[]
    for c in cur:
        w=(c.get('wikipedia') or '').replace('_',' ')
        if w and (w in links or w in dabs): mem.append(c['bioguide']); continue
        fn=f"{c['first']} {c['last']}"
        if fn in sortn or (c.get('nick') and f"{c['nick']} {c['last']}" in sortn): mem.append(c['bioguide']); continue
        cl=c['last'].lower(); cf={c['first'][:3].lower(), (c.get('nick') or '')[:3].lower(), c['name'].split()[0][:3].lower()}
        cf |= {'C001110': {'lou'}, 'S001156': {'lin'}}.get(c['bioguide'], set())
        NICK = {'tho': {'tom'}, 'wil': {'bil', 'wil'}, 'rob': {'bob', 'bob'}, 'jam': {'jim'}, 'jos': {'joe'}, 'ric': {'dic', 'ric'},
                'don': {'don'}, 'hen': {'han'}, 'edw': {'ed', 'ed '}, 'ste': {'ste'}, 'chr': {'chr'}, 'mic': {'mik'}, 'pat': {'pat'},
                'tim': {'tim'}, 'nic': {'nik'}, 'gil': {'gil'}, 'her': {'her'}, 'mar': {'mar'}, 'jen': {'jen'}, 'vic': {'vic'}}
        for x in list(cf): cf |= NICK.get(x, set())
        if any(l==cl and f[:3] in cf for f,l in pairs): mem.append(c['bioguide'])
    out[f]=mem
    print(f,len(mem),'| links in section',len(links))
json.dump(out,open(f'{S}/bulk/caucus_members.json','w'),indent=1)
