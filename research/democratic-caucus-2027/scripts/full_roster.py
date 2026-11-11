import json,re,sys,unicodedata,yaml
S=sys.argv[1]
def norm(s): return re.sub(r'[^a-z ]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip()
leg=yaml.safe_load(open(f'{S}/bulk/legislators-current.yaml'))
cur=[]
for p in leg:
    t=p['terms'][-1]
    cur.append(dict(bioguide=p['id']['bioguide'],name=p['name'].get('official_full') or (p['name']['first']+' '+p['name']['last']),
        first=p['name']['first'],last=p['name']['last'],nick=p['name'].get('nickname',''),type=t['type'],state=t['state'],district=t.get('district'),
        party=t['party'],start_first=p['terms'][0]['start'],nterms_house=sum(1 for x in p['terms'] if x['type']=='rep'),
        sen_since=min([x['start'] for x in p['terms'] if x['type']=='sen'],default=None),birthday=p['bio'].get('birthday'),
        fec=p['id'].get('fec',[]),icpsr=p['id'].get('icpsr'),wikipedia=p['id'].get('wikipedia'),ballotpedia=p['id'].get('ballotpedia')))
fresh=json.load(open(f'{S}/roster.json'))
fresh_names={norm(r['name']) for r in fresh}
res=json.load(open(f'{S}/raw/house_results.json'))
def find_cur(name,st,typ='rep'):
    n=norm(re.sub(r'\(.*?\)','',name)).split()
    if not n: return None
    last=n[-1]; first=n[0]
    c=[x for x in cur if x['type']==typ and x['state']==st and (norm(x['last']).split()[-1]==last or last in norm(x['last']))]
    c=[x for x in c if norm(x['first'])[:3]==first[:3] or norm(x['nick'] or '')[:3]==first[:3] or norm(x['name']).split()[0][:3]==first[:3]]
    return c[0] if c else None
house=[]
for x in res:
    w=x['winner']
    prov=False
    if not w:
        # provisional democratic leads
        if (x['st'],x['d']) in [('MN','1'),('NC','5'),('TN','4')]:
            w=[c for c in x['cands'] if '(Democratic' in c or '(DFL' in c][0]; prov=True
        elif (x['st'],x['d'])==('CA','4'):
            w='Mike Thompson (Democratic)'; prov=True
        else: continue
    if not re.search(r'\((Democratic|DFL)',w): continue
    name=re.sub(r'^[*\s]+','',re.sub(r'\s*\(.*$','',w)).strip()
    c=find_cur(name,x['st'])
    if not c and 're-elected' in x['status'].lower():
        last=norm(name).split()[-1]
        cc=[y for y in cur if y['type']=='rep' and y['state']==x['st'] and norm(y['last']).split()[-1]==last]
        c=cc[0] if len(cc)==1 else None
    house.append(dict(name=name,state=x['st'],district=x['d'],chamber='House',incumbent=bool(c),
        bioguide=c['bioguide'] if c else None,provisional=prov,status_text=x['status'][:120],is_fresh_listed=norm(name) in fresh_names))
# PR resident commissioner (not up in 2026)
for c in cur:
    if c['type']=='rep' and c['state']=='PR':
        house.append(dict(name=c['name'],state='PR',district='AL',chamber='House',incumbent=True,bioguide=c['bioguide'],provisional=False,status_text='Not up in 2026 (4-year term); caucuses with Democrats',is_fresh_listed=False))
inc=[h for h in house if h['incumbent']]; new=[h for h in house if not h['incumbent']]
print('House total',len(house),'incumbents',len(inc),'new',len(new))
print('NEW not in freshman roster:',[ (h['name'],h['state'],h['district']) for h in new if not h['is_fresh_listed']])
print('freshman roster not found among winners:',[r['name'] for r in fresh if r['chamber']=='House' and norm(r['name']) not in {norm(h['name']) for h in house}])
# Senate
sen_cur=[c for c in cur if c['type']=='sen' and c['party'] in ('Democrat','Independent')]
leaving={'Richard J. Durbin','Gary C. Peters','Tina Smith','Jeanne Shaheen'}
print('current D/I senators',len(sen_cur),[c['name'] for c in sen_cur if c['party']=='Independent'])
senate=[]
for c in sen_cur:
    if c['name'] in leaving or c['last'] in ('Durbin','Peters','Shaheen') or (c['last']=='Smith' and c['state']=='MN'): continue
    senate.append(dict(name=c['name'],state=c['state'],district='SEN',chamber='Senate',incumbent=True,bioguide=c['bioguide'],provisional=False,
        status_text='Klobuchar is governor-elect of Minnesota and will resign; an appointee will take the seat' if c['last']=='Klobuchar' else ('Independent, caucuses with Democrats' if c['party']=='Independent' else 'Continuing senator')))
print('continuing D/I senators',len(senate))
json.dump(dict(cur=cur,house=house,senate=senate),open(f'{S}/bulk/full_roster_raw.json','w'),indent=1)
