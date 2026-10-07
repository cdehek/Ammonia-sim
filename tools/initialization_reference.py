"""Regenerate starting-inventory references with direct CoolProp (not interpolation)."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, '/workspace/scratch/python-deps')
import CoolProp
from CoolProp.CoolProp import PropsSI

cases = []
for low, high, fills in [(2.5, 12, [.3, .1, .1]), (.35, 3, [0, .2, 1]), (8, 30, [.8, .01, .4])]:
    vessels = {}
    for name, volume, fraction in zip(['receiver', 'evaporator', 'condenser'], [.25, .08, .12], fills):
        pressure = low if name == 'evaporator' else high
        rho_f, rho_g = [PropsSI('Dmass', 'P', pressure*1e5, 'Q', q, 'HEOS::Ammonia') for q in [0, 1]]
        u_f, u_g = [PropsSI('Umass', 'P', pressure*1e5, 'Q', q, 'HEOS::Ammonia')/1000 for q in [0, 1]]
        liquid_mass, vapor_mass = volume*fraction*rho_f, volume*(1-fraction)*rho_g
        vessels[name] = {'massKg': liquid_mass+vapor_mass, 'internalEnergyKJ': liquid_mass*u_f+vapor_mass*u_g}
    cases.append({'suctionPressure': low, 'dischargePressure': high,
                  'liquidFractions': dict(zip(['receiver', 'evaporator', 'condenser'], fills)),
                  'vessels': vessels})
result = {'source': f'CoolProp {CoolProp.__version__} HEOS::Ammonia direct saturated Dmass/Umass', 'cases': cases}
(root/'tests/initialization-reference.json').write_text(json.dumps(result, indent=2)+'\n')
print(result['source'], len(cases), 'cases')
