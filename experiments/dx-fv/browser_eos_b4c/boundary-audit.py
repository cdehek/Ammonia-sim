"""Phase-aware boundary, lifecycle and shared-caller regression audit."""
import json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,save
def read(n):return json.loads((E/n).read_text())
failures=[]
def check(ok,kind,**details):
 if not ok:failures.append(dict(kind=kind,**details))
sat=Backend();out=dict(failures=failures,fullVLE={},lifecycle={},shared={},knownLimitations={})
for label in ['controlA','candidateB']:
 rows=read(f'native-{label}-full-vle.json')['rows'];canonical=[];upper=[];equilibrium=[];probes=[]
 for r in rows:
  ident=r['request']['id'];check('error' not in r,'fullVLEBaseError',label=label,id=ident)
  if 'base' not in r:continue
  if not r['inventories']['C']['canonicalPass']:canonical.append(dict(id=ident,p=r['request']['args'][0],error=r['inventories']['C'].get('error')))
  for name,x in [('base',r['base'])]+[(q['axis']+str(q['step']),q.get('output')) for q in r['probes']]:
   if not x:continue
   s=x['PH']['values'];q=s['Q']
   if q>1:upper.append(dict(id=ident,sample=name,Q=q))
   if s['phase']==6 and 0<=q<=1:
    f=x['saturation']['liquid']['values'];g=x['saturation']['vapor']['values'];rho=1/((1-q)/f['rho']+q/g['rho']);V=.003/5
    v=dict(id=ident,sample=name,quality=q,T=s['T']-f['T'],h=s['h']-((1-q)*f['h']+q*g['h']),u=s['u']-((1-q)*f['u']+q*g['u']),normalizedLeverMass=abs(s['rho']-rho)*V/max(.01,s['rho']*V));equilibrium.append(v)
    if label=='candidateB':check(abs(v['T'])<=1e-4 and abs(v['h'])<=.1 and abs(v['u'])<=.1 and v['normalizedLeverMass']<=1e-11,'fullVLEEquilibrium',**v)
   elif label=='candidateB':
    check(abs(x['residuals']['p'])<=.1 and abs(x['residuals']['h'])<=.1,'fullVLEHomogeneousEOS',id=ident,sample=name,residuals=x['residuals'])
  for q in r['probes']:
   if q.get('samePhysicalBranch') and q.get('output',{}).get('supportedInput'):
    probes.append(dict(id=ident,axis=q['axis'],step=q['step'],passOriginal=q['nonlinearScalePass']))
    if label=='candidateB':check(q['nonlinearScalePass'],'fullVLESamePhaseProbe',id=ident,probe=q)
 out['fullVLE'][label]=dict(baseRows=len(rows),invalidUpperQualities=upper,canonicalFailures=canonical,equilibrium=equilibrium,samePhaseProbes=probes)
 if label=='candidateB':check(not upper,'fullVLEUpperQuality',upper=upper)
check(out['fullVLE']['candidateB']['canonicalFailures']==out['fullVLE']['controlA']['canonicalFailures'],'changedFullVLECanonicalFailures')
check(all(r['p']==3500000 for r in out['fullVLE']['candidateB']['canonicalFailures']),'non35barCanonicalFailure')
# Lifecycle exceptions remain explicit, including inherited legitimate PT rejections.
for runtime in ['native','chromium','webkit']:
 for label in ['controlA','candidateB']:
  d=read(f'lifecycle-{label}.json' if runtime=='native' else f'{runtime}-{label}-lifecycle.json');rows=d.get('rows',[]);errors=[];derivs=[];energies=[]
  check(bool(rows),'lifecycleMissing',runtime=runtime,label=label,data=d)
  for r in rows:
   if 'error' in r:errors.append(dict(id=r['request']['id'],error=r['error']));continue
   for x in [r['base']]+r['sequences']:
    if 'error' in x:errors.append(dict(id=r['request']['id'],mode=x['mode'],error=x['error']));continue
    derivs+=list(x.get('derivativeDifferences',{}).values());energies.append(x.get('normalizedEnergyInconsistency',0))
    if label=='candidateB':
     check(x.get('normalizedEnergyInconsistency',0)<=1e-11,'lifecycleEnergy',runtime=runtime,id=r['request']['id'])
     if 'equilibrium' in x:check(x['equilibrium']['validQuality'],'lifecycleQuality',runtime=runtime,id=r['request']['id'])
     if 'equilibriumQualityValid' in x and not x['equilibriumQualityValid']:
      # HSU_D_flash uses Q=10000 for homogeneous DU, not mixture quality.
      # Establish the meaning from unchanged native phase/source and fresh EOS.
      nr=next(v for v in read(f'lifecycle-{label}.json')['rows'] if v['request']['id']==r['request']['id'])
      ns=next((v for v in nr['sequences'] if v.get('mode')==x['mode'] and 'state' in v),{})
      n=ns.get('state',{}).get('values',{});s=x['state'];dt=x['independentDT']
      valid=x['mode']=='DU' and s['Q']==10000 and n.get('phase')!=6 and n.get('Q')==10000 and all(abs(s[k]-dt[k])<=.1 for k in ['p','h','u'])
      check(valid,'lifecycleQuality',runtime=runtime,id=r['request']['id'])
      out['knownLimitations'].setdefault('unchangedHomogeneousDUqualitySentinels',[]).append(dict(runtime=runtime,label=label,id=r['request']['id'],Q=s['Q'],nativePhase=n.get('phase')))
  out['lifecycle'][runtime+'-'+label]=dict(cases=len(rows),errors=errors,maxDerivativeDifference=max(map(abs,derivs),default=0),maxNormalizedEnergy=max(energies,default=0))
 check(out['lifecycle'][runtime+'-candidateB']['errors']==out['lifecycle'][runtime+'-controlA']['errors'],'changedLifecycleExceptions',runtime=runtime)
