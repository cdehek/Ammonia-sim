"""Independent reporting ledger; failed/unsupported rows remain in raw evidence."""
import hashlib,json,os,statistics
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'));R=B.parents[2]
def read(n):return json.loads((E/n).read_text())
def save(n,d):
 p=E/n;assert not p.exists();p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
gate=read('focused-gate.json');assert gate['eligibleForLimitedA2']
out=dict(classification='PARTIAL / INCONCLUSIVE',fullQualification=False,regressions={},A2={},performance={},limitations={})
for engine in ['chromium','webkit']:
 old=read(f'{engine}-control44-focused.json');new=read(f'{engine}-liquid44-focused.json');comparisons=[]
 for a,b in zip(old['rows'],new['rows']):
  assert a['id']==b['id'];comparisons.append(dict(id=a['id'],baseEqual=a.get('base')==b.get('base'),probesEqual=a.get('probes')==b.get('probes')))
 b1=next(c for c in comparisons if c['id']=='B1-liquid-precision');vapor=next(c for c in comparisons if c['id']=='B1-vapor-regression');assert b1['baseEqual']and b1['probesEqual']and vapor['baseEqual']and vapor['probesEqual']
 physical={r['id']:r['physicalPhase']for r in gate['browser'][engine]['rows']}
 unrelated=[c for c in comparisons if physical[c['id']]in ['gas','equilibrium']];assert all(c['baseEqual']for c in unrelated)
 oldguards=[r['id']for r in old['rows']if r.get('inventories',{}).get('C',{}).get('acceptedAdapterError')]
 newguards=[r['id']for r in new['rows']if r.get('inventories',{}).get('C',{}).get('acceptedAdapterError')];assert oldguards==newguards
 endpointRows=[r for r in new['rows']if r['id'].startswith('ULP-')or r['id'].endswith('-0.0')]
 endpointSummary=[dict(id=r['id'],args=r['args'],phase=r['base']['phase'],Q=r['base']['state']['Q'],rho=r['base']['state']['rho'],T=r['base']['state']['T'],canonical=r['inventories']['C'].get('differences'),canonicalPass=r['inventories']['C']['canonicalPass'],adapterError=r['inventories']['C'].get('acceptedAdapterError'))for r in endpointRows]
 out['regressions'][engine]=dict(B1Unchanged=True,vaporUnchanged=True,physicalGasAndCoexistenceBasesUnchanged=len(unrelated),comparisons=comparisons,endpointSummary=endpointSummary,adapterGuardFailureIdentitiesUnchanged=newguards,invalidUpperBand=[dict(id=r['id'],Q=r['base']['state']['Q'])for r in new['rows']if r['base']['state']['Q']>1 and r['base']['phase']==6])
 out['A2'][engine]={}
 for case in ['zero','cold','warm','feed-step','heat-reversal']:
  d=read(f'{engine}-A2-{case}.json');assert 'error'not in d,d
  if case=='zero':
   assert all(r.get('trial',{}).get('completed')and r.get('exactTrialStatePreserved')and'error'not in r for r in d['rows']);out['A2'][engine][case]=dict(passed=True,exactTrialStatePreserved=True,work=d['rows'][0]['trial']['work'])
  else:
   assert d['completedAllSelectedSamples'];assert all(r['record']['stop']is None and r['record']['seconds']==t for r,t in zip(d['rows'],d['samples']))
   cons=d['rows'][-1]['conservation'];assert all(v<(1e-8 if'mass'in k.lower()else 1e-6)for k,v in cons.items())
   out['A2'][engine][case]=dict(passed=True,samples=d['samples'],conservation=cons,elapsedSeconds=d['elapsedSeconds'])
def strip_times(x):
 if isinstance(x,dict):return {k:strip_times(v)for k,v in x.items()if k!='elapsedSeconds'}
 if isinstance(x,list):return [strip_times(v)for v in x]
 return x
