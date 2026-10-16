"""Fail closed on original focused physical, canonical and numerical gates."""
import argparse,json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,save
ap=argparse.ArgumentParser();ap.add_argument('--native-only',action='store_true');ap.add_argument('--output',required=True);args=ap.parse_args()
audit=Backend();failures=[]
def read(n):return json.loads((E/n).read_text())
def check(ok,kind,**details):
 if not ok:failures.append(dict(kind=kind,**details))
def energy(p,h,s,dt):
 V=.003/5;M=s['rho']*V;U=M*(h/1000)-100*(p/1e5)*V
 return abs(M*dt['u']/1000-U)/max(1,abs(U))
def maxima(rows):return {k:max([abs(r.get(k,0)) for r in rows]+[0]) for k in ['p','h','T','getterP','getterH','getterU','normalizedEnergy']}
control=read('native-controlA.json')['rows'];candidate=read('native-candidateB.json')['rows'];out=dict(native={},browser={},failures=failures)
ids=['B1-liquid-precision','approach-30298.937123458254-liquid-0.001','B1-vapor-regression']
for label,rows in [('controlA',control),('candidateB',candidate)]:
 samples=[];probes=[];upper=[];changes=[];canonical=[];errors=[]
 for r in rows:
  ident=r['request']['id'];old=next(q for q in control if q['request']['id']==ident)
  if 'error' in r:errors.append(r);continue
  base=r['base'];s=base['PH']['values'];p,h=r['request']['args']
  check(r['request']==old['request'],'changedOriginalRequest',id=ident)
  check([(q['axis'],q['step'],q.get('output',{}).get('inputBits')) for q in r['probes']]==[(q['axis'],q['step'],q.get('output',{}).get('inputBits')) for q in old['probes']],'changedOriginalSignedProbes',id=ident)
  if s!=old['base']['PH']['values']:changes.append(dict(id=ident,before=old['base']['PH'],after=base['PH'],physicalPhase=base['physicalPhase']))
  for name,x in [('base',base)]+[(q['axis']+str(q['step']),q.get('output')) for q in r['probes']]:
   if not x:continue
   z=x['PH']['values'];dt=x['independentDT']['values'];pp,hh=x['p'],x['h']
   if z['Q']>1:upper.append(dict(id=ident,sample=name,Q=z['Q']))
   if z['phase']==6:continue
   v=dict(id=ident,sample=name,p=dt['p']-pp,h=dt['h']-hh,getterP=z['p']-dt['p'],getterH=z['h']-dt['h'],getterU=z['u']-dt['u'],normalizedEnergy=energy(pp,hh,z,dt))
   rt=x.get('reference',{})
   if rt.get('converged'):
    v['T']=z['T']-rt['state']['T'];v['stability']=rt['stability']
   samples.append(v)
   if label=='candidateB':
    check(abs(v['p'])<=.1 and abs(v['h'])<=.1 and abs(v.get('T',0))<=1e-4,'requestedEOS',**v)
    check(v['normalizedEnergy']<=1e-11,'localNonlinearEnergy',**v)
    check(abs(v['getterP'])<=.1 and abs(v['getterH'])<=.1 and abs(v['getterU'])<=.1,'getterConsistency',**v)
  c=r['inventories']['C'];canonical.append(dict(id=ident,result=c))
  if label=='candidateB':check(c['canonicalPass'],'canonicalRecovery',id=ident,result=c)
  for q in r['probes']:
   if q.get('samePhysicalBranch') and q.get('output',{}).get('supportedInput'):
    probes.append(dict(id=ident,axis=q['axis'],step=q['step'],mass=q['normalizedMassProbeContamination'],energy=q['normalizedEnergyProbeContamination'],passOriginal=q['nonlinearScalePass']))
    if label=='candidateB':check(q['nonlinearScalePass'],'signedSamePhaseProbe',id=ident,probe=q)
  if label=='candidateB' and old['base']['physicalPhase']=='gas' and old['base']['PH']['values']['Q']>1:
   check(s['phase']==5 and s['Q']<0,'resolvedUpperVaporDispatch',id=ident,state=s)
  if label=='candidateB' and ident in ids:
   check(s['phase']==(5 if ident=='B1-vapor-regression' else 0),'inheritedRepairPhase',id=ident,state=s)
 out['native'][label]=dict(baseRows=len(rows),signedProbes=sum(len(r['probes']) for r in rows),homogeneousSnapshots=samples,maxima=maxima(samples),invalidUpperQualities=upper,changedStates=changes,canonical=canonical,samePhysicalSupportedProbes=probes,errors=errors)
 if label=='candidateB':check(not upper and not errors,'nativeInvalidQualityOrErrors',upper=upper,errors=errors)
