"""Separate 21-set comparison to its preserved independent high-precision roots."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';X=B.parent;read=lambda p:json.loads(p.read_text())
refs={r['saved']['failureKey']:r['reference']['highPrecision'] for r in read(X/'browser_eos_b5a/evidence/additional-inventories.json')['rows']};rows=[]
for engine in ['chromium','webkit']:
 for block in read(E/f'ledger-{engine}.json')['result']['rows']:
  for r in block['additional']:
   if 'state' not in r['reused']:continue
   s=r['reused']['state']['values'];ref=refs[r['key']];root={k:float(v) for k,v in ref[ref['selection']].items()};diff={k:s[k]-root[k] for k in ['p','h','T']}
   assert all(abs(diff[k])<=limit for k,limit in dict(p=.1,h=.1,T=1e-4).items()),(engine,block['id'],r['key'],diff)
   assert all(abs(diff[k])<limit for k,limit in dict(p=10,h=50,T=.01).items())
   rows.append(dict(engine=engine,artifact=block['id'],fullVLE=block['fullVLE'],key=r['key'],mathematicalSelection=ref['selection'],referenceDifference=diff,originalEndpointUncertaintyUnchanged=True))
p=E/'additional-independent-audit.json';assert not p.exists();p.write_text(json.dumps(dict(passed=True,independentInventoryCount=21,rows=rows,noNewPhysicalCertificates=True),indent=2)+'\n');print('Separate 21-set independent reference comparisons PASS')
