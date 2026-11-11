"""Merge roster + research + bulk data, compute rubric scores, classify every member.
Usage: python3 -I score.py <scratchpad dir>   -> writes <S>/final.json, prints summary
"""
import glob, json, re, sys, collections

S = sys.argv[1]

# ---------- roster ----------
roster = []
for r in json.load(open(f'{S}/roster.json')):           # freshmen (int ids 1..93)
    r = dict(r); r['key'] = str(r['id']); r['incumbent'] = False; roster.append(r)
for r in json.load(open(f'{S}/bulk/incumbents.json')):  # incumbents (bioguide)
    r = dict(r); r['key'] = r['bioguide']; r['incumbent'] = True
    r['how'] = 'Continuing member'; r['background'] = ''
    roster.append(r)
roster.append(dict(key='NEW-NC5', name='Chuck Hubbard', chamber='House', state='NC', district='5', incumbent=False,
                   how='Would flip; vs Virginia Foxx (R)', background='', status='PROVISIONAL - uncalled; led Foxx by ~325 votes, recount likely', fec=None))
# CA-4: challenger Eric Jones (D) led incumbent Mike Thompson (D); count Jones, keep Thompson as the alternate
roster.append(dict(key='NEW-CA4', name='Eric Jones', chamber='House', state='CA', district='4', incumbent=False,
                   how='Leading incumbent Mike Thompson (D) in a Democrat-vs-Democrat race', background='',
                   status='PROVISIONAL - uncalled; led Thompson 52.1-47.9 on 10 Nov (about 75% counted)',
                   fec=dict(fec_name='JONES, ERIC', through='10/14/2026', total_receipts=18060000, indiv=3200000, small_dollar_share=0.004,
                            pac_share_of_receipts=None, self_funding=14860000, transfers=0)))
ALTERNATES = {r['key'] for r in roster if r['name'] == 'Mike Thompson' and r['state'] == 'CA'}

# ---------- research ----------
research = {}
for fn in sorted(glob.glob(f'{S}/research/batch_*.json')) + sorted(glob.glob(f'{S}/research/inc_*.json')):
    try:
        for m in json.load(open(fn)):
            research[str(m['id'])] = m
    except Exception as e:
        print('WARN could not load', fn, e)
try:
    endo = json.load(open(f'{S}/research/endorsements.json'))
except Exception:
    endo = {'orgs': {}, 'by_member': {}}
try:
    overrides = json.load(open(f'{S}/overrides.json'))
except Exception:
    overrides = {}
try:
    status_ov = json.load(open(f'{S}/status_overrides.json'))
except Exception:
    status_ov = {}
try:  # analyst corrections to individual marker codings: {key: {"C7": {"v": 0, "e": "why"}}}
    marker_ov = json.load(open(f'{S}/marker_overrides.json'))
except Exception:
    marker_ov = {}


def norm(s):
    return re.sub(r'[^a-z0-9 ]', '', (s or '').lower())


def central_endorsements(name):
    out = []
    n = norm(name).split()
    if not n: return out
    for k, v in endo.get('by_member', {}).items():
        kn = norm(k.split('(')[0])
        if kn.strip() == ' '.join(n) or (n[-1] in kn.split() and n[0][:3] == kn.split()[0][:3] if kn.split() else False):
            out += v
    return out

LEFT_ORGS = [(r'justice democrats', 2), (r'\bdsa\b|democratic socialists', 2), (r'working families|\bwfp\b', 1),
             (r'our revolution', 1), (r'sunrise', 1), (r'bernie|sanders|fighting oligarchy', 1),
             (r'ocasio|\baoc\b|courage to change', 1), (r'progressive caucus|\bcpc\b', 1),
             (r'progressive change|pccc', 1), (r'leaders we deserve|hogg', 1)]
