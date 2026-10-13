"""Summarize retained measurements; no EOS calls, fitting or coupled execution."""
import hashlib,json,statistics as S
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';load=lambda f:json.loads((E/f).read_text())
fields=['p','T','h','s','rho','u'];summary=dict(experimental=True,qualifiedPropertyEngine=False,testedOnPhysicalIPad=False,browsers={})
inputs=json.loads((B/'inputs.json').read_text());source={q['id']:q for q in inputs['requests']}
for name in ['chromium','webkit']:
 data=load(name+'-accuracy.json');br=dict(version=data['version'],accuracy={})
 for a in data['builds']:
  rr=[r for r in a['rows'] if r.get('errors')];valid=[r for r in rr if not source[r['id']].get('expectedFailure')]
  metrics={k:max(abs(r['errors'][k]) for r in valid) for k in fields}
  expected_matches=all(bool(r.get('error'))==bool(r['referenceError']) for r in a['rows'])
  br['accuracy'][a['requestedVersion']]=dict(requests=len(a['rows']),successfulRows=sum('state'in r for r in a['rows']),errors=sum('error'in r for r in a['rows']),failureBehaviorMatchesPython=expected_matches,maxMatchingPythonDifferencesSI=metrics,staticValueGatesPass=metrics['p']<10 and metrics['T']<.01 and metrics['h']<50,
    maxWorkIdentityJkg=max(abs(r['workIdentityJkg']) for r in valid),maxMaxwell=a['maxMaxwell'],stress=a['stress'],linearMemoryFinal=a['linearMemoryFinal'],capabilities=a['capabilities'])
 init=load(name+'-initialization.json')['rounds'];br['initializationMS']=dict(mean=S.mean(r['init']['totalMS'] for r in init),minimum=min(r['init']['totalMS'] for r in init),maximum=max(r['init']['totalMS'] for r in init),firstFactoryMean=S.mean(r['init']['firstFactoryMS'] for r in init))
 perf=load(name+'-performance.json');br['microsecondsPerState']={}
 for group in sorted(set(r['group'] for r in perf['timings'])):
  br['microsecondsPerState'][group]={}
  for method in ['table','state8','high-level8']:
   a=[r for r in perf['timings'] if r['group']==group and r['method']==method];v=[r['elapsedMS']/r['calls']*1000 for r in a]
   br['microsecondsPerState'][group][method]=dict(mean=S.mean(v),sd=S.stdev(v),calls=sum(r['calls'] for r in a),failedCalls=sum(r['failures'] for r in a))
 pat=load(name+'-interior-patterns.json')['rounds'];br['interiorPatternMS']={}
 for n in [5,9]:
  br['interiorPatternMS'][str(n)]={}
  for region in ['liquid','vapor','two-phase']:
   br['interiorPatternMS'][str(n)][region]={}
   for method in ['table','state8','cached-state8']:
    a=[r for r in pat if r['n']==n and r['region']==region and r['method']==method];v=[r['elapsedMS']/r['repeats'] for r in a]
    br['interiorPatternMS'][str(n)][region][method]=dict(mean=S.mean(v),sd=S.stdev(v),logicalCallsPerPattern=a[0]['calls'],actualCache=a[0]['cache'])
 legacy=load(name+'-legacy-high-level.json')['timings'];br['legacy7MillisecondsPerState']={g:S.mean(r['elapsedMS']/r['calls'] for r in legacy if r['group']==g) for g in ['PH-liquid','DU-liquid','SAT']}
 br['sustained']=perf['sustained'];br['cacheEquivalentOnTestedRequests']=max(r['maxDifference'] for r in perf['cacheProof']['rows'])==0
 br['memory']=dict(linearBytes=perf['linearMemoryFinal'],summedBaselineProcessRSSKiB=perf['baselineProcessMemory']['summedRSSKiB'],summedFinalProcessRSSKiB=perf['finalProcessMemory']['summedRSSKiB'],chromiumHeap=perf.get('chromiumHeapUsage'),processRSSIsNotExclusiveMemory=True)
 work=load(name+'-worker.json');br['worker']=dict(startupRoundtripMS=work['startupRoundtripMS'],mainThreadTicks=work['mainThreadTicks'],mainThreadElapsedMS=work['mainThreadElapsedMS'],calls=work['work']['calls'],computationMS=work['work']['elapsedMS'])
 off=load(name+'-offline-server-disabled.json');br['offline']=dict(reloadAndFreshEOSRecoveryPass='state'in off['offline'],verification=off['offlineVerification'],badMIMEFallbackPass=not off['mimeFallback']['init']['streaming'],missingAssetError=off['missingAssetError'])
 supp=load(name+'-scientific-supplement.json');cc=[r for r in supp['canonical'] if 'recoveryErrors'in r]
 br['acceptedAccountingRecovery']=dict(requests=len(supp['canonical']),successes=len(cc),maxErrorsSI={k:max(abs(r['recoveryErrors'][k]) for r in cc) for k in ['p','T','h','rho','u']})
 br['finiteDifferenceCompatibility']=supp['derivatives']
 br['historical']=[r for r in data['builds'][1]['rows'] if source[r['id']].get('historical')]
 summary['browsers'][name]=br
