"""Independent A2 trajectory, growth-decision, conservation and matched-work audit.

Usage: python audit_roadmap_a2.py /tmp/evidence /tmp/audit.json
No JavaScript engine, solver or exact-column helper is imported.
"""
import hashlib
import json
import math
import platform
import statistics
import sys
from pathlib import Path

directory = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()
repository = Path(__file__).resolve().parents[2]
assert not target.is_relative_to(repository)
assert target.parent.is_dir()
assert target.parent == directory


def read(name):
    value = json.loads((directory / name).read_text())
    assert value['passed'], name
    return value


def close(a, b, absolute=2e-14, relative=2e-13):
    assert math.isfinite(a) and math.isfinite(b)
    assert abs(a-b) <= absolute + relative*max(abs(a), abs(b)), (a, b)


length = .003 / (math.pi * .020**2 / 4)
tube = 7850 * math.pi / 4 * (.024**2 - .020**2) * length * .470
fin_plan = math.pi / 4 * (.080**2 - .024**2)
fin = 1910 * fin_plan * .0002 * 2700 * .900
air_tube = math.pi * .024 * (length - 1910 * .0002) * 50 / 1000
air_fin = 1910 * (2 * fin_plan + math.pi * .080 * .0002) * 50 / 1000
capacities = [v/5 for _ in range(5) for v in (tube, fin)] + [6 * .718]

choices = ('baseline', 'exact', 'fd-aware', 'exact-aware')
phase_only = '--phase-only' in sys.argv
smoke_only = '--smoke-only' in sys.argv
methods_only = '--methods-only' in sys.argv
if phase_only:
    diagnosis = read('phase-diagnosis.json')
    assert len(diagnosis['runs']) == 6
    comparison = dict(cases=[dict(name=r['choice']+('-seeded' if r['seeded'] else '-unseeded'), relativeTolerance=1e-6, runs={r['choice']: r}) for r in diagnosis['runs']])
    for case in comparison['cases']:
        for run in case['runs'].values():
            s = run['state']
            run['work'] = dict(acceptedTrials=s['acceptedSteps']/2, rejectedTrials=s['rejectedSteps'],
                              failures=sum(a['kind'] == 'solver' for a in s['rejectionTrace']),
                              iterations=s['attemptedIterations'], linearSolves=s['attemptedLinearSolves'])
else:
    comparison = read('methods.json' if methods_only else 'smoke.json' if smoke_only else 'compare.json')
    assert len(comparison['cases']) == (3 if methods_only else 1 if smoke_only else 15)
    if not smoke_only and not methods_only:
        ancestor = read('baseline.json')
        assert len(ancestor['cases']) == 14
        for baseline in ancestor['cases']:
            matched = next(v for v in comparison['cases'] if v['name'] == baseline['name'] and v['relativeTolerance'] == baseline['relativeTolerance'])['runs'][baseline['choice']]
            for key in ('work', 'propertyCalls', 'stateHash', 'recordHash'):
                assert baseline[key] == matched[key], (baseline['name'], baseline['choice'], key)
    read('rules-qualified.json')
accounting_rows = 0
worst = dict(massKg=0., fluidKJ=0., thermalNodeKJ=0., combinedKJ=0.)
regrowth = []


def attempts(state):
    result = [dict(seconds=a['seconds'], dt=a['trialSeconds'], failure=a['kind'], error=a.get('error', 0)) for a in state['rejectionTrace']]
    result += [dict(seconds=a['startSeconds'], end=a['endSeconds'], dt=a['trialSeconds'], failure=None, error=a['error']) for a in state['trace']]
    # Stable sort preserves the recorded order of retries at the same state.
    return sorted(result, key=lambda a: (a['seconds'], a['failure'] is None))


