"""Independent DT roots and unchanged canonical inventory experiments.

The wheel supplies homogeneous reference EOS derivatives. Optional source shared
libraries are exercised through their C API; no corrected state enters a model.
"""
import argparse, ctypes as ct, json, math, os, struct, sys
from pathlib import Path
import CoolProp
from CoolProp import AbstractState, CoolProp as C
B=Path(__file__).resolve().parent
FIELDS={'p':'P','T':'T','rho':'Dmass','h':'Hmass','u':'Umass','Q':'Q','phase':'Phase'}
def bits(x): return struct.pack('>d',x).hex()
def pack(s): return dict(values=s,bits={k:bits(float(v)) for k,v in s.items()})
def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
class Backend:
    def __init__(self,lib=None):
        self.lib=ct.CDLL(lib) if lib else None
        if self.lib:
            L=self.lib
            L.AbstractState_factory.restype=ct.c_long
            L.AbstractState_factory.argtypes=[ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
            L.AbstractState_update.argtypes=[ct.c_long,ct.c_long,ct.c_double,ct.c_double,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
            L.AbstractState_keyed_output.restype=ct.c_double
            L.AbstractState_keyed_output.argtypes=[ct.c_long,ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
            for n in ['get_param_index','get_input_pair_index']:
                getattr(L,n).argtypes=[ct.c_char_p];getattr(L,n).restype=ct.c_long
            self.handle=self.call(L.AbstractState_factory,b'HEOS',b'Ammonia')
        else: self.a=AbstractState('HEOS','Ammonia')
    def call(self,f,*args):
        e=ct.c_long();msg=ct.create_string_buffer(4096)
        r=f(*args,ct.byref(e),msg,4096)
        if e.value: raise ValueError(msg.value.decode())
        return r
    def state(self,mode,a,b):
        pairs={'PH':('HmassP_INPUTS',b,a),'DU':('DmassUmass_INPUTS',a,b),'DT':('DmassT_INPUTS',a,b),'PQ':('PQ_INPUTS',a,b),'PT':('PT_INPUTS',a,b)}
        pair,x,y=pairs[mode]
        if self.lib:
            self.call(self.lib.AbstractState_update,self.handle,self.lib.get_input_pair_index(pair.encode()),x,y)
            return {k:self.call(self.lib.AbstractState_keyed_output,self.handle,self.lib.get_param_index(v.encode())) for k,v in FIELDS.items()}
        self.a.update(getattr(C,pair),x,y)
        return {k:self.a.keyed_output(C.get_parameter_index(v)) for k,v in FIELDS.items()}
def root(p,h,phase,seed):
    a=AbstractState('HEOS','Ammonia');a.specify_phase(getattr(C,'iphase_'+phase));rho,T=seed
    trace=[]
    for i in range(16):
        a.update(C.DmassT_INPUTS,rho,T);rp,rh=a.p()-p,a.hmass()-h
        trace.append(dict(rho=rho,T=T,pResidual=rp,hResidual=rh))
        if abs(rp)<1e-5 and abs(rh)<1e-8:break
        pr=a.first_partial_deriv(C.iP,C.iDmass,C.iT);pt=a.first_partial_deriv(C.iP,C.iT,C.iDmass)
        hr=a.first_partial_deriv(C.iHmass,C.iDmass,C.iT);ht=a.first_partial_deriv(C.iHmass,C.iT,C.iDmass)
        det=pr*ht-pt*hr
        rho+=(-rp*ht+pt*rh)/det;T+=(-pr*rh+hr*rp)/det
    return dict(state={k:a.keyed_output(C.get_parameter_index(v)) for k,v in FIELDS.items()},
        trace=trace,converged=abs(rp)<1e-5 and abs(rh)<1e-8,
        stability=dict(cp=a.cpmass(),cv=a.cvmass(),kappa=a.isothermal_compressibility()),
        derivatives=dict(rhoP=a.first_partial_deriv(C.iDmass,C.iP,C.iHmass),rhoH=a.first_partial_deriv(C.iDmass,C.iHmass,C.iP)))
def inventory(backend,p,h,rho,T):
    # Follow accepted bar/kJ arithmetic, including its actual binary64 operations.
    V=.003/5;M=rho*V;U=M*(h/1000)-100*(p/1e5)*V
    d=M/V;u=(U/M)*1000
    out=dict(input=pack(dict(M=M,U_kJ=U,V=V,rho=d,u=u)),accounting='accepted bar/kJ equations')
    try:
        du=backend.state('DU',d,u);audit=Backend().state('DT',du['rho'],du['T'])
        dif=dict(p=du['p']-p,h=du['h']-h,T=du['T']-T)
        out.update(DU=pack(du),independentDT=pack(audit),canonicalDifferences=dif,
            canonicalPass=all(abs(dif[k])<=v for k,v in dict(p=.1,h=.1,T=1e-4).items()),
            inventoryResiduals=dict(rho=du['rho']-d,u=du['u']-u),
            independentDUResiduals=dict(p=audit['p']-du['p'],h=audit['h']-du['h'],u=audit['u']-u),
            recoveredPressureInAcceptedRange=3e4<=du['p']<=35e5)
    except Exception as e: out.update(error=str(e),canonicalPass=False)
    return out
def run(lib,label):
    backend=Backend(lib);reference=Backend();rows=[]
    for request in json.loads((B/'inputs.json').read_text()):
        p,h=request['args'];row=dict(request=request)
        print(json.dumps(dict(marker=request['id'],args=[p,h],bits=[bits(p),bits(h)])),file=sys.stderr,flush=True)
        try:
            ph=backend.state('PH',p,h);dt=reference.state('DT',ph['rho'],ph['T'])
            sf=reference.state('PQ',p,0);sg=reference.state('PQ',p,1)
            distance=h-sf['h'];distanceg=h-sg['h'];tol=1e-8
            phase='liquid' if distance < -tol else 'gas' if distanceg > tol else 'equilibrium' if distance>tol and distanceg < -tol else 'endpoint-unresolved'
            row.update(PH=pack(ph),independentDT=pack(dt),residuals=dict(p=dt['p']-p,h=dt['h']-h),physicalPhase=phase,
                saturation=dict(liquid=pack(sf),vapor=pack(sg)),hMinusHf=distance,hMinusHg=distanceg)
            row['inventoryB']=inventory(backend,p,h,ph['rho'],ph['T'])
            if phase in ('liquid','gas'):
                rt=root(p,h,phase,(sf['rho'] if phase=='liquid' else sg['rho'],sf['T']))
                row['reference']=rt
                if rt['converged']:
                    a=rt['state'];row['inventoryA']=inventory(backend,p,h,a['rho'],a['T'])
                    row['reference']['binary64']=pack(a)
            if request['id']=='B1-vapor-regression':
                pt=backend.state('PT',p,ph['T']);dtpt=reference.state('DT',pt['rho'],pt['T'])
                row['PTatReturnedT']=pack(pt);row['PTindependentDT']=pack(dtpt)
                row['PTcacheDifference']={k:pt[k]-dtpt[k] for k in ('p','h','u')}
        except Exception as e: row['error']=str(e)
        rows.append(row)
    return dict(label=label,library=lib,wheelReference=dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__),rows=rows)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--library');ap.add_argument('--label',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args();save(Path(args.output),run(args.library,args.label))
