"""Independent derivative checks and static recovery cost; no fitting/EOS calls."""
import hashlib,json,math,time
import mpmath as mp
import numpy as np
from model import BASE,TERMS,load
E=BASE/'evidence';mp.mp.dps=65
models=load();rows=[];timings=[];rejects=[]
for name,c in models.items():
    def g(p,T):
        x=(p-mp.mpf(c.pc))/mp.mpf(c.ps);y=(T-mp.mpf(c.tc))/mp.mpf(c.ts)
        return mp.fsum(mp.mpf(v)*x**i*y**j for (i,j),v in zip(TERMS,c.c))
    for f in [.1,.5,.9]:
        p=c.pc+(2*f-1)*c.ps
        for z in [.1*c.zmax,.5*c.zmax,.9*c.zmax]:
            a=c.at_z(p,z);pp=mp.mpf(p);T=mp.mpf(a['T'])
            gp=mp.diff(lambda x:g(x,T),pp);gt=mp.diff(lambda t:g(pp,t),T)
            gpp=mp.diff(lambda x:g(x,T),pp,2);gtt=mp.diff(lambda t:g(pp,t),T,2)
            gpt=mp.diff(lambda x:mp.diff(lambda t:g(x,t),T),pp)
            h=lambda x,t:g(x,t)-t*mp.diff(lambda q:g(x,q),t)
            hp=mp.diff(lambda x:h(x,T),pp);ht=mp.diff(lambda t:h(pp,t),T)
            rho=lambda x,t:100/mp.diff(lambda q:g(q,t),x)
            rt=mp.diff(lambda t:rho(pp,t),T)
            rows.append(dict(patch=name,p=p,z=z,derivativeErrors={k:float(mp.mpf(a[k])-v) for k,v in [('gp',gp),('gpp',gpp),('gpt',gpt),('gtt',gtt),('cp',ht)]},
                independentMaxwellResidual=float(hp-100*(1/rho(pp,T)+T*rt/rho(pp,T)**2)),workIdentity=float(mp.mpf(a['h'])-mp.mpf(a['u'])-100*pp/mp.mpf(a['rho']))))
    inputs=[c.at_z(c.pc+c.ps*f,c.zmax*z) for f in [-.5,0,.5] for z in [.2,.5,.8]]
    for _ in range(5):
        t=time.perf_counter();solved=[c.recover(a['rho'],a['u']) for a in inputs]
        timings.append(dict(patch=name,recoveries=len(inputs),seconds=time.perf_counter()-t,maxPressureRoundtripPa=max(abs((a['p']-b['p'])*1e5) for a,b in zip(inputs,solved))))
    for p,z in [(c.pc-c.ps-1e-5,.5*c.zmax),(c.pc+c.ps+1e-5,.5*c.zmax),(c.pc,-1e-5),(c.pc,c.zmax+1e-5)]:
        try:c.at_z(p,z)
        except ValueError as exc:rejects.append(dict(patch=name,p=p,z=z,rejected=True,message=str(exc)))
        else:raise AssertionError('Out-of-domain state admitted')
obj=dict(candidateSHA256=hashlib.sha256((E/'candidate.json').read_bytes()).hexdigest(),mpDigits=mp.mp.dps,derivativeChecks=rows,recoveryTimings=timings,domainRejections=rejects)
(E/'supplement.json').write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
print('Independent derivatives, static recovery cost and domain checks complete')
