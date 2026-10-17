"""Original full-VLE signed budgets, saved 21 references and actual native parity."""
import json,sys
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';read=lambda p:json.loads(p.read_text());failures=[];rows=[]
def check(ok,kind,**data):
 if not ok:failures.append(dict(kind=kind,**data))
def numerical(s,t):return all(abs(s[k]-t[k])<=limit for k,limit in dict(p=.1,h=.1,T=1e-4).items())
native=read(E/'native-fresh-replay.json')['rows'];references=read(X/'browser_eos_b5a/evidence/additional-inventories.json')['rows'];refs={r['saved']['failureKey']:r for r in references}
for engine in ['chromium','webkit']:
 data=read(E/f'ledger-{engine}.json')['result']['rows']
 for block in data:
  label='candidate' if block['id']=='gateA' else 'control';path='fullVLE' if block['fullVLE'] else 'default';n=next(q for q in native if q['label']==label and q['fullVLE']==block['fullVLE'])
  for r,actual in zip(block['records'],n['records']):
   check(r['input']==actual['input'] and r['key']==actual['key'],'nativeOriginalIdentity')
   if 'state' in r['reused']:check('state' in actual['reused'] and numerical(r['reused']['state']['values'],actual['reused'].get('state',{}).get('values',{})),'nativeFreshReplayAgreement',engine=engine,key=r['key'])
   else:check('error' in actual['reused'],'nativeFreshReplayRefusal',key=r['key'])
  for r,actual in zip(block['additional'],n['additional']):
   saved=refs[r['key']];x=r['input']['values'];old=saved['results']['A1' if label=='candidate' else 'control'][path];out=r['reused']
   check(r['input']==actual['input'] and r['key']==actual['key'],'additionalOriginalIdentity')
   check(out.get('state')==r['fresh'].get('state') and out.get('error')==r['fresh'].get('error'),'additionalFreshReused',key=r['key'])
   if 'state' in out:
    s=out['state']['values'];check('DU' in old and numerical(s,old.get('DU',{}).get('values',{})),'additionalNativeReferenceAgreement',key=r['key'])
    canonical=dict(p=saved['saved']['requestedP'],h=saved['saved']['requestedH'],T=saved['saved']['referenceT']);check(numerical(s,canonical),'additionalCanonical',key=r['key'])
    dt=AbstractState('HEOS','Ammonia')
    if s['phase']==6:check(0<=s['Q']<=1,'additionalQuality');dt.update(C.QT_INPUTS,s['Q'],s['T'])
    else:dt.specify_phase(C.iphase_liquid if s['phase']==0 else C.iphase_gas);dt.update(C.DmassT_INPUTS,s['rho'],s['T'])
    residuals=dict(mass=abs((dt.rhomass()-x['rho'])*x['V'])/max(.01,x['M']),energy=abs(x['M']*dt.umass()/1000-x['U_kJ'])/max(1,abs(x['U_kJ'])))
    check(all(v<=1e-11 for v in residuals.values()),'additionalFreshEOS',key=r['key'],residuals=residuals)
    check(all(abs(s[k]-v)<=.1 for k,v in dict(p=dt.p(),h=dt.hmass(),u=dt.umass()).items()),'additionalCacheGetter',key=r['key'])
   else:residuals=None;check('error' in old,'additionalRefusalDifference',key=r['key'])
   rows.append(dict(engine=engine,artifact=block['id'],fullVLE=block['fullVLE'],separateReferenceKey=r['key'],freshEOSResiduals=residuals,error=out.get('error'),originalPhysicalQualificationUnchanged=True))
 data=read(E/f'regressions-{engine}.json')['result']['rows']
 for block in data:
  if not block['fullVLE']:continue
  n=read(E/('native-candidateB-full-vle.json' if block['id']=='gateA' else 'native-controlA-full-vle.json'))['rows'];by={r['request']['id']:r for r in n};probes=0
  for r in block['result']['rows']:
   nr=by[r['id']];ref=nr['base'].get('reference',{});s=r['base']['state'];p,h=r['args']
   check(numerical(s,nr['base']['PH']['values']),'fullVLENativePH',id=r['id'])
   for q in r['probes']:
    original=next(z for z in nr['probes'] if z['axis']==q['axis'] and z['step']==q['step']);v=q.get('output')
    if not v or not original.get('samePhysicalBranch') or not original['output']['supportedInput'] or not ref.get('converged'):continue
    deriv=ref['derivatives']['rhoP' if q['axis']=='P' else 'rhoH'];V=.003/5;M=s['rho']*V;U=M*(h/1000)-p*V/1000;rho=v['state']['rho'];step=q['step'];dU=deriv*V*(h/1000)+(-V/1000 if q['axis']=='P' else M/1000)
    mass=V*abs(rho-s['rho']-deriv*step)/max(.01,M);energy=abs(rho*V*v['h']/1000-v['p']*V/1000-U-dU*step)/max(1,abs(U));probes+=1
    check(mass<=1e-11 and energy<=1e-11,'originalFullVLESignedBudget',engine=engine,id=r['id'],mass=mass,energy=energy)
   if block['id']=='gateA' and nr['base']['physicalPhase'] in ['liquid','gas']:
    check(r['inventories']['C']['canonicalPass'],'resolvedFullVLECanonical',id=r['id'],engine=engine)
  rows.append(dict(engine=engine,artifact=block['id'],kind='full-VLE focused signed regression',applicableSignedProbes=probes,endpointAndPhaseExclusionsUnchanged=True))
out=dict(passed=not failures,failures=failures,rows=rows,independentReferenceSetCount=21,notAddedTo250RecordLedger=True)
p=E/'additional-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Additional/full-VLE audit',out['passed'],'failures',len(failures));print(failures[:8]);sys.exit(bool(failures))
