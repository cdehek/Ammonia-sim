"""Independent artifact checks and descriptive timing summaries. Timeout 120s."""
import csv,gzip,hashlib,json,math,statistics
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(name):
 p=E/name;return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(name,x):(E/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def dist(a):
 if not a:return None
 a=sorted(a);return dict(n=len(a),median=statistics.median(a),p95=a[math.ceil(.95*len(a))-1],max=max(a),min=min(a))
def phase(g,spans):
 hits=[(max(0,min(g['end'],s['end'])-max(g['start'],s['start'])),s['phase']) for s in spans]
 return max(hits)[1] if hits else 'unclassified'
parity={};cross=[];mainRecords={}
for engine in ['chromium','webkit']:
 data=read(f'parity-{engine}-serialized.json.gz');assert data['passed'] and data['result']['passed'];parity[engine]=[];mainRecords[engine]={}
 for row in data['result']['results']:
  a,b=row['main'],row['worker'];assert a['science']==b['science'];assert a['diagnostics']['counts']==b['diagnostics']['counts'];assert a['diagnostics']['attempts']==b['diagnostics']['attempts']
  assert all(a['science'][i]['state']['seconds']==a['science'][i]['record']['seconds'] for i in range(4))
  mainRecords[engine][row['fixture']]=a['records']
  parity[engine].append(dict(fixture=row['fixture'],exactStatesRecordsAttempts=True,checkpointCount=4,propertyCalls=a['diagnostics']['counts'],audits=a['audits'],events=[r['events'] for r in a['records']],boundaryEvents=[r['boundaryEvents'] for r in a['records']],acceptedSteps=[r['acceptedSteps'] for r in a['records']],rejectedSteps=[r['rejectedSteps'] for r in a['records']],newtonIterations=[r['attemptedIterations'] for r in a['records']]))
for fixture in ['cold','warm']:
 for i,(a,b) in enumerate(zip(mainRecords['chromium'][fixture],mainRecords['webkit'][fixture])):
  error=dict(pBar=max(abs(x['p']-y['p']) for x,y in zip(a['sections'],b['sections'])),hKJkg=max(abs(x['h']-y['h']) for x,y in zip(a['sections'],b['sections'])),fluidK=max(abs(x['T']-y['T']) for x,y in zip(a['sections'],b['sections'])),thermalK=max(abs(x['temperatureK']-y['temperatureK']) for x,y in zip(a['nodes'],b['nodes'])))
  for k,limit in [('pBar',1e-4),('hKJkg',.05),('fluidK',.01),('thermalK',.01)]:assert error[k]<limit
  assert a['seconds']==b['seconds'] and a['events']==b['events']
  cross.append(dict(fixture=fixture,index=i,differences=error,originalCoupledBrowserLimitsPass=True))
write('scientific-audit.json',dict(passed=True,sameEngine=parity,crossEngine=cross,fullA2Qualification=False))
performance={}
for engine in ['chromium','webkit']:
 data=read(f'benchmark-{engine}-sealed.json.gz');assert data['passed'];performance[engine]={}
 assert len(data['blocks'])==6
 for mode in ['main','worker']:
  blocks=[b for b in data['blocks'] if b['mode']==mode];runs=[r for b in blocks for r in b['runs']];assert len(runs)==12 and all(r['baselineVerified'] for r in runs)
  summaries={}
  for fixture in ['cold','warm']:
   rs=[r for r in runs if r['fixture']==fixture]
   summaries[fixture]=dict(advanceMS=dist([s['advanceMS'] for r in rs for s in r['samples'] if s['type']=='advance']),throughputSimulatedSecondsPerWallSecond=dist([.001/(sum(s['advanceMS'] for s in r['samples'] if s['type']=='advance')/1000) for r in rs]),requestedWorkPerRunSeconds=.001,recordMS=dist([s['recordMS'] for r in rs for s in r['samples'] if s['type']=='snapshot']),propertyCounts=[r['diagnostics']['counts'] for r in rs])
  phases={key:dist([g['ms'] for r in runs for g in r['heartbeat']['gaps'] if phase(g,r['heartbeat']['spans'])==key]) for key in ['initialization','physics','snapshot','render','diagnostics','idle']}
  timings=[s for r in runs for s in r['samples']]
  init={temp:dist([s['client']['roundtripMS'] for r in runs if r['temperature']==temp for s in r['samples'] if s['type']=='initialize']) for temp in ['cold-session','warm-restart']}
  components={k:dist([s[k] for s in timings if s['type']=='initialize' and k in s]) for k in ['importMS','factoryMS','constructionMS','firstRenderMS','firstRenderableMS']}
  communication={k:dist([s['client'][k] for s in timings if s['client'].get(k) is not None]) for k in ['postMS','handlingMS','roundtripMS','workerCreationMS','requestDispatchUpperBoundMS','queueUpperBoundMS','responseDispatchUpperBoundMS']}
  communication['previousWorkerPostMS']=dist([s['client']['workerTransport']['previousResponsePostMS'] for s in timings if s['client'].get('workerTransport') and s['client']['workerTransport'].get('previousResponsePostMS') is not None])
  communication['roundtripMinusServiceUpperBoundMS']=dist([s['client']['roundtripMS']-s['timing']['serviceMS'] for s in timings])
  performance[engine][mode]=dict(fixtures=summaries,initializationRoundtripMS=init,initializationComponentsMS=components,communicationMS=communication,heartbeatByLargestOverlapMS=phases,allHeartbeatMS=dist([g['ms'] for r in runs for g in r['heartbeat']['gaps']]),frameGapMS=dist([g['ms'] for r in runs for g in r['heartbeat']['frames'][1:]]),longTasks=[g for r in runs for g in r['heartbeat']['longTasks']],automationInputRoundtripMS=dist([g for b in blocks for g in b['automationInputRoundtripMS']]),browserInputTimestampLatencyMS=dist([g['latencyMS'] for b in blocks for g in b['browserInputAcks']]),renderMS=dist([s['renderMS'] for s in timings if s['type']=='snapshot']),recordJSONEstimateBytes=dist([s['recordJSONEstimateBytes'] for s in timings if s['type']=='snapshot']),heapObservations=[r['diagnostics']['heap'] for r in runs],scientificBaselineVerified=True)
seal=json.loads((E/'timed-harness-source-manifest.json').read_text());assert all(hashlib.sha256((B/n).read_bytes()).hexdigest()==h for n,h in seal.items()),'timed harness source drift'
write('performance-summary.json',performance)
errors={};optional={}
for engine in ['chromium','webkit']:
 c1=read(f'c1-{engine}.json.gz');assert c1['passed'] and c1['result']['passed'];worker=c1['result']['worker'];assert len(worker['exactRollback']['attempts'])==20;assert worker['exactRollback']['objectIdentityInThisRealm']
 life=read(f'lifecycle-{engine}-display-sequence.json.gz');assert life['passed'] and life['result']['passed']
 eb=read(f'errorsbench-{engine}.json.gz');assert eb['passed'];errors[engine]={}
 for mode in ['main','worker']:
  rs=[r for block in eb['blocks'] if block['mode']==mode for r in block['runs']]
  assert len(rs)==3 and all(r['result']['passed'] for r in rs)
  errors[engine][mode]=dict(sequenceMS=dist([r['elapsedMS'] for r in rs]),heartbeatMS=dist([g['ms'] for r in rs for g in r['heartbeat']['gaps']]),automationInputRoundtripMS=dist([g for b in eb['blocks'] if b['mode']==mode for g in b['automationInputRoundtripMS']]))
 b7=read(f'b7-{engine}-phase-getter.json.gz');assert b7['passed'] and b7['result']['passed'];r=b7['result'];optional[engine]=dict(passed=True,exactMainWorkerSubset=r['exactMainWorkerSubset'],qualification=r['main']['qualification'],memoryBytes=[x['memory'] for x in r['worker']['rows']],tests=[{'fullVLE':x['fullVLE'],'tests':[t['test'] for t in x['states']]} for x in r['worker']['rows']])
 # Outward evidence contains no native pointer field or raw ABI args.
 def check(v):
  if isinstance(v,dict):
   assert not set(v)&{'excPtr','ptr','pointer','handle'},set(v)
   for z in v.values():check(z)
  elif isinstance(v,list):
   for z in v:check(z)
 check(r)
write('failure-lifecycle-audit.json',dict(passed=True,engines=['chromium','webkit'],C1ExactRollbackAnd20Attempts=True,lifecycle=True,errorSequenceTiming=errors))
write('b7-subset-audit.json',optional)
print(json.dumps({'scientificAudit':True,'failureAudit':True,'optionalB7':True,'engines':list(performance)}))
