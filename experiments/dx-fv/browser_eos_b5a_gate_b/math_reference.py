"""Standalone fixed-inventory EOS research, using B5's independent evaluator.

No reference or prototype output is consumed by CoolProp or the coupled solver.
All decimal strings in evidence are diagnostics, never replacement input values.
"""
import importlib.util, json, math, os, struct, time
from pathlib import Path
import mpmath as mp
B=Path(__file__).resolve().parent; E=Path(os.environ.get('GATE_B_EVIDENCE',B/'evidence'))
spec=importlib.util.spec_from_file_location('b5_hp',B.parent/'browser_eos_b5/high-precision.py')
hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp)
def precision(n):
    mp.mp.dps=n; hp.D=hp.lift(hp.data); hp.R=hp.D['gas_constant']/hp.D['molar_mass']
    hp.Tc=hp.D['STATES']['reducing']['T'];hp.dc=hp.D['STATES']['reducing']['rhomolar']*hp.D['molar_mass']
def enc(x):
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [enc(v) for v in x]
    if isinstance(x,mp.mpf):return mp.nstr(x,mp.mp.dps-5)
    return x
def write(n,x):
    p=E/n;assert not p.exists(),p;p.write_text(json.dumps(enc(x),indent=2)+'\n')
def bits(v):return struct.pack('>d',v).hex()
def exact(r):return tuple(struct.unpack('>d',bytes.fromhex(r['input']['bits'][k]))[0] for k in ['rho','u'])
def newton(f,seed,maxiter=14):
    x=mp.matrix(seed); trace=[];start=time.perf_counter();calls=0
    def fun(*a):
        nonlocal calls
        calls+=1; return mp.matrix(f(*a))
    for i in range(maxiter):
        y=fun(*x);norm=max(abs(v) for v in y)
        trace.append(dict(iteration=i,coordinates=list(x),scaledResidual=list(y)))
        if norm<mp.power(10,-mp.mp.dps+15):
            return list(x),dict(iterations=i,termination='precision-scaled diagnostic residual reached',residualEvaluations=calls,seconds=time.perf_counter()-start,trace=trace)
        J=mp.matrix([[mp.diff(lambda z: fun(*(list(x[:j])+[z]+list(x[j+1:])))[k],x[j]) for j in range(len(x))] for k in range(len(y))])
        x+=mp.lu_solve(J,-y)
    raise ArithmeticError('bounded Newton iteration limit')
def fraction(d,rL,rV):
    # Small endpoint fraction is computed directly, avoiding 1-q cancellation.
    if d<hp.dc:
        w=(d-rV)*rL/(d*(rL-rV));return 1-w,w
    q=(rL-d)*rV/(d*(rL-rV));return q,1-q
