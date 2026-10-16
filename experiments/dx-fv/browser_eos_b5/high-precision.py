"""Arbitrary precision evaluation of the unchanged pinned ammonia Helmholtz EOS.

Coefficients are lifted from their exact binary64 values, not refitted. This
separate evaluator checks rounding/conditioning; it is never a backend repair.
"""
import json,sys,hashlib
from pathlib import Path
import os
import mpmath as mp
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'))
F=Path('/workspace/coolprop-b5/dev/fluids/Ammonia.json');raw=F.read_bytes();data=json.loads(raw)['EOS'][0]
mp.mp.dps=65
def lift(x):
 if isinstance(x,(int,float)):return mp.mpf(x)
 if isinstance(x,list):return [lift(a)for a in x]
 if isinstance(x,dict):return {k:lift(v)for k,v in x.items()}
 return x
D=lift(data);R=D['gas_constant']/D['molar_mass'];Tc=D['STATES']['reducing']['T'];dc=D['STATES']['reducing']['rhomolar']*D['molar_mass']
def eos(rho,T):
 delta,tau=rho/dc,Tc/T;ar=mp.mpf(0);art=mp.mpf(0);ard=mp.mpf(0)
 for group in D['alphar']:
  for i,n in enumerate(group['n']):
   d,t=group['d'][i],group['t'][i];f=n*delta**d*tau**t;lt=t/tau;ld=d/delta
   if group['type']=='ResidualHelmholtzPower':
    l=group['l'][i]
    if l:f*=mp.exp(-delta**l);ld-=l*delta**(l-1)
   elif group['type']=='ResidualHelmholtzGaussian':
    eta,beta,eps,gamma=[group[k][i]for k in ['eta','beta','epsilon','gamma']]
    f*=mp.exp(-eta*(delta-eps)**2-beta*(tau-gamma)**2);ld-=2*eta*(delta-eps);lt-=2*beta*(tau-gamma)
   elif group['type']=='ResidualHelmholtzGaoB':
    eta,beta,eps,gamma,b=[group[k][i]for k in ['eta','beta','epsilon','gamma','b']];z=b+beta*(tau-gamma)**2
    f*=mp.exp(eta*(delta-eps)**2+1/z);ld+=2*eta*(delta-eps);lt-=2*beta*(tau-gamma)/z**2
   else:raise ValueError(group['type'])
   ar+=f;art+=f*lt;ard+=f*ld
 lead,log,planck=D['alpha0'];a0=mp.log(delta)+lead['a1']+lead['a2']*tau+log['a']*mp.log(tau);a0t=lead['a2']+log['a']/tau
 for n,t in zip(planck['n'],planck['t']):a0+=n*mp.log(1-mp.exp(-t*tau));a0t+=n*t/mp.expm1(t*tau)
 p=rho*R*T*(1+delta*ard);u=R*T*tau*(a0t+art);h=u+p/rho;s=R*(tau*(a0t+art)-a0-ar)
 return dict(p=p,u=u,h=h,s=s,g=h-T*s,rho=rho,T=T)
def enc(d):return {k:mp.nstr(v,60)for k,v in d.items()}
def equilibrium(d,u,seed):
 st=seed['state']['values'];rL=seed['liquid']['values']['rho'];rV=seed['vapor']['values']['rho'];T=st['T']
 def f(rL,rV,T):
  l,g=eos(rL,T),eos(rV,T);q=(1/d-1/rL)/(1/rV-1/rL)
  return ((l['p']-g['p'])/mp.mpf(1e6),(l['g']-g['g'])/mp.mpf(1e6),((1-q)*l['u']+q*g['u']-u)/mp.mpf(1e6))
 rL,rV,T=mp.findroot(f,(rL,rV,T),tol=mp.mpf('1e-52'),maxsteps=15)
 l,g=eos(rL,T),eos(rV,T);q=(1/d-1/rL)/(1/rV-1/rL)
 return dict(p=(l['p']+g['p'])/2,T=T,rho=d,u=(1-q)*l['u']+q*g['u'],h=(1-q)*l['h']+q*g['h'],Q=q,rhoL=rL,rhoV=rV,pDifference=l['p']-g['p'],gDifference=l['g']-g['g'],uResidual=(1-q)*l['u']+q*g['u']-u)
if __name__=='__main__':
 inputs=json.loads((E/'fixed-inputs.json').read_text());refs=json.loads((E/'independent-fixed-references.json').read_text())['rows'];cache={};rows=[];validation=[]
 from CoolProp import AbstractState,CoolProp as C
 for rho,T in [(521.53,345.56),(26.0,345.57),(500.,350.),(20.,350.)]:
  a=AbstractState('HEOS','Ammonia');a.specify_phase(C.iphase_liquid if rho>225 else C.iphase_gas);a.update(C.DmassT_INPUTS,rho,T);s=eos(mp.mpf(rho),mp.mpf(T))
  validation.append(dict(rho=rho,T=T,residuals={k:float(s[k])-v for k,v in dict(p=a.p(),h=a.hmass(),u=a.umass(),s=a.smass()).items()}))
 for r,ref in zip(inputs,refs):
  assert r['key']==ref['key'];x=r['input']['values'];d,u=mp.mpf(x['rho']),mp.mpf(x['u']);key=(x['rho'],x['u'])
  if key not in cache:
   try:
    eq=equilibrium(d,u,ref['reference']['equilibrium']);T0=ref['reference']['homogeneous']['state']['values']['T']
    T=mp.findroot(lambda T:eos(d,T)['u']-u,(T0-mp.mpf('.00001'),T0+mp.mpf('.00001')),tol=mp.mpf('1e-52'),maxsteps=15);hom=eos(d,T)
    selection='equilibrium' if 0<=eq['Q']<=1 else 'homogeneous';s=eq if selection=='equilibrium'else hom
    cv=mp.diff(lambda t:eos(d,t)['u'],T);pu=mp.diff(lambda t:eos(d,t)['p'],T)/cv;pr=mp.diff(lambda z:eos(z,T)['p'],d)-pu*mp.diff(lambda z:eos(z,T)['u'],d)
    cache[key]=dict(homogeneous=enc(hom),equilibrium=enc(eq),selection=selection,pMinusLimit=mp.nstr(s['p']-3500000,60),conditioning=enc(dict(cv=cv,pU_rho=pu,pRho_u=pr)),uResidual=mp.nstr(s['u']-u,60))
   except Exception as ex:cache[key]=dict(error=str(ex))
  rows.append(dict(key=r['key'],reference=cache[key]))
 out=dict(dps=mp.mp.dps,coefficientConvention='exact binary64 constants promoted to arbitrary precision',ammoniaSHA256=hashlib.sha256(raw).hexdigest(),validation=validation,uniqueInventories=len(cache),rows=rows)
 (E/'high-precision-references.json').write_text(json.dumps(out,indent=2)+'\n');print(len(cache),'MP roots; errors',sum('error'in r['reference']for r in rows),flush=True)
