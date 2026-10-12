"""Diagnostic-only local Radau continuations; never writes accepted references.

Loads the already independently assembled Stage 2B equations without running its
generator. A saved original cold endpoint at 120 s supplies the extended case's
exact pre-boundary trajectory. Same equations, EOS, method and original atol.
"""
import ast
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(sys.argv[1])
TARGET = Path(sys.argv[2]).resolve()
assert not TARGET.is_relative_to(ROOT)
assert not TARGET.is_relative_to(EVIDENCE.resolve()), 'Preserved failure evidence is read-only'
N = int(sys.argv[3])
assert N in (5, 9)
SEED_KIND = sys.argv[4] if len(sys.argv) > 4 else 'eos'
RTOL = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-10
MAX_STEP = float(sys.argv[6]) if len(sys.argv) > 6 else .025
PROPERTY_KIND = sys.argv[7] if len(sys.argv) > 7 else 'direct-eos'
assert SEED_KIND in ('eos', 'js', 'checkpoint')
assert PROPERTY_KIND in ('direct-eos', 'table', 'sat-temperature')

source = ROOT / 'experiments/dx-fv/generate_coupled_stage2b_reference.py'
tree = ast.parse(source.read_text())
prefix = []
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SAMPLES' for t in node.targets):
        break
    prefix.append(node)
else:
    raise AssertionError('Missing independent equation boundary')
# Pin the source's section-count argument; no generation loop is executed.
argv = sys.argv
sys.argv = [str(source), str(TARGET), str(N)]
ns = {'__file__': str(source)}
exec(compile(ast.Module(body=prefix, type_ignores=[]), str(source), 'exec'), ns)
sys.argv = argv
F, J = ns['FLUID'], ns['JOINT']
CAP = ns['CAPACITIES']
mesh = 'five' if N == 5 else 'nine'
reference = json.loads((EVIDENCE / f'{mesh}-fresh-reference.json').read_text())
cold = next(c for c in reference['cases'] if c['name'] == 'cold')
seed_run = cold['runs'][0 if RTOL >= 1e-8 else 1]
row = next(v for v in seed_run['samples'] if v['seconds'] == 120)
start, end = 120., 147.5
if SEED_KIND == 'checkpoint':
    local = json.loads(Path(sys.argv[8]).read_text())
    event = next(e for e in local['run']['state']['events'] if e['section'] == N-1 and e['boundary'] == 'vapor')
    point = max((c for c in local['run']['captures'] if c['kind'] == 'accepted-start' and c['seconds'] <= event['bracketStartSeconds']), key=lambda c: c['seconds'])
    start, end = point['seconds'], point['seconds']+.001
    fluid = np.array([x for c in point['fluid'] for x in (c['massKg'], c['internalEnergyKJ'])])
    thermal = CAP*(np.array(point['thermalK'])-273.15)
    budgets = np.zeros(ns['BUDGETS'])
    seed_run = {'relativeTolerance': None}
elif SEED_KIND == 'eos':
    fluid = np.array([x for c in row['sections'] for x in (c['rho']*.003/N, c['rho']*.003/N*c['u'])])
    thermal = CAP*(np.array(row['temperaturesK'])-273.15)
    budgets = np.r_[np.array(row['faces']).reshape(-1), row['tubeRefrigerantKJ'], row['linksKJ'], row['airLoadKJ']]
else:
    # This is a comparator initialized with JS's saved conserved state, not an
    # alternate initial condition substituted into qualification or a solver.
    matrix = json.loads((EVIDENCE / f'{mesh}-extra.json').read_text())
    run = next(v for v in matrix['runs'] if v['name'].startswith('extended') and v['tolerance'] == 1e-8)
    row = next(v for v in run['rows'] if v['seconds'] == 120)
    fluid = np.array([x for c in row['sections'] for x in (c['massKg'], c['internalEnergyKJ'])])
    thermal = CAP*(np.array([v['temperatureK'] for v in row['nodes']])-273.15)
    led = row['ledger']
    budgets = np.r_[np.array([[v['massKg'], v['energyKJ']] for v in led['faces']]).reshape(-1), led['tubeRefrigerantKJ'], led['thermalLinksKJ'], led['airLoadKJ']]
