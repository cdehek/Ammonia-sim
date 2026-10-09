"""Independent direct-EOS pathway; no embedded table or JS solver is used.

CoolProp is the same EOS source as properties.json: this checks interpolation,
recovery and implementation, not independent experimental equipment accuracy.
Run: python experiments/dx-fv/generate_reference.py [output.json]
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
import CoolProp
from CoolProp.CoolProp import PropsSI

if CoolProp.__version__ != '7.2.0':
    raise RuntimeError('References require CoolProp 7.2.0')
FLUID = 'HEOS::Ammonia'

def ph(p, h):
    args = ('P', p*1e5, 'Hmass', h*1000, FLUID)
    return dict(p=p, h=h, T=PropsSI('T', *args)-273.15,
                rho=PropsSI('Dmass', *args), u=PropsSI('Umass', *args)/1000,
                quality=PropsSI('Q', *args))

states = []
for p in [0.5, 2.5, 4.0, 12.0, 25.0]:
    for quality in [1e-5, 0.2, 0.8, 1-1e-5]:
        h = PropsSI('Hmass', 'P', p*1e5, 'Q', quality, FLUID)/1000
        states.append(dict(kind='mixture', **ph(p, h)))
    saturation = PropsSI('T', 'P', p*1e5, 'Q', 0, FLUID)
    for kind, offset in [('liquid', -2), ('liquid', -15), ('vapor', 5), ('vapor', 40)]:
        h = PropsSI('Hmass', 'P', p*1e5, 'T', saturation+offset, FLUID)/1000
        states.append(dict(kind=kind, **ph(p, h)))

# Separate steady shooting solution: common flow, section enthalpy rise Q/m,
# pressure drops accumulated downstream using direct EOS donor density.
D, V, mu, f = .02, .003, 1e-5, .02
A = math.pi*D*D/4
length = V/A/3
faces = [(length/2, 1000), (length, 0), (length, 0), (length/2, 2)]

def steady_at(flow, heat):
    p, h, sections = 4.0, 500.0, []
    for i, (L, K) in enumerate(faces):
        rho = ph(p, h)['rho']
        dp = 128*mu*L/(math.pi*D**4*rho)*flow + (f*L/D+K)/(2*rho*A*A)*flow**2
        p -= dp/1e5
        if p < .3:
            raise ValueError('Reference pressure left prototype domain')
        if i < 3:
            h += heat[i]/flow
            sections.append(ph(p, h))
    return dict(flowKgS=flow, outletPressure=p, sections=sections)

steady = []
for heat in [[4.0]*3, [6.0]*3, [2.0, 4.0, 12.0]]:
    low, high = .012, .02
    assert steady_at(low, heat)['outletPressure'] > 3.5
    assert steady_at(high, heat)['outletPressure'] < 3.5
    for _ in range(55):
        mid = (low+high)/2
        if steady_at(mid, heat)['outletPressure'] > 3.5:
            low = mid
        else:
            high = mid
    steady.append(dict(heatKW=heat, **steady_at((low+high)/2, heat)))

def transient_reference():
    """Separate direct-EOS backward-Euler solve for one startup second."""
    Vcell, dt = .001, .025
    x = np.array([3.9, 1000.0, 3.8, 1400.0, 3.65, 1650.0])

    def inventory(values):
        states = [ph(values[2*i], values[2*i+1]) for i in range(3)]
        stored = np.array([[v['rho']*Vcell, v['rho']*Vcell*v['u']] for v in states])
        return states, stored

    def fluxes(states):
        nodes = [ph(4.0, 500.0)] + states + [ph(3.5, 1700.0)]
        rates = []
        for i, (L, K) in enumerate(faces):
            left, right = nodes[i:i+2]
            dp = (left['p']-right['p'])*1e5
            donor = left if dp >= 0 else right
            rho = donor['rho']
            a = 128*mu*L/(math.pi*D**4*rho)
            b = (f*L/D+K)/(2*rho*A*A)
            flow = math.copysign(2*abs(dp)/(a+math.sqrt(a*a+4*b*abs(dp))), dp)
            rates.append([flow, flow*donor['h']])
        return np.array(rates)

    for _ in range(40):
        _, old = inventory(x)
        scales = np.maximum(np.abs(old), [.01, 1.0])

        def residual(values):
            if any(values[2*i] < .3 or values[2*i] > 35 for i in range(3)):
                raise ValueError('Transient reference pressure outside domain')
            states, stored = inventory(values)
            flows = fluxes(states)
            rates = flows[:-1]-flows[1:]
            rates[:, 1] += 4.0
            return ((stored-old-dt*rates)/scales).reshape(6)

        guess = x.copy()
        for iteration in range(30):
            r = residual(guess)
            error = max(abs(r))
            if error < 1e-11:
                break
            jac = np.empty((6, 6))
            for k in range(6):
                epsilon = (1e-5 if k%2 == 0 else 1e-4)*max(1, abs(guess[k]))
                trial = guess.copy(); trial[k] += epsilon
                jac[:, k] = (residual(trial)-r)/epsilon
            delta = np.linalg.solve(jac, -r)
            factor = 1.0
            while factor >= 1/4096:
                trial = guess+factor*delta
                try:
                    if max(abs(residual(trial))) < error:
                        guess = trial
                        break
                except (ValueError, OverflowError):
                    pass
                factor /= 2
            else:
                raise RuntimeError('Direct-EOS transient line search failed')
        else:
            raise RuntimeError('Direct-EOS transient iteration failed')
        x = guess
    states, _ = inventory(x)
    return dict(seconds=1.0, stepSeconds=dt, heatKW=[4.0]*3,
                initial=[dict(p=3.9, h=1000.0), dict(p=3.8, h=1400.0), dict(p=3.65, h=1650.0)],
                sections=states, flowKgS=float(fluxes(states)[0, 0]))

out = dict(source='CoolProp 7.2.0 HEOS::Ammonia; direct P/H states and independent steady shooting',
           units=dict(p='bar absolute', h='kJ/kg', u='kJ/kg', T='C', rho='kg/m3'),
           sectionCount=3, states=states, steady=steady, transient=transient_reference())
target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('reference.json')
target.write_text(json.dumps(out, indent=2)+'\n')
print(f'{len(states)} property references, {len(steady)} three-section steady solutions: {target}')
