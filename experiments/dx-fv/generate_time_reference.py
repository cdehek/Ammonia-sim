"""Independent continuous-time direct-EOS reference for the three-cell startup.
Uses SciPy Radau in conserved M/U coordinates, not the JS integration or table.
CoolProp is the table's EOS source, so this is not measured equipment validation.
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import CoolProp
from CoolProp import AbstractState, HmassP_INPUTS, DmassUmass_INPUTS, DmassT_INPUTS, PQ_INPUTS

assert CoolProp.__version__ == '7.2.0'
assert scipy.__version__ == '1.16.2'
eos = AbstractState('HEOS', 'Ammonia')
recovery_fallbacks = 0

def ph(p, h):
    eos.update(HmassP_INPUTS, h*1000, p*1e5)
    return dict(p=p, h=h, T=eos.T()-273.15, rho=eos.rhomass(), u=eos.umass()/1000)

def mu(mass, energy):
    global recovery_fallbacks
    rho, target_u = mass/.001, energy*1000/mass
    try:
        eos.update(DmassUmass_INPUTS, rho, target_u)
    except ValueError as error:
        # CoolProp D/U can fail exactly at Q=1 while locating an event.
        # Independent D/T flash + scalar energy root recovers the SAME rho/u;
        # no phase/inventory clamp, vapor selection or table recovery is used.
        if 'Input vapor quality' not in str(error):
            raise
        def energy_residual(temperature):
            eos.update(DmassT_INPUTS, rho, temperature)
            return eos.umass()-target_u
        temperature = brentq(energy_residual, 200, 600, xtol=1e-10)
        eos.update(DmassT_INPUTS, rho, temperature)
        if abs(eos.umass()-target_u)>1e-4:
            raise RuntimeError('Direct-EOS fallback energy recovery failed')
        recovery_fallbacks += 1
    return dict(p=eos.p()/1e5, h=eos.hmass()/1000, T=eos.T()-273.15, rho=eos.rhomass())

def saturation(p, quality):
    eos.update(PQ_INPUTS, p*1e5, quality)
    return eos.hmass()/1000

D, viscosity, friction = .02, 1e-5, .02
area = math.pi*D*D/4
length = .001/area
faces = [(length/2, 1000), (length, 0), (length, 0), (length/2, 2)]
inlet, outlet = ph(4, 500), ph(3.5, 1700)
initial = [dict(p=3.9, h=1000.), dict(p=3.8, h=1400.), dict(p=3.65, h=1650.)]
y0 = np.array([[s['rho']*.001, s['rho']*.001*s['u']] for s in [ph(**v) for v in initial]]).reshape(6)

def rhs(t, y):
    nodes = [inlet] + [mu(*y[2*i:2*i+2]) for i in range(3)] + [outlet]
    fluxes = []
    for i, (L, K) in enumerate(faces):
        left, right = nodes[i:i+2]
        dp = (left['p']-right['p'])*1e5
        donor = left if dp >= 0 else right
        rho = donor['rho']
        a = 128*viscosity*L/(math.pi*D**4*rho)
        b = (friction*L/D+K)/(2*rho*area*area)
        flow = math.copysign(2*abs(dp)/(a+math.sqrt(a*a+4*b*abs(dp))), dp)
        fluxes.append([flow, flow*donor['h']])
    rates = np.array(fluxes[:-1])-np.array(fluxes[1:])
    rates[:, 1] += 4
    return rates.reshape(6)

def dry_event(t, y):
    terminal = mu(*y[-2:])
    return terminal['h']-saturation(terminal['p'], 1)

dry_event.direction = -1
runs = []
for tolerance in [1e-8, 1e-10]:
    result = solve_ivp(rhs, (0, 1), y0, method='Radau', rtol=tolerance,
                       atol=np.tile([1e-13, 1e-10], 3), events=dry_event,
                       max_step=.01)
    if not result.success:
        raise RuntimeError(result.message)
    runs.append(dict(relativeTolerance=tolerance, steps=len(result.t)-1,
                     evaluations=result.nfev, sections=[mu(*result.y[2*i:2*i+2, -1]) for i in range(3)],
                     terminalDryToWetSeconds=float(result.t_events[0][0])))
out = dict(source='CoolProp 7.2.0 direct D/U EOS; SciPy 1.16.2 Radau conserved M/U continuous-time startup',
           sectionCount=3, seconds=1, boundaryFlashFallbacks=recovery_fallbacks, initial=initial, heatKW=[4, 4, 4], runs=runs)
target = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('time-reference.json')
target.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