CENTER_ORGS = [(r'blue dog', 2), (r'new dem', 1), (r'welcome ?pac|welcomepac', 1), (r'majority democrats', 1),
               (r'problem solvers|no labels', 1), (r'third way', 1)]
NEG = re.compile(r'\b(not|no|declined|rejected|opposed|against|withdrew|rescinded)\b')


def org_points(names, table, cap):
    hits = {}; labels = []
    for n in names:
        nl = n.lower()
        if NEG.search(nl): continue
        for rx, pts in table:
            if re.search(rx, nl):
                hits[rx] = max(hits.get(rx, 0), pts)
                if n not in labels: labels.append(n)
    return min(cap, sum(hits.values())), labels


def mv(d, code):
    x = (d or {}).get(code) or {}
    try: return int(x.get('v', 0))
    except Exception: return 0

L_POINTS = {f'L{i}': 1 for i in range(1, 13)}; L_POINTS['L4'] = 2
C_CODES = [f'C{i}' for i in range(2, 9)]
CAT_NAMES = {1: 'Ideological left', 2: 'Inexperienced & base-dependent', 3: 'Credentialed but disengaged', 4: 'Clinton-style centrist'}
BILL_URL = {
    'Medicare for All Act (H.R.3069, 119th)': 'https://www.congress.gov/bill/119th-congress/house-bill/3069/cosponsors',
    'Medicare for All Act (S.1506, 119th)': 'https://www.congress.gov/bill/119th-congress/senate-bill/1506/cosponsors',
    'Ultra-Millionaire Tax Act of 2026 (H.R.8085)': 'https://www.congress.gov/bill/119th-congress/house-bill/8085/cosponsors',
    'Ultra-Millionaire Tax Act of 2026 (S.4246)': 'https://www.congress.gov/bill/119th-congress/senate-bill/4246/cosponsors',
    'Abolish ICE Act (H.R.7123)': 'https://www.congress.gov/bill/119th-congress/house-bill/7123',
    'Melt ICE Act (H.R.7190)': 'https://www.congress.gov/bill/119th-congress/house-bill/7190/cosponsors',
    'Washington, D.C. Admission Act (H.R.51, 119th)': 'https://www.congress.gov/bill/119th-congress/house-bill/51/cosponsors',
    'Washington, D.C. Admission Act (S.51, 119th)': 'https://www.congress.gov/bill/119th-congress/senate-bill/51/cosponsors',
    'Block the Bombs to Israel Act (H.R.3565)': 'https://www.congress.gov/bill/119th-congress/house-bill/3565/cosponsors',
    'Green New Deal resolution (H.Res.319, 118th)': 'https://www.congress.gov/bill/118th-congress/house-resolution/319/cosponsors',
    'For the 99.5 Percent Act (S.1178, 118th)': 'https://www.congress.gov/bill/118th-congress/senate-bill/1178/cosponsors',
    'Judiciary Act of 2023 - Supreme Court expansion (S.1616, 118th)': 'https://www.congress.gov/bill/118th-congress/senate-bill/1616/cosponsors',
    'Judiciary Act of 2021 - Supreme Court expansion (H.R.2584, 117th)': 'https://www.congress.gov/bill/117th-congress/house-bill/2584/cosponsors',
    'Judiciary Act of 2021 - Supreme Court expansion (S.1141, 117th)': 'https://www.congress.gov/bill/117th-congress/senate-bill/1141/cosponsors',
    'Green New Deal resolution (H.Res.332, 117th)': 'https://www.congress.gov/bill/117th-congress/house-resolution/332/cosponsors',
    'Judiciary Act of 2023 - Supreme Court expansion (H.R.3422, 118th)': 'https://www.congress.gov/bill/118th-congress/house-bill/3422/cosponsors',
}
MARKER_OF = {'Medicare for All': 'L3', 'Ultra-Millionaire': 'L1', 'Abolish ICE': 'L9', 'Melt ICE': 'L9', 'Admission Act': 'L11',
             'Block the Bombs': 'L12', 'Green New Deal': 'L5', '99.5': 'L2', 'Judiciary Act': 'L10'}