def replay(case, choice, run):
    state, rows = run['state'], run['rows']
    settings = rows[-1]['settings']
    exponent = -1/(2 if settings['method'] == 'backward-euler' else 3)
    aware = choice.endswith('aware')
    h = dict(ceilingSeconds=None, pendingFailure=False, successes=0, lastFailedSeconds=None, lastRecoverySeconds=None,
             nonlinearFailures=0, limitedProposals=0, releases=0, resets={})
    if run.get('seeded'):
        h.update(ceilingSeconds=.25,lastFailedSeconds=.5,lastRecoverySeconds=.25,nonlinearFailures=1,limitedProposals=1)
    if 'initialHistory' in run and aware:
        assert h == run['initialHistory']

    def reset(reason):
        for key in ('ceilingSeconds', 'lastFailedSeconds', 'lastRecoverySeconds'):
            h[key] = None
        h['pendingFailure'], h['successes'] = False, 0
        h['resets'][reason] = h['resets'].get(reason, 0)+1

    scheduled = list(state['boundaryEvents'])
    applied = 0
    proposed = settings['maxStep']
    events = attempts(state)
    for a in events:
        while applied < len(scheduled) and scheduled[applied]['seconds'] <= a['seconds']:
            assert scheduled[applied]['seconds'] == a['seconds']
            proposed = min(.05, settings['maxStep'])
            if aware:
                reset('scheduled-boundary')
            applied += 1
        target = min(r['seconds'] for r in rows if r['seconds'] > a['seconds'])
        boundary = min([target]+[e['seconds'] for e in scheduled[applied:] if e['seconds'] > a['seconds']])
        close(a['dt'], min(proposed, boundary-a['seconds']), absolute=1e-12)
        if a['failure']:
            if a['failure'] == 'solver':
                if aware:
                    h['pendingFailure'], h['successes'], h['lastFailedSeconds'] = True, 0, a['dt']
                    h['nonlinearFailures'] += 1
                proposed = a['dt']/2
            elif a['failure'] == 'event':
                if aware:
                    reset('event-refinement')
                proposed = min(a['dt']/2, 2*settings['eventStepSeconds'])
            elif a['failure'] == 'accuracy':
                if aware:
                    h['successes'] = 0
                proposed = a['dt']*max(.1, min(.8, .85*a['error']**exponent))
            else:
                raise AssertionError('Unexpected domain/property failure in supported fixtures')
            continue
        factor = 2 if a['error'] == 0 else max(.1, min(2, .85*a['error']**exponent))
        proposed = min(settings['maxStep'], a['dt']*factor)
        if not aware:
            continue
        crossed = any(e['bracketStartSeconds'] >= a['seconds']-1e-12 and e['bracketEndSeconds'] <= a['end']+1e-12 for e in state['events'])
        if crossed:
            reset('phase-event')
            continue
        if h['pendingFailure']:
            h['ceilingSeconds'] = h['lastRecoverySeconds'] = a['dt']
            h['pendingFailure'], h['successes'] = False, 0
        elif h['ceilingSeconds'] is not None and a['dt'] >= h['ceilingSeconds']*(1-1e-12):
            h['successes'] += 1
            if h['successes'] == 4:
                h['ceilingSeconds'] = min(settings['maxStep'], 1.25*h['ceilingSeconds'])
                h['successes'] = 0
                h['releases'] += 1
        if h['ceilingSeconds'] == settings['maxStep']:
            reset('normal-growth')
        elif h['ceilingSeconds'] is not None and proposed > h['ceilingSeconds']:
            h['limitedProposals'] += 1
            proposed = h['ceilingSeconds']
    while applied < len(scheduled):
        assert scheduled[applied]['seconds'] == state['seconds']
        proposed = min(.05, settings['maxStep'])
        if aware:
            reset('scheduled-boundary')
        applied += 1
    close(proposed, state['nextStepSeconds'])
    if aware:
        assert h == state['growthHistory'], (case['name'], choice, h, state['growthHistory'])
    else:
        assert 'growthHistory' not in state
    stats = dict(solverFailures=0, nextAttemptHalved=0, sameStateRepeatedFailures=0,
                 successfulRetryFollowedByGrowth=0, grownProposalFailed=0)
    for i, a in enumerate(events):
        prev = events[i-1] if i else None
        after = events[i+1] if i+1 < len(events) else None
        if a['failure'] == 'solver':
            stats['solverFailures'] += 1
            if after and after['seconds'] == a['seconds']:
                stats['nextAttemptHalved'] += after['dt'] == a['dt']/2
                stats['sameStateRepeatedFailures'] += after['failure'] == 'solver'
        if a['failure'] is None and prev and prev['failure'] == 'solver' and prev['seconds'] == a['seconds'] and after and after['seconds'] > a['seconds'] and after['dt'] > a['dt']:
            stats['successfulRetryFollowedByGrowth'] += 1
            stats['grownProposalFailed'] += after['failure'] == 'solver'
    return stats


