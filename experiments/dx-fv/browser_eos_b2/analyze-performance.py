import os,json,statistics
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'))
def stats(values):return dict(median=statistics.median(values),minimum=min(values),maximum=max(values),samples=len(values))
out={'standalone':[],'coupled':[],'offline':{},'physicalIPad':False,'memoryScope':'WASM linear memory, worker-exposed JavaScript heap and page CDP heap are separate; total browser/device memory not measured.'}
for browser in ['chromium','webkit']:
 for build in ['build30','build44']:
  f=E/f'{browser}-performance-{build}.json'
  if f.exists():
   d=json.loads(f.read_text());w=d['worker']['result'];p=w.get('performance',{});groups={}
   for r in p.get('timings',[]):groups.setdefault(r['group'],[]).append(r)
   item=dict(file=f.name,browser=browser,build=build,workerOK=w.get('ok'),initializationMS=stats([s['init']['totalMS'] for s in d['startup']]),groups={name:dict(microsecondsPerState=stats([r['elapsedMS']*1000/r['calls'] for r in rows]),calls=sum(r['calls'] for r in rows),failures=sum(r['failures'] for r in rows)) for name,rows in groups.items()},peakObservedLinearMemoryMiB=max([r['linearMemory'] for r in p.get('timings',[])]+[r['linearMemory'] for r in p.get('sustained',[])]+[p.get('linearMemory',0)])/1048576,pageMaxTimerGapMS=d['worker']['maxTimerGapMS'],workerJSHeap=p.get('jsHeap'),pageCDPHeap=d.get('pageHeap'),errorRecovery=p.get('errorRecovery'),sustained=p.get('sustained'))
   out['standalone'].append(item)
  f=E/f'{browser}-coupled-cost-{build}.json'
  if f.exists():
   d=json.loads(f.read_text());r=d['result'];groups={}
   for row in r.get('rows',[]):
    if not row.get('warmup') and 'error' not in row:groups.setdefault(row['case'],[]).append(row)
   out['coupled'].append(dict(file=f.name,browser=browser,build=build,error=r.get('error'),failedRows=[v for v in r.get('rows',[]) if 'error' in v],missingCases=[name for name in ['cold','warm','heat-reversal'] if name not in groups],initializationMS=r.get('init',{}).get('totalMS'),pageMaxTimerGapMS=d['pageMaxTimerGapMS'],peakObservedLinearMemoryMiB=r.get('linearMemory',0)/1048576,workerJSHeap=r.get('workerJSHeap'),pageCDPHeapAfterWorker=d.get('pageCDPHeapAfterWorker'),cases={name:dict(elapsedMS=stats([v['elapsedMS'] for v in rows]),allTargetsReached=len(rows)==3 and all(v.get('completedTarget',False) for v in rows),repeatedWorkExactlyMatches=all({k:v[k] for k in ['propertyCalls','acceptedHalfSteps','rejectedSteps','iterations','residualEvaluations','linearSolves']}=={k:rows[0][k] for k in ['propertyCalls','acceptedHalfSteps','rejectedSteps','iterations','residualEvaluations','linearSolves']} for v in rows),work={k:rows[0][k] for k in ['propertyCalls','acceptedHalfSteps','rejectedSteps','accuracyRejected','eventRejected','domainRejected','iterations','residualEvaluations','linearSolves']},stops=[v['stop'] for v in rows]) for name,rows in groups.items()},scope=r.get('measurement')))
for name in ['offline-context.json','offline-origin-only.json']:
 f=E/name
 if f.exists():
  d=json.loads(f.read_text());out['offline'][name]=[dict(browser=r['browser'],error=r.get('error'),blockedOriginRequests=r.get('blockedOriginRequests'),builds=[dict(build=b['build'],ok=b.get('result',{}).get('ok',False),error=b.get('error') or b.get('result',{}).get('error'),contextOffline=b.get('contextOffline'),originDisabled=b.get('originDisabled')) for b in r.get('builds',[])]) for r in d]
out['matchedRatios']=[]
for browser in ['chromium','webkit']:
 a=next((r for r in out['coupled'] if r['browser']==browser and r['build']=='build30'),None);b=next((r for r in out['coupled'] if r['browser']==browser and r['build']=='build44'),None)
 if a and b:
  for case,x in a['cases'].items():
   y=b['cases'].get(case)
   if y:out['matchedRatios'].append(dict(browser=browser,case=case,ratio44Over30=y['elapsedMS']['median']/x['elapsedMS']['median'],comparableCompletedTargets=x['allTargetsReached'] and y['allTargetsReached']))
(E/'performance-summary.json').write_text(json.dumps(out,indent=2)+'\n')
lines=['# Browser runtime and memory results','','These are new B2 desktop observations. Physical Safari/iPad is **NOT RUN**.','Serial matched 30/44 measurements are separate from concurrent scientific campaign elapsed times.','','| Engine | Build | Median init ms (3 contexts) | PH liquid / vapor / two-phase µs | DU liquid / vapor / two-phase µs | Peak observed WASM MiB | Page maximum timer gap ms |','|---|---|---:|---|---|---:|---:|']
for r in out['standalone']:
 latency=lambda mode:' / '.join(f"{r['groups'][mode+'-'+region]['microsecondsPerState']['median']:.3f}" for region in ['liquid','vapor','two-phase'])
 lines.append(f"| {r['browser']} | {r['build']} | {r['initializationMS']['median']:.2f} | {latency('PH')} | {latency('DU')} | {r['peakObservedLinearMemoryMiB']:.2f} | {r['pageMaxTimerGapMS']:.2f} |")