control=read('native-control44.json');repair=read('native-liquid44.json');nativeB1=[]
for a,b in zip(control['rows'],repair['rows']):
 assert a['request']['id']==b['request']['id']
 if a['request']['id']in ['B1-liquid-precision','B1-vapor-regression']:
  assert strip_times(a)==strip_times(b);nativeB1.append(a['request']['id'])
roots=[r['base']['reference']for r in repair['rows']if'reference'in r.get('base',{})];assert all(r['converged']for r in roots)
extraControl=read('extra-native-control44.json')['rows'];extraRepair=read('extra-native-liquid44.json')['rows'];shared=[]
for a,b in zip(extraControl,extraRepair):
 assert a.get('label')==b.get('label')and a.get('pair')==b.get('pair')and a.get('p')==b.get('p')
 if'pair'in b:
  assert'error'not in b
  if b['phaseReference']=='liquid':assert b['state']['values']['phase']==0
  else:assert a==b
  shared.append(dict(pair=b['pair'],p=b['p'],physicalPhase=b['phaseReference'],backendPhase=b['state']['values']['phase'],residuals=b['eosResiduals'],canonicalPass=b['inventory']['canonicalPass']))
 else:assert a==b
out['regressions']['native']=dict(B1AndVaporRowsUnchanged=nativeB1,independentRoots=len(roots),allConverged=True,sharedCaloricCallers=shared,domainCasesUnchanged=len(extraRepair)-len(shared))
for platform in ['native','chromium','webkit']:
 rows={}
 for build in ['control44','liquid44']:
  name=f'performance-native-{build}.json'if platform=='native'else f'{platform}-{build}-performance.json';d=read(name)
  samples=d['rows'];groups={}
  for g in sorted({r['group']for r in samples}):
   x=[r for r in samples if r['group']==g];assert all(not r['errors']for r in x)
   micros=[r['elapsedSeconds']*1e6/r['calls']if platform=='native'else r['elapsedMS']*1000/r['calls']for r in x];groups[g]=dict(medianMicrosecondsPerCall=statistics.median(micros),roundMicrosecondsPerCall=micros)
  rows[build]=dict(groups=groups,init=d.get('init'),maxRSSKiB=d.get('maxRSSKiB'),memoryBytes=d.get('memoryBytes'),jsHeap=d.get('jsHeap'))
 rows['repairOverControl']={g:rows['liquid44']['groups'][g]['medianMicrosecondsPerCall']/rows['control44']['groups'][g]['medianMicrosecondsPerCall']for g in rows['control44']['groups']}
 out['performance'][platform]=rows
out['limitations']=dict(fullVLE35bar=read('full-vle-35bar-fixed-inventory-control.json')['comparisons'],native72='Historical B3 three 35-bar DU exceptions are preserved unchanged; no claim of a fresh 7.2 campaign.',vapor='UNRESOLVED, unchanged failure',upperQuality='UNRESOLVED, unchanged invalid extrapolation',A2='Limited selected fixtures only; full matrix, temporal refinement and frozen-reference qualification pending',physicalIPad=False)
start=read('preservation-start.json');changed=[p for p,h in start['trackedSHA256'].items()if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];assert not changed
stages=[read(f'source-stage-{n}.json')for n in ['control44','liquid44']];modified=[p for p,h in stages[0]['trackedSourceSHA256'].items()if stages[1]['trackedSourceSHA256'][p]!=h];assert modified==['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp'],modified
out['preservation']=dict(originalTrackedFiles=len(start['trackedSHA256']),changed=[],controlToRepairModifiedSource=modified,B1FlashSHA256=stages[1]['trackedSourceSHA256']['src/Backends/Helmholtz/FlashRoutines.cpp'])
out['classification']='FOCUSED REPAIR PASS'
save('summary.json',out);print(out['classification']);print('Unchanged starting files:',out['preservation']['originalTrackedFiles']);print('Performance multipliers:',{k:v['repairOverControl']for k,v in out['performance'].items()})
