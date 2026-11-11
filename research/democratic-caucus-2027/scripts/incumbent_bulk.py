"""Assemble objective bulk data for every incumbent in the Jan-2027 Democratic roster.
Writes <S>/bulk/incumbents.json (list) and <S>/roster_full.json (everyone, incl. freshmen).
"""
import csv, json, re, sys, collections

S = sys.argv[1]
d = json.load(open(f'{S}/bulk/full_roster_raw.json'))
cur = {c['bioguide']: c for c in d['cur']}
cos = json.load(open(f'{S}/bulk/cosponsors.json'))
cauc = json.load(open(f'{S}/bulk/caucus_members.json'))

# Voteview members -> icpsr<->bioguide, dw-nominate
vv = {}
for ch in ('H', 'S'):
    for r in csv.DictReader(open(f'{S}/bulk/{ch}119_members.csv')):
        if r['bioguide_id']:
            vv.setdefault(r['bioguide_id'], {})[ch] = r
icpsr2bio = {}
for b, x in vv.items():
    for ch, r in x.items():
        icpsr2bio[(ch, r['icpsr'])] = b

KEY = {
    ('H', '22'): 'laken_riley', ('H', '11'): 'trans_sports_bill', ('H', '284'): 'nov2025_cr', ('H', '69'): 'mar2025_cr',
    ('H', '304'): 'denounce_socialism_2025', ('H', '649'): 'denounce_socialism_2026',
    ('S', '7'): 'laken_riley', ('S', '617'): 'nov2025_cr', ('S', '128'): 'mar2025_cr_cloture',
    ('H', '603'): 'end_israel_military_aid', ('S', '739'): 'block_israel_arms_sale_apr2026',
}
CAST = {'1': 'Yea', '2': 'Yea', '3': 'Yea', '4': 'Nay', '5': 'Nay', '6': 'Nay', '7': 'Present', '8': 'Present', '9': 'Not voting', '0': 'Not member'}
votes = collections.defaultdict(dict)
for ch in ('H', 'S'):
    for r in csv.DictReader(open(f'{S}/bulk/{ch}119_votes.csv')):
        k = KEY.get((ch, r['rollnumber']))
        if k:
            b = icpsr2bio.get((ch, r['icpsr']))
            if b:
                votes[b][k] = CAST.get(r['cast_code'], r['cast_code'])

BILLS = {
    'hr3069': 'Medicare for All Act (H.R.3069, 119th)', 's1506': 'Medicare for All Act (S.1506, 119th)',
    'hr8085': 'Ultra-Millionaire Tax Act of 2026 (H.R.8085)', 's4246': 'Ultra-Millionaire Tax Act of 2026 (S.4246)',
    'hr7123': 'Abolish ICE Act (H.R.7123)', 'hr7190': 'Melt ICE Act (H.R.7190)',
    'hr51': 'Washington, D.C. Admission Act (H.R.51, 119th)', 's51': 'Washington, D.C. Admission Act (S.51, 119th)',
    'hr3565': 'Block the Bombs to Israel Act (H.R.3565)',
    '118_hres319': 'Green New Deal resolution (H.Res.319, 118th)', '118_s1178': 'For the 99.5 Percent Act (S.1178, 118th)',
    '118_s1616': 'Judiciary Act of 2023 - Supreme Court expansion (S.1616, 118th)',
    '117_hr2584': 'Judiciary Act of 2021 - Supreme Court expansion (H.R.2584, 117th)',
    '117_s1141': 'Judiciary Act of 2021 - Supreme Court expansion (S.1141, 117th)',
    '117_hres332': 'Green New Deal resolution (H.Res.332, 117th)',
    '118_hr3422': 'Judiciary Act of 2023 - Supreme Court expansion (H.R.3422, 118th)',
}
MARKER_OF = {'hr3069': 'L3', 's1506': 'L3', 'hr8085': 'L1', 's4246': 'L1', 'hr7123': 'L9', 'hr7190': 'L9',
             'hr51': 'L11', 's51': 'L11', 'hr3565': 'L12', '118_hres319': 'L5', '118_s1178': 'L2', '118_s1616': 'L10',
             '117_hr2584': 'L10', '117_s1141': 'L10', '117_hres332': 'L5', '118_hr3422': 'L10'}
