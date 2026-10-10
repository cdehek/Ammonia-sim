"""Direct-EOS discrete steady and continuous-time references for approved 3/5 or 3/5/9 cells.
No JS solver or embedded table; same CoolProp EOS source, not plant calibration.
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
D, volume, viscosity, friction = .02, .003, 1e-5, .02
area = math.pi*D*D/4
fallbacks = 0
meshes = tuple(map(int, sys.argv[2].split(','))) if len(sys.argv)>2 else (3, 5)
assert meshes in ((3, 5), (3, 5, 9)), 'Only the approved comparison meshes may be integrated'

def ph(p, h):
    eos.update(HmassP_INPUTS, h*1000, p*1e5)
    return dict(p=p, h=h, T=eos.T()-273.15, rho=eos.rhomass(), u=eos.umass()/1000)

def mu(mass, energy, cell_volume):
    global fallbacks
    rho, target_u = mass/cell_volume, energy*1000/mass
    try:
        eos.update(DmassUmass_INPUTS, rho, target_u)
    except ValueError as error:
        if 'Input vapor quality' not in str(error):
            raise
        def residual(temperature):
            eos.update(DmassT_INPUTS, rho, temperature)
            return eos.umass()-target_u
        temperature = brentq(residual, 200, 600, xtol=1e-10)
        eos.update(DmassT_INPUTS, rho, temperature)
        if abs(eos.umass()-target_u)>1e-4:
            raise RuntimeError('Reference D/T recovery does not conserve energy')
        fallbacks += 1
    return dict(p=eos.p()/1e5, h=eos.hmass()/1000, T=eos.T()-273.15, rho=eos.rhomass())

def sat(p, quality):
    eos.update(PQ_INPUTS, p*1e5, quality)
    return dict(h=eos.hmass()/1000, T=eos.T()-273.15)

def geometry(n):
    assert n in meshes
    length = volume/area/n
    return [(length/2, 1000)] + [(length, 0)]*(n-1) + [(length/2, 2)]

def heat(n, total, profile):
    return [total/n if profile=='uniform' else total*(.5/n+.5*(((i+1)/n)**2-(i/n)**2)) for i in range(n)]

def drop(flow, donor, face):
    L, K = face
    rho = donor['rho']
    return 128*viscosity*L/(math.pi*D**4*rho)*flow + (friction*L/D+K)/(2*rho*area*area)*flow*abs(flow)

def steady(n, total, profile):
    heat_kw, faces = heat(n, total, profile), geometry(n)
    def shoot(flow):
        p, h, sections = 4., 500., []
        for i, face in enumerate(faces):
            p -= drop(flow, ph(p, h), face)/1e5
            if i<n:
                h += heat_kw[i]/flow
                sections.append(ph(p, h))
        return dict(flowKgS=flow, outletPressure=p, sections=sections)
    flow = brentq(lambda m: shoot(m)['outletPressure']-3.5, .012, .02, xtol=1e-14)
    return dict(sectionCount=n, totalHeatKW=total, heatProfile=profile, **shoot(flow))

def startup(n, tolerance, total_heat=12.):
    cell_volume, faces = volume/n, geometry(n)
    state = ph(3.65, 1650.)
    initial = np.tile([state['rho']*cell_volume, state['rho']*cell_volume*state['u']], n)
    inlet, outlet = ph(4., 500.), ph(3.5, 1700.)
    def states(y):
        return [mu(*y[2*i:2*i+2], cell_volume) for i in range(n)]
    def rhs(t, y):
        nodes, fluxes = [inlet]+states(y)+[outlet], []
        for i, (L, K) in enumerate(faces):
            left, right = nodes[i:i+2]
            dp = (left['p']-right['p'])*1e5
            donor = left if dp>=0 else right
            rho = donor['rho']
            a = 128*viscosity*L/(math.pi*D**4*rho)
            b = (friction*L/D+K)/(2*rho*area*area)
            flow = math.copysign(2*abs(dp)/(a+math.sqrt(a*a+4*b*abs(dp))), dp)
            fluxes.append([flow, flow*donor['h']])
        rates = np.array(fluxes[:-1])-np.array(fluxes[1:])
        rates[:, 1] += total_heat/n
        return rates.reshape(2*n)
    def wet_event(t, y):
        terminal = states(y)[-1]
        return terminal['h']-sat(terminal['p'], 1)['h']
    wet_event.direction = -1
    def property_limit(t, y):
        return 250-max(v['T']-sat(v['p'], 1)['T'] for v in states(y))
    property_limit.direction = -1
    property_limit.terminal = True
    solution = solve_ivp(rhs, (0, 2), initial, method='Radau', rtol=tolerance,
                         atol=np.tile([1e-13, 1e-10], n), max_step=.005,
                         events=[wet_event, property_limit], dense_output=True)
    if not solution.success:
        raise RuntimeError(solution.message)
    samples = [dict(seconds=t, sections=states(solution.sol(t))) for t in [.01, .05, .2] if t<=solution.t[-1]]
    return dict(relativeTolerance=tolerance, seconds=float(solution.t[-1]), steps=len(solution.t)-1,
                evaluations=solution.nfev, samples=samples,
                wetEventsSeconds=solution.t_events[0].tolist(), domainEventsSeconds=solution.t_events[1].tolist())

out = dict(source='CoolProp 7.2.0 HEOS::Ammonia; independent steady shooting and SciPy 1.16.2 Radau M/U startup',
           geometry=dict(totalVolumeM3=volume, diameterM=D, tubeLengthM=volume/area, viscosityPaS=viscosity, darcyF=friction, inletMinorK=1000, outletMinorK=2),
           steady=[], startup=[])
for n in meshes:
    for total, profile in [(12., 'uniform'), (18., 'uniform'), (18., 'graded')]:
        out['steady'].append(steady(n, total, profile))
    out['startup'].append(dict(sectionCount=n, initial=dict(p=3.65, h=1650.), totalHeatKW=12,
                              runs=[startup(n, tolerance) for tolerance in (1e-8, 1e-10)]))
if meshes == (3, 5, 9):
    out['heatSensitivity'] = [dict(sectionCount=n, totalHeatKW=q, runs=[startup(n, tolerance, q) for tolerance in (1e-8, 1e-10)]) for q in (0., 6.) for n in meshes]
out['boundaryFlashFallbacks'] = fallbacks
target = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('spatial-reference.json')
target.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(dict(path=str(target), steadyCases=len(out['steady']), meshes=[v['sectionCount'] for v in out['startup']], boundaryFlashFallbacks=fallbacks), indent=2))
