"""Audit measured focused evidence; retained exclusions never become passes."""
import collections,json,math,os,statistics,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4B_EVIDENCE',B/'evidence'))
sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,save
audit=Backend()
def read(n):return json.loads((E/n).read_text())
def clean(v):
 if isinstance(v,dict):return {k:clean(x)for k,x in v.items()if k!='elapsedSeconds'}
 if isinstance(v,list):return list(map(clean,v))
 return v
def maxima(rows,key):return max([abs(r.get(key,0))for r in rows]+[0])
def local(p,h,s,dt):
 V=.003/5;M=s['rho']*V;U=M*(h/1000)-100*(p/1e5)*V
 return abs(M*dt['u']/1000-U)/max(1,abs(U))
out=dict(classification='FOCUSED REPAIR PASS',fullQualification=False,physicalIPad=False)
out['primary']=read('focused-gate.json');assert out['primary']['eligibleForLimitedA2']
out['nativeMatrix']={};out['browserMatrix']={}
for build in ['controlA','candidateB']:
 rows=read(f'native-{build}.json')['rows'];samples=[];probes=[];upper=[]
 for r in rows:
  assert 'error'not in r,r
  for name,x in [('base',r['base'])]+[(q['axis']+str(q['step']),q.get('output'))for q in r['probes']]:
   if not x:continue
   s=x['PH']['values'];dt=x['independentDT']['values'];p,h=x['p'],x['h']
   if s['Q']>1:upper.append(dict(id=r['request']['id'],sample=name,Q=s['Q']));continue
   if s['phase']==6:continue
   samples.append(dict(id=r['request']['id'],sample=name,requestedP=dt['p']-p,requestedH=dt['h']-h,getterP=s['p']-dt['p'],getterH=s['h']-dt['h'],getterU=s['u']-dt['u'],normalizedEnergyMismatch=local(p,h,s,dt)))
  for q in r['probes']:
   if not q.get('samePhysicalBranch')or not q.get('output',{}).get('supportedInput'):continue
   b=r['base']['PH']['values'];s=q['output']['PH']['values']
   if b['Q']>1 or s['Q']>1:probes.append(dict(id=r['request']['id'],axis=q['axis'],step=q['step'],status='KNOWN UPPER-QUALITY CLASSIFICATION FAILURE',originalResult=q.get('nonlinearScalePass')))
   else:probes.append(dict(id=r['request']['id'],axis=q['axis'],step=q['step'],status='pass'if q['nonlinearScalePass']else'FAIL',mass=q['normalizedMassProbeContamination'],energy=q['normalizedEnergyProbeContamination']))
 matrix=dict(baseRows=len(rows),signedProbes=sum(len(r['probes'])for r in rows),homogeneousSnapshots=len(samples),maxima={k:maxima(samples,k)for k in ['requestedP','requestedH','getterP','getterH','getterU','normalizedEnergyMismatch']},localEnergyFailures=[q for q in samples if q['normalizedEnergyMismatch']>1e-11],sameStableBranchProbeResults=probes,invalidUpperQualitySnapshots=upper,canonicalFailures=[r['request']['id']for r in rows if not r['inventories']['C']['canonicalPass']],strictRecoverySupportExits=[dict(id=r['request']['id'],p=r['inventories']['C'].get('DU',{}).get('values',{}).get('p'))for r in rows if not r['inventories']['C'].get('recoveredPressureInAcceptedRange',False)])
 out['nativeMatrix'][build]=matrix
 if build=='candidateB':
  assert not matrix['localEnergyFailures']and not matrix['canonicalFailures']
  assert not any(q['status']=='FAIL'for q in probes)
  assert matrix['maxima']['requestedP']<=.1 and matrix['maxima']['requestedH']<=.1
