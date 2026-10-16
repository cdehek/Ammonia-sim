"""Independent assertions over preserved actual results; no property mutation."""
import json,hashlib,statistics,subprocess,struct
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence'
def read(n):return json.loads((E/n).read_text())
def write(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
def same(a,b,label):assert a==b,label
A=read('gate-a-summary.json');assert A['decision']=='ROOT CAUSE CONFIRMED' and len(A['instances'])==4
assert all(r['secondaryAssertions']==6 and r['liveReferenceCounts']==[0]*6 and r['controlDiagnosticRowsExact'] for r in A['instances'])
refs=json.loads((X/'browser_eos_b4c/evidence/native-candidateB.json').read_text())['rows']
summary={};matrix=[];perf={};scientific={}
for engine in ['chromium','webkit']:
 original=read(f'gate-b-{engine}-0.json');corrected=read(f'gate-corrected-{engine}-0.json');assert 'harnessError' not in original and 'harnessError' not in corrected
 r={**original['result'],**{k:v for k,v in corrected['result'].items() if k!='passed'}}
 r['javascriptPaths']=read(f'gate-diagnostic-complete-{engine}-0.json')['result']['javascriptPaths']
 final=read(f'gate-final-{engine}-0.json')['result']
 assert final['passed'] and final['defaultSelection']['passed'] and final['workers']['passed']
 r['originalCandidate']=final['originalCandidate'];r['originalDiagnostic']=final['originalDiagnostic']
 archive=json.loads((X/f'browser_eos_b4c/evidence/{engine}-candidateB-lifecycle.json').read_text())
 for replica in [0,1]:same(read(f'gate-a-{engine}-{replica}.json')['runs'][0]['result']['rows'],archive['rows'],'full historical lifecycle reproduction')
 for old,current in zip(archive['rows'],r['originalCandidate']['rows']):
  for saved,op in zip([old['base']]+old['sequences'],current['operations']):
   if 'value' in op:
    expected={k:struct.pack('>d',v).hex() for k,v in saved['state'].items()}
    same(op['value']['bits'],expected,'archived supported lifecycle bits')
 same(final['workers']['rows'][1]['result']['lastSupported'],r['workers']['rows'][1]['result']['lastSupported'],'final worker supported bits')
 for k,v in r.items():
  if isinstance(v,dict):assert v.get('passed') is not False,(engine,k,v.get('error'))
 c,z,d=[r[k] for k in ['originalControl','originalCandidate','originalDiagnostic']]
 assert len(c['rows'])==len(z['rows'])==len(d['rows'])==47
 errorCount=successCount=0
 for cr,zr,dr in zip(c['rows'],z['rows'],d['rows']):
  for co,zo,do in zip(cr['operations'],zr['operations'],dr['operations']):
   same(co['request'],zo['request'],'fixed operation request');same(zo['request'],do['request'],'instrumented input identity')
   if 'value'in co:
    same(co['value'],zo['value'],'original supported bits');successCount+=1
   else:
    errorCount+=1;assert 'referenceCount > 0'in co['error']['message']
    assert 'Saturation pressure'in zo['error']['message'] and 'Assertion' not in zo['error']['message']
    assert zo['error']['nativeException']['representation']=='CppException'
   same(zo.get('value'),do.get('value'),'diagnostic supported values');same(zo.get('error',{}).get('message'),do.get('error',{}).get('message'),'diagnostic errors')
 assert errorCount==6
 catches=[(i,e) for i,e in enumerate(d['events']) if e['kind']=='loader-catch'];assert len(catches)==6
 for i,e in catches:
  assert e['header']['referenceCount']==0
  following=d['events'][i+1:];bc=next(x for x in following if x['kind']=='__cxa_begin_catch' and x['stage']=='before');ec=next(x for x in following if x['kind']=='__cxa_end_catch' and x['stage']=='before')
  assert bc['header']['referenceCount']==0 and ec['header']['referenceCount']==1 and ec['header']['caught']==1
 L=r['lifecycleCandidate'];assert len(L['rows'])==32 and L['deleted'] and L['secondDelete'] and L['invalidReuse']
 assert L['secondDelete']['constructor']=='BindingError'
 assert L['invalidReuse']['constructor']=='Error' and 'Cannot pass deleted object' in L['invalidReuse']['message'] and not L['invalidReuse']['nativeException']
 valid=refused=freshComparisons=0
 for row in L['rows']:
  if row['fresh']:assert row['deleted']
  for o in row['operations']:
   same(o['before']['stack'],o['after']['stack'],'per-call stack')
   if o['expectReject']:
    assert 'error'in o and 'value'not in o and 'Assertion'not in o['error']['message'];refused+=1
   else:assert 'value'in o and 'error'not in o;valid+=1
   if 'fresh'in o:same(o['value'],o['fresh'],'fresh supported equality');freshComparisons+=1
  matrix.append(dict(engine=engine,sequence=row['name'],fresh=row['fresh'],operations=len(row['operations']),refusals=sum(o['expectReject'] for o in row['operations']),allSupportedFreshComparisonsExact=True,terminalDeleted=row['deleted']))
 for name in {x['name'] for x in L['rows']}:
  reused=next(x for x in L['rows'] if x['name']==name and not x['fresh']);fresh=next(x for x in L['rows'] if x['name']==name and x['fresh'])
  same([o.get('value') for o in reused['operations']],[o.get('value') for o in fresh['operations']],'fresh/reused sequence values')
  same([o.get('error',{}).get('message') for o in reused['operations']],[o.get('error',{}).get('message') for o in fresh['operations']],'fresh/reused sequence errors')
 lowhigh=next(x for x in L['rows'] if x['name']=='low-high-supported' and not x['fresh'])['operations'];lh={k:lowhigh[1]['value']['values'][k]-lowhigh[0]['value']['values'][k] for k in ['p','h','T']};assert abs(lh['p'])<=.1 and abs(lh['h'])<=.1 and abs(lh['T'])<=1e-4
 js=r['javascriptPaths']
 for i,e in enumerate(js['events']):
  if e['kind']=='loader-catch' and 'header' in e:
   assert e['header']['referenceCount']==0
   end=next(v for v in js['events'][i+1:] if v['kind']=='__cxa_end_catch' and v['stage']=='before')
   assert end['header']['referenceCount']==1
   complete=next(v for v in js['events'][i+1:] if v['kind']=='__cxa_end_catch' and v['stage']=='returned')
   assert complete['uncaught']==0 and complete['observedCatchDepth']==0
 for o in js['rows']:
  if o['synthetic']:
   ev=js['events'][o['events'][0]:o['events'][1]];assert not any(e['kind'] in ['__cxa_begin_catch','__cxa_end_catch','decrementExceptionRefcount','incrementExceptionRefcount'] for e in ev),'synthetic must not clean a native ref'
   assert all('header' not in e for e in ev),'synthetic pointer must not be dereferenced by observer'
   assert not o.get('error',{}).get('nativeException')
 assert r['workers']['passed']
 for w in r['workers']['rows']:
  assert w['result']['deleted'] and w['result']['alternations']==64 and w['mainThreadTicks']>0
  same(w['result']['lastSupported'],L['warmup']['value'],'worker/main property bits')
 S=r['science'];assert S['passed'];same(S['control'],S['candidate'],'science control/candidate exact')
 samples=[];probes=[]
 for row in S['candidate']['rows']:
  ref=next(q for q in refs if q['request']['id']==row['id']);s=row['base']['state'];p,h=row['args'];rt=ref['base'].get('reference',{})
  for name,z in [('base',row['base'])]+[(q['axis']+str(q['step']),q.get('output')) for q in row['probes']]:
   assert z is not None
   if z['phase']==6:continue
   a=z['state'];dt=z['direct'];pp,hh=z['p'],z['h'];V=.003/5;M=a['rho']*V;U=M*(hh/1000)-100*(pp/1e5)*V
   v=dict(id=row['id'],sample=name,p=dt['p']-pp,h=dt['h']-hh,normalizedEnergy=abs(M*dt['u']/1000-U)/max(1,abs(U)),getterP=a['p']-dt['p'],getterH=a['h']-dt['h'],getterU=a['u']-dt['u'])
   if name=='base' and rt.get('converged'):v['T']=a['T']-rt['state']['T']
   assert abs(v['p'])<=.1 and abs(v['h'])<=.1 and abs(v.get('T',0))<=1e-4 and v['normalizedEnergy']<=1e-11
   assert all(v[k]==0 for k in ['getterP','getterH','getterU']);samples.append(v)
  for q in row['probes']:
   n=next(z for z in ref['probes'] if z['axis']==q['axis'] and z['step']==q['step']);v=q.get('output')
   if not v or not n.get('samePhysicalBranch') or not n['output']['supportedInput'] or not rt.get('converged'):continue
   deriv=rt['derivatives']['rhoP' if q['axis']=='P' else 'rhoH'];V=.003/5;M=s['rho']*V;U=M*(h/1000)-p*V/1000;rho=v['state']['rho'];st=q['step'];dU=deriv*V*(h/1000)+(-V/1000 if q['axis']=='P' else M/1000)
   mass=V*abs(rho-s['rho']-deriv*st)/max(.01,M);energy=abs(rho*V*v['h']/1000-v['p']*V/1000-U-dU*st)/max(1,abs(U));assert mass<=1e-11 and energy<=1e-11
   probes.append(dict(id=row['id'],axis=q['axis'],step=st,mass=mass,energy=energy))
 assert len(probes)==13
 C=r['c1'];assert C['passed'] and len(C['rows'])==7 and len(C['falseAcceptance'])==2
 assert all(h['qualificationBlocker'] and not h['certified'] for h in C['falseAcceptance'])
 pe=C['ptError'];assert pe['faultKind']=='solver' and pe['evidence']['propertyFailure']['reason']=='inverse-recovery-failure' and pe['evidence']['propertyFailure']['rawCoordinates'] is None
 assert pe['evidence']['propertyFailure']['physicalTrajectoryExit']=='unproved'
 a2rows=[]
 for a2 in C['a2']:
  assert a2['result']['passed'];assert len(a2['result']['rows'])==5
  for o in a2['result']['rows']:
   a2rows.append(dict(label=a2['label'],scenario=o['scenario'],persistent=o.get('persistent'),limit=o.get('limit')))
   if o.get('persistent'):assert o['acceptedRollback'] and o['identityPreserved'] and o['record']['stop']['kind']=='solver' and not o['record']['stop']['evidence']['confirmed']
 P=r['performance'];assert all(f['deleted'] for f in P['factories']);costs={}
 for g in ['PT','rejected-PT','PH','DU','alternating']:
  costs[g]={}
  for label in ['control','candidate']:
   q=[v for v in P['rows'] if v['group']==g and v['label']==label];assert len(q)==3
   assert all(v['failures']==(v['calls'] if g=='rejected-PT' else v['calls']//2 if g=='alternating' else 0) for v in q)
   if label=='candidate':assert all('Assertion' not in (v['firstError'] or '') for v in q)
   costs[g][label]=statistics.median(v['elapsedMS']/v['calls']*1000 for v in q)
  costs[g]['ratio']=costs[g]['candidate']/costs[g]['control']
 perf[engine]=dict(version=original['browserVersion'],medianMicrosecondsPerCall=costs,factories={label:dict(factoryMS=statistics.median(f['factoryMS'] for f in P['factories'] if f['label']==label),disposeMS=statistics.median(f['disposeMS'] for f in P['factories'] if f['label']==label)) for label in ['control','candidate']},samples=len(P['rows']),worker=[{k:v for k,v in w.items() if k!='result'} for w in r['workers']['rows']],linearMemorySizes=sorted({v[k] for v in P['rows'] for k in ['memoryBefore','memoryAfter']}))
 scientific[engine]=dict(independentSamples=samples,originalSignedFDProbes=probes,canonical=S['recovery'],nativeComparisons=S['nativeComparisons'],a2Scenarios=a2rows)
 summary[engine]=dict(version=original['browserVersion'],originalSequences=47,originalSecondaryAssertions=6,candidatePrimaryRefusals=6,unchangedOriginalSuccesses=successCount,sequenceVariants=32,validLifecycleCalls=valid,refusedLifecycleCalls=refused,freshObjectComparisons=freshComparisons,lowHighDifferences=lh,workerAlternationsPerVariant=64,originalSevenRefused=7,unchangedInwardQualificationHazards=2,signedFDProbes=len(probes),C1A2Scenarios=len(a2rows),memoryLeakProof=False,qualificationSources=[f'gate-b-{engine}-0.json',f'gate-corrected-{engine}-0.json',f'gate-diagnostic-complete-{engine}-0.json',f'gate-final-{engine}-0.json',f'abi-{engine}.json'])
 # Bookkeeping check uses final diagnostic code and actual generated callbacks.
 abi=read(f'abi-{engine}.json');control,candidate=abi['rows'];assert control['before']['uncaught']==0 and control['after']['uncaught']==16
 assert candidate['before']==candidate['after']==dict(uncaught=0,observedCatchDepth=0)
 assert all(v['status']==dict(uncaught=0,observedCatchDepth=0) for v in candidate['operations'])
 summary[engine]['candidateUncaughtCountBeforeAfter']=[0,0];summary[engine]['historicalUncaughtCountBeforeAfter']=[0,16]
assert read('native-controls.json')['passed']
# Gate A sealed before candidate existence; no guessed design identity.
root=B.parents[2]
for c in ['6b1c69b','183295983435deea4d59a926dac8b8d86666123c']:
 assert not subprocess.check_output(['git','ls-tree',c,'--',str(B.relative_to(root)/'loader.mjs')],cwd=root)
write('lifecycle-matrix.json',matrix);write('performance-summary.json',perf);write('scientific-audit.json',scientific)
write('verification.json',dict(assessment='FOCUSED LOADER REPAIR PASS',gateA='PASS — ROOT CAUSE CONFIRMED',gateB='PASS — FOCUSED LIFECYCLE REPAIR',engines=summary,nativeSamples=20,originalBudgetsUnchanged=True,broaderBackendAndA2Qualified=False,physicalIPadQualified=False,initialHarnessFailuresRetained=True,allAssertionsPassed=True))
print(json.dumps(summary,indent=2))