lines+=['','Each property state returns the same seven fields; three timed rounds per physical region. Group calls/failures, min/max latency, sustained epochs, error recovery, startup components and heap scopes are retained in performance-summary.json and raw files. Fresh contexts may reuse browser/compiler/OS caches. WebKit reverses build order. The first Chromium30 measurement overlapped a brief independent audit and remains under performance-overlap; its isolated repeat is reported here. The recorded order is Chromium30 (archived), Chromium44, WebKit44, WebKit30, then the isolated Chromium30 repeat.','','| Engine | Build | Original fixture through 0.2 s | Median solver ms (3 repeats) | Accepted half-steps | Rejected trials | Iterations | PH / sat / MUV public calls | Completed target |','|---|---|---|---:|---:|---:|---:|---|---|']
for r in out['coupled']:
 for name,v in r['cases'].items():
  w=v['work'];c=w['propertyCalls'];lines.append(f"| {r['browser']} | {r['build']} | {name} | {v['elapsedMS']['median']:.3f} | {w['acceptedHalfSteps']} | {w['rejectedSteps']} | {w['iterations']} | {c['ph']} / {c['sat']} / {c['stateMVU']} | {v['allTargetsReached']} |")
lines+=['','The coupled timer includes original model creation, advances/records and the adapter/table support guard; WASM initialization, input transfer and JSON output are outside it. One warmup precedes three measured repetitions. These short startup workloads are cost measurements, **not full scientific trajectories** and contain no 15/30 s disturbance. They preserve original solver options and physics.','','| Engine | Fixture | Median cost 44 / 30 | Both targets complete |','|---|---|---:|---|']
for r in out['matchedRatios']:lines.append(f"| {r['browser']} | {r['case']} | {r['ratio44Over30']:.4f} | {r['comparableCompletedTargets']} |")
lines+=['','Ratios are descriptive for these matched workloads; three repeats do not establish universal cost or an optimal precision setting. Scientific qualification timings include source transfer, assertions and diagnostic/persistence overhead and were collected with competing workers; they are not controlled backend speed ratios.','','WASM linear memory is not total browser or device memory. Page CDP heap excludes the worker; worker performance.memory is nonstandard and can be unavailable. Heap snapshots after a worker terminates may include uncollected harness data. No total iPad memory or physical-device responsiveness is inferred.','','Offline results are separate for browser offline-context emulation and an origin returning 503. Local service-worker/worker execution is not a physical-device test or hosted deployment.']
lines+=['','| Scope | Chromium30 page JS used / allocated MiB | Chromium44 page JS used / allocated MiB |','|---|---:|---:|']
for scope,key,records in [('Standalone after worker','pageCDPHeap',out['standalone']),('Coupled after worker','pageCDPHeapAfterWorker',out['coupled'])]:
 heaps=[]
 for build in ['build30','build44']:
  item=next((r for r in records if r['browser']=='chromium' and r['build']==build),{})
  h=item.get(key);heaps.append(f"{h['usedSize']/1048576:.3f} / {h['totalSize']/1048576:.3f}" if h else 'NOT MEASURED')
 lines.append(f"| {scope} | {' | '.join(heaps)} |")
complete=len(out['coupled'])==4 and all(not r['error'] and not r['failedRows'] and not r['missingCases'] and all(v['allTargetsReached'] and v['repeatedWorkExactlyMatches'] for v in r['cases'].values()) for r in out['coupled'])
lines+=['','Worker JS heap is unavailable in both engines; WebKit page heap is NOT MEASURED. These page-only values must not be added to WASM memory and called a total browser footprint.',f'All coupled repetitions reach the 0.2 s target with repeatable work counts: **{complete}**. Failed/missing rows, if present, remain explicit in the summary.']
for name,rows in out['offline'].items():
 lines+=['',f'**{name}**']
 for r in rows:
  failures=sorted(set(str(b['error']).splitlines()[0] for b in r['builds'] if not b['ok']))
  lines.append(f"- {r['browser']}: {sum(b['ok'] for b in r['builds'])}/{len(r['builds'])} backend workers completed; preparation error={r['error']!r}; origin requests blocked (cumulative within this mode)={r['blockedOriginRequests']}; backend/page failures={failures}.")
lines+=['','Chromium passes both offline experiments. WebKit passes the origin-disabled cache replay but **FAILS offline-context emulation** during fresh navigation with an internal error (all four builds). The successful origin-disabled result is a different experiment and does not clear that compatibility gate. Neither result qualifies actual Safari airplane-mode/device behavior.']
lines+=['','Long-duration memory growth, hour-scale cost and actual iPad Safari remain **NOT RUN** because earlier scientific gates fail. No hosting or Cloudflare changes were made.']
(B/'PERFORMANCE_RESULTS.md').write_text('\n'.join(lines)+'\n')
print(len(out['standalone']),'standalone,',len(out['coupled']),'coupled matched measurements')
