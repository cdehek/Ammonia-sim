"""Bounded independent root seed checks, without importing evidence writers."""
import json
from pathlib import Path
import os
from CoolProp import AbstractState,CoolProp as C
def local_roots():
 E=Path(os.environ.get('B5_EVIDENCE',Path(__file__).resolve().parent/'evidence'));rows=[]
 for r in json.loads((E/'original-failures.json').read_text())['rows']:
  if r['runtime']=='webkit':continue
  d,u=r['fixedInput']['values']['rho'],r['fixedInput']['values']['u'];base=r['independentReference']['homogeneous']['state']['values']['T'];roots=[]
  for offset in [-1.,-.01,.01,1.]:
   a=AbstractState('HEOS','Ammonia');a.specify_phase(C.iphase_liquid if d>225 else C.iphase_gas);T=base+offset;trace=[]
   for i in range(16):
    a.update(C.DmassT_INPUTS,d,T);res=a.umass()-u;trace.append(dict(T=T,uResidual=res,cv=a.cvmass()))
    if abs(res)<1e-8:break
    T-=res/a.cvmass()
   roots.append(dict(seedOffset=offset,T=T,p=a.p(),uResidual=res,converged=abs(res)<1e-8,trace=trace))
  rows.append(dict(failureKey=r['failureKey'],roots=roots,temperatureSpan=max(x['T']for x in roots)-min(x['T']for x in roots),note='Dome-interior homogeneous roots are diagnostic algebraic solutions, not stable references.'))
 return rows
