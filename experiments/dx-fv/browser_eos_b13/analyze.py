"""Derive all numerical tables from retained B13 receipts; no scientific execution."""
import collections,gzip,json,statistics,functools
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
@functools.cache
def read(name):
 with gzip.open(E/name,'rt') as f:rows=[json.loads(l) for l in f]
 for r in rows:
  if 'scienceReference' in r:
   ref=r['scienceReference'];src=next(x for x in read(ref['file']) if x['type']=='checkpoint' and x['seconds']==ref['seconds'])
   for k in ['science','scienceExact','attempts']:r[k]=src[k]
 return rows
def checkpoints(name):return [r for r in read(name) if r['type']=='checkpoint']
def delta(a,b):return {k:a.get(k,0)-b.get(k,0) for k in a.keys()|b.keys()}
def summary(rows):
 last=rows[-1];s=last['science']['state'];r=last['science']['record'];attempts=last['attempts']
 intervals=[];previous=rows[0]
 for x in rows[1:]:
  st=x['science']['state'];p=previous['science']['state']
  intervals.append(dict(start=previous['seconds'],end=x['seconds'],requested=x['requestedIncrement'],actual=x['actualIncrement'],wallMS=x['wallMS'],cpuMS=x['cpuMS'],observerMS=x['observerMS'],acceptedSubsteps=st['acceptedSteps']-p['acceptedSteps'],rejectedTrials=st['rejectedSteps']-p['rejectedSteps'],residuals=st['attemptedResidualEvaluations']-p['attemptedResidualEvaluations'],corrections=st['attemptedIterations']-p['attemptedIterations'],linearSolves=st['attemptedLinearSolves']-p['attemptedLinearSolves'],nextStepSeconds=st['nextStepSeconds'],combinedEnergyResidualKJ=x['science']['record']['combinedEnergyResidualKJ']))
  previous=x
 events=[v for a in attempts for v in a['events']]
 it=[v for v in events if v['type']=='iteration'];der=[v for v in events if v['type']=='derivative'];ls=[v for v in events if v['type']=='line-search']
 stages={};
 for a in attempts:
  for v in a['events']:
   if v['type']=='iteration':stages.setdefault((a['startSeconds'],a['trialSeconds'],v['solveId']),[]).append(v)
 iterations=[max(v['iteration'] for v in group) for group in stages.values()]
 conservation={k:max(abs(x['science']['record'][k]) for x in rows) for k in ['massResidualKg','refrigerantEnergyResidualKJ','thermalEnergyResidualKJ','combinedEnergyResidualKJ']}
 conservation.update(maxSectionMassKg=max(abs(z['massKg']) for x in rows for z in x['science']['record']['sectionResiduals']),maxSectionEnergyKJ=max(abs(z['energyKJ']) for x in rows for z in x['science']['record']['sectionResiduals']),maxNodeEnergyKJ=max(abs(z['residualKJ']) for x in rows for z in x['science']['record']['nodes']))
 out=dict(seconds=s['seconds'],stop=s['stop'],intervals=intervals,totalAdvanceWallMS=sum(x['wallMS'] for x in rows),totalCPUms=sum(x.get('cpuMS',0) for x in rows),observerMS=sum(x.get('observerMS',0) for x in rows),acceptedSubsteps=s['acceptedSteps'],rejectedTrials=s['rejectedSteps'],attempts=len(attempts),residuals=s['attemptedResidualEvaluations'],corrections=s['attemptedIterations'],linearSolves=s['attemptedLinearSolves'],jacobianBuilds=s['attemptedIterations'],minAttemptSeconds=min(a['trialSeconds'] for a in attempts),maxAttemptSeconds=max(a['trialSeconds'] for a in attempts),minAcceptedSubstepSeconds=s['minAcceptedStepSeconds'],maxAcceptedSubstepSeconds=s['maxAcceptedStepSeconds'],nextStepSeconds=s['nextStepSeconds'],reasons=dict(collections.Counter(a['failure']['message'] if a['failure'] else a['rejectionReason'] or 'accepted' for a in attempts)),newtonIterationHistogram=dict(collections.Counter(iterations)),derivativeOutcomes=dict(collections.Counter(v['outcome'] for v in der)),maxDerivativeShrink=max((v['shrink'] for v in der),default=0),lineSearchOutcomes=dict(collections.Counter(v['outcome'] for v in ls)),minLineSearchFactor=min((v['factor'] for v in ls),default=1),conservation=conservation,phaseEvents=s['events'],growthHistory=s['growthHistory'],maxRSSKiB=max(x['resource']['maxRSS'] for x in rows),maxHeapUsedBytes=max(x['memory']['heapUsed'] for x in rows),initialRecord=rows[0]['science']['record'],finalRecord=r,lastScienceHash=last['scienceHash'],lastAttemptsHash=last['attemptsHash'])
 if last['stats']:
  out['profileIntervals']=[dict(start=p['seconds'],end=x['seconds'],**{k:delta(x['stats'][k],p['stats'][k]) for k in ['counts','calls','ms','section','boundary']}) for p,x in zip(rows,rows[1:])]
  out['profile']={k:delta(last['stats'][k],rows[0]['stats'][k]) for k in ['counts','calls','ms','section','boundary']};out['profile']['newton']=last['stats']['newton'];out['profile']['propertyErrors']=last['stats']['propertyErrors'];out['propertyRangesByInterval']=[{'seconds':x['seconds'],'ranges':x['stats'].get('propertyRanges')} for x in rows]
 return out
