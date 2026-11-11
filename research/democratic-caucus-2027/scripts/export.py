"""Export final dataset to CSV + JSON for the repository."""
import csv, json, sys
S, OUT = sys.argv[1], sys.argv[2]
F = [o for o in json.load(open(f'{S}/final.json')) if not o.get('missing')]
cols = ['name', 'chamber', 'state', 'district', 'member_type', 'provisional', 'category', 'category_name', 'fit', 'confidence',
        'LI', 'CI', 'EPD', 'EO', 'small_dollar_share', 'dw_nominate_dim1', 'caucuses', 'left_endorsements', 'centre_endorsements',
        'rule', 'rationale', 'status']
with open(f'{OUT}/members.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for o in sorted(F, key=lambda o: (o['chamber'] != 'Senate', o['state'], o['district'].zfill(3))):
        w.writerow(dict(name=o['name'], chamber=o['chamber'], state=o['state'], district=o['district'],
            member_type='returning' if o['incumbent'] else 'new', provisional='PROVISIONAL' in (o.get('status') or ''),
            category=o['category'], category_name=o['category_name'], fit=o['fit'], confidence=o['confidence'],
            LI=o['LI'], CI=o['CI'], EPD=o['EPD'], EO=o['EO'], small_dollar_share=(o.get('fec') or {}).get('small_dollar_share'),
            dw_nominate_dim1=o.get('dw'), caucuses='; '.join(o.get('caucuses', [])),
            left_endorsements='; '.join(o.get('left_endorsements', [])), centre_endorsements='; '.join(o.get('centre_endorsements', [])),
            rule=o['rule'], rationale=o.get('rationale', ''), status=o.get('status', '')))
json.dump(F, open(f'{OUT}/members.json', 'w'), indent=1, ensure_ascii=False)
print('exported', len(F))
