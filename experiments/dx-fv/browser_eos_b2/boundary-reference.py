import os
"""Independent homogeneous liquid roots for negative-quality flash outputs.

Phase imposition exists only in this native diagnostic root calculation. The
browser candidate, adapter, solver and original physical fixtures are untouched.
"""
import json
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
import CoolProp
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
source=json.loads((E/'chromium-phase-build44.json').read_text());rows=[]
for q in source['rows']:
 s=q.get('base')
 if not s or not (s['phase']==6 and s['state']['Q']<0):continue
 p,h=q['args'];rho,T=s['state']['rho'],s['state']['T'];a=AbstractState('HEOS','Ammonia');a.specify_phase(C.iphase_liquid);trace=[]
 for _ in range(12):
  a.update(C.DmassT_INPUTS,rho,T);rp,rh=a.p()-p,a.hmass()-h
  trace.append(dict(rho=rho,T=T,pResidual=rp,hResidual=rh))
  if abs(rp)<1e-5 and abs(rh)<1e-8:break
  pr=a.first_partial_deriv(C.iP,C.iDmass,C.iT);pt=a.first_partial_deriv(C.iP,C.iT,C.iDmass);hr=a.first_partial_deriv(C.iHmass,C.iDmass,C.iT);ht=a.first_partial_deriv(C.iHmass,C.iT,C.iDmass);det=pr*ht-pt*hr
  rho+=(-rp*ht+pt*rh)/det;T+=(-pr*rh+hr*rp)/det
 last=trace[-1];rows.append(dict(id=q['id'],args=q['args'],inputBits=q['inputBits'],flash=s,trace=trace,referencePass=abs(last['pResidual'])<1e-5 and abs(last['hResidual'])<1e-8,referenceDensityMinusFlash=last['rho']-s['state']['rho'],referenceTemperatureMinusFlash=last['T']-s['state']['T'],referenceHomogeneousDerivatives=dict(rhoP=a.first_partial_deriv(C.iDmass,C.iP,C.iHmass),rhoH=a.first_partial_deriv(C.iDmass,C.iHmass,C.iP),cp=a.cpmass(),cv=a.cvmass(),kappa=a.isothermal_compressibility()),note='Homogeneous derivatives refer to the independent stable liquid root, not the invalid negative-quality browser mixture.'))
target=E/'boundary-native-roots.json';assert not target.exists(),'Use a new B2_EVIDENCE directory'
target.write_text(json.dumps(dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,referenceOnly=True,rows=rows),indent=2)+'\n')
print(len(rows),'roots',sum(r['referencePass'] for r in rows),'meet diagnostic residual limits')
