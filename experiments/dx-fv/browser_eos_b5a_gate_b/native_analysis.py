"""Focused Gate A replay, actual internal-coordinate references, and raw neighbors."""
import ctypes as ct, json, os, sys, time
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));import math_reference as m
sys.path.insert(0,str(B.parent/'browser_eos_b3'));from native import Backend,pack
E=m.E
def load(n):return json.loads((E/n).read_text())
def close(b):
    b.lib.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long];b.call(b.lib.AbstractState_free,b.handle)
def call(b,d,u):
    t=time.perf_counter()
    try:r=dict(DU=pack(b.state('DU',d,u)))
    except Exception as ex:r=dict(error=str(ex),exceptionType=type(ex).__name__)
    return r,time.perf_counter()-t
def hom64(d,u,T):
    a=AbstractState('HEOS','Ammonia');a.specify_phase(C.iphase_liquid if d>225 else C.iphase_gas);trace=[]
    for i in range(12):
        a.update(C.DmassT_INPUTS,d,T);eu=a.umass()-u;trace.append(dict(T=T,uResidual=eu))
        if abs(eu)<1e-8:reason='original reference caloric residual';break
        nt=T-eu/a.cvmass()
        if nt==T:reason='coordinate stagnation';break
        T=nt
    else:reason='12-iteration diagnostic bound'
    sat=AbstractState('HEOS','Ammonia');sat.update(C.QT_INPUTS,0,a.T());rl=sat.rhomass();sat.update(C.QT_INPUTS,1,a.T());rv=sat.rhomass()
    return dict(state=dict(p=a.p(),h=a.hmass(),T=a.T(),rho=a.rhomass(),u=a.umass()),trace=trace,iterations=i,termination=reason,
        stability=dict(cv=a.cvmass(),cp=a.cpmass(),dp_drho_T=a.first_partial_deriv(C.iP,C.iDmass,C.iT)),
        binary64Saturation=dict(rhoL=rl,rhoV=rv),densityMinusRelevantEndpoint=d-(rl if d>225 else rv),
        certification='NONE: stable-side sign requires original independently resolved phase contract')
def run():
    native=load('native-results.json');diag=load('native-trace-results.json')
    assert native['rows']==diag['rows']
    old={r['key']:r for r in json.loads((B.parent/'browser_eos_b5a/evidence/A1-uninstrumented.json').read_text())['rows']}
    for r in native['rows']:assert r==old[r['key']]
    blocks={};key=None
    for ln in (E/'native-trace.jsonl').read_text().splitlines():
        r=json.loads(ln)
        if 'marker'in r:key=r['marker'];blocks[key]=[]
        else:blocks[key].append(r)
    maths={r['case']['key']:r for r in load('mathematical-references.json')['rows']};summary=[]
    fixed={r['key']:r for r in load('fixed-inputs.json')}
    for key,ev in blocks.items():
        entries=[i for i,e in enumerate(ev) if e['event']=='DU_entry_rhomolar_umolar_config'];ev=ev[:entries[1]]
        def last(n):return [e for e in ev if e['event']==n][-1]
        entry=last('DU_entry_rhomolar_umolar_config');phase=last('legacy_phase_value_satValue_satT_satRho');coord=last('satD_final_rhoL_rhoV_TL_TV')
        requested=fixed[key]['input'];seed=tuple(float(maths[key]['levels'][-1]['equilibrium'][k]) for k in ['rhoL','rhoV','T']);levels=[]
        for n in [65,90]:
            m.precision(n);M=m.hp.D['molar_mass'];d=m.mp.mpf(entry['a'])*M;u=m.mp.mpf(entry['b'])/M;sat=m.saturation_density(d,seed)
            l,v=m.hp.eos(m.mp.mpf(coord['a'])*M,m.mp.mpf(coord['c'])),m.hp.eos(m.mp.mpf(coord['b'])*M,m.mp.mpf(coord['d']))
            levels.append(m.enc(dict(dps=n,internalMassEquivalent=dict(rho=d,u=u),saturationAtActualInternalDensity=sat,uMinusSat=u-sat['endpoint']['u'],cachedCoordinatesIndependentEOSResiduals=dict(p=l['p']-v['p'],mu=l['g']-v['g']))))
        row=dict(key=key,originalInput=requested,internalBinary64=dict(rhomolar=entry['a'],umolar=entry['b'],bits=dict(rhomolar=m.bits(entry['a']),umolar=m.bits(entry['b']))),internalReferences=levels,phaseDecision=phase,finalSaturation=coord,events=ev,
            selectedPhase='coexistence attempted' if any(e['event']=='legacy_dispatch_two_phase'for e in ev) else 'homogeneous liquid',
            finalSaturationDecision='input <= saturation u' if phase['a']<=phase['b'] else 'input > saturation u',
            result=next(r for r in native['rows'] if r['key']==key),brentReturns=[e for e in ev if e['event']=='Brent_return_b_fb_iter_threshold'],brentStops=[e for e in ev if e['event'].startswith('Brent_stop')])
        row['homogeneousBinary64']=[dict(seedOffsetK=dt,result=hom64(*m.exact(fixed[key]),seed[2]+dt))for dt in [-.01,0,.01]]
        two=[e for e in ev if e['event']=='legacy_two_phase_return_Treturn_Tstate_Qd']
        if two:
            T=two[-1]['a'];q=two[-1]['c'];a=AbstractState('HEOS','Ammonia');ends=[]
            for quality in [0,1]:
                a.update(C.QT_INPUTS,quality,T);ends.append(dict(rho=a.rhomass(),u=a.umass(),p=a.p(),g=a.gibbsmass()))
            l,v=ends;dd,uu=m.exact(fixed[key]);vol=(1-q)/l['rho']+q/v['rho'];en=(1-q)*l['u']+q*v['u']
            row['refusedAlgebraicMixtureAudit']=dict(label='Independent saturation QT evaluation at traced T; extrapolated Q is unphysical; NOT a returned DU state or captured failed cache',T=T,Q=q,endpoints=ends,pResidual=l['p']-v['p'],muResidual=l['g']-v['g'],volumeResidual=vol-1/dd,uResidual=en-uu)
        else:
            s=row['result']['reused']['DU']['values'];a=AbstractState('HEOS','Ammonia');a.specify_phase(C.iphase_liquid);a.update(C.DmassT_INPUTS,s['rho'],s['T']);dd,uu=m.exact(fixed[key])
            row['returnedIndependentAudit']=dict(volumeResidual=1/a.rhomass()-1/dd,uResidual=a.umass()-uu,pGetterMinusFreshEOS=s['p']-a.p(),hGetterMinusFreshEOS=s['h']-a.hmass())
        summary.append(row)
    m.write('four-case-reproduction-and-controls.json',dict(parityWithInheritedGateA=True,loggingParity=True,rows=summary))
    b=Backend('/workspace/gate-b-libs/A1.so');b.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];b.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',False);rows=[]
    for c in load('cases.json'):
        reuse,cost=call(b,c['rho'],c['u']);fresh=Backend('/workspace/gate-b-libs/A1.so');fr,fcost=call(fresh,c['rho'],c['u']);close(fresh)
        rows.append(dict(case=c,reused=reuse,fresh=fr,equal=reuse==fr,reusedSeconds=cost,freshCallSeconds=fcost))
    close(b);m.write('native-neighbors.json',dict(library='/workspace/gate-b-libs/A1.so',fullVLE=True,rows=rows))
if __name__=='__main__':run()
