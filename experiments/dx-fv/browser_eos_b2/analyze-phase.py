import os
import json,hashlib,struct
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True);out={'builds':[],'native':[]}
inputs=json.loads((B/'inputs.json').read_text());expected={q['id']:q for q in inputs}
for f in sorted(E.glob('*-phase-*.json')):
 d=json.loads(f.read_text());samples=[];ratios=[];errors=[];cross=0;exclusions=0
 for q in d['rows']:
  assert q['args']==expected[q['id']]['args'] and q['inputBits']==expected[q['id']]['inputBits']
  if q.get('error'):errors.append({'id':q['id'],'error':q['error']})
  if q.get('base'):samples.append(q['base'])
  for p in q['probes']:
   if p.get('error'):errors.append({'id':q['id'],'axis':p['axis'],'step':p['step'],'error':p['error']})
   if p.get('output'):samples.append(p['output'])
   cross+=bool(p.get('crossesPhase'));exclusions+=('output' in p and 'ratio' not in p)
   if 'ratio' in p:ratios.append({'id':q['id'],'axis':p['axis'],'step':p['step'],'ratio':p['ratio']})
 for s in samples:assert s['inputBits']==[struct.pack('>d',x).hex() for x in [s['p'],s['h']]]
 regression=next(q for q in d['rows'] if q['id']=='B1-vapor-regression')
 item=dict(file=f.name,browser=d['browser'],build=d['build'],rows=len(d['rows']),samples=len(samples),errors=errors,phaseCrossingProbes=cross,homogeneousDerivativeExclusions=exclusions,phaseCounts={str(k):sum(s['phase']==k for s in samples) for k in sorted({s['phase'] for s in samples})},maximumPressureResidualPa=max(abs(s['pResidual']) for s in samples),maximumEnthalpyResidualJkg=max(abs(s['hResidual']) for s in samples),largestPressureResidual=max(samples,key=lambda s:abs(s['pResidual'])),largestEnthalpyResidual=max(samples,key=lambda s:abs(s['hResidual'])),descriptiveRatiosBeyondOnePercent=[r for r in ratios if abs(r['ratio']-1)>.01],ratioRange=[min(r['ratio'] for r in ratios),max(r['ratio'] for r in ratios)],regression=dict(base=regression['base'],probes=regression['probes']),linearMemory=d['linearMemory'],init=d['init'])
 out['builds'].append(item)
for f in sorted(E.glob('native-*.json')):
 d=json.loads(f.read_text());audits=[s for a in d['browserAudits'] for s in a['states']]
 out['native'].append(dict(file=f.name,version=d['version'],git=d['git'],rows=len(d['rows']),auditedBrowserFiles=len(d['browserAudits']),auditedStates=len(audits),maxNativeMinusBrowserPressurePa=max(abs(s['nativePMinusBrowser']) for s in audits if 'error' not in s),maxNativeMinusBrowserEnthalpyJkg=max(abs(s['nativeHMinusBrowser']) for s in audits if 'error' not in s),errors=[s for s in audits if 'error' in s]))
out['engineEquality']={}
for build in ['official8','build30','build44','official72']:
 a=json.loads((E/f'chromium-phase-{build}.json').read_text());b=json.loads((E/f'webkit-phase-{build}.json').read_text());out['engineEquality'][build]=a['rows']==b['rows']
out['controlEqualsOfficial']={name:json.loads((E/f'{name}-phase-official8.json').read_text())['rows']==json.loads((E/f'{name}-phase-build30.json').read_text())['rows'] for name in ['chromium','webkit']}
(E/'phase-summary.json').write_text(json.dumps(out,indent=2)+'\n')
regions=[]
for f in sorted(E.glob('*-phase-*.json')):
 d=json.loads(f.read_text());samples=[x for q in d['rows'] for x in [q.get('base')]+[p.get('output') for p in q['probes']] if x]
 for name,predicate in [('homogeneous',lambda s:s['phase'] in [0,1,2,3,5]),('physicalCoexistence',lambda s:s['phase']==6 and 0<=s['state']['Q']<=1),('unphysicalCoexistenceQuality',lambda s:s['phase']==6 and not 0<=s['state']['Q']<=1)]:
  group=[s for s in samples if predicate(s)];regions.append(dict(file=f.name,group=name,count=len(group),maxPressurePa=max([abs(s['pResidual']) for s in group]+[0]),maxEnthalpyJkg=max([abs(s['hResidual']) for s in group]+[0])))
(E/'phase-region-summary.json').write_text(json.dumps(regions,indent=2)+'\n')
for d in out['builds']:print(d['browser'],d['build'],'errors',len(d['errors']),'crossings',d['phaseCrossingProbes'],'max P/h',d['maximumPressureResidualPa'],d['maximumEnthalpyResidualJkg'],'ratios',d['ratioRange'])
print(out['native'])