VOTE_URL = {'H': 'https://voteview.com/rollcall/RH119{:04d}', 'S': 'https://voteview.com/rollcall/RS119{:04d}'}
VOTES = {  # key -> (marker, chamber, rollnumber, label)
    ('House', 'laken_riley'): ('C4', 'H', 22, 'Voted for the Laken Riley Act (Jan 2025)'),
    ('Senate', 'laken_riley'): ('C4', 'S', 7, 'Voted for the Laken Riley Act (Jan 2025)'),
    ('House', 'trans_sports_bill'): ('C6', 'H', 11, 'Voted for the Protection of Women and Girls in Sports Act (Jan 2025)'),
    ('House', 'nov2025_cr'): ('C7', 'H', 284, 'Broke with party leadership to vote for the Nov 2025 bill ending the shutdown'),
    ('Senate', 'nov2025_cr'): ('C7', 'S', 617, 'Broke with party leadership to vote for cloture on the Nov 2025 bill ending the shutdown'),
    ('House', 'mar2025_cr'): ('C7', 'H', 69, 'Broke with party leadership to vote for the March 2025 GOP stopgap'),
    ('House', 'end_israel_military_aid'): ('L12', 'H', 603, 'Voted for the July 2026 Massie amendment to end all US military aid to Israel'),
}


def merge_bulk(r, L, C, l_names, c_names):
    L = {k: dict(v) for k, v in (L or {}).items()}; C = {k: dict(v) for k, v in (C or {}).items()}
    for bill in r.get('cosponsored', []):
        mk = next((m for k, m in MARKER_OF.items() if k in bill), None)
        if mk and mv(L, mk) != 1:
            L[mk] = {'v': 1, 'e': f'Sponsored/co-sponsored the {bill}.', 'src': BILL_URL.get(bill, '')}
    for cauc in r.get('caucuses', []):
        if 'Progressive' in cauc: l_names.append('Congressional Progressive Caucus (member)')
        elif 'New Democrat' in cauc: c_names.append('New Democrat Coalition (member)')
        elif 'Blue Dog' in cauc: c_names.append('Blue Dog Coalition (member)')
        elif 'Problem Solvers' in cauc: c_names.append('Problem Solvers Caucus (member)')
    for (ch, key), (mk, cc, rn, label) in VOTES.items():
        tgt = L if mk.startswith('L') else C
        if r['chamber'] == ch and r.get('key_votes', {}).get(key) == 'Yea' and mv(tgt, mk) != 1:
            tgt[mk] = {'v': 1, 'e': label + '.', 'src': VOTE_URL[cc].format(rn)}
    return L, C

