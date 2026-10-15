import os
"""Public-API diagnostics only. Never feeds corrected states to the model."""
import json,os,struct
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True);p,h=799999.9981754856,1624022.744737779
def snap(a):return dict(T=a.T(),rho=a.rhomass(),p=a.p(),h=a.hmass(),u=a.umass(),phase=int(a.phase()))
def dt(s):
 a=AbstractState('HEOS','Ammonia');a.update(C.DmassT_INPUTS,s['rho'],s['T']);return snap(a)
rows=[]
for superanc in [True,False]:
 C.set_config_bool(C.ENABLE_SUPERANCILLARIES,superanc)
 for imposed in [False,True]:
  a=AbstractState('HEOS','Ammonia')
  if imposed:a.specify_phase(C.iphase_gas)
  a.update(C.HmassP_INPUTS,h,p);s=snap(a);d=dt(s)
  a.update(C.DmassT_INPUTS,s['rho'],s['T']);reset=snap(a)
  b=AbstractState('HEOS','Ammonia');b.update(C.PT_INPUTS,p,s['T']);pt=snap(b)
  rows.append(dict(superancillaries=superanc,imposedGas=imposed,PH=s,independentDT=d,sameObjectResetDT=reset,PT=pt,PTindependentDT=dt(pt)))
# Independent reference root of true EOS P/H, Newton in (rho,T), diagnostic only.
C.set_config_bool(C.ENABLE_SUPERANCILLARIES,True)
a=AbstractState('HEOS','Ammonia');a.update(C.HmassP_INPUTS,h,p);rho,T=a.rhomass(),a.T();trace=[]
for _ in range(8):
 a.update(C.DmassT_INPUTS,rho,T);rp,rh=a.p()-p,a.hmass()-h
 trace.append(dict(rho=rho,T=T,pResidual=rp,hResidual=rh))
 if abs(rp)<1e-5 and abs(rh)<1e-8:break
 pr=a.first_partial_deriv(C.iP,C.iDmass,C.iT);pt=a.first_partial_deriv(C.iP,C.iT,C.iDmass)
 hr=a.first_partial_deriv(C.iHmass,C.iDmass,C.iT);ht=a.first_partial_deriv(C.iHmass,C.iT,C.iDmass);det=pr*ht-pt*hr
 rho+=(-rp*ht+pt*rh)/det;T+=(-pr*rh+hr*rp)/det
out=dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,inputs=[p,h],inputBits=[struct.pack('>d',v).hex() for v in [p,h]],environmentDirectEOS=os.environ.get('PXFLASH_DIRECT_EOS','default'),rows=rows,independentRootTrace=trace,referenceOnly=True)
suffix=os.environ.get('PXFLASH_DIRECT_EOS','default')
target=E/f'forensics-{CoolProp.__version__}-{suffix}.json';assert not target.exists(),'Use a new B2_EVIDENCE directory'
target.write_text(json.dumps(out,indent=2)+'\n')
print(CoolProp.__version__,suffix,trace[-1])
