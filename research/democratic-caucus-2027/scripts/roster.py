import json,re,csv,sys
S=sys.argv[1]
d=json.load(open(f'{S}/raw/dems.json'))
abbr={'Illinois':'IL','Iowa':'IA','Kansas':'KS','Maine':'ME','Michigan':'MI','Minnesota':'MN','New Hampshire':'NH','North Carolina':'NC','South Carolina':'SC','Texas':'TX'}
ros=[]
for o in d:
    sen=o['section'].startswith('Senate')
    seat=o['seat']
    seat=re.sub(r'<br.*','',seat)
    if sen: st=abbr[seat]; dist='SEN'
    else:
        m=re.match(r'([A-Z]{2})-(\w+)',seat) or re.match(r'(Arizona|Colorado) (\d+)',seat)
        st={'Arizona':'AZ','Colorado':'CO'}.get(m.group(1),m.group(1)); dist=m.group(2)
    cells=o['cells']
    ros.append(dict(name=o['name'],chamber='Senate' if sen else 'House',state=st,district=dist,
        how=cells[2] if sen else cells[1], background=(cells[3] if sen else cells[2]) if len(cells)>3 else '', status='Won (per Wikipedia new-members list, 11 Nov)'))
ros.append(dict(name='Sherrod Brown',chamber='Senate',state='OH',district='SEN',how='Yes; Defeated Jon Husted (R) in special election (takes office on certification, before Jan 3)',background='Former U.S. Senator 2007-2025; U.S. House; Ohio Secretary of State',status='Won'))
ros.append(dict(name='Mary Peltola',chamber='Senate',state='AK',district='SEN',how='Would flip; vs Dan Sullivan (R)',background='Former U.S. Representative (AK-AL) 2022-2025; Alaska House',status='PROVISIONAL - uncalled, RCV tabulation Nov 18'))
ros.append(dict(name='Scott Colom',chamber='Senate',state='MS',district='SEN',how='Would flip; vs Cindy Hyde-Smith (R)',background='District Attorney, 16th Circuit District of Mississippi',status='PROVISIONAL - uncalled, narrow lead'))
for r in ros:
    if (r['state'],r['district']) in [('NC','3'),('CO','4'),('MN','1'),('TN','4')]:
        r['status']='Listed as winner on Wikipedia; 270toWin listed as uncalled on Nov 10 - verify'
for i,r in enumerate(ros): r['id']=i+1
json.dump(ros,open(f'{S}/roster.json','w'),indent=1)
print(len(ros), sum(r['chamber']=='Senate' for r in ros))