out = []
for r in roster:
    m = research.get(r['key'])
    rec = dict(key=r['key'], name=r['name'], chamber=r['chamber'], state=r['state'], district=r['district'],
               seat=f"{r['state']}-{r['district']}", incumbent=r['incumbent'], how=r.get('how', ''),
               status=status_ov.get(r['key'], r.get('status', '')), fec=r.get('fec'), dw=r.get('dw_nominate_dim1'), dw_pct=r.get('dw_pctile_moderate'),
               caucuses=r.get('caucuses', []), cosponsored=r.get('cosponsored', []), key_votes=r.get('key_votes', {}),
               first_took_office=r.get('first_took_office'))
    if not m:
        rec['missing'] = True; out.append(rec); continue
    l_names = list(dict.fromkeys((m.get('L13_endorsements') or []) + central_endorsements(r['name'])))
    c_names = list(dict.fromkeys(m.get('C1_endorsements') or []))
    for n in list(l_names):
        if any(re.search(rx, n.lower()) for rx, _ in CENTER_ORGS):
            l_names.remove(n); c_names.append(n)
    L, C = m.get('L', {}), m.get('C', {})
    for code, val in marker_ov.get(r['key'], {}).items():
        tgt = L if code.startswith('L') else C
        tgt = dict(tgt); tgt[code] = dict(tgt.get(code) or {}, v=val['v'], e=val.get('e', (tgt.get(code) or {}).get('e', '')), src=val.get('src', (tgt.get(code) or {}).get('src', '')))
        if code.startswith('L'): L = tgt
        else: C = tgt
    if r['incumbent']:
        L, C = merge_bulk(r, L, C, l_names, c_names)
    l13, l13_labels = org_points(l_names, LEFT_ORGS, 3)
    c1, c1_labels = org_points(c_names, CENTER_ORGS, 3)
    li_parts = {k: (p if mv(L, k) == 1 else 0) for k, p in L_POINTS.items()}
    LI = sum(li_parts.values()) + l13
    ci_parts = {k: (1 if mv(C, k) == 1 else 0) for k in C_CODES}
    CI = sum(ci_parts.values()) + c1
    epd = dict(m.get('EPD', {}) or {}); eo = dict(m.get('EO', {}) or {})
    g = lambda d, k: int(d.get(k, 0) or 0)
    if r['incumbent']:
        if r['chamber'] == 'Senate' or (r.get('first_took_office') or '9999') < '2025-01-01':
            epd['office'] = 3
        else:
            epd['office'] = max(2, g(epd, 'office'))
    # Normalise engagement scoring across batches: a 0 counts only when avoidance is documented;
    # missing evidence is neutral (1), per the brief.
    note = (eo.get('note') or '')
    documented_skip = re.search(r'declin|skip|refus|pull(ed)? out|no-show|did not (attend|participate|show|debate)|'
                                r'didn.t debate|avoid|duck|withdrew|turned down|no debates? (were )?held because|sat out', note, re.I)
    if g(eo, 'debate') == 0 and not documented_skip:
        eo['debate'] = 1; eo['note'] = note + ' [debate score set to neutral 1: no documented refusal]'
    documented_quiet = re.search(r'avoid|no (unscripted|press|interviews|town halls?)|declin\w* (interview|press)|scripted|rarely|refus', note, re.I)
    if g(eo, 'media') == 0 and not documented_quiet:
        eo['media'] = 1; eo['note'] = eo['note'] + ' [media score set to neutral 1: no documented avoidance]'
    EPD = g(epd, 'office') + g(epd, 'cred') + g(epd, 'policy')
    EO = g(eo, 'debate') + g(eo, 'media') + g(eo, 'substance')
    fit = 'clean'
    if LI >= 6:
        cat, rule = 1, 'LI ≥ 6'
        if CI >= 5: fit = 'mixed (also CI ≥ 5)'
    elif CI >= 5 and LI <= 3:
        cat, rule = 4, 'CI ≥ 5 and LI ≤ 3'
    elif EPD <= 3:
        cat, rule = 2, 'not 1/4; EPD ≤ 3'
    elif EO <= 2:
        cat, rule = 3, 'not 1/4; EPD ≥ 4 and EO ≤ 2'
    else:
        if CI >= 3 and CI >= LI:
            cat, why = 4, 'CI ≥ 3 and CI ≥ LI: leans centrist'
        elif LI >= 4 and LI > CI:
            cat, why = 1, 'LI ≥ 4 and LI > CI: leans left'
        elif r['incumbent'] and r.get('dw_pctile_moderate') is not None and r['dw_pctile_moderate'] >= 2/3 and CI >= 1 and LI <= 2:
            cat, why = 4, 'weak position evidence, some centrist markers, and a voting record (DW-NOMINATE) in the most moderate third of chamber Democrats'
        else:
            cat, why = 3, 'no clear ideological signal either way: credentialed party-liner' + (' (votes with the caucus; DW-NOMINATE not in the most moderate third)' if r['incumbent'] and r.get('dw_pctile_moderate') is not None else '')
        rule = 'residual (credentialed and engaged): ' + why
        fit = 'imperfect fit'
    n_ev = sum(1 for k in L_POINTS if mv(L, k) != 0) + sum(1 for k in C_CODES if mv(C, k) != 0) + len(l13_labels) + len(c1_labels)
    if cat == 1: margin = LI - 6
    elif cat == 4: margin = min(CI - 5, 3 - LI)
    elif cat == 2: margin = 3 - EPD
    else: margin = 2 - EO
    conf = 'High' if (n_ev >= 5 and margin >= 1) else ('Medium' if n_ev >= 3 else 'Low')
    if cat == 2:  # base-dependence modifies confidence in the "follows the base" call
        sd = ((r.get('fec') or {}).get('small_dollar_share') or 0)
        base_dep = sd >= 0.40 or l13 > 0
        if base_dep and conf == 'Medium': conf = 'High'
        if not base_dep and sd < 0.20: conf = {'High': 'Medium', 'Medium': 'Low'}.get(conf, conf)
    eo_unverified = bool(re.search(r'unverified|not verified|could not (confirm|verify)|no (debate )?record found', eo.get('note', '') or '', re.I))
    if cat == 3 and eo_unverified:
        conf = 'Low'
        if fit == 'clean': fit = 'engagement evidence partly unverified'
    if fit != 'clean': conf = 'Low'
    ov = overrides.get(r['key'])
    if ov:
        rec['rule_category'] = cat
        cat = ov['category']; rule = 'analyst override: ' + ov['note']; conf = ov.get('confidence', conf); fit = ov.get('fit', fit)
    rec.update(dict(category=cat, category_name=CAT_NAMES[cat], rule=rule, fit=fit, confidence=conf,
        agent_category=m.get('suggested_category'), LI=LI, CI=CI, EPD=EPD, EO=EO, li_parts=li_parts, ci_parts=ci_parts,
        l13=l13, c1=c1, left_endorsements=l13_labels, centre_endorsements=c1_labels, L=L, C=C, EPD_detail=epd, EO_detail=eo,
        bio=m.get('bio', {}), self_description=m.get('self_description', ''), primary_context=m.get('primary_context', ''),
        call_status=m.get('call_status', ''), outside_support=m.get('outside_support', []),
        notable_positions=m.get('notable_positions', []), rationale=m.get('rationale', ''), sources=m.get('sources', [])))
    out.append(rec)