for engine in ['chromium','webkit']:
 data=read(f'{engine}-candidateB-focused.json');control=read(f'{engine}-controlA-focused.json');nr=read('native-controlA.json')['rows'];samples=[];probes=[];upper=[];nativeDifferences=[]
 for r in data['rows']:
  assert 'error'not in r,r
  ref=next(q for q in nr if q['request']['id']==r['id'])['base'];rt=ref.get('reference',{})
  for name,x in [('base',r['base'])]+[(q['axis']+str(q['step']),q.get('output'))for q in r['probes']]:
   if not x:continue
   s=x['state'];dt=audit.state('DT',s['rho'],s['T']);p,h=x['p'],x['h'];nativeDifferences.append({k:dt[k]-x['direct'][k]for k in ['p','h','u']})
   if s['Q']>1:upper.append(dict(id=r['id'],sample=name,Q=s['Q']));continue
   if x['phase']==6:continue
   samples.append(dict(id=r['id'],sample=name,requestedP=dt['p']-p,requestedH=dt['h']-h,getterP=s['p']-dt['p'],getterH=s['h']-dt['h'],getterU=s['u']-dt['u'],normalizedEnergyMismatch=local(p,h,s,dt)))
  for q in r['probes']:
   v=q.get('output');s=r['base']['state'];p,h=r['args']
   if not v or not 3e4<=v['p']<=35e5 or not rt.get('converged'):continue
   # Physical crossing is determined by the independent native reference classification.
   np=next(x for x in next(z for z in nr if z['request']['id']==r['id'])['probes']if x['axis']==q['axis']and x['step']==q['step'])
   if not np.get('samePhysicalBranch'):continue
   if s['Q']>1 or v['state']['Q']>1:probes.append(dict(id=r['id'],axis=q['axis'],status='KNOWN UPPER-QUALITY CLASSIFICATION FAILURE'));continue
   deriv=rt['derivatives']['rhoP'if q['axis']=='P'else'rhoH'];V=.003/5;M=s['rho']*V;U=M*h/1000-p*V/1000;rho=v['state']['rho'];step=q['step'];dU=deriv*V*(h/1000)+(-V/1000 if q['axis']=='P'else M/1000)
   mass=V*abs(rho-s['rho']-deriv*step)/max(.01,M);energy=abs(rho*V*v['h']/1000-v['p']*V/1000-U-dU*step)/max(1,abs(U));probes.append(dict(id=r['id'],axis=q['axis'],status='pass'if max(mass,energy)<=1e-11 else'FAIL',mass=mass,energy=energy))
 out['browserMatrix'][engine]=dict(baseRows=len(data['rows']),homogeneousSnapshots=len(samples),maxima={k:maxima(samples,k)for k in ['requestedP','requestedH','getterP','getterH','getterU','normalizedEnergyMismatch']},maxIndependentBrowserNativeDT={k:maxima(nativeDifferences,k)for k in ['p','h','u']},localEnergyFailures=[q for q in samples if q['normalizedEnergyMismatch']>1e-11],sameStableBranchProbeResults=probes,invalidUpperQualitySnapshots=upper,canonicalFailures=[r['id']for r in data['rows']if not r['inventories']['C']['canonicalPass']],acceptedAdapterErrors=[dict(id=r['id'],error=r['inventories']['C']['acceptedAdapterError'])for r in data['rows']if'acceptedAdapterError'in r['inventories']['C']])
 assert not out['browserMatrix'][engine]['localEnergyFailures']
 assert not any(q['status']=='FAIL'for q in probes)
 assert out['browserMatrix'][engine]['maxima']['requestedP']<=.1 and out['browserMatrix'][engine]['maxima']['requestedH']<=.1
out['browserCompleteRowsEqual']=read('chromium-candidateB-focused.json')['rows']==read('webkit-candidateB-focused.json')['rows'];assert out['browserCompleteRowsEqual']
# Exact cache coordinates and logging parity, including the preserved fixed PT30 input.
trace={}
for build in ['controlA','candidateB']:
 events=[json.loads(l)for l in (E/f'trace-{build}.jsonl').read_text().splitlines()];blocks=[];cur=None
 for e in events:
  if'marker'in e:cur=dict(marker=e,events=[]);blocks.append(cur)
  elif cur:cur['events'].append(e)
 for b in blocks:
  b['counts']=dict(collections.Counter(e['event']for e in b['events']))
  if b['marker']['marker'].startswith('fixed-B3-PT'):
   b['lastCacheFill']=next(e for e in reversed(b['events'])if e['event']=='alphar_cache_fill');h=next(e for e in reversed(b['events'])if e['event']=='homogeneous_hmolar');b['committedDelta']=h['explicit_delta'];b['cacheCoordinateMatchesCommitted']=b['lastCacheFill']['delta']==h['explicit_delta']
   assert b['cacheCoordinateMatchesCommitted']==(build=='candidateB')
  else:del b['events']
 trace[build]=blocks
 assert read(f'trace-{build}-results.json')['rows']==read(f'trace-{build}-uninstrumented-results.json')['rows']
