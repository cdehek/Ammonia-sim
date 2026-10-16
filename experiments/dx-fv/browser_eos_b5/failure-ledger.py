"""Derive original failure identities from saved results, without count constants."""
import json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));H=B.parent/'browser_eos_b4c/evidence'
inputs=json.loads((E/'fixed-inputs.json').read_text());refs={r['key']:r for r in json.loads((E/'independent-fixed-references.json').read_text())['rows']};mp={r['key']:r for r in json.loads((E/'high-precision-references.json').read_text())['rows']};rows=[]
for runtime,file in [('native-full-VLE','native-candidateB-full-vle.json'),('chromium','chromium-candidateB-focused.json'),('webkit','webkit-candidateB-focused.json')]:
 for r in json.loads((H/file).read_text())['rows']:
  q=r.get('request',r)
  if q['args'][0]!=3500000:continue
  v=r.get('inventories',{}).get('C',{});err=v.get('error')or v.get('acceptedAdapterError')
  if not err:continue
  matches=[x for x in inputs if x['id']==q['id']and x['input']['bits']==v['input']['bits']and (x['origin']=='B4C-current-PH'and x['fullVLE'] if runtime=='native-full-VLE' else x['origin']==runtime+'-candidateB')]
  assert len(matches)==1,(runtime,q['id'],matches);fixed=matches[0];ref=refs[fixed['key']]['reference'];hp=mp[fixed['key']]['reference'];base=r['base'];ph=base['PH']if runtime=='native-full-VLE'else dict(values=base['state'],bits={})
  rows.append(dict(failureKey=runtime+'/'+q['id'],runtime=runtime,id=q['id'],originalPHInput=q['args'],originalInputBits=q.get('inputBits'),originalPH=ph,fixedKey=fixed['key'],fixedInput=fixed['input'],originalError=err,originalRecovery=v,independentReference=ref,highPrecisionReference=hp))
out=dict(rows=rows,counts={k:sum(x['runtime']==k for x in rows)for k in ['native-full-VLE','chromium','webkit']},note='Counts are derived from preserved candidate C results, not expected totals. Historical A/B failure inventories remain in fixed-inputs.json.')
(E/'original-failures.json').write_text(json.dumps(out,indent=2)+'\n');print(out['counts'])
