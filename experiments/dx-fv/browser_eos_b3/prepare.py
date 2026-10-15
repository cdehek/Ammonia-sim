"""Create a focused, additive B3 matrix. Never rewrite B1/B2 evidence."""
import json, struct
from pathlib import Path
B = Path(__file__).resolve().parent
def bits(x): return struct.pack('>d', x).hex()
def write(name, value):
    p = B / name
    assert not p.exists(), p
    p.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
old = json.loads((B.parent / 'browser_eos_b2/inputs.json').read_text())
# Reuse historical endpoints and signed-offset inputs without regenerating them.
rows = [q for q in old if q['id'] == 'B1-vapor-regression' or
        (q['id'].startswith('approach-') and q['id'].endswith(('-0.0', '-0.001', '-0.01')))]
for p in sorted({q['args'][0] for q in rows if q['id'].startswith('approach-')}):
    sat = next(q['saturationSource'] for q in rows if q['args'][0] == p and 'saturationSource' in q)
    for endpoint in ('hf', 'hg'):
        # Explicitly diagnostic tolerance sweep; these are never solver probes.
        for qoff in (-1.01e-9, -0.99e-9, 0.99e-9, 1.01e-9):
            h = sat[endpoint] + qoff * (sat['hg'] - sat['hf'])
            rows.append(dict(id=f'diagnostic-quality-band-{p}-{endpoint}-{qoff}', mode='PH',
                args=[p,h], inputBits=[bits(p),bits(h)], origin='B3 diagnostic tolerance sweep',
                saturationSource=sat, nominalQualityOffset=qoff, endpoint=endpoint))
for q in rows: assert q['inputBits'] == [bits(x) for x in q['args']]
assert any(q['args'] == [30298.937123458254,98904.56398938334] for q in rows)
write('inputs.json', rows)
print(len(rows), 'focused base inputs')