results={};parity=[]
for fixture in ['cold','warm']:
 canonical=[checkpoints(f'canonical-{fixture}-010-r{i}.jsonl.gz') for i in [1,2,3]]
 observed=checkpoints(f'observed-{fixture}-010-ranges.jsonl.gz')
 rangeRows=checkpoints(f'observed-{fixture}-010-ranges.jsonl.gz')
 assert len(rangeRows)==len(observed)
 for x,y in zip(rangeRows,observed):assert x['scienceHash']==y['scienceHash'] and x['attemptsHash']==y['attemptsHash']
 for i,c in enumerate(canonical):
  assert len(c)==7 and len(observed)==7
  for a,b in zip(c,observed):
   assert a['scienceHash']==b['scienceHash'] and a['attemptsHash']==b['attemptsHash'],(fixture,i,a['seconds'])
   assert not a.get('auditError') and not a.get('error')
  parity.append(dict(fixture=fixture,replicate=i+1,allSevenStateRecordAndAttemptHashesExact=True))
 s=summary(canonical[0]);s['observed']=summary(observed)
 s['propertyRangesByInterval']=[dict(seconds=x['seconds'],ranges=x['stats']['propertyRanges']) for x in rangeRows]
 totals=[sum(r['wallMS'] for r in c) for c in canonical]
 cpus=[sum(r.get('cpuMS',0) for r in c) for c in canonical]
 latest=[c[-1]['wallMS']/.005/1000 for c in canonical]
 s['timingReplicates']=dict(totalAdvanceWallMS=totals,totalCPUms=cpus,secondsWallPerSimSecond=[v/10 for v in totals],lastIntervalSecondsWallPerSimSecond=latest,medianSecondsWallPerSimSecond=statistics.median(totals)/10,medianCPUSecondsPerSimSecond=statistics.median(cpus)/10,observedOverCanonicalMedian=s['observed']['totalAdvanceWallMS']/statistics.median(totals))
 s['conditionalProjection']={str(t):dict(fastestRecentWindowWallSeconds=min(latest)*t,medianWholeProbeWallSeconds=statistics.median(totals)/10*t,slowestObservedWindowWallSeconds=max(x['wallMS']/x['actual']/1000 for c in canonical for x in summary(c)['intervals'])*t) for t in [.1,1,10,60,3600]}
 results[fixture]=s
(E/'analysis.json').write_text(json.dumps(dict(scope='UNQUALIFIED RESEARCH; fresh Node 24 process instrumentation, not desktop/browser benchmark',maxActualHorizonSeconds=.01,results=results,parity=parity),indent=2,sort_keys=True)+'\n')
for fixture,r in results.items():
 print(fixture,json.dumps({k:v for k,v in r.items() if k not in ['observed','initialRecord','finalRecord']},indent=2))
 print('PROFILE',json.dumps({k:v for k,v in r['observed']['profile'].items() if k!='newton'},indent=2))
