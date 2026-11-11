"""Print items needing analyst review from final.json."""
import json, sys, re
S = sys.argv[1]
F = json.load(open(f'{S}/final.json'))
done = [o for o in F if not o.get('missing')]
print('== C7 evidence where it may be a LEFT-wing break with leadership (LI>=2 or mentions Schumer/Jeffries)')
for o in done:
    c7 = (o.get('C') or {}).get('C7') or {}
    if c7.get('v') == 1 and (o['LI'] >= 2 or re.search(r'schumer|jeffries|leadership', c7.get('e', ''), re.I)) and 'Broke with party leadership to vote' not in c7.get('e', ''):
        print(f"  {o['key']:8} {o['name'][:24]:24} LI{o['LI']} CI{o['CI']} c{o['category']} :: {c7.get('e','')[:200]}")
print('== Members with both left and centrist endorsements')
for o in done:
    if o.get('left_endorsements') and o.get('centre_endorsements'):
        print(f"  {o['key']:8} {o['name'][:24]:24} c{o['category']} L:{o['left_endorsements']} C:{o['centre_endorsements']}")
print('== Missing research')
print('  ', [o['name'] for o in F if o.get('missing')])
