"""Independent mpmath evaluator and seed proposals; never validated arithmetic.

The inherited B5 source is executed unchanged except for redirecting its one
hardcoded JSON file path to the saved byte-identical C2 JSON. No source checkout,
CoolProp build or mutation occurs. Diagnostic derivatives use mp.diff.
"""
import hashlib,json,struct,types
from pathlib import Path
from fractions import Fraction as F

B=Path(__file__).resolve().parent
C2=B.parent/'browser_eos_b5b_c2'
source=B.parent/'browser_eos_b5/high-precision.py'
original=source.read_text()
needle="F=Path('/workspace/coolprop-b5/dev/fluids/Ammonia.json')"
assert original.count(needle)==1
hp=types.ModuleType('inherited_diagnostic')
hp.__file__=str(source)
exec(compile(original.replace(needle,'F=Path('+repr(str(C2/'evidence/Ammonia.json'))+')'),str(source),'exec'),hp.__dict__)
mp=hp.mp

def precision(n):
    mp.mp.dps=n
    hp.D=hp.lift(hp.data)
    hp.R=hp.D['gas_constant']/hp.D['molar_mass']
    hp.Tc=hp.D['STATES']['reducing']['T']
    hp.dc=hp.D['STATES']['reducing']['rhomolar']*hp.D['molar_mass']

def number(q):
    q=F(q)
    return mp.mpf(q.numerator)/q.denominator

def enc(x):
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    if isinstance(x,(tuple,list,mp.matrix)):return [enc(v) for v in x]
    if isinstance(x,mp.mpf):return mp.nstr(x,mp.mp.dps-5)
    return x

def bits(x):return struct.pack('>d',x).hex()
def decode(s):return struct.unpack('>d',bytes.fromhex(s))[0]
def target(b):
    m,U,v=[F(decode(b[k])) for k in ['M','U_kJ','V']]
    assert m>0 and v>0
    return m/v,1000*U/m

def inventory(d,h,P):
    # Original binary64 order, including original bar/kJ work term.
    V=.003/5
    M=d*V
    U_kJ=M*(h/1000)-100*(P/1e5)*V
    return {k:bits(v) for k,v in dict(M=M,U_kJ=U_kJ,V=V,rho=M/V,u=(U_kJ/M)*1000).items()}

def sat_res(x,T):
    l,v=hp.eos(x[0],T),hp.eos(x[1],T)
    return [(l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6]

def mix_res(x,d,u,mode):
    rl,rv,T=x
    l,v=hp.eos(rl,T),hp.eos(rv,T)
    q=(rl-d)*rv/(d*(rl-rv))
    w=(d-rv)*rl/(d*(rl-rv))
    fu=(l['u']-u)+q*(v['u']-l['u']) if mode=='liquid' else (v['u']-u)-w*(v['u']-l['u'])
    return sat_res(x,T)+[fu/10**6]

def inverse(fun,x):
    J=mp.matrix([[mp.diff(lambda y:fun([y if k==j else x[k] for k in range(len(x))])[i],x[j])
                  for j in range(len(x))] for i in range(len(x))])
    inv=J**-1
    return [[mp.nstr(inv[i,j],mp.mp.dps-5) for j in range(len(x))] for i in range(len(x))]

def solve(b,homseed,mixseed,offset=0):
    dd,uu=target(b)
    d,u=number(dd),number(uu)
    mode='liquid' if d>200 else 'vapor'
    T0=mp.mpf(homseed)+offset
    T=mp.findroot(lambda t:hp.eos(d,t)['u']-u,(T0-mp.mpf('.01'),T0+mp.mpf('.01')),
                  tol=mp.power(10,-mp.mp.dps+12),maxsteps=20)
    sat=mp.findroot(lambda a,b:sat_res([a,b],T),tuple(mp.mpf(v) for v in mixseed[:2]),
                    tol=mp.power(10,-mp.mp.dps+12),maxsteps=20)
    mix=mp.findroot(lambda a,b,t:mix_res([a,b,t],d,u,mode),tuple(mp.mpf(v) for v in mixseed),
                    tol=mp.power(10,-mp.mp.dps+12),maxsteps=20)
    return dict(homT=T,sat=list(sat),mix=list(mix),mode=mode,
                satInverse=inverse(lambda x:sat_res(x,T),list(sat)),
                mixInverse=inverse(lambda x:mix_res(x,d,u,mode),list(mix)),
                satResidual=sat_res(sat,T),mixResidual=mix_res(mix,d,u,mode))

def generated():
    precision(90)
    out=[]
    satseed=[mp.mpf('521.5'),mp.mpf('28.05')]
    for key,P,T0,dseed in [('generated-subcooled-liquid',3400000,335,540),
                          ('generated-superheated-vapor',3400000,365,25),
                          ('generated-outside-liquid',3600000,335,540)]:
        T=mp.mpf(T0)
        d=mp.findroot(lambda d:hp.eos(d,T)['p']-P,(dseed,dseed+1),maxsteps=20)
        z=hp.eos(d,T)
        b=inventory(float(d),float(z['h']),float(P))
        out.append(dict(key=key,inputBits=b,origin='separately generated diagnostic',homseed=str(T),mixseed=['521.5','28.05','345.56'],construction=dict(rhoBits=bits(float(d)),hBits=bits(float(z['h'])),PBits=bits(float(P)))))
    T=mp.mpf(344)
    rl,rv=mp.findroot(lambda a,b:sat_res([a,b],T),satseed,maxsteps=20)
    l,v=hp.eos(rl,T),hp.eos(rv,T)
    d=1/((1/rl+1/rv)/2)
    h=(l['h']+v['h'])/2
    b=inventory(float(d),float(h),float(l['p']))
    # This mixture needs no homogeneous root; a homogeneous seed is only a
    # diagnostic proposal and can fail. Do not force it into the scalar proof.
    out.append(dict(key='generated-interior-mixture',inputBits=b,origin='separately generated diagnostic',homseed=None,mixseed=[str(rl),str(rv),str(T)],construction=dict(rhoBits=bits(float(d)),hBits=bits(float(h)),PBits=bits(float(l['p'])))))
    d,T=mp.mpf(30),mp.mpf('345.56')
    z=hp.eos(d,T)
    b=inventory(float(d),float(z['h']),float(z['p']))
    out.append(dict(key='generated-dome-interior-homogeneous',inputBits=b,origin='separately generated adversarial diagnostic',homseed=str(T),mixseed=['521.5','28.05','345.56'],construction=dict(rhoBits=bits(float(d)),hBits=bits(float(z['h'])),PBits=bits(float(z['p'])))))
    return out
