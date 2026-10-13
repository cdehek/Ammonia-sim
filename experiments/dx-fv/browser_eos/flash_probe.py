"""Independent native PH flash-noise diagnostic. Changes no solver or tolerance."""
import json,sys
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;a=AbstractState('HEOS','Ammonia');p=.3029893712344606*1e5;h=94.52334612321303*1000
saved=len(sys.argv)>1 and sys.argv[1]=='saved'
if saved:
 q=next(q for q in json.loads((B/'inputs.json').read_text())['requests'] if q['id']=='p0.3029893712344606-liquid-z1.0-PH');p,h=q['args']
rows=[]
for implementation in ['reused-state','fresh-state','high-level']:
 def sample(p,h):
  global a
  if implementation=='high-level':
   return dict(p=C.PropsSI('P','P',p,'Hmass',h,'HEOS::Ammonia'),T=C.PropsSI('T','P',p,'Hmass',h,'HEOS::Ammonia'),rho=C.PropsSI('Dmass','P',p,'Hmass',h,'HEOS::Ammonia'),h=C.PropsSI('Hmass','P',p,'Hmass',h,'HEOS::Ammonia'))
  if implementation=='fresh-state':a=AbstractState('HEOS','Ammonia')
  a.update(C.HmassP_INPUTS,h,p);return dict(p=a.p(),T=a.T(),rho=a.rhomass(),h=a.hmass())
 base=sample(p,h)
 analytic=C.PropsSI('d(Dmass)/d(P)|Hmass','P',p,'Hmass',h,'HEOS::Ammonia')
 for dp in [.003,.01,.03,.1,.3,1.,3.]:
  q=sample(p+dp,h);rows.append(dict(implementation=implementation,pressureStepPa=dp,base=base,perturbed=q,analyticRhoPAtH=analytic,finiteRhoPAtH=(q['rho']-base['rho'])/dp,baseHResidualJkg=base['h']-h,perturbedHResidualJkg=q['h']-h))
# Independent DT identity: actual returned state remains consistent with the
# same EOS despite an imperfect target-enthalpy flash. No derivative is fitted.
r=dict(inputVariant='exact saved PH inputs' if saved else 'declared historical pressure and enthalpy',version=CoolProp.__version__,git=CoolProp.__gitrevision__,pPa=p,hJkg=h,unchangedSolverPressureStepPa=.01,rows=rows,conclusion='diagnostic only; do not enlarge finite-difference steps or alter scientific tolerances without authorization')
(B/'evidence'/(f'flash-probe-{CoolProp.__version__}'+('-saved' if saved else '')+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print(CoolProp.__version__,[(q['implementation'],q['finiteRhoPAtH'],q['analyticRhoPAtH'],q['perturbedHResidualJkg']) for q in rows if q['pressureStepPa']==.01])
