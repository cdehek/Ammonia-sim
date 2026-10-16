"""Measure physical saturation brackets on adjacent representable temperatures."""
import json, math, sys
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));import math_reference as m
def run():
    m.precision(90);mp=m.mp;rows=[];a=AbstractState('HEOS','Ammonia')
    refs=json.loads((m.E/'mathematical-references.json').read_text())['rows']
    for r in refs:
        c=r['case']
        if c['label']!='exact saved inventory' or c['key'] in ['native-ledger-146','native-ledger-151','native-ledger-152']:continue
        hi=r['levels'][-1];eq=hi['equilibrium'];boundary=hi['fixedDensityBoundary']['endpoint'];T0=float(eq['T']);pts=[]
        for j in range(-4,5):
            T=T0
            for _ in range(abs(j)):T=math.nextafter(T,math.inf if j>0 else -math.inf)
            states=[]
            for q in [0,1]:
                a.update(C.QT_INPUTS,q,T);states.append(dict(rho=a.rhomass(),u=a.umass(),p=a.p(),g=a.gibbsmass()))
            l,v=states;d,u=c['rho'],c['u']
            if d<225:
                w=(d-v['rho'])*l['rho']/(d*(l['rho']-v['rho']));q=1-w;eu=math.fsum([v['u'],-u,-w*(v['u']-l['u'])])
            else:
                q=(l['rho']-d)*v['rho']/(d*(l['rho']-v['rho']));w=1-q;eu=math.fsum([l['u'],-u,q*(v['u']-l['u'])])
            independent=[m.hp.eos(mp.mpf(s['rho']),mp.mpf(T))for s in states]
            pts.append(dict(T=T,TBits=m.bits(T),offsetULP=j,Q=q,liquidFraction=w,physical=bool(0<=q<=1 and 0<=w<=1),energyResidual=eu,endpoints=states,
                freshHighPrecisionEndpointErrors=[dict(p=mp.mpf(s['p'])-z['p'],u=mp.mpf(s['u'])-z['u'],g=mp.mpf(s['g'])-z['g']) for s,z in zip(states,independent)]))
        brackets=[]
        for l,v in zip(pts,pts[1:]):
            if l['physical'] and v['physical'] and l['energyResidual']*v['energyResidual']<=0:
                brackets.append(dict(low=l['offsetULP'],high=v['offsetULP'],zeroAtEndpoint=l['energyResidual']==0 or v['energyResidual']==0))
        rows.append(dict(key=c['key'],input=c,temperatureULP=math.ulp(T0),equilibriumTMinusDensityBoundaryT=mp.mpf(eq['T'])-mp.mpf(boundary['T']),
            separationInTemperatureULP=(mp.mpf(eq['T'])-mp.mpf(boundary['T']))/math.ulp(T0),physicalBinary64SignBrackets=brackets,grid=pts,
            interpretation='Observed sign brackets only; no interval error bound or phase certification'))
    m.write('temperature-brackets.json',rows)
if __name__=='__main__':run()
