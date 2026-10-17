"""Verify unchanged caller behavior, original lifecycle semantics and C1 guards."""
import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';read=lambda p:json.loads(p.read_text());failures=[];summary=[]
def check(ok,kind,**data):
 if not ok:failures.append(dict(kind=kind,**data))
check(read(E/'inherited-focused-audit.json')['passOriginalFocusedRequirements'],'originalFocusedAuditor')
for engine in ['chromium','webkit']:
 focused=read(E/f'regressions-{engine}.json')['result']['rows'];lookup={(r['id'],r['fullVLE']):r for r in focused}
 for full in [False,True]:
  control,candidate=(lookup[(id,full)]['result']['rows'] for id in ['rebuiltB4C','gateA'])
  for before,after in zip(control,candidate):
   check(before['id']==after['id'] and before['args']==after['args'],'focusedInput')
   check(before['base']==after['base'] and before['probes']==after['probes'],'unchangedPHProbes',id=before['id'],engine=engine,full=full)
  summary.append(dict(engine=engine,kind='focused-PH',fullVLE=full,baseFixtures=len(candidate),signedProbes=sum(len(r['probes']) for r in candidate),equivalentBeforeAfter=True))
 shared=read(E/f'shared-{engine}.json')['result']['rows'];lookup={(r['id'],r['fullVLE']):r for r in shared}
 for full in [False,True]:
  control,candidate=(lookup[(id,full)]['results'] for id in ['rebuiltB4C','gateA'])
  for before,after in zip(control,candidate):
   for field in ['state','error']:
    check(before['reused'].get(field)==after['reused'].get(field),'unchangedSharedCaller',engine=engine,full=full,id=before['id'],mode=before['mode'])
    check(after['reused'].get(field)==after['fresh'].get(field),'sharedFreshReused',engine=engine,id=after['id'],mode=after['mode'])
  summary.append(dict(engine=engine,kind='shared-callers',fullVLE=full,records=len(candidate),errors=sum('error' in r['reused'] for r in candidate)))
 lifecycle=read(E/f'lifecycle-{engine}-serialized.json');check('harnessError' not in lifecycle,'lifecycleHarness')
 archive=read(X/f'browser_eos_b4c/evidence/{engine}-candidateB-lifecycle.json')['rows']
 for block in lifecycle['result']['rows']:
  supported=rejected=0
  for old,new in zip(archive,block['original']['rows']):
   for expected,actual in zip([old['base']]+old['sequences'],new['operations']):
    if 'error' in expected:
     rejected+=1;check('error' in actual and 'within 1e-4 %' in actual['error']['message'] and 'Assertion failed' not in actual['error']['message'],'historicalPTMeaning',engine=engine)
    else:
     supported+=1;check(actual.get('value',{}).get('values')==expected['state'],'historicalSupportedBits',engine=engine)
  check(supported==315 and rejected==6,'historicalLifecycleCounts',engine=engine,supported=supported,rejected=rejected)
  synthetic=0
  for row in block['javascript']['rows']:
   if row['synthetic'] and row['expectReject']:
    synthetic+=1;check(row['error']['nativeException'] is None,'syntheticNativeOwnership',engine=engine)
    lo,hi=row['events'];events=block['javascript']['events'][lo:hi];check(not any(e['kind'].startswith('__cxa_') for e in events),'syntheticCleanup',engine=engine)
  life=block['lifecycle'];check(life['deleted'] and life['secondDelete'] and life['invalidReuse'],'disposalContract',engine=engine)
  operations=[o for r in life['rows'] for o in r['operations']]
  check(all(r['before']['stack']==r['after']['stack'] for r in operations),'lifecycleStacks',engine=engine)
  summary.append(dict(engine=engine,artifact=block['id'],kind='lifecycle',originalSupported=supported,originalPTRefused=rejected,variants=len(life['rows']),supported=sum('value' in r for r in operations),rejected=sum('error' in r for r in operations),syntheticRefusals=synthetic,disposal=True))
 c1=read(E/f'c1-{engine}-explicit-bar.json');check('harnessError' not in c1,'C1Harness',engine=engine)
 lookup={(r['id'],r['fullVLE']):r for r in c1['result']['rows']}
 for full in [False,True]:
  before,after=(lookup[(id,full)] for id in ['rebuiltB4C','gateA'])
  for control,candidate in zip(before['cases'],after['cases']):
   check(bool(control.get('state'))==bool(candidate.get('state')),'strictAdapterOutcomeChanged',engine=engine,full=full,key=candidate['key'])
   if not full:check(candidate.get('error') and not candidate.get('state'),'originalSevenRefusal',engine=engine,key=candidate['key'])
  for r in after['hazards']:check(r['qualificationBlocker'] and not r['certified'],'hazardUnqualified')
  summary.append(dict(engine=engine,kind='C1',fullVLE=full,originalSevenRefused=sum(bool(r.get('error')) for r in after['cases']),unqualifiedReturns=sum(bool(r.get('state')) for r in after['cases']),guardOutcomeEquivalent=True,hazardsUnqualified=True))
sources={}
for name in ['libexceptions.js','libexceptions_stub.js','cxa_exception.h','cxa_exception_emscripten.cpp']:
 preserved=X/'browser_eos_b6/evidence'/name
 actual=Path('/workspace/b7-work/emsdk/upstream/emscripten')/('src/lib/'+name if name.endswith('.js') else 'system/lib/libcxxabi/src/'+name)
 h=hashlib.sha256(actual.read_bytes()).hexdigest();check(h==hashlib.sha256(preserved.read_bytes()).hexdigest(),'pinnedRuntimeSource',name=name);sources[name]=h
out=dict(passed=not failures,failures=failures,summary=summary,pinnedRuntimeSources=sources,acceptedC1CodeUnchanged=True,applicableEssentialMainThreadRegressionsPassed=not failures,workersAndA2Pending=True)
target=E/'regression-audit.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n');print('Regression/lifecycle/C1 audit',out['passed'],'failures',len(failures));print(failures[:8]);sys.exit(bool(failures))
