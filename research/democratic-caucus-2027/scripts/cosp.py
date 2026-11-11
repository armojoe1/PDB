import xml.etree.ElementTree as ET,glob,json,sys,os
S=sys.argv[1]; out={}
for f in sorted(glob.glob(f'{S}/bulk/cosp/BS_*.xml')):
    b=os.path.basename(f)[3:-4]
    r=ET.parse(f).getroot().find('bill')
    title=r.findtext('title')
    spons=[x.findtext('bioguideId') for x in r.findall('sponsors/item')]
    cos=[(x.findtext('bioguideId'),x.findtext('sponsorshipWithdrawnDate')) for x in r.findall('cosponsors/item')]
    ids=spons+[c for c,w in cos if not w]
    out[b]=dict(title=title,members=ids)
    print(b,len(ids),title[:80])
json.dump(out,open(f'{S}/bulk/cosponsors.json','w'),indent=1)
