"""Descriptive summaries, explicit phase attribution and original scientific limits."""
import csv,gzip,json,math,statistics,struct
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(n):
 p=E/n;return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(n,v):(E/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def dist(a):
 if not a:return None
 a=sorted(a);return dict(n=len(a),median=statistics.median(a),p95=a[math.ceil(.95*len(a))-1],max=max(a),min=min(a))
def phase(g,spans):return max((max(0,min(g['end'],s['end'])-max(g['start'],s['start'])),s['phase']) for s in spans)[1]
def unexact(x):
 if isinstance(x,dict):
  if set(x)=={'f64'}:return struct.unpack('>d',bytes.fromhex(x['f64']))[0]
  return {k:unexact(v) for k,v in x.items()}
 if isinstance(x,list):return [unexact(v) for v in x]
 return x
performance={};science={};attribution={}
for engine in ['chromium','webkit']:
 baseline=read(f'baseline-{engine}-export-fixed.json.gz');assert baseline['passed']
 science[engine]={}
 for mode in ['B','C']:
  p=read(f'parity{mode}-{engine}-record-cadence.json.gz');assert p['passed'];science[engine][mode]=[]
  for r in p['result']['results']:
   full=r['proof']['verifiedEndpoints'];assert len(full)==7
   points=[full[0]]+full[1::2];assert len(points)==4
   ref=next(z for z in baseline['result']['results'] if z['fixture']==r['fixture'])['worker']
   for point,expected in zip(points,ref['science']):assert point['state']==expected['state'] and point['record']==expected['record']
   assert r['proof']['counts']==ref['diagnostics']['counts']
   science[engine][mode].append(dict(fixture=r['fixture'],exactMUVAllStateAndRecord=True,exactOriginalObserverAttempts=True,insideWorker=True,checkpoints=[unexact(p['state'])['seconds'] for p in points],propertyCounts=r['proof']['counts'],acceptedSteps=[unexact(p['state'])['acceptedSteps'] for p in points],rejectedSteps=[unexact(p['state'])['rejectedSteps'] for p in points],audits=[p['audit'] for p in points],events=[unexact(p['state'])['events'] for p in points],boundaryEvents=[unexact(p['state'])['boundaryEvents'] for p in points]))
 data=read(f'benchmark-{engine}-reviewed.json.gz');assert data['passed'] and len(data['blocks'])==9;performance[engine]={'browserVersion':data['browserVersion'],'modes':{}}
 for mode in ['A','B','C']:
  blocks=[b for b in data['blocks'] if b['mode']==mode];runs=[r for b in blocks for r in b['runs']];assert len(runs)==12 and all(r['baselineVerifiedInsideOwner'] for r in runs)
  timings=[s for r in runs for s in r['samples']];initial=[s for s in timings if s['type']=='initialize'];adv=[s for s in timings if s['type']=='advance'];snaps=[s for s in timings if s['type']=='snapshot']
  components={k:dist([s['components'][k] for s in initial if s.get('components') and k in s['components']]) for k in ['importMS','tableParseAndLoaderMS','engineConstructionMS','modelFactoryMS','modelConstructionMS','initialRecordMS','projectionMS']}
  # Original A initialization components are not in the minimal benchmark row; retained in B9 baseline evidence.
  metrics=dict(sessionInitRoundtripMS={t:dist([s['client']['roundtripMS'] for r in runs if r['temperature']==t for s in r['samples'] if s['type']=='initialize']) for t in ['cold-session','warm-restart']},firstRenderMS=dist([s['firstRenderableMS'] for s in initial]),firstFrameUpperBoundMS=dist([s['firstActualFrameUpperBoundMS'] for s in initial]),workerCreationMS=dist([s['creationMS'] for s in initial]),initialComponents=components,advanceMS=dist([s['advanceMS'] for s in adv]),advanceServiceMS=dist([s['timing']['serviceMS'] for s in adv]),advanceRoundtripMS=dist([s['client']['roundtripMS'] for s in adv]),cacheCopyMS=dist([s['timing']['cacheCopyMS'] for s in timings if 'cacheCopyMS' in s['timing']]),hashVerificationMS=dist([s['verificationMS'] for s in timings if s.get('verificationMS') is not None]),projectionMS=dist([s['components']['projectionMS'] for s in timings if s.get('components') and 'projectionMS' in s['components']]),originalRecordMS=dist([s['components']['recordMS'] for s in snaps if s.get('components') and 'recordMS' in s['components']]),renderMS=dist([s['renderMS'] for s in timings if 'renderMS' in s]),nextFrameUpperBoundMS=dist([s['nextFrameUpperBoundMS'] for s in snaps]),disposalRoundtripMS=dist([s['client']['roundtripMS'] for s in timings if s['type']=='dispose']),heartbeatMS=dist([g['ms'] for r in runs for g in r['heartbeat']['gaps']]),heartbeatByPhaseMS={key:dist([g['ms'] for r in runs for g in r['heartbeat']['gaps'] if phase(g,r['heartbeat']['spans'])==key]) for key in ['initialization','physics','snapshot','render','diagnostics','dispose','idle']},frameIntervalsMS=dist([g['ms'] for r in runs for g in r['heartbeat']['frames'][1:]]),automationInputMS=dist([g for b in blocks for g in b['automationInputRoundtripMS']]),browserInputMS=dist([g['latencyMS'] for b in blocks for g in b['browserInputAcks']]),payloadJSONEstimateBytes={t:dist([p['jsonEstimateBytes'] for r in runs for p in r['payloads'] if p['type']==t]) for t in ['advance','snapshot','diagnostics']},fixtures={})
  for fixture in ['cold','warm']:
   rs=[r for r in runs if r['fixture']==fixture]
   metrics['fixtures'][fixture]=dict(originalAdvanceSumMS=dist([sum(s['advanceMS'] for s in r['samples'] if s['type']=='advance') for r in rs]),endToEndAdvanceSumMS=dist([sum(s['client']['roundtripMS'] for s in r['samples'] if s['type']=='advance') for r in rs]),simulatedSecondsPerSolverWallSecond=dist([1/sum(s['advanceMS'] for s in r['samples'] if s['type']=='advance') for r in rs]),simulatedSecondsPerEndToEndAdvanceWallSecond=dist([1/sum(s['client']['roundtripMS'] for s in r['samples'] if s['type']=='advance') for r in rs]),perAdvancePropertyCounts=[s['propertyCalls'] for r in rs for s in r['samples'] if s['type']=='advance'])
  metrics['communication']={k:dist([s['client'][k] for s in timings if s['client'].get(k) is not None]) for k in ['postMS','handlingMS','roundtripMS','requestDispatchUpperBoundMS','queueUpperBoundMS','responseDispatchUpperBoundMS']}
  metrics['communication']['previousResponsePostMS']=dist([s['client']['workerTransport']['previousResponsePostMS'] for s in timings if s['client'].get('workerTransport') and s['client']['workerTransport'].get('previousResponsePostMS') is not None])
  metrics['communication']['rttMinusServiceAndHashMS']=dist([s['client']['roundtripMS']-s['timing']['serviceMS']-(s.get('verificationMS') or 0) for s in timings]);performance[engine]['modes'][mode]=metrics
 a=read(f'attribution-{engine}.json.gz');assert a['passed'];attribution[engine]={}
 for fixture in ['cold','warm']:
  rr=[r for block in a['result']['results'] if block['fixture']==fixture for r in block['runs']];no=[r for r in rr if not r['instrumented']];yes=[r for r in rr if r['instrumented']]
  attribution[engine][fixture]=dict(uninstrumentedAdvanceSumMS=dist([sum(r['advances']) for r in no]),instrumentedAdvanceSumMS=dist([sum(r['advances']) for r in yes]),inclusiveCostMS={k:dist([r['cost'][k] for r in yes]) for k in yes[0]['cost']},microbenchmarkMS={k:dist([v for r in no for v in r['micro'][k]]) for k in no[0]['micro']},payloadEstimateBytes=no[0]['payloadJSONEstimateBytes'],eventTypes=no[0]['eventTypes'],instrumentationExactParity=True)
cross=[]
for fixture in ['cold','warm']:
 records=[]
 for engine in ['chromium','webkit']:
  b=read(f'baseline-{engine}-export-fixed.json.gz');records.append(next(r for r in b['result']['results'] if r['fixture']==fixture)['worker']['records'])
 for i,(a,b) in enumerate(zip(*records)):
  errors={k:max(abs(x[f]-y[f]) for x,y in zip(a[group],b[group])) for k,group,f in [('pressureBar','sections','p'),('enthalpyKJkg','sections','h'),('fluidK','sections','T'),('thermalK','nodes','temperatureK')]}
  for k,limit in [('pressureBar',1e-4),('enthalpyKJkg',.05),('fluidK',.01),('thermalK',.01)]:assert errors[k]<limit
  cross.append(dict(fixture=fixture,checkpoint=i,errors=errors,originalLimitsPass=True))
write('scientific-audit.json',dict(passed=True,engines=science,crossEngine=cross,fullA2Qualification=False));write('performance-summary.json',performance);write('attribution-summary.json',attribution)
print('Science, matched performance and attribution summaries PASS')

import hashlib
seal=read("benchmark-source-manifest-reviewed.json")
assert all(hashlib.sha256((B/n).read_bytes()).hexdigest()==h for n,h in seal.items()),"Timed source drift"
