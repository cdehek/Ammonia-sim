"""Seal prerequisite decisions only after both actual-browser reviews succeed."""
import gzip,json,struct
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def decode(x):
 if isinstance(x,list):return list(map(decode,x))
 if isinstance(x,dict):
  if set(x)=={'f64'}:return struct.unpack('>d',bytes.fromhex(x['f64']))[0]
  if set(x)=={'undefined'}:return None
  return {k:decode(v) for k,v in x.items()}
 return x
summary={}
for browser in ['chromium','webkit']:
 d=json.loads(gzip.decompress((E/f'review-{browser}.json.gz').read_bytes()));assert d['passed'];r=d['results']
 assert r['hardening']['passed'] and r['c1']['passed'] and r['regressions']['exact'] and r['additional']['exact']
 cases=[{'name':x['name'],'exact':True,'stop':decode(x['state']).get('stop')} for x in r['regressions']['candidate']['cases']]
 cases += [{'name':x['name'],'exact':True,'stop':x['stop']} for x in r['additional']['candidate']['rows']]
 summary[browser]={'version':d['version'],'fixtures':{f:{'exact':r[f]['exact'],'savedB9CMatch':r[f]['savedB9CMatch'],'hash':r[f]['candidate']['scienceHash'],'work':r[f]['candidate']['work']} for f in ['cold','warm']},'cases':cases,'hardening':r['hardening'],'C1':True}
assert json.loads((E/'source-review.json').read_text())['passed']
(E/'review-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
gates={'gate0':'PASS','gate1':'HARDENING PASS','gate2':'PASS','gate3':'PASS — field mapping VERIFIED; whole-plant fields unavailable','gate4':'PASS — served research contract; offline workstation packaging OPEN','prototypeAuthorized':True,'scope':'isolated HTTP-served read-only five-section research; no workstation integration','browsers':list(summary)}
(E/'gates-1-4.json').write_text(json.dumps(gates,indent=2)+'\n')
print(json.dumps(gates,indent=2))