y0 = np.r_[fluid, thermal, budgets]
assert len(y0) == J+ns['BUDGETS'] and np.all(np.isfinite(y0))
atol = np.r_[np.tile([1e-13, 1e-10], N), np.full(ns['THERMAL'], 1e-10), np.full(ns['BUDGETS'], 1e-10)]
original_saturation = ns['saturation']
original_mu = ns['mu']
fallback_records = []
def recorded_mu(mass, energy):
    before = ns['fallbacks']
    result = original_mu(mass, energy)
    if ns['fallbacks'] != before:
        # Capture an existing successful result. No extra EOS evaluations and
        # no result or accepted input alteration. Failed evaluations still raise.
        fallback_records.append(dict(massKg=float(mass), internalEnergyKJ=float(energy),
                                     inputDensityKgM3=float(mass/ns['CELL_VOLUME']),
                                     inputUKJkg=float(energy/mass), result=dict(result)))
    return result
ns['mu'] = recorded_mu
if PROPERTY_KIND != 'direct-eos':
    from phase_event_table_comparator import TableComparator
    table = TableComparator(ROOT/'properties.json')
    if PROPERTY_KIND == 'table':
        # Diagnostic independent integrator with the same table constitutive
        # values. The JS engine and accepted direct-EOS references stay untouched.
        ns['mu'] = lambda m, e: table.mu(m, e, ns['CELL_VOLUME'])
        ns['ph'] = table.ph
        ns['saturation'] = table.saturation
def rhs(t, y):
    value = ns['rates'](y, 3.5, 0., False)
    if PROPERTY_KIND == 'sat-temperature':
        # A controlled property-component sensitivity, never qualification:
        # only the saturation-temperature interpolation offset enters heat.
        # Hydraulic PH/rho, event definition and all balances remain direct EOS.
        for i, state in enumerate(ns['states'](y)):
            delta = table.saturation(state['p'])['T']-original_saturation(state['p'])['T']
            dq = -.60/N*delta
            value[2*i+1] += dq
            value[F+2*i] -= dq
            value[ns['FACE_END']+i] += dq
    return value
# Continue only through the first event (the later 180/240 s changes are irrelevant).
solution = solve_ivp(rhs, (start, end), y0, method='Radau', rtol=RTOL,
                     atol=atol, max_step=MAX_STEP,
                     events=[ns['wet_event'], ns['domain_event']], dense_output=True)
assert solution.success and not solution.t_events[1].size
assert len(solution.t_events[0]) == 1
t = float(solution.t_events[0][0]); y = solution.sol(t)
state = ns['mu'](*y[F-2:F]); sat = ns['saturation'](state['p'])
def observation(seconds):
    z = solution.sol(seconds); v = ns['mu'](*z[F-2:F]); s = ns['saturation'](v['p'])
    return dict(seconds=seconds, marginKJkg=v['h']-s['hg'], state=v,
                massKg=float(z[F-2]), internalEnergyKJ=float(z[F-1]),
                thermalK=(273.15+z[F:J]/CAP).tolist())
samples = [observation(t+offset) for offset in [-.01, -.001, -.0001, -.00001, 0., .00001, .0001, .001, .01] if start <= t+offset <= end]
derivatives = []
center = ns['wet_event'](t, y)
for epsilon in [.01, .001, .0001, .00001]:
    if t-epsilon < start or t+epsilon > end:
        continue
    left, right = ns['wet_event'](t-epsilon, solution.sol(t-epsilon)), ns['wet_event'](t+epsilon, solution.sol(t+epsilon))
    derivatives.append(dict(epsilonSeconds=epsilon, wetSideKJkgS=(center-left)/epsilon,
                            drySideKJkgS=(right-center)/epsilon,
                            centralKJkgS=(right-left)/(2*epsilon)))
index = int(np.searchsorted(solution.t, t)); bracket = [float(solution.t[index-1]), float(solution.t[index])]
report = dict(diagnosticOnly=True, sectionCount=N, seedKind=SEED_KIND, propertyKind=PROPERTY_KIND,
              seedSeconds=start, seedPhysical=y0[:J].tolist(), seedVector=y0.tolist(),
              referenceSeedRtol=seed_run['relativeTolerance'], rtol=RTOL, maxStep=MAX_STEP,
              sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
              eventSeconds=t, rootResidualKJkg=float(center), eventState=state,
              saturation=sat, eventVector=y.tolist(), eventRHS=rhs(t, y).tolist(),
              samples=samples, derivatives=derivatives, integrationBracketSeconds=bracket,
              steps=len(solution.t)-1, nfev=solution.nfev, njev=solution.njev, nlu=solution.nlu,
              fallbacks=ns['fallbacks'], fallbackRecords=fallback_records, warnings=ns['warning_records'],
              coolProp=ns['CoolProp'].__version__, scipy=ns['scipy'].__version__, numpy=np.__version__,
              passed=True)
TARGET.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(dict(target=str(TARGET), eventSeconds=t, derivatives=derivatives)))
