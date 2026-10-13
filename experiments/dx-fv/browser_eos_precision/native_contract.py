"""Independent EOS residual checks and static canonical targets; no fitted backend."""
import json,math,hashlib
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;a=AbstractState('HEOS','Ammonia');seed=AbstractState('HEOS','Ammonia')
assert CoolProp.__version__=='8.0.0'
def snapshot():return dict(p=a.p(),h=a.hmass(),rho=a.rhomass(),T=a.T(),u=a.umass())
browser=json.loads((B/'evidence/chromium-8.0.0.json').read_text());cross=[]
for r in browser['rows']:
 if r['method']=='reused' and ((r['id']=='exact-saved' and r['step']==.01) or r['id'].startswith('p')):
  for label in ['base','perturbed']:
   s=r[label];a.update(C.DmassT_INPUTS,s['rho'],s['T']);cross.append(dict(id=r['id'],axis=r['axis'],state=label,rho=s['rho'],T=s['T'],native=snapshot(),nativeMinusWASM={'pEOS':a.p()-s['pEOS'],'hEOS':a.hmass()-s['hEOS']},firstPartial=a.first_partial_deriv(C.iDmass,C.iP,C.iHmass)))
inputs=json.loads((B/'inputs.json').read_text());p,h=inputs['cases'][0]['args'];targets=[]
for name,pt,ht in [('saved-base',p,h),('saved-P-plus',p+.01,h),('saved-H-plus',p,h+inputs['cases'][0]['dh']),('nominal-text',*inputs['cases'][1]['args'])]:
 seed.update(C.HmassP_INPUTS,ht,pt);rho,T=seed.rhomass(),seed.T();trace=[]
 for i in range(10):
  a.update(C.DmassT_INPUTS,rho,T);ep,eh=a.p()-pt,a.hmass()-ht;trace.append(dict(pResidual=ep,hResidual=eh,rho=rho,T=T))
  if abs(ep)<1e-5 and abs(eh)<1e-8:break
  pr=a.first_partial_deriv(C.iP,C.iDmass,C.iT);pT=a.first_partial_deriv(C.iP,C.iT,C.iDmass)
  hr=a.first_partial_deriv(C.iHmass,C.iDmass,C.iT);hT=a.first_partial_deriv(C.iHmass,C.iT,C.iDmass)
  det=pr*hT-pT*hr;rho+=(-ep*hT+pT*eh)/det;T+=(hr*ep-pr*eh)/det
 else:raise RuntimeError('Independent DT residual polish did not reach its declared numerical floor')
 targets.append(dict(id=name,args=[pt,ht],reference=snapshot(),trace=trace,referenceEvaluationLimits={'pPa':1e-5,'hJkg':1e-8},note='Diagnostic reference root using official native DT derivatives. These are reference evaluation limits, not changes to solver tolerances.'))
out=dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,crossEOSChecks=cross,targets=targets,sourceBrowserSHA256=hashlib.sha256((B/'evidence/chromium-8.0.0.json').read_bytes()).hexdigest())
f=B/'evidence/native-contract.json';assert not f.exists();f.write_text(json.dumps(out,indent=2)+'\n');print('Cross checks',len(cross),'canonical targets',len(targets))
