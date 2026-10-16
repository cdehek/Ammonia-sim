"""Independent DT and equilibrium roots for exact saved DU inventories.

No public DU inversion supplies these roots. Same EOS, separate states and
independent Newton equations; no reference output is fed back to a backend.
"""
import json,sys,math
from pathlib import Path
import os
import numpy as np
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import pack,root,inventory,Backend
H=B.parent/'browser_eos_b4c/evidence'
def state(a):return {k:getattr(a,f)() for k,f in dict(p='p',T='T',rho='rhomass',h='hmass',u='umass',s='smass').items()}
def stable(a):return dict(cp=a.cpmass(),cv=a.cvmass(),kappa=a.isothermal_compressibility(),pRho=a.first_partial_deriv(C.iP,C.iDmass,C.iT))
def sat(T):
 a=AbstractState('HEOS','Ammonia');a.update(C.QT_INPUTS,0,T);L=state(a);a.update(C.QT_INPUTS,1,T);return L,state(a)
def homogeneous(d,u,T):
 a=AbstractState('HEOS','Ammonia');a.specify_phase(C.iphase_liquid if d>225 else C.iphase_gas);trace=[]
 for i in range(20):
  a.update(C.DmassT_INPUTS,d,T);res=a.umass()-u;trace.append(dict(T=T,uResidual=res))
  if abs(res)<1e-8:break
  T-=res/a.cvmass()
 L,G=sat(T);s=state(a);st=stable(a)
 inside=G['rho']<d<L['rho'];distance=d-(L['rho']if d>225 else G['rho'])
 return dict(state=pack(s),trace=trace,converged=abs(res)<1e-8,stability=st,insideDome=inside,densityDistanceFromEndpoint=distance,saturation=dict(liquid=L,vapor=G),derivatives=dict(pU_rho=a.first_partial_deriv(C.iP,C.iT,C.iDmass)/a.cvmass(),pRho_u=a.first_partial_deriv(C.iP,C.iDmass,C.iT)-a.first_partial_deriv(C.iP,C.iT,C.iDmass)*a.first_partial_deriv(C.iUmass,C.iDmass,C.iT)/a.cvmass()))
def equilibrium(d,u,T):
 l,g=sat(T);rL,rV=l['rho']*(1+1e-7),g['rho']*(1-1e-7);T+=.001
 L=AbstractState('HEOS','Ammonia');G=AbstractState('HEOS','Ammonia');L.specify_phase(C.iphase_liquid);G.specify_phase(C.iphase_gas);trace=[]
 for i in range(16):
  L.update(C.DmassT_INPUTS,rL,T);G.update(C.DmassT_INPUTS,rV,T)
  den=1/rV-1/rL;q=(1/d-1/rL)/den
  p=L.p()-G.p();eg=L.gibbsmass()-G.gibbsmass();eu=(1-q)*L.umass()+q*G.umass()-u
  trace.append(dict(T=T,rhoL=rL,rhoV=rV,Q=q,pDifference=p,gDifference=eg,uResidual=eu))
  if abs(p)<1e-5 and abs(eg)<1e-8 and abs(eu)<1e-8:break
  prL=L.first_partial_deriv(C.iP,C.iDmass,C.iT);prV=G.first_partial_deriv(C.iP,C.iDmass,C.iT)
  ptL=L.first_partial_deriv(C.iP,C.iT,C.iDmass);ptV=G.first_partial_deriv(C.iP,C.iT,C.iDmass)
  urL=L.first_partial_deriv(C.iUmass,C.iDmass,C.iT);urV=G.first_partial_deriv(C.iUmass,C.iDmass,C.iT);du=G.umass()-L.umass()
  J=np.array([[prL,-prV,ptL-ptV],[prL/rL,-prV/rV,-L.smass()+ptL/rL+G.smass()-ptV/rV],[(1-q)*urL+du*(1-q)/(rL*rL*den),q*urV+du*q/(rV*rV*den),(1-q)*L.cvmass()+q*G.cvmass()]])
  drL,drV,dT=np.linalg.solve(J,-np.array([p,eg,eu]));rL+=float(drL);rV+=float(drV);T+=float(dT)
 out=dict(p=(L.p()+G.p())/2,T=T,rho=d,u=(1-q)*L.umass()+q*G.umass(),h=(1-q)*L.hmass()+q*G.hmass(),Q=q)
 return dict(state=pack(out),trace=trace,converged=abs(p)<1e-5 and abs(eg)<1e-8 and abs(eu)<1e-8,physicalQuality=0<=q<=1,endpointUnresolved=min(abs(q),abs(q-1))<1e-12,liquid=pack(state(L)),vapor=pack(state(G)),liquidStability=stable(L),vaporStability=stable(G))
