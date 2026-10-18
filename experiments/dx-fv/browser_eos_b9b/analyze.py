"""Independent exact evidence comparisons, work reconciliation and descriptive statistics."""
import json,gzip,hashlib,statistics,collections,csv
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';R=B.parents[2]
def read(n):
 p=E/n;return json.loads(gzip.decompress(p.read_bytes()) if n.endswith('.gz') else p.read_text())
def save(n,v):(E/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def stats(a):return dict(n=len(a),median=statistics.median(a),min=min(a),max=max(a),samples=a)
def addmap(rows):
 c=collections.Counter()
 for r in rows:c.update(r)
 return dict(c)
def census(r):
 attempts=[];solves=[]
 for ai,a in enumerate(r['science']['attempts']):
  groups=collections.defaultdict(list)
  for e in a['events']:groups[e['solveId']].append(e)
  derivative=[e for e in a['events'] if e['type']=='derivative'];ls=[e for e in a['events'] if e['type']=='line-search']
  for id,events in groups.items():
   initial=[e for e in events if e['type']=='iteration' and e['iteration']==0]
   fd=[e for e in events if e['type']=='derivative'];line=[e for e in events if e['type']=='line-search']
   iterations=[e for e in events if e['type']=='iteration'];jac={(e['solveId'],e['iteration']) for e in fd}
   for e in iterations:
    if e['status']=='converged':
     assert e['fluidNorm']<=1e-11 and e['thermalNorm']<=1e-11
     assert e['thermalNorm']*r['settings']['thermalResidualK']/r['settings']['nonlinearTolerance']<=1e-12
   solves.append(dict(attempt=ai,solveId=id,context=initial[0].get('context') if initial else None,initialResidual=len(initial),NewtonCorrections=len(jac),residuals=len(initial)+len(fd)+len(line),jacobians=len(jac),FD=len(fd),lineSearch=len(line),converged=any(e.get('status')=='converged' for e in iterations),finalNorm=max(abs(v) for v in iterations[-1]['residual']) if iterations else None,initialDominant=initial[0]['dominantIndex'] if initial else None,finalIteration=iterations[-1]['iteration'] if iterations else None))
  assert a['evaluations']==len(groups)+len(derivative)+len(ls),'residual reconciliation'
  assert a['iterations']==len({(e['solveId'],e['iteration']) for e in derivative})==a['linearSolves']
  attempts.append(dict(index=ai,startSeconds=a['startSeconds'],trialSeconds=a['trialSeconds'],temporalError=a['temporalError'],rejectionReason=a['rejectionReason'],failure=a['failure'],TRBDF2Trials=len(groups)//2,stages=len(groups),evaluations=a['evaluations'],NewtonCorrections=a['iterations'],JacobianAssemblies=a['iterations'],FD=len(derivative),FDByKind=dict(collections.Counter(e['kind'] for e in derivative)),FDOutcomes=dict(collections.Counter(e['outcome'] for e in derivative)),FDSigns=dict(collections.Counter('positive' if e['step']>0 else 'negative' for e in derivative)),lineSearch=len(ls),lineOutcomes=dict(collections.Counter(e['outcome'] for e in ls)),lineFactors=dict(collections.Counter(str(e['factor']) for e in ls)),linearSolves=a['linearSolves'],acceptedHalfSteps=0 if a['rejectionReason'] or a['failure'] else 2))
 final=r['science']['rows'][-1]['state'];aggregate={k:sum(a[k] for a in attempts) for k in ['TRBDF2Trials','stages','evaluations','NewtonCorrections','JacobianAssemblies','FD','lineSearch','linearSolves','acceptedHalfSteps']}
 aggregate.update(attempts=len(attempts),rejected=final['rejectedSteps'],acceptedSimulatedSeconds=final['seconds'],requestedSimulatedSeconds=.001,publicProperties=r['propertyCounts'],FDByKind=addmap(a['FDByKind'] for a in attempts),FDOutcomes=addmap(a['FDOutcomes'] for a in attempts),lineOutcomes=addmap(a['lineOutcomes'] for a in attempts),NewtonIterationDistribution=dict(collections.Counter(s['finalIteration'] for s in solves)))
 if r['mode']=='instrumented':
  m=r['metrics'];aggregate.update(cache=m['cache'],internalCounts={k:v for k,v in m['counts'].items() if k.startswith('internal.') or k.startswith('inverse.')},advanceInclusiveMS=addmap(v for k,v in m['phaseInclusiveMS'].items() if k.startswith('advance-')),advanceExclusiveMS=addmap(v for k,v in m['phaseExclusiveMS'].items() if k.startswith('advance-')))
  aggregate['advancePublicPropertyCounts']=addmap(v for k,v in m['propertyByContext'].items() if k.startswith('advance-'))
  assert aggregate['advancePublicPropertyCounts']=={k:sum(t['propertyDelta'][k] for t in r['timing'])-3*extra for k,extra in [('ph',8),('sat',13),('stateMVU',5)]}
  assert aggregate['stages']==m['counts']['NewtonInclusive']==m['counts']['model.solveStage']
  assert aggregate['TRBDF2Trials']==m['counts']['model.trial']
  assert m['cache']['requests']==5*aggregate['evaluations'] and m['cache']['requests']==m['cache']['hits']+m['cache']['misses']
  assert aggregate['acceptedHalfSteps']==m['counts']['model.commit']
 return dict(aggregate=aggregate,attempts=attempts,solves=solves,advances=r['timing'],initialRecord=r['science']['rows'][0]['record'],finalRecord=r['science']['rows'][-1]['record'],sourceEvents=r['metrics']['events'],propertyByContext=r['metrics']['propertyByContext'])
frozen=json.loads((B.parent/'browser_eos_b9/evidence/frozen-browser-scientific-hashes.json').read_text())
parity={};performance={};work={};failures={}
for engine in ['chromium','webkit']:
 baseline=read('baseline-'+engine+'.json.gz');matrix=read('matrix-'+engine+'.json.gz');validation=read('validation-'+engine+'.json.gz');passive=read('passive-'+engine+'.json.gz');failure=read('failure-'+engine+'.json.gz')
 assert all(v['passed'] for v in [baseline,matrix,validation,passive,failure])
 parity[engine]={};performance[engine]={};work[engine]={};failures[engine]=dict(C1=failure['failure']['passed'],acceptedObservationalCopy=failure['acceptedCopyFailure']['passed'])
 historical=json.loads(gzip.decompress((B.parent/f'browser_eos_b9a/evidence/baseline-{engine}-export-fixed.json.gz').read_bytes()))
 for fixture in ['cold','warm']:
  control=next(r for r in baseline['runs'] if r['fixture']==fixture)
  old=next(r for r in historical['result']['results'] if r['fixture']==fixture)['main']
  tagged={'rows':[{'state':r['state'],'record':r['record'],'attempts':r['attempts']} for r in old['science']],'attempts':old['diagnostics']['attempts']}
  historicalFullHash=hashlib.sha256(json.dumps(tagged,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
  assert historicalFullHash==control['scienceHash'],'Saved B9A full binary64 scientific state/record/observer identity'
  rows=[r for dataset in [baseline,matrix,validation,passive] for r in dataset['runs'] if r['fixture']==fixture]
  for r in rows:
   assert r['checkpointHashes']==frozen[engine][fixture],(engine,fixture,r['mode'],'saved baseline')
   assert r['science']==control['science'],(engine,fixture,r['mode'],'all original state/record/attempt fields')
   assert r['scienceHash']==control['scienceHash'] and r['propertyCounts']==control['propertyCounts']
  seq=[r for r in validation['runs'] if r['fixture']==fixture];assert seq[0]['sequenceHash']==seq[1]['sequenceHash']
  parity[engine][fixture]=dict(passed=True,allOriginalFieldsExact=True,savedFullScientificRowsAndObserverAttemptsExact=True,savedFullScientificSHA256=historicalFullHash,savedCheckpointHashes=control['checkpointHashes'],comparedRuns=len(rows),sequenceHash=seq[0]['sequenceHash'],publicProperties=control['propertyCounts'],audits=control['audits'])
  instrumented=next(r for r in matrix['runs'] if r['fixture']==fixture and r['mode']=='instrumented');work[engine][fixture]=census(instrumented)
  grouped={mode:[r for r in matrix['runs'] if r['fixture']==fixture and r['mode']==mode] for mode in ['original','pass-through','instrumented']}
  performance[engine][fixture]={mode:dict(advanceSumMS=stats([sum(t['advanceMS'] for t in r['timing']) for r in rr]),initializationMS=stats([r['initializationMS'] for r in rr]),extraSnapshotRecordMS=stats([sum(t['snapshotRecordMS'] for t in r['timing']) for r in rr]),stateAndAttemptCopyMS=stats([sum(t['stateAndAttemptCopyMS'] for t in r['timing']) for r in rr]),workerRoundtripMS=stats([r['workerRoundtripMS'] for r in rr]),timerResolutionMS=sorted({r['timerResolutionMS'] for r in rr},key=lambda x:-1 if x is None else x)) for mode,rr in grouped.items()}
  overhead=[]
  for round in range(3):
   block=[r for r in matrix['runs'] if r['fixture']==fixture and r['round']==round];times=[sum(t['advanceMS'] for t in r['timing']) for r in block];reference=(times[0]+times[3])/2
   overhead.append(dict(round=round,originalBeforeMS=times[0],passThroughMS=times[1],instrumentedMS=times[2],originalAfterMS=times[3],bracketMeanMS=reference,passThroughDeltaMS=times[1]-reference,instrumentedDeltaMS=times[2]-reference,instrumentedRatio=times[2]/reference))
  performance[engine][fixture]['overhead']=overhead
  performance[engine][fixture]['inclusiveCostMS']={k:stats([census(r)['aggregate']['advanceInclusiveMS'].get(k,0) for r in grouped['instrumented']]) for k in work[engine][fixture]['aggregate']['advanceInclusiveMS']}
  performance[engine][fixture]['passive']=[dict(passive=r.get('passive',False),advanceSumMS=sum(t['advanceMS'] for t in r['timing'])) for r in passive['runs'] if r['fixture']==fixture]
save('scientific-parity.json',dict(passed=True,engines=parity,failures=failures))
save('performance-summary.json',performance);save('nonlinear-census.json',work)
# Sample containment: each leaf gets one source category; inclusive property
# containment is reported separately, never added to the leaf partition.
manifest=read('accepted-source-manifest.json');bundle=(B.parent/'browser_eos_b9/accepted-bundle.mjs').read_text();ranges=[]
for v in manifest.values():
 path=R/v['snapshot'];raw=path.read_text()
 if path.suffix=='.json':continue
 at=bundle.index(raw);lo=bundle[:at].count('\n');ranges.append((lo,lo+raw.count('\n'),path.name))
def source(f):
 if 'accepted-bundle.mjs' not in f.get('url',''):return f.get('url','') or '<runtime/unattributed>'
 line=f['lineNumber'];return next((n for lo,hi,n in ranges if lo<=line<=hi),'accepted-loader')
profiles={}
for p in sorted(list(E.glob('cpu-chromium-*.json'))+list(E.glob('cpu-node-*.json'))):
 v=json.loads(p.read_text())['profile'];nodes={n['id']:n for n in v['nodes']};parent={c:n['id'] for n in v['nodes'] for c in n.get('children',[])};leaf=collections.Counter();functions=collections.Counter();leafSamples=collections.Counter();lines=collections.Counter();propertyTime=0;propertySamples=0;samples=0;total=0;outside=0
 for id,dt in zip(v.get('samples',[]),v.get('timeDeltas',[])):
  chain=[];n=id
  while n in nodes:chain.append(nodes[n]['callFrame']);n=parent.get(n)
  if not any(f['functionName']=='advance' and 'accepted-bundle' in f['url'] for f in chain):outside+=dt;continue
  samples+=1;total+=dt;frame=nodes[id]['callFrame'];s=source(frame);leaf[s]+=dt;leafSamples[s]+=1;functions[s+':'+(frame['functionName'] or '<anonymous>')]+=dt
  offset=next((lo for lo,hi,n in ranges if n==s),None);originalLine=frame['lineNumber']-offset+1 if offset is not None else None;lines[s+':'+str(originalLine)]+=dt
  if any(source(f)=='engine.js' for f in chain):propertyTime+=dt;propertySamples+=1
 profiles[p.stem]=dict(advanceSamples=samples,advanceSampleWeightedMS=total/1000,outsideAdvanceSampleWeightedMS=outside/1000,propertyEngineStackWeightedMS=propertyTime/1000,propertyEngineStackFraction=propertyTime/total if total else None,propertyEngineStackSamples=propertySamples,leafSourceSamples=dict(leafSamples),leafSourceWeightedMS={k:v/1000 for k,v in leaf.most_common()},leafFunctionWeightedMS={k:v/1000 for k,v in functions.most_common()},leafOriginalLineWeightedMS={k:v/1000 for k,v in lines.most_common()},intervalRequestedUS=500,limitation='One sampled session per fixture; sample-delta weighting estimates sampled wall exposure, not exact exclusive CPU cycles; GC/unrooted samples excluded from advance containment')
save('cpu-attribution.json',profiles)
print('Exact saved-browser state/record/attempt/property-sequence parity PASS; work census reconciled')