if not args.native_only:
 for engine in ['chromium','webkit']:
  data=read(f'{engine}-candidateB-focused.json');before=read(f'{engine}-controlA-focused.json');samples=[];probes=[];upper=[];canonical=[];changes=[]
  check('rows' in data,'browserMatrixMissing',engine=engine,result=data)
  for r in data.get('rows',[]):
   ident=r['id'];nr=next(q for q in control if q['request']['id']==ident);old=next(q for q in before['rows'] if q['id']==ident)
   if 'error' in r:check(False,'browserRowError',engine=engine,row=r);continue
   s=r['base']['state'];p,h=r['args'];ref=nr['base'].get('reference',{})
   if s!=old['base']['state']:changes.append(dict(id=ident,before=old['base'],after=r['base']))
   for name,x in [('base',r['base'])]+[(q['axis']+str(q['step']),q.get('output')) for q in r['probes']]:
    if not x:continue
    z=x['state'];dt=audit.state('DT',z['rho'],z['T']);pp,hh=x['p'],x['h']
    if z['Q']>1:upper.append(dict(id=ident,sample=name,Q=z['Q']))
    if x['phase']==6:continue
    v=dict(id=ident,sample=name,p=dt['p']-pp,h=dt['h']-hh,getterP=z['p']-dt['p'],getterH=z['h']-dt['h'],getterU=z['u']-dt['u'],normalizedEnergy=energy(pp,hh,z,dt))
    if name=='base' and ref.get('converged'):v['T']=z['T']-ref['state']['T']
    samples.append(v);check(abs(v['p'])<=.1 and abs(v['h'])<=.1 and abs(v.get('T',0))<=1e-4 and v['normalizedEnergy']<=1e-11,'browserEOSOrLocalEnergy',engine=engine,**v)
    check(all(abs(z[k]-dt[k])<=.1 for k in ['p','h','u']),'browserGetterConsistency',engine=engine,id=ident,sample=name)
   c=r['inventories']['C'];canonical.append(dict(id=ident,result=c));check(c['canonicalPass'],'browserRawCanonicalRecovery',engine=engine,id=ident,result=c)
   for q in r['probes']:
    n=next(x for x in nr['probes'] if x['axis']==q['axis'] and x['step']==q['step']);v=q.get('output')
    if not v or not n.get('samePhysicalBranch') or not n['output']['supportedInput'] or not ref.get('converged'):continue
    deriv=ref['derivatives']['rhoP' if q['axis']=='P' else 'rhoH'];V=.003/5;M=s['rho']*V;U=M*(h/1000)-p*V/1000;rho=v['state']['rho'];step=q['step'];dU=deriv*V*(h/1000)+(-V/1000 if q['axis']=='P' else M/1000)
    mass=V*abs(rho-s['rho']-deriv*step)/max(.01,M);en=abs(rho*V*v['h']/1000-v['p']*V/1000-U-dU*step)/max(1,abs(U));probes.append(dict(id=ident,axis=q['axis'],step=step,mass=mass,energy=en))
    check(mass<=1e-11 and en<=1e-11,'browserSignedSamePhaseProbe',engine=engine,probe=probes[-1])
  out['browser'][engine]=dict(baseRows=len(data.get('rows',[])),maxima=maxima(samples),homogeneousSnapshots=samples,invalidUpperQualities=upper,samePhysicalSupportedProbes=probes,canonical=canonical,changedStates=changes)
  check(not upper,'browserInvalidUpperQuality',engine=engine,upper=upper)
 out['browserRowsEqual']=read('chromium-candidateB-focused.json').get('rows')==read('webkit-candidateB-focused.json').get('rows')
 check(out['browserRowsEqual'],'browserParity')
out.update(passOriginalFocusedRequirements=not failures,eligibleForLimitedA2=not args.native_only and not failures,fullQualification=False,physicalIPad=False)
save(Path(args.output),out);print('Focused gates',not failures,'failures',len(failures))
if failures:print([(r['kind'],r.get('id')) for r in failures[:20]])
sys.exit(bool(failures))
