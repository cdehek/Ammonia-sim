"""Regenerate bounded storage-inversion references using direct CoolProp 7.2.0."""
import json
import random
import sys
from pathlib import Path
sys.path.insert(0, '/workspace/scratch/python-deps')
import CoolProp
from CoolProp.CoolProp import PropsSI
assert CoolProp.__version__ == '7.2.0'
rng = random.Random(4512)
states = []
for kind in ['liquid', 'vapor', 'mixture']:
    for _ in range(30):
        p = .35*(30/.35)**rng.random()
        saturation = PropsSI('T', 'P', p*1e5, 'Q', 0, 'HEOS::Ammonia')
        if kind == 'mixture':
            args = ('P', p*1e5, 'Q', .01+.98*rng.random(), 'HEOS::Ammonia')
        else:
            offset = 5+150*rng.random() if kind == 'vapor' else -(1+15*rng.random())
            args = ('P', p*1e5, 'T', saturation+offset, 'HEOS::Ammonia')
        states.append({'kind': kind, 'p': p, 'T': PropsSI('T', *args)-273.15,
                       'rho': PropsSI('Dmass', *args), 'u': PropsSI('Umass', *args)/1000})
out = {'source': f'CoolProp {CoolProp.__version__} HEOS::Ammonia direct density/internal-energy states', 'states': states}
(Path(__file__).resolve().parents[1]/'tests/storage-reference.json').write_text(json.dumps(out, indent=2)+'\n')
print(out['source'], len(states), 'states')