def equations(d,u,rL,rV,T):
    l,v=hp.eos(rL,T),hp.eos(rV,T);q,w=fraction(d,rL,rV)
    eu=(v['u']-u)-w*(v['u']-l['u']) if d<hp.dc else (l['u']-u)+q*(v['u']-l['u'])
    return (l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6,eu/10**6
def solve(d,u,seed):
    (rL,rV,T),trace=newton(lambda a,b,c:equations(d,u,a,b,c),seed)
    l,v=hp.eos(rL,T),hp.eos(rV,T);q,w=fraction(d,rL,rV)
    vMix=w/rL+q/rV;uMix=w*l['u']+q*v['u']
    return dict(T=T,rhoL=rL,rhoV=rV,p=(l['p']+v['p'])/2,Q=q,liquidFraction=w,
        qualityDistance=min(abs(q),abs(w)),mixtureDensity=1/vMix,mixtureU=uMix,
        pResidual=l['p']-v['p'],muResidual=l['g']-v['g'],volumeResidual=vMix-1/d,uResidual=uMix-u,
        physicalQuality=bool(0<=q<=1),liquid=l,vapor=v,convergence=trace)
def stability(d,T):
    a=hp.eos(d,T);cv=mp.diff(lambda t:hp.eos(d,t)['u'],T)
    pr=mp.diff(lambda r:hp.eos(r,T)['p'],d);pt=mp.diff(lambda t:hp.eos(d,t)['p'],T)
    cp=cv+T*pt**2/(d*d*pr)
    return dict(cv=cv,cp=cp,dp_drho_T=pr,kappa=1/(d*pr),positive=bool(cv>0 and cp>0 and pr>0))
def homogeneous(d,u,T):
    (T,),tr=newton(lambda t:[(hp.eos(d,t)['u']-u)/10**6],[T])
    return dict(**hp.eos(d,T),stability=stability(d,T),convergence=tr)
def saturation_density(d,seed):
    liquid=d>hp.dc
    def f(ro,T):
        l,v=(hp.eos(d,T),hp.eos(ro,T)) if liquid else (hp.eos(ro,T),hp.eos(d,T))
        return (l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6
    (ro,T),tr=newton(f,[seed[1] if liquid else seed[0],seed[2]])
    a=hp.eos(d,T);l,v=(a,hp.eos(ro,T)) if liquid else (hp.eos(ro,T),a)
    return dict(endpoint=a,otherDensity=ro,pResidual=l['p']-v['p'],muResidual=l['g']-v['g'],convergence=tr)
def at_temperature(T,seed):
    def f(a,b):
        l,v=hp.eos(a,T),hp.eos(b,T)
        return (l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6
    (a,b),tr=newton(f,seed[:2]);return dict(rhoL=a,rhoV=b,convergence=tr)
def run():
    fixed=json.loads((E/'fixed-inputs.json').read_text())
    inherited={r['key']:r['reference'] for r in json.loads((B.parent/'browser_eos_b5a/evidence/high-precision-references.json').read_text())['rows']}
    rows=[]; cases=[];starts={}
    for r in fixed:
        d,u=exact(r); starts[r['key']]=tuple(float(inherited[r['key']]['equilibrium'][k]) for k in ['rhoL','rhoV','T'])
        cases.append(dict(key=r['key'],originalKey=r['key'],label='exact saved inventory',rho=d,u=u,bits=dict(rho=bits(d),u=bits(u))))
    for r in fixed:
        if r['key'] not in ['native-ledger-148','native-ledger-162','native-ledger-164','native-ledger-165']:continue
        d,u=exact(r)
        for name,n in [('rho',-1),('rho',1),('u',-1),('u',1),('rho',-16),('rho',16),('u',-16),('u',16)]:
            val=d if name=='rho' else u
            for _ in range(abs(n)):val=math.nextafter(val,math.inf if n>0 else -math.inf)
            dd,uu=(val,u) if name=='rho' else (d,val)
            cases.append(dict(key=r['key']+'-'+name+str(n),originalKey=r['key'],label=f'diagnostic {name} {n:+} ULP',rho=dd,u=uu,bits=dict(rho=bits(dd),u=bits(uu))))
        for du in [-.01,.01]:
            cases.append(dict(key=r['key']+'-du'+str(du),originalKey=r['key'],label=f'diagnostic fixed-density u {du:+} J/kg (binary64 addition)',rho=d,u=u+du,bits=dict(rho=bits(d),u=bits(u+du))))
    write('cases.json',cases)
    for c in cases:
        try:
            levels=[65,90] if c['label']=='exact saved inventory' else [65]
            rr=[]
            for n in levels:
                precision(n);d,u=mp.mpf(c['rho']),mp.mpf(c['u']);seed=starts[c['originalKey']]
                eq=solve(d,u,seed);hm=homogeneous(d,u,seed[2]);st=at_temperature(hm['T'],seed)
                stableSide=bool(d>=st['rhoL'] if d>hp.dc else d<=st['rhoV'])
                hm['saturationAtHomogeneousT']=st;hm['stableSideOfSaturation']=stableSide
                selection='equilibrium' if eq['physicalQuality'] else 'homogeneous' if stableSide and hm['stability']['positive'] else 'unresolved'
                out=dict(dps=n,equilibrium=eq,homogeneous=hm,selection=selection)
                if c['label']=='exact saved inventory':
                    sat=saturation_density(d,seed);out['fixedDensityBoundary']=sat;out['uMinusBoundary']=u-sat['endpoint']['u']
                    eq['liquidStability']=stability(eq['rhoL'],eq['T']);eq['vaporStability']=stability(eq['rhoV'],eq['T'])
                rr.append(enc(out))
            rows.append(dict(case=c,levels=rr))
        except Exception as ex:rows.append(dict(case=c,error=repr(ex)))
        print(c['key'],rows[-1].get('error',rows[-1].get('levels',[{}])[-1].get('selection')),flush=True)
    write('mathematical-references.json',dict(coefficientConvention='exact binary64 EOS coefficients and constants, freshly lifted at each precision; exact saved external mass rho/u',mpmath=mp.__version__,rows=rows))
    # Distinct initial guesses for the four original unresolved inventories.
    precision(65);sensitivity=[]
    for c in cases:
        if c['label']!='exact saved inventory' or c['originalKey'] in ['native-ledger-146','native-ledger-151','native-ledger-152']:continue
        for dt in [-.01,.01]:
            seed=starts[c['originalKey']];seed=(seed[0]*(1+dt/100),seed[1]*(1-dt/100),seed[2]+dt)
            try:sensitivity.append(dict(key=c['key'],offsetK=dt,result=solve(mp.mpf(c['rho']),mp.mpf(c['u']),seed)))
            except Exception as ex:sensitivity.append(dict(key=c['key'],offsetK=dt,error=repr(ex)))
    write('seed-sensitivity.json',sensitivity)
if __name__=='__main__':run()
