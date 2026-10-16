"""Primary scientific gates retain original normalization and budgets."""
import json,sys,os
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4B_EVIDENCE',B/'evidence'))
sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,save
audit=Backend()
ids=['B1-vapor-regression','approach-30298.937123458254-liquid-0.001','B1-liquid-precision']
def read(n):return json.loads((E/n).read_text())
def energy(p,h,s,dt):
 V=.003/5;M=s['rho']*V;U=M*(h/1000)-100*(p/1e5)*V
 return dict(M=M,U_kJ=U,V=V,physicalEOSenergyKJ=M*dt['u']/1000,normalizedEnergyMismatch=abs(M*dt['u']/1000-U)/max(1,abs(U)),originalNonlinearScale=1e-11)
out=dict(native={},browser={},eligibleForLimitedA2=False)
nativepass=True
for build in ['controlA','candidateB']:
 d=read(f'native-{build}.json');rows=d['rows'];results={}
 for ident in ids:
  r=next(r for r in rows if r['request']['id']==ident);base=r['base'];s=base['PH']['values'];dt=base['independentDT']['values'];p,h=r['request']['args'];en=energy(p,h,s,dt)
  requested=dict(p=dt['p']-p,h=dt['h']-h,T=s['T']-base['reference']['state']['T'])
  requestedPass=all(abs(requested[k])<=v for k,v in dict(p=.1,h=.1,T=1e-4).items())
  getter={k:s[k]-dt[k]for k in ['p','h','u']}
  probes=[q for q in r['probes']if q.get('samePhysicalBranch')and q.get('output',{}).get('supportedInput')]
  passed=requestedPass and en['normalizedEnergyMismatch']<=1e-11 and r['inventories']['C']['canonicalPass'] and all(q['nonlinearScalePass']for q in probes)
  if ident=='approach-30298.937123458254-liquid-0.001':passed &= s['phase']==0
  results[ident]=dict(returned=s,independentDT=dt,requestedResiduals=requested,getterMinusIndependent=getter,inventoryEnergy=en,canonical=r['inventories']['C'],probes=probes,passOriginalRequirements=bool(passed))
  if build=='candidateB':nativepass &= passed
 out['native'][build]=results
browserpass=True
for engine in ['chromium','webkit']:
 pth=E/f'{engine}-candidateB-focused.json'
 if not pth.exists():browserpass=False;continue
 d=read(pth.name);results={}
 for ident in ids:
  r=next(r for r in d['rows']if r['id']==ident);s=r['base']['state'];p,h=r['args'];dt=audit.state('DT',s['rho'],s['T']);en=energy(p,h,s,dt)
  n=out['native']['candidateB'][ident];requested=dict(p=dt['p']-p,h=dt['h']-h,T=s['T']-n['returned']['T'])
  passed=all(abs(requested[k])<=v for k,v in dict(p=.1,h=.1,T=1e-4).items()) and en['normalizedEnergyMismatch']<=1e-11 and r['inventories']['C']['canonicalPass']
  if ident=='B1-vapor-regression':passed &= all(abs(v)<=lim for v,lim in zip([r['PTcacheDifference'][k]for k in ['p','h','u']],[.1,.1,.1]))
  results[ident]=dict(returned=s,phase=r['base']['phase'],independentNativeDT=dt,browserNativeDTdifferences={k:r['base']['direct'][k]-dt[k]for k in ['p','h','u']},requestedResiduals=requested,inventoryEnergy=en,canonical=r['inventories']['C'],passOriginalRequirements=bool(passed))
  browserpass &= passed
 out['browser'][engine]=results
out.update(nativePrimaryGate=bool(nativepass),browserPrimaryGate=bool(browserpass),eligibleForLimitedA2=bool(nativepass and browserpass))
save(E/'focused-gate.json',out);print('native',nativepass,'browser',browserpass,'eligible',out['eligibleForLimitedA2'])
