"""Canonical inventory at every unique invalid base OR signed-probe coordinate."""
import json,os,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,inventory,save
def read(n):return json.loads((E/n).read_text())
def snapshots(rows):
 out={}
 for r in rows:
  for x in [r['base']]+[q['output'] for q in r['probes'] if 'output'in q]:out[tuple(x['inputBits'])]=x
 return out
old=snapshots(read('native-controlA.json')['rows']);new=snapshots(read('native-candidateB.json')['rows']);rows=[];libs={label:Backend('/workspace/b4c-libs/'+label+'.so') for label in ['controlA','candidateB']}
for bits,a in old.items():
 if not 1<a['PH']['values']['Q']<=1+1e-9:continue
 b=new[bits];p,h=a['p'],a['h'];canonical={}
 for label,x in [('controlA',a),('candidateB',b)]:
  s=x['PH']['values'];canonical[label]=inventory(libs[label],p,h,s['rho'],s['T'])
 assert canonical['candidateB']['canonicalPass']
 rows.append(dict(inputBits=bits,p=p,h=h,independentPhysicalPhase=a['physicalPhase'],saturation=a['saturation'],hMinusHg=a['hMinusHg'],rawQuality=a['rawQuality'],reference=a.get('reference'),before=a,after=b,canonical=canonical))
save(E/'upper-quality-native-before-after.json',dict(rows=rows,allCandidateCanonicalPass=True,endpointUncertaintyNotLabeledProvenVapor=True))
print(len(rows),'unique native invalid base/probe inventories; all candidate canonical pass')
