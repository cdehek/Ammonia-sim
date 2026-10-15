"""Independent EOS coexistence solve at fixed P, seeded by public saturation.

Solve pL=P, pV=P and gL=gV. No reference state is returned to a backend/model.
"""
import json,os
from pathlib import Path
import numpy as np
import CoolProp
from CoolProp import AbstractState,CoolProp as C
from native import pack,save
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B3_EVIDENCE',B/'evidence'));rows=[]
for p in sorted({q['args'][0] for q in json.loads((B/'inputs.json').read_text())}):
 a=AbstractState('HEOS','Ammonia');a.update(C.PQ_INPUTS,p,0);T=a.T();rL=a.rhomass();a.update(C.PQ_INPUTS,p,1);rV=a.rhomass()
 seed=dict(T=T,rhoL=rL,rhoV=rV)
 # Deliberately displaced diagnostic seed demonstrates independent convergence
 # of the coexistence equations, rather than merely accepting a PQ seed.
 T+=.01;rL*=1+1e-6;rV*=1-1e-6
 L=AbstractState('HEOS','Ammonia');L.specify_phase(C.iphase_liquid)
 G=AbstractState('HEOS','Ammonia');G.specify_phase(C.iphase_gas);trace=[]
 for i in range(12):
  L.update(C.DmassT_INPUTS,rL,T);G.update(C.DmassT_INPUTS,rV,T)
  eL,eV=L.p()-p,G.p()-p;eg=(L.hmass()-T*L.smass())-(G.hmass()-T*G.smass())
  trace.append(dict(T=T,rhoL=rL,rhoV=rV,pLResidual=eL,pVResidual=eV,gLMinusGV=eg))
  if abs(eL)<1e-5 and abs(eV)<1e-5 and abs(eg)<1e-8:break
  prL=L.first_partial_deriv(C.iP,C.iDmass,C.iT);ptL=L.first_partial_deriv(C.iP,C.iT,C.iDmass)
  prV=G.first_partial_deriv(C.iP,C.iDmass,C.iT);ptV=G.first_partial_deriv(C.iP,C.iT,C.iDmass)
  A=np.array([[prL,0,ptL],[0,prV,ptV],[prL/rL,-prV/rV,-L.smass()+ptL/rL+G.smass()-ptV/rV]])
  drL,drV,dT=np.linalg.solve(A,[-eL,-eV,-eg]);rL+=float(drL);rV+=float(drV);T+=float(dT)
 out=dict(p=p,publicPQSeed=seed,diagnosticSeed='T+0.01 K; rhoL*(1+1e-6); rhoV*(1-1e-6)',trace=trace,converged=abs(eL)<1e-5 and abs(eV)<1e-5 and abs(eg)<1e-8,
  liquid=pack(dict(p=L.p(),T=T,rho=rL,h=L.hmass(),s=L.smass(),g=L.hmass()-T*L.smass())),
  vapor=pack(dict(p=G.p(),T=T,rho=rV,h=G.hmass(),s=G.smass(),g=G.hmass()-T*G.smass())))
 rows.append(out)
save(E/f'saturation-reference-{CoolProp.__version__}.json',dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,rows=rows))
print(len(rows),'EOS coexistence roots;',sum(r['converged']for r in rows),'converged')
