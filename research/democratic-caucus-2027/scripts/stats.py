import json,sys,statistics as st,collections
S=sys.argv[1]; F=[o for o in json.load(open(f'{S}/final.json')) if not o.get('missing')]
C=collections.Counter
def dist(xs): c=C(o['category'] for o in xs); n=len(xs); return {k:(c[k],round(100*c[k]/n)) for k in (1,2,3,4)}, n
print('ALL',dist(F))
for ch in ('Senate','House'): print(ch,dist([o for o in F if o['chamber']==ch]))
print('new',dist([o for o in F if not o['incumbent']])); print('incumbent',dist([o for o in F if o['incumbent']]))
flips=[o for o in F if not o['incumbent'] and (o['how'].lower().startswith('yes') or 'would flip' in o['how'].lower())]
print('flips',dist(flips)); print('new non-flip',dist([o for o in F if not o['incumbent'] and o not in flips]))
print('confidence',C(o['confidence'] for o in F)); print('fit',C(o['fit'] for o in F))
for k in (1,2,3,4):
    xs=[o for o in F if o['category']==k]
    sd=[o['fec']['small_dollar_share'] for o in xs if o.get('fec') and o['fec'].get('small_dollar_share') is not None]
    print('cat',k,'n',len(xs),'median small$',round(st.median(sd),2) if sd else None,'clean',sum(o['fit']=='clean' for o in xs),'High',sum(o['confidence']=='High' for o in xs))
# rule path counts
print(C(o['rule'].split(':')[0] for o in F))
print('residual reasons',C(o['rule'].split(': ',1)[1] for o in F if o['rule'].startswith('residual')))