CAUCUS = {'Congressional_Progressive_Caucus': 'Congressional Progressive Caucus member',
          'New_Democrat_Coalition': 'New Democrat Coalition member', 'Blue_Dog_Coalition': 'Blue Dog Coalition member',
          'Problem_Solvers_Caucus': 'Problem Solvers Caucus member'}

# FEC
def load_fec(y):
    rows = {}
    for r in csv.DictReader(open(f'{S}/fec/cs{y}.csv', encoding='utf-8', errors='ignore')):
        rows[r['Cand_Id']] = r
    return rows
FEC = {y: load_fec(y) for y in (2026, 2024, 2022)}
def f(x):
    try: return float(x or 0)
    except Exception: return 0.0
def fec_for(c, chamber):
    want = 'S' if chamber == 'Senate' else 'H'
    best = None
    for y in (2026, 2024, 2022):
        for cid in c.get('fec', []):
            if cid.startswith(want) and cid in FEC[y]:
                r = FEC[y][cid]
                if f(r['Individual_Contribution']) > 0:
                    best = (y, r); break
        if best: break
    if not best: return None
    y, x = best
    ind = f(x['Individual_Contribution']); un = f(x['Individual_Unitemized_Contribution']); tot = f(x['Total_Receipt'])
    return dict(cycle=y, cand_id=x['Cand_Id'], through=x['Coverage_End_Date'], total_receipts=round(tot), indiv=round(ind),
                small_dollar_share=round(un / ind, 3) if ind else None,
                pac_share_of_receipts=round(f(x['Other_Committee_Contribution']) / tot, 3) if tot else None,
                self_funding=round(f(x['Cand_Contribution']) + f(x['Cand_Loan'])), transfers=round(f(x['Transfer_From_Other_Auth_Committee'])))

inc = []
for h in d['house'] + d['senate']:
    if not h.get('incumbent'): continue
    b = h['bioguide']; c = cur[b]
    ch = 'S' if h['chamber'] == 'Senate' else 'H'
    m = vv.get(b, {}).get(ch) or next(iter(vv.get(b, {}).values()), None)
    cosp = [k for k in BILLS if b in cos.get(k, {}).get('members', [])]
    rec = dict(
        name=c['name'], bioguide=b, chamber=h['chamber'], state=h['state'], district=h['district'],
        party=c['party'], provisional=h.get('provisional', False), status=h.get('status_text', ''),
        first_took_office=c['start_first'], senate_since=c.get('sen_since'), house_terms=c['nterms_house'], birthday=c.get('birthday'),
        dw_nominate_dim1=float(m['nominate_dim1']) if m and m['nominate_dim1'] else None,
        caucuses=[CAUCUS[k] for k, v in cauc.items() if b in v],
        cosponsored=[BILLS[k] for k in cosp], cosponsor_markers=sorted({MARKER_OF[k] for k in cosp}),
        key_votes=votes.get(b, {}), fec=fec_for(c, h['chamber']), wikipedia=c.get('wikipedia'), ballotpedia=c.get('ballotpedia'),
    )
    inc.append(rec)

# rank DW-NOMINATE within Democratic caucus per chamber (0 = most liberal, 1 = most moderate)
for ch in ('House', 'Senate'):
    xs = sorted([r for r in inc if r['chamber'] == ch and r['dw_nominate_dim1'] is not None], key=lambda r: r['dw_nominate_dim1'])
    for i, r in enumerate(xs):
        r['dw_pctile_moderate'] = round(i / max(1, len(xs) - 1), 3)
json.dump(inc, open(f'{S}/bulk/incumbents.json', 'w'), indent=1, ensure_ascii=False)
print('incumbents', len(inc), 'House', sum(r['chamber'] == 'House' for r in inc), 'Senate', sum(r['chamber'] == 'Senate' for r in inc))
print('no dw', [r['name'] for r in inc if r['dw_nominate_dim1'] is None])
print('no fec', [r['name'] for r in inc if not r['fec']])
cnt = collections.Counter(k for r in inc for k in r['cosponsor_markers']); print('marker counts', dict(cnt))
print('caucus counts', collections.Counter(k for r in inc for k in r['caucuses']))
kv = collections.Counter((r['chamber'], k) for r in inc for k, v in r['key_votes'].items() if v == 'Yea'); print('yea counts', dict(kv))
