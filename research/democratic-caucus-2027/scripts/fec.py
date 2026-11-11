import json,csv,sys,re,unicodedata
S=sys.argv[1]
ros=json.load(open(f'{S}/roster.json'))
rows=list(csv.DictReader(open(f'{S}/fec/cs26.csv',encoding='utf-8',errors='ignore')))
def norm(s): return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().upper()
def f(x):
    try: return float(x or 0)
    except: return 0.0
for r in ros:
    last=norm(r['name'].split()[-1]).replace('.','')
    if r['name'].endswith('Jr.'): last='SMITH'
    if r['name']=='Frederick Haynes III': last='HAYNES'
    cands=[x for x in rows if x['Cand_Office_St']==r['state'] and x['Cand_Party_Affiliation'] in ('DEM','DFL') and last.split('-')[0] in norm(x['Cand_Name'])
           and ((r['chamber']=='Senate' and x['Cand_Office']=='S') or (r['chamber']=='House' and x['Cand_Office']=='H'))]
    if r['chamber']=='House':
        dd='00' if r['district']=='AL' else r['district'].zfill(2)
        c2=[x for x in cands if x['Cand_Office_Dist']==dd]
        cands=c2 or cands
    if not cands: r['fec']=None; print('NO MATCH',r['name'],r['state'],r['district']); continue
    x=max(cands,key=lambda x:f(x['Total_Receipt']))
    ind=f(x['Individual_Contribution']); un=f(x['Individual_Unitemized_Contribution']); tot=f(x['Total_Receipt'])
    pac=f(x['Other_Committee_Contribution']); self_=f(x['Cand_Contribution'])+f(x['Cand_Loan'])
    r['fec']=dict(fec_name=x['Cand_Name'],cand_id=x['Cand_Id'],through=x['Coverage_End_Date'],total_receipts=round(tot),
        indiv=round(ind),small_dollar_share=round(un/ind,3) if ind else None,pac_share_of_receipts=round(pac/tot,3) if tot else None,
        self_funding=round(self_), transfers=round(f(x['Transfer_From_Other_Auth_Committee'])))
json.dump(ros,open(f'{S}/roster.json','w'),indent=1)
for r in ros:
    e=r.get('fec')
    if e: print(f"{r['state']}-{r['district']:4} {r['name'][:24]:24} {e['fec_name'][:28]:28} ${e['total_receipts']/1e6:6.2f}M small={e['small_dollar_share']} pac={e['pac_share_of_receipts']} self={e['self_funding']} thru {e['through']}")
