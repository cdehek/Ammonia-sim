"""Diagnostic float64 equilibrium Newton; no CoolProp source or policy changes.

Uses separate unmodified DT EOS states and analytic thermodynamic Jacobians.
Unphysical qualities, stagnant residuals and all exceptions remain results.
"""
import json, math, os, platform, struct, sys, time
from pathlib import Path
import numpy as np
from CoolProp import AbstractState, CoolProp as C
import CoolProp
B=Path(__file__).resolve().parent; E=Path(os.environ.get('GATE_B_EVIDENCE',B/'evidence'))
sys.path.insert(0,str(B));import math_reference as ref
L=AbstractState('HEOS','Ammonia');V=AbstractState('HEOS','Ammonia')
L.specify_phase(C.iphase_liquid);V.specify_phase(C.iphase_gas)
dc=float(ref.hp.dc);Tc=float(ref.hp.Tc)
def prop(a):
    return dict(p=a.p(),u=a.umass(),g=a.gibbsmass(),h=a.hmass(),cv=a.cvmass(),cp=a.cpmass(),
        pr=a.first_partial_deriv(C.iP,C.iDmass,C.iT),pt=a.first_partial_deriv(C.iP,C.iT,C.iDmass),
        ur=a.first_partial_deriv(C.iUmass,C.iDmass,C.iT),s=a.smass())
def evaleq(x,d,u,coordinates=None):
    rL,rV,T=x*np.array([dc,dc,Tc]) if coordinates is None else coordinates
    if not (rL>rV>0 and T>0):raise ValueError('inadmissible density ordering/temperature iterate')
    L.update(C.DmassT_INPUTS,rL,T);V.update(C.DmassT_INPUTS,rV,T);l,v=prop(L),prop(V)
    den=1/rV-1/rL
    if d<dc:
        w=(d-rV)*rL/(d*(rL-rV));q=1-w
        eu=math.fsum([v['u'],-u,-w*(v['u']-l['u'])])
    else:
        q=(rL-d)*rV/(d*(rL-rV));w=1-q
        eu=math.fsum([l['u'],-u,q*(v['u']-l['u'])])
    qnaive=(1/d-1/rL)/den
    naive=(1-qnaive)*l['u']+qnaive*v['u']-u
    J=np.array([[l['pr'],-v['pr'],l['pt']-v['pt']],
        [l['pr']/rL,-v['pr']/rV,-l['s']+l['pt']/rL+v['s']-v['pt']/rV],
        [w*l['ur']+(v['u']-l['u'])*w/(rL*rL*den),q*v['ur']+(v['u']-l['u'])*q/(rV*rV*den),w*l['cv']+q*v['cv']]])
    J=J*np.array([dc,dc,Tc])/1e6
    f=np.array([l['p']-v['p'],l['g']-v['g'],eu])/1e6
    vm=math.fsum([w/rL,q/rV]);um=math.fsum([w*l['u'],q*v['u']])
    o=dict(T=T,rhoL=rL,rhoV=rV,Q=q,liquidFraction=w,p=(l['p']+v['p'])/2,
        residuals=dict(p=f[0]*1e6,mu=f[1]*1e6,u=eu,naiveU=naive,volume=vm-1/d),
        reconstructedDensity=1/vm,reconstructedU=um,physicalQuality=bool(q>=0 and w>=0 and q<=1 and w<=1),
        endpointsStable=bool(l['cv']>0 and l['cp']>0 and l['pr']>0 and v['cv']>0 and v['cp']>0 and v['pr']>0),
        jacobianConditionScaled=float(np.linalg.cond(J)),jacobianConditionUnscaled=float(np.linalg.cond(J*1e6/np.array([dc,dc,Tc]))),
        liquid=l,vapor=v)
    o['originalReferenceResidualsPass']=bool(abs(f[0]*1e6)<1e-5 and abs(f[1]*1e6)<1e-8 and abs(eu)<1e-8)
    # Local DU screening with the accepted scale constants. This reconstruction
    # is not an A2 stage check against the saved original M/U ledger.
    o['normalizedMassResidual']=abs((1/vm-d)*.003/5)/max(.01,d*.003/5)
    o['normalizedEnergyResidual']=abs(((1/vm)*um-d*u)*(.003/5)/1000)/max(1,abs(d*u*(.003/5)/1000))
    return f,J,o
def solve(d,u,seed,stop):
    x=np.array(seed)/np.array([dc,dc,Tc]);trace=[];seen=set();start=time.perf_counter()
    for i in range(20):
        f,J,o=evaleq(x,d,u);trace.append(dict(iteration=i,**o))
        key=tuple(struct.pack('>d',float(a)).hex() for a in x)
        if stop=='original-reference' and o['originalReferenceResidualsPass']:reason='original reference residual limits reached';break
        if key in seen:reason='binary64 coordinate stagnation/cycle';break
        seen.add(key);step=np.linalg.solve(J,-f);xn=x+step
        if np.array_equal(x,xn):reason='binary64 correction rounds to same coordinates';break
        x=xn
    else:reason='20-iteration diagnostic bound'
    return dict(stopPolicy=stop,iterations=i,termination=reason,seconds=time.perf_counter()-start,final=o,trace=trace)
def run():
    cases=json.loads((E/'cases.json').read_text());old={r['key']:r['reference'] for r in json.loads((B.parent/'browser_eos_b5a/evidence/high-precision-references.json').read_text())['rows']}
    rows=[]
    for c in cases:
        seed=tuple(float(old[c['originalKey']]['equilibrium'][k]) for k in ['rhoL','rhoV','T']);attempts=[]
        for shift in [-.01,0,.01]:
            initial=(seed[0]*(1+shift/100),seed[1]*(1-shift/100),seed[2]+shift)
            for stop in ['original-reference','coordinate-stagnation']:
                try:attempts.append(dict(seedShiftK=shift,initial=initial,result=solve(c['rho'],c['u'],initial,stop)))
                except Exception as ex:attempts.append(dict(seedShiftK=shift,initial=initial,stopPolicy=stop,error=repr(ex)))
        rows.append(dict(case=c,attempts=attempts));print(c['key'],'done',flush=True)
    ref.write('binary64-results.json',dict(precision='IEEE binary64, NumPy float64; no fast-math requested',wheel=CoolProp.__version__,wheelGit=CoolProp.__gitrevision__,numpy=np.__version__,platform=platform.platform(),rows=rows))
    coordinate_grid()
def coordinate_grid():
    # Local representability and residual signs at neighboring state coordinates.
    maths=json.loads((E/'mathematical-references.json').read_text());grid=[]
    for r in maths['rows']:
        if r['case']['label']!='exact saved inventory' or 'error'in r:continue
        eq=r['levels'][-1]['equilibrium'];seed=[float(eq[k]) for k in ['rhoL','rhoV','T']];pts=[]
        for j in range(3):
            for direction in [-math.inf,math.inf]:
                s=seed.copy();s[j]=math.nextafter(s[j],direction)
                _,_,o=evaleq(None,r['case']['rho'],r['case']['u'],coordinates=s)
                pts.append(dict(coordinate=['rhoL','rhoV','T'][j],direction=str(direction),requestedCoordinates=s,state=o))
        _,_,o=evaleq(None,r['case']['rho'],r['case']['u'],coordinates=seed)
        grid.append(dict(key=r['case']['key'],roundedReference=o,adjacent=pts))
    ref.write('coordinate-grid.json',grid)
if __name__=='__main__':
    if '--grid-only' in sys.argv:coordinate_grid()
    else:run()