p7=load('python-7.2.0.json')['rows'];p8=load('python-8.0.0.json')['rows'];both=[(a,b) for a,b in zip(p7,p8) if 'state'in a and 'state'in b and not source[a['id']].get('expectedFailure')]
summary['versionDifferences']=dict(comparableSuccessfulStates=len(both),maxDifferencesSI={k:max(abs(a['state'][k]-b['state'][k]) for a,b in both) for k in fields},rawQualitySentinelChanges=[dict(id=a['id'],Q7=a['state']['Q'],Q8=b['state']['Q']) for a,b in both if abs(a['state']['Q']-b['state']['Q'])>1],failedIn7SuccessfulIn8=[a['id'] for a,b in zip(p7,p8) if 'error'in a and 'state'in b])
# Conditional property-only projections. Nine uses an explicit hypothetical
# common iteration rate, not invented nine-section trajectory evidence.
R=B.parents[2];old=json.loads((R/'experiments/dx-fv/COUPLED_R_CONTROL_RESULTS.json').read_text())['cases'];rates={r['name']:r['attemptedIterations']/120 for r in old if r['name'] in ['cold','warm']}
summary['longDurationProjections']=dict(noLongCoupledRuns=True,assumptions='Historical accepted five-section cold/warm iterations per simulated second held constant. Nine-section rates assumed equal only for a what-if cost comparison. One timed pattern includes final canonical recovery, which may overcount per-iteration cost; failed trials/line searches could undercount.',historicalFiveIterationsPerSimSecond=rates,costs=[])
for name,br in summary['browsers'].items():
 for n in [5,9]:
  for method in ['table','state8','cached-state8']:
   values=[br['interiorPatternMS'][str(n)][r][method]['mean'] for r in ['liquid','vapor','two-phase']]
   lo=min(rates.values())*3600*min(values)/1000;hi=max(rates.values())*3600*max(values)/1000
   summary['longDurationProjections']['costs'].append(dict(browser=name,sections=n,method=method,propertyOnlyWallSecondsPerSimulatedHour=[lo,hi],sixHourScenarioWallSeconds=[6*lo,6*hi],notDevicePerformanceOrFullSimulationPrediction=True))
stress=next(r for r in json.loads((R/'experiments/dx-fv/COUPLED_R_DIAGNOSTICS.json').read_text())['cases'] if r['name']=='heat-reversal' and r['tolerance']==1e-6)
stressrate=stress['stats']['lineSearchOutcomes']['accepted']/stress['intervalSeconds']
summary['longDurationProjections']['historicalStressCase']=dict(name='heat-reversal',simulatedIntervalSeconds=60,NewtonIterationsPerSimSecond=stressrate,extraRejectedLineSearchEvaluations=stress['stats']['lineSearchOutcomes']['not-reduced'],failedNewtonAttempts=stress['stats']['failedNewton'],warning='Holding this pathological short-run rate constant is not a prediction, but shows how existing nonlinear failures can dominate long-duration costs.')
summary['longDurationProjections']['stressCosts']=[]
for name,br in summary['browsers'].items():
 for n in [5,9]:
  ms=br['interiorPatternMS'][str(n)]['vapor']['cached-state8']['mean']
  summary['longDurationProjections']['stressCosts'].append(dict(browser=name,sections=n,propertyOnlyWallSecondsPerSimulatedHour=stressrate*3600*ms/1000,excludesExtraRejectedLineSearchCost=True))
summary['classification']='Desktop browser EOS architecture conditionally feasible; migration blocked pending flash-precision/unchanged-solver compatibility and physical iPad validation.'
summary['recommendation']='Persistent official 8.0.0 HEOS::Ammonia in one Web Worker with exact bounded memoization; do not adopt or integrate. Investigate observed low-pressure PH flash convergence sensitivity under unchanged solver budgets before migration.'
summary['codeHashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in B.iterdir() if p.is_file() and p.suffix in ['.cjs','.mjs','.py','.js']}
(E/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print(summary['classification'])
for n,b in summary['browsers'].items():print(n,b['initializationMS'],b['interiorPatternMS'])