for case in comparison['cases']:
    if not phase_only:
        assert set(case['runs']) == set(choices)
    for choice, run in case['runs'].items():
        state, rows, work = run['state'], run['rows'], run['work']
        assert state['stop'] is None
        assert work['acceptedTrials'] == len(state['trace']) == state['acceptedSteps']/2
        assert work['rejectedTrials'] == len(state['rejectionTrace'])
        assert work['failures'] == sum(a['kind'] == 'solver' for a in state['rejectionTrace'])
        assert work['linearSolves'] == work['iterations']
        assert all(0 <= a['error'] <= 1 for a in state['trace'])
        assert rows[-1]['settings']['nonlinearTolerance'] == 1e-11
        assert rows[-1]['settings']['thermalResidualK'] == 1e-12
        for e in state['events']:
            assert e['bracketEndSeconds']-e['bracketStartSeconds'] <= rows[-1]['settings']['eventStepSeconds']+1e-12
        regrowth.append(dict(name=case['name'], relativeTolerance=case['relativeTolerance'], choice=choice,
                            **replay(case, choice, run)))
        for row in rows:
            accounting_rows += 1
            assert row['stop'] is None and row['lastResidual'] <= 1e-11
            ledger = row['ledger']
            expected = [0.]*10+[ledger['airLoadKJ']]
            combined = 0.
            for i, node in enumerate(row['sections']):
                initial = state['initialCells'][i]
                left, right = ledger['faces'][i:i+2]
                mass = node['massKg']-initial['massKg']-left['massKg']+right['massKg']
                energy = node['internalEnergyKJ']-initial['internalEnergyKJ']-left['energyKJ']+right['energyKJ']-ledger['tubeRefrigerantKJ'][i]
                assert abs(mass) < 1e-8 and abs(energy) < 1e-6
                worst['massKg'] = max(worst['massKg'], abs(mass))
                worst['fluidKJ'] = max(worst['fluidKJ'], abs(energy))
                combined += node['internalEnergyKJ']-initial['internalEnergyKJ']
                at, af, ft = ledger['thermalLinksKJ'][3*i:3*i+3]
                expected[10] -= at+af
                expected[2*i] += at+ft-ledger['tubeRefrigerantKJ'][i]
                expected[2*i+1] += af-ft
            for i, node in enumerate(row['nodes']):
                change = capacities[i]*(node['temperatureK']-(273.15+state['initialEnergies'][i]/capacities[i]))
                residual = change-expected[i]
                assert abs(residual) < 1e-6
                worst['thermalNodeKJ'] = max(worst['thermalNodeKJ'], abs(residual))
                combined += change
            combined -= ledger['faces'][0]['energyKJ']-ledger['faces'][-1]['energyKJ']+ledger['airLoadKJ']
            assert abs(combined) < 1e-6
            worst['combinedKJ'] = max(worst['combinedKJ'], abs(combined))