for o in out:
    if o['key'] in ALTERNATES: o['alternate'] = True
alts = [o for o in out if o.get('alternate')]
json.dump(alts, open(f'{S}/alternates.json', 'w'), indent=1, ensure_ascii=False)
out = [o for o in out if not o.get('alternate')]
json.dump(out, open(f'{S}/final.json', 'w'), indent=1, ensure_ascii=False)
done = [o for o in out if not o.get('missing')]
print('researched', len(done), 'of', len(out))
for ch in ('Senate', 'House'):
    for inc in (False, True):
        sub = [o for o in done if o['chamber'] == ch and o['incumbent'] == inc]
        print(f"{ch:6} {'incumbent' if inc else 'new':9}", dict(sorted(collections.Counter(o['category'] for o in sub).items())), len(sub))
print('all', dict(sorted(collections.Counter(o['category'] for o in done).items())))
if '-v' in sys.argv:
    for o in done:
        flag = '' if o['agent_category'] == o['category'] else f" <-- agent {o['agent_category']}"
        sd = (o['fec'] or {}).get('small_dollar_share')
        print(f"{o['seat']:7} {o['name'][:26]:26} c{o['category']} {o['confidence'][0]} LI{o['LI']:3} CI{o['CI']:3} EPD{o['EPD']} EO{o['EO']} sd {sd} dw {o.get('dw')} {o['fit'] if o['fit']!='clean' else ''}{flag}")