for runtime in ['native','native-full-vle','chromium','webkit']:
 for label in ['controlA','candidateB']:
  name=f'shared-{label}'+('-full-vle' if runtime.endswith('full-vle') else '')+'.json' if runtime.startswith('native') else f'{runtime}-{label}-shared.json'
  d=read(name);rows=d.get('rows',[]);errors=[];upper=[];fresh=[];equilibrium=[];residuals=[]
  check(len(rows)==96,'sharedMissing',runtime=runtime,label=label,data=d if not rows else len(rows))
  for r in rows:
   if 'error' in r:errors.append(dict(id=r['id'],error=r['error']));continue
   s=r['state'].get('values',r['state']);q=s['Q']
   if q>1:upper.append(dict(id=r['id'],Q=q))
   if not r['freshEqualsReused']:fresh.append(r['id'])
   if label=='candidateB':
    check(q<0 or 0<=q<=1,'sharedQuality',runtime=runtime,id=r['id'])
    check(r['freshEqualsReused'],'sharedFreshReused',runtime=runtime,id=r['id'])
    if q<0:
     dif=r['getterDifferences'];check(all(abs(dif[k])<=.1 for k in ['p','h','u']),'sharedGetterConsistency',runtime=runtime,id=r['id'],differences=dif)
     stability=r.get('stability',r.get('derivatives',{}));check(all(v>0 for v in stability.values()),'sharedStabilityOrCaloricOrdering',runtime=runtime,id=r['id'],stability=stability)
     residuals.append(dict(id=r['id'],requestedResiduals=r.get('requestedResiduals'),getterDifferences=dif))
    else:equilibrium.append(dict(id=r['id'],Q=q))
  out['shared'][runtime+'-'+label]=dict(cases=len(rows),errors=errors,invalidUpperQualities=upper,freshReusedDifferences=fresh,residuals=residuals,equilibrium=equilibrium)
  if label=='candidateB':check(not errors and not upper,'sharedExceptionsOrUpperQuality',runtime=runtime,errors=errors,upper=upper)
fixed=read('35bar-fixed-inventories.json');check(fixed['allEqual'],'changedFixedNativeDU')
out['knownLimitations']['nativeFixed35bar']=dict(cases=len(fixed['rows']),allIdentical=fixed['allEqual'],errors=sum('error' in r['result']['candidateB'] for r in fixed['rows']),strictGuardExits=sum(not r['result']['candidateB'].get('strictSupport',False) for r in fixed['rows']))
for runtime in ['chromium','webkit']:
 d=read(f'{runtime}-35bar-fixed-inventories.json');check(d['allEqual'],'changedFixedBrowserDU',runtime=runtime)
 out['knownLimitations'][runtime+'Fixed35bar']=dict(cases=len(d['comparisons']),allIdentical=d['allEqual'])
out['originalSignedProbeExclusions']=[dict(id=r['request']['id'],axis=q['axis'],step=q['step'],basePhysicalPhase=r['base']['physicalPhase'],probePhysicalPhase=q.get('output',{}).get('physicalPhase'),supportedInput=q.get('output',{}).get('supportedInput'),reason=q.get('derivativeExclusion','unsupported input')) for r in read('native-candidateB.json')['rows'] for q in r['probes'] if not q.get('samePhysicalBranch') or not q.get('output',{}).get('supportedInput')]
out.update(passOriginalBoundaryRequirements=not failures,eligibleForLimitedA2=not failures and read('focused-gate.json')['eligibleForLimitedA2'],knownRejectedPTLoaderUnchanged=True,fullQualification=False)
save(E/'boundary-gate.json',out);print('Boundary/shared/lifecycle gates',not failures,'failures',len(failures));print([(q['kind'],q.get('id')) for q in failures[:10]])
sys.exit(bool(failures))
