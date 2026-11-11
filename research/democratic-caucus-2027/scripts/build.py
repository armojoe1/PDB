"""Build the artifact page from final.json + template.html + narrative.json.
Usage: python3 -I build.py <scratchpad dir> <out html path>
"""
import json, sys

S, OUT = sys.argv[1], sys.argv[2]
final = json.load(open(f'{S}/final.json'))
narr = json.load(open(f'{S}/narrative.json'))
tpl = open(f'{S}/template.html').read()

STATES = dict(AL='Alabama', AK='Alaska', AZ='Arizona', CA='California', CO='Colorado', CT='Connecticut', DC='District of Columbia',
              FL='Florida', GA='Georgia', GU='Guam', IL='Illinois', IN='Indiana', IA='Iowa', KS='Kansas', KY='Kentucky', ME='Maine',
              MD='Maryland', MA='Massachusetts', MI='Michigan', MN='Minnesota', MS='Mississippi', MO='Missouri', MT='Montana',
              NE='Nebraska', NV='Nevada', NH='New Hampshire', NJ='New Jersey', NY='New York', NC='North Carolina', OH='Ohio',
              PA='Pennsylvania', SC='South Carolina', TN='Tennessee', TX='Texas', UT='Utah', VA='Virginia', VI='Virgin Islands',
              WI='Wisconsin')
RETURNING = {'Hilda Solis', 'Melissa Bean', 'Colin Allred', 'Ben McAdams', 'Elaine Luria', 'Sherrod Brown', 'Mary Peltola'}

L_LABELS = {
    'L1': 'Wealth tax or very high top/corporate rates', 'L2': 'Lower estate-tax exemption / higher estate tax',
    'L3': 'Medicare for All / single payer', 'L4': 'Public ownership or democratic socialist identity',
    'L5': 'Green New Deal / fossil-fuel ban', 'L6': 'Aggressive anti-corporate measures',
    'L7': 'Contested trans-policy position', 'L8': 'Regulating online misinformation / hate speech',
    'L9': 'Defund police / abolish ICE', 'L10': 'Expand the Supreme Court',
    'L11': 'DC / Puerto Rico statehood or end Electoral College', 'L12': 'Gaza "genocide" / arms embargo on Israel',
}
C_LABELS = {
    'C2': 'Opposes Medicare for All; build on the ACA', 'C3': 'Fiscal restraint; no broad tax rises',
    'C4': 'Border security / enforcement', 'C5': 'Rejects "defund"; funds police',
    'C6': 'Breaks with progressive cultural positions', 'C7': 'Independent of party leadership / bipartisan record',
    'C8': 'Pro-growth: energy, permitting, housing supply, trade',
}


VOTE_LABELS = {'laken_riley': 'Laken Riley Act', 'trans_sports_bill': 'Protection of Women and Girls in Sports Act',
               'mar2025_cr': 'March 2025 GOP stopgap', 'mar2025_cr_cloture': 'March 2025 GOP stopgap (cloture)',
               'nov2025_cr': 'Nov 2025 bill ending the shutdown', 'denounce_socialism_2025': 'Resolution denouncing socialism (Nov 2025)',
               'denounce_socialism_2026': 'Resolution condemning socialism (Sep 2026)',
               'end_israel_military_aid': 'Amendment to end all US military aid to Israel (Jul 2026)',
               'block_israel_arms_sale_apr2026': 'Resolution blocking an arms sale to Israel (Apr 2026)'}


def trim_markers(d, labels):
    out = {}
    for k in labels:
        x = (d or {}).get(k) or {}
        try:
            v = int(x.get('v', 0))
        except Exception:
            v = 0
        if v:
            out[k] = {'v': v, 'e': x.get('e', ''), 'src': x.get('src', '')}
    return out

members = []
for o in final:
    if o.get('missing'):
        continue
    fec = o.get('fec')
    bio = o.get('bio') or {}
    members.append(dict(
        id=o['key'], name=o['name'], seat=(STATES.get(o['state'], o['state']) + ' · Senate') if o['chamber'] == 'Senate' else o['seat'].replace('-AL', ' at-large'), chamber=o['chamber'],
        state_name=STATES.get(o['state'], o['state']), flip=(not o.get('incumbent')) and (o['how'].strip().lower().startswith('yes') or 'would flip' in o['how'].lower()),
        provisional='PROVISIONAL' in (o.get('status') or '') or 'uncalled' in (o.get('call_status') or '').lower()[:40],
        returning=o['name'] in RETURNING,
        category=o['category'], confidence=o['confidence'], rule=o['rule'], fit=o['fit'],
        LI=o['LI'], CI=o['CI'], EPD=o['EPD'], EO=o['EO'], sd=(fec or {}).get('small_dollar_share'),
        rationale=o.get('rationale', ''), positions=o.get('notable_positions', [])[:6],
        L=trim_markers(o.get('L'), L_LABELS), C=trim_markers(o.get('C'), C_LABELS),
        left_endorsements=o.get('left_endorsements', []), centre_endorsements=o.get('centre_endorsements', []),
        outside=o.get('outside_support', [])[:10],
        epd_note=(o.get('EPD_detail') or {}).get('note', ''), eo_note=(o.get('EO_detail') or {}).get('note', ''),
        career=bio.get('career', ''), education=bio.get('education', ''), prior_office=bio.get('prior_office', ''),
        self_description=o.get('self_description', ''), primary_context=o.get('primary_context', ''),
        how=('' if o.get('incumbent') else o.get('how', '')), call_status=o.get('call_status', ''), fec=fec, sources=o.get('sources', [])[:14],
        incumbent=o.get('incumbent', False), caucuses=o.get('caucuses', []), cosponsored=o.get('cosponsored', []),
        key_votes=o.get('key_votes', {}), dw=o.get('dw'), dw_pct=o.get('dw_pct'),
    ))

data = dict(meta=narr['meta'], categories=narr['categories'], findings=narr['findings'], steps=narr['steps'],
            method_cards=narr['method_cards'], limits=narr['limits'], pending=narr['pending'], footer=narr['footer'],
            Llabels=L_LABELS, Clabels=C_LABELS, voteLabels=VOTE_LABELS, members=members)
blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
open(OUT, 'w').write(tpl.replace('/*__DATA__*/', blob))
print('wrote', OUT, len(blob) // 1024, 'KB data,', len(members), 'members')
