"""Static polynomial Gibbs model. No EOS imports, fitting or production use."""
import json
import math
from pathlib import Path
import numpy as np
from numpy.polynomial import polynomial as poly
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
TERMS = [(a,b) for a in range(6) for b in range(6) if a+b <= 5]

def basis(x,y,dp=0,dt=0,ps=1.,ts=1.):
    f=math.factorial
    return np.array([0. if a<dp or b<dt else f(a)/f(a-dp)*f(b)/f(b-dt)*x**(a-dp)*y**(b-dt)/ps**dp/ts**dt for a,b in TERMS])

class Patch:
    def __init__(self,d):
        self.d=d
        for k in ['pc','ps','tc','ts','zmax']: setattr(self,k,d[k])
        self.c=np.array(d['coefficients'])
        self.satc=np.array(d['saturationCoefficients'])
        self.svc=np.array(d['vaporEntropyCoefficients'])
    def saturation(self,p,der=0):
        return float(poly.polyval((p-self.pc)/self.ps,poly.polyder(self.satc,der))/self.ps**der)
    def weights(self,p,T,dp=0,dt=0):
        return basis((p-self.pc)/self.ps,(T-self.tc)/self.ts,dp,dt,self.ps,self.ts)
    def at(self,p,T,check=True):
        z=self.saturation(p)-T
        if check and not (self.pc-self.ps-1e-14<=p<=self.pc+self.ps+1e-14 and -2e-12<=z<=self.zmax+2e-12):
            raise ValueError('Outside declared liquid patch')
        g,gp,gt,gpp,gpt,gtt=[float(self.weights(p,T,*ab)@self.c) for ab in [(0,0),(1,0),(0,1),(2,0),(1,1),(0,2)]]
        h=g-T*gt;u=h-p*gp;rho=100/gp;det=gpp*gtt-gpt*gpt
        cp=-T*gtt;cv=-T*det/gpp
        rp=-100*gpp/gp**2;rt=-100*gpt/gp**2
        J=np.array([[rp,rt],[-T*gpt-p*gpp,cp-p*gpt]])
        cond=float(np.linalg.cond(np.diag([1/rho,1/max(1,abs(u))])@J@np.diag([p,T])))
        return dict(p=float(p),T=float(T),z=z,g=g,h=h,s=-gt,rho=rho,u=u,v=gp/100,cp=cp,cv=cv,kappa=-gpp/gp,
                    gp=gp,gpp=gpp,gpt=gpt,gtt=gtt,det=det,rhoP=rp,rhoT=rt,condition=cond,
                    maxwell=(gp-T*gpt)-100*(1/rho+T*rt/rho**2))
    def at_z(self,p,z): return self.at(p,self.saturation(p)-z)
    def vapor(self,p):
        T=self.saturation(p);f=self.at(p,T);sv=float(poly.polyval((p-self.pc)/self.ps,self.svc))
        v=(f['gp']+self.saturation(p,1)*(sv-f['s']))/100
        return dict(p=p,T=T,g=f['g'],s=sv,h=f['g']+T*sv,rho=1/v,v=v)
    def ph(self,p,h):
        Ts=self.saturation(p)
        T=brentq(lambda T:self.at(p,T)['h']-h,Ts-self.zmax,Ts,xtol=1e-12,rtol=1e-15)
        return self.at(p,T)
    def at_density(self,p,rho):
        Ts=self.saturation(p)
        T=brentq(lambda T:self.at(p,T)['rho']-rho,Ts-self.zmax,Ts,xtol=1e-12,rtol=1e-15)
        return self.at(p,T)
    def density_pressure_interval(self,rho):
        # Valid only after certificate proves boundary rho strictly decreasing
        # in p, and rho strictly decreasing in T on the complete patch.
        lo=self.pc-self.ps;hi=self.pc+self.ps
        hot=lambda p:self.at_z(p,0)['rho']-rho
        cold=lambda p:self.at_z(p,self.zmax)['rho']-rho
        if hot(hi)>0 or cold(lo)<0:raise ValueError('Inventory density outside patch')
        if hot(lo)>0:lo=brentq(hot,lo,hi,xtol=5e-15,rtol=1e-15)
        if cold(hi)<0:hi=brentq(cold,lo,hi,xtol=5e-15,rtol=1e-15)
        return lo,hi
    def recover(self,rho,u):
        lo,hi=self.density_pressure_interval(rho)
        def at(p):
            # Endpoint root rounding may put density a few ulps outside its
            # bracket. Only evaluate exact endpoint if residual is <2e-10.
            try:return self.at_density(p,rho)
            except ValueError:
                q=min([self.at_z(p,0),self.at_z(p,self.zmax)],key=lambda q:abs(q['rho']-rho))
                if abs(q['rho']-rho)>2e-10:raise
                return q
        f=lambda p:at(p)['u']-u
        p=brentq(f,lo,hi,xtol=5e-15,rtol=1e-15)
        q=at(p);q.update(densityResidual=q['rho']-rho,energyResidual=q['u']-u,pressureBracket=[lo,hi])
        return q

def load(path=None):
    data=json.loads(Path(path or BASE/'evidence/candidate.json').read_text())
    return {d['name']:Patch(d) for d in data['patches']}