if not phase_only and not smoke_only and not methods_only and '--comparison-only' not in sys.argv:
    reference = json.loads((directory/'fresh-reference.json').read_text())
    assert reference['boundaryFlashFallbacks'] == 0
    assert (directory/'fresh-reference.json').read_bytes() == (repository/'experiments/dx-fv/coupled-reference.json').read_bytes()
    for choice in choices:
        frozen, fresh = read(choice+'-frozen.json'), read(choice+'-fresh.json')

        def untimed(v):
            if isinstance(v, dict):
                return {k: untimed(x) for k, x in v.items() if k not in ('elapsedMS', 'elapsedSeconds')}
            if isinstance(v, list):
                return list(map(untimed, v))
            return v

        assert untimed(frozen) == untimed(fresh)
        for name in ('frozen-audit', 'fresh-audit', 'controls', 'domain', 'browser'):
            read(choice+'-'+name+'.json')
        if choice != 'baseline':
            assert len(read(choice+'-domain.json')['cases']) == 36
        assert {b['name'] for b in read(choice+'-browser.json')['browsers']} == {'chromium', 'webkit'}
        for c in frozen['cases']:
            for r in c['runs']:
                match = next(v for v in comparison['cases'] if v['name'] == c['name'] and v['relativeTolerance'] == r['relativeTolerance'])['runs'][choice]
                assert r['final']['attemptedResidualEvaluations'] == match['work']['evaluations']
                assert r['final']['attemptedIterations'] == match['work']['iterations']
                for compact, full in zip(r['rows'], match['rows']):
                    assert compact['ledger'] == full['ledger'] and compact['events'] == full['events']
                    assert compact['temperaturesK'] == [n['temperatureK'] for n in full['nodes']]
        observed = read('observed.json')
        for o in observed['cases']:
            match = next(v for v in comparison['cases'] if v['name'] == 'heat-reversal' and v['relativeTolerance'] == 1e-6)['runs'][o['choice']]
            assert o['stateHash'] == match['stateHash'] and o['recordHash'] == match['recordHash']
            assert o['work'] == match['work'] and o['propertyCalls'] == match['propertyCalls']
            assert o['observed']['maxFluid'] <= 1e-11 and o['observed']['maxThermalK'] <= 1e-12
            assert o['observed']['failedSolves'] == len(o['observed']['failures']) == o['work']['failures']
            for failed in o['observed']['failures']:
                assert failed['kind'] == 'solver' and 0 <= failed['iteration'] <= 30
                assert max(failed['fluidNorm'], failed['thermalK']/.1) > 1e-11
            for key in ('evaluations', 'iterations', 'linearSolves'):
                assert sum(a[key] for a in o['observed']['attempts']) == o['work'][key]

timing = []
if not phase_only and not smoke_only and not methods_only and '--qualification-only' not in sys.argv and '--comparison-only' not in sys.argv:
    p = read('performance.json')
    assert p['warmups'] >= 1 and len(p['pairs']) >= 5
    for pair in p['pairs']:
        assert set(pair['order']) == set(choices) and len(pair['order']) == 4
        orders = ((0,1,3,2),(1,2,0,3),(2,3,1,0),(3,0,2,1))
        assert pair['order'] == [choices[i] for i in orders[pair['pair'] % 4]]
        for choice in choices:
            for run, first in zip(pair['runs'][choice], p['pairs'][0]['runs'][choice]):
                for key in ('name', 'work', 'propertyCalls', 'stateHash', 'recordHash'):
                    assert run[key] == first[key]
                match = next(v for v in comparison['cases'] if v['name'] == run['name'] and v['relativeTolerance'] == 1e-6)['runs'][choice]
                assert run['work'] == match['work'] and run['propertyCalls'] == match['propertyCalls']
                assert run['elapsedMS'] > 0
    for name in [c['name'] for c in comparison['cases'] if c['relativeTolerance'] == 1e-6]+['total']:
        times = {choice: [sum(r['elapsedMS'] for r in pair['runs'][choice] if name == 'total' or r['name'] == name) for pair in p['pairs']] for choice in choices}
        ratios = {}
        for a, b in (('fd-aware', 'baseline'), ('exact-aware', 'exact'), ('exact-aware', 'baseline'), ('exact', 'baseline')):
            values = [x/y for x, y in zip(times[a], times[b])]
            ratios[a+'/'+b] = dict(median=statistics.median(values), minimum=min(values), maximum=max(values))
        timing.append(dict(name=name, paths={c: dict(medianMS=statistics.median(v), minimumMS=min(v), maximumMS=max(v), stdevMS=statistics.stdev(v), rawMS=v) for c, v in times.items()}, ratios=ratios))

result = dict(passed=True, python=platform.python_version(), accountingRows=accounting_rows, worstAccounting=worst,
              regrowth=regrowth, timing=timing,
              evidenceDigests={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.json') if p.resolve() != target})
target.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: v for k, v in result.items() if k not in ('regrowth', 'timing', 'evidenceDigests')}))