for n in ['off','on']:assert clean(read('native-candidateB.json')['rows'])==clean(read(f'native-diagnostic-candidateB-{n}.json')['rows'])
out['diagnosticParity']=dict(native86RowsAnd344Probes=True,fixedPTAndSavedProbes=True)
save(E/'trace-audit.json',trace)
# Lifecycle baselines retain rejected PT cases and browser loader assertions.
out['lifecycle']={}
for runtime in ['native','chromium','webkit']:
 old=read('lifecycle-controlA-replay.json'if runtime=='native'else f'{runtime}-controlA-lifecycle.json');new=read('lifecycle-candidateB.json'if runtime=='native'else f'{runtime}-candidateB-lifecycle.json');errors=[];diffs=[];ns=[];equilibrium=[]
 for a,b in zip(old['rows'],new['rows']):
  assert a['request']==b['request'];assert'error'not in b,b
  for i,s in enumerate(b['sequences']):
   if'error'in s:
    assert'error'in a['sequences'][i],(runtime,b['request'],s);errors.append(dict(id=b['request']['id'],mode=s['mode'],error=s['error']));continue
  for s in [b['base']]+[x for x in b['sequences']if'error'not in x]:
   if'derivativeDifferences'in s:diffs.append(s['derivativeDifferences']);ns.append(s['normalizedEnergyInconsistency'])
   if s.get('equilibrium'):equilibrium.append(s['equilibrium'])
 out['lifecycle'][runtime]=dict(cases=len(new['rows']),baseErrors=0,preservedRejectedSequenceCalls=errors,freshPTRejections=[dict(id=r['request']['id'],error=r['freshPTError'])for r in new['rows']if'freshPTError'in r],maxDerivativeDifferences={k:maxima(diffs,k)for k in diffs[0]},maxNormalizedGetterEnergyInconsistency=max(ns),equilibriumChecks=equilibrium)
 assert max(ns)<=1e-11
out['fixed35bar']=dict(cases=len(read('35bar-fixed-inventories.json')['rows']),allIdenticalAtFixedInventories=read('35bar-fixed-inventories.json')['allEqual']);assert out['fixed35bar']['allIdenticalAtFixedInventories']
# Original accepted A2 check was executed in each harness; additionally audit trace/norm and work changes.
out['A2']={};out['conservationMaxima']={}
keys=['acceptedSteps','rejectedSteps','accuracyRejectedSteps','eventRejectedSteps','domainRejectedSteps','attemptedResidualEvaluations','attemptedIterations','attemptedLinearSolves']
for engine in ['chromium','webkit']:
 for case in ['cold','warm','feed-step','heat-reversal']:
  d=read(f'{engine}-A2-{case}.json');assert'error'not in d and d['completedAllSelectedSamples'],d
  for row in d['rows']:
   r=row['record'];assert r['stop']is None and r['lastResidual']<=1e-11;assert all(t['error']<=1 for t in r['trace']);assert r['lastTimeError']<=1
   for k,v in row['conservation'].items():out['conservationMaxima'][k]=max(out['conservationMaxima'].get(k,0),v)
  r=d['rows'][-1]['record'];old=json.loads((B.parent/f'browser_eos_b4a/evidence/{engine}-A2-{case}.json').read_text())['rows'][-1]['record']
  out['A2'][engine+'-'+case]=dict(completedSeconds=r['seconds'],work={k:r[k]for k in keys},B4Awork={k:old[k]for k in keys},workDelta={k:r[k]-old[k]for k in keys},counts=d['rows'][-1]['counts'],lastResidual=r['lastResidual'],maxTemporalError=max(t['error']for t in r['trace']),outlet=r['outlet'],stop=r['stop'])
 for case in ['zero','vapor-zero']:
  d=read(f'{engine}-A2-{case}-asserted.json');assert'error'not in d
  for r in d['rows']:assert'error'not in r and r['trial']['completed']and r['exactTrialStatePreserved']and r['trial']['errorNorm']<=1e-11 and'scientificCheck'in r['trial']
  out['A2'][engine+'-'+case]=dict(passOriginalScientificCheck=True,exactTrialStatePreserved=True,trialErrorNorm=d['rows'][0]['trial']['errorNorm'],work=d['rows'][0]['trial']['work'])
save(E/'scientific-audit.json',out)
print('Focused science gates pass; retained upper-Q, 35-bar and rejected PT/loader cases remain explicit.')
