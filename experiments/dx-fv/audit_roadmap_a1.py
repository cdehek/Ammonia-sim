"""Independent A1 assembly, conservation, equivalence and paired-work audit.

Usage: python audit_roadmap_a1.py /tmp/evidence /tmp/audit.json
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
links = [(10, 2*i, air_tube/5) for i in range(5)]
links += [(10, 2*i+1, air_fin/5) for i in range(5)]
links += [(2*i+1, 2*i, 2/5) for i in range(5)]


def columns(context, conductances):
    scales = context['physicalScales']
    for i, c in enumerate(capacities):
        close(context['thermalCapacitiesKJK'][i], c)
        close(scales[10+i], c * 1e-12 / 1e-11)
    tau = context['stageSeconds'] * context['stageWeight']
    result = []
    for col in range(11):
        # Independently apply a unit kJ perturbation through signed link incidence.
        rate = [0.] * 11
        for source, sink, g in links:
            q = g * ((1/capacities[source] if col == source else 0)
                     - (1/capacities[sink] if col == sink else 0))
            rate[source] -= q
            rate[sink] += q
        q_fluid = [conductances[i]/capacities[col] if col == 2*i else 0. for i in range(5)]
        for i, q in enumerate(q_fluid):
            rate[2*i] -= q
        column = [0.] * 21
        for i, q in enumerate(q_fluid):
            column[2*i+1] = -tau*q/scales[2*i+1]
        for i, rate_i in enumerate(rate):
            column[10+i] = ((1. if i == col else 0.) - tau*rate_i)/scales[10+i]
        energy_rows = list(range(1, 10, 2)) + list(range(10, 21))
        close(sum(column[row]*scales[row] for row in energy_rows), 1.)
        result.append(column)
    return result


assembly = read('columns.json')
assert assembly['detachedColumnMutationPassed']
matrix_entries = probe_entries = groups = 0
matrix_absolute = fd_relative = fd_thermal = fd_fluid = 0.
covered = set()
for trial in assembly['trials']:
    covered.add((trial['name'], trial['method'], trial['dt']))
    conductances = trial['conductancesKWK']
    for g in conductances:
        close(g, 0 if trial['name'] in ('zero-exchange', 'closed-relaxation') else .12)
    for group in trial['groups']:
        context = group['context']
        if trial['method'] == 'backward-euler':
            close(context['stageWeight'], 1.)
            close(context['stageSeconds'], trial['dt'])
        else:
            gamma = 2-math.sqrt(2)
            if abs(context['stageWeight']-.5) < 1e-15:
                close(context['stageSeconds'], gamma*trial['dt'])
            else:
                close(context['stageWeight'], (1-gamma)/(2-gamma))
                close(context['stageSeconds'], trial['dt'])
        expected = columns(context, conductances)
        assert [c['column'] for c in group['columns']] == list(range(10, 21))
        groups += 1
        for col, observed in enumerate(group['columns']):
            assert len(observed['values']) == 21
            for row, value in enumerate(observed['values']):
                exact = expected[col][row]
                close(value, exact)
                if exact == 0:
                    assert value == 0
                matrix_entries += 1
                matrix_absolute = max(matrix_absolute, abs(value-exact))
    for group in trial['baselineGroups']:
        context = group['context']
        expected = columns(context, conductances)
        assert len(group['probes']) == 11
        for probe in group['probes']:
            col = probe['column']-10
            close(probe['actualPerturbation'], probe['perturbedCoordinate']-probe['originalCoordinate'])
            for row, exact in enumerate(expected[col]):
                actual = (probe['residual'][row]-group['residual'][row])/probe['step']
                defect = actual-exact
                probe_entries += 1
                if exact:
                    fd_relative = max(fd_relative, abs(defect/exact))
                    assert abs(defect/exact) < 1e-5
                else:
                    assert actual == 0
                if row >= 10:
                    error = abs(defect*context['physicalScales'][row]*capacities[col]/capacities[row-10])
                    fd_thermal = max(fd_thermal, error)
                elif row % 2:
                    fd_fluid = max(fd_fluid, abs(defect*context['physicalScales'][row]*capacities[col]))
assert len(covered) == 20
if '--assembly-only' in sys.argv[3:]:
    result = dict(passed=True, trials=len(covered), groups=groups, entries=matrix_entries,
                  maximumAbsoluteError=matrix_absolute, finiteDifferenceEntries=probe_entries,
                  maximumFiniteDifferenceRelativeError=fd_relative,
                  maximumFiniteDifferenceThermalKPerK=fd_thermal,
                  maximumFiniteDifferenceFluidKJPerK=fd_fluid)
    target.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    sys.exit(0)

baseline = read('baseline.json')
assert len(baseline['cases']) == 7
assert next(c for c in baseline['cases'] if c['name'] == 'heat-reversal' and c['relativeTolerance'] == 1e-6)['work']['rejectedTrials'] == 922
comparison = read('compare.json')
assert len(comparison['cases']) == 15
sequence_differences = []
for case in comparison['cases']:
    evidence = dict(name=case['name'], relativeTolerance=case['relativeTolerance'])
    for kind, key, fields in (('accepted', 'trace', ('startSeconds', 'endSeconds', 'trialSeconds')),
                              ('rejected', 'rejectionTrace', ('seconds', 'trialSeconds', 'kind'))):
        sequences = [[{k: v[k] for k in fields} for v in case[choice+'State'][key]] for choice in ('baseline', 'exact')]
        a, b = sequences
        first = next((i for i in range(max(len(a), len(b))) if i >= len(a) or i >= len(b) or a[i] != b[i]), None)
        evidence[kind] = dict(identical=a == b, baselineCount=len(a), exactCount=len(b),
            firstDifference=None if first is None else dict(index=first, baseline=a[first] if first < len(a) else None,
                                                           exact=b[first] if first < len(b) else None))
    sequence_differences.append(evidence)
accounting_rows = 0
worst = dict(massKg=0.,fluidEnergyKJ=0.,thermalNodeKJ=0.,combinedEnergyKJ=0.)
for case in comparison['cases']:
    for choice in ('baseline', 'exact'):
        state = case[choice+'State']
        rows = case[choice+'Rows']
        counts = case[choice]['work']
        assert counts['linearSolves'] == counts['iterations']
        assert counts['acceptedTrials']*2 == state['acceptedSteps']
        assert counts['rejectedTrials'] == len(state['rejectionTrace'])
        assert counts['acceptedTrials'] == len(state['trace'])
        assert counts['failures'] == sum(v['kind'] == 'solver' for v in state['rejectionTrace'])
        assert all(v['error'] <= 1 for v in state['trace'])
        for event in state['events']:
            assert event['bracketEndSeconds']-event['bracketStartSeconds'] <= rows[-1]['settings']['eventStepSeconds'] + 1e-12
        for row in rows:
            accounting_rows += 1
            assert row['stop'] is None
            assert row['lastResidual'] is None or row['lastResidual'] <= 1e-11
            ledger = row['ledger']
            thermal = [0.]*10+[ledger['airLoadKJ']]
            combined = 0.
            for i, node in enumerate(row['sections']):
                initial = state['initialCells'][i]
                left, right = ledger['faces'][i:i+2]
                mass = node['massKg']-initial['massKg']-left['massKg']+right['massKg']
                energy = node['internalEnergyKJ']-initial['internalEnergyKJ']-left['energyKJ']+right['energyKJ']-ledger['tubeRefrigerantKJ'][i]
                assert abs(mass) < 1e-8 and abs(energy) < 1e-6
                worst['massKg'] = max(worst['massKg'], abs(mass))
                worst['fluidEnergyKJ'] = max(worst['fluidEnergyKJ'], abs(energy))
                combined += node['internalEnergyKJ']-initial['internalEnergyKJ']
                at, af, ft = ledger['thermalLinksKJ'][3*i:3*i+3]
                thermal[10] -= at+af
                thermal[2*i] += at+ft-ledger['tubeRefrigerantKJ'][i]
                thermal[2*i+1] += af-ft
            for i, node in enumerate(row['nodes']):
                # Temperature-coordinate accounting independent of reported node ledgers.
                initial_k = 273.15+state['initialEnergies'][i]/capacities[i]
                change = capacities[i]*(node['temperatureK']-initial_k)
                residual = change-thermal[i]
                assert abs(residual) < 1e-6
                worst['thermalNodeKJ'] = max(worst['thermalNodeKJ'], abs(residual))
                combined += change
            combined -= ledger['faces'][0]['energyKJ']-ledger['faces'][-1]['energyKJ']+ledger['airLoadKJ']
            assert abs(combined) < 1e-6
            worst['combinedEnergyKJ'] = max(worst['combinedEnergyKJ'], abs(combined))

frozen = read('exact-frozen.json')
fresh = read('exact-fresh.json')
reference = json.loads((directory/'fresh-reference.json').read_text())
assert reference['boundaryFlashFallbacks'] == 0
assert (directory/'fresh-reference.json').read_bytes() == (repository/'experiments/dx-fv/coupled-reference.json').read_bytes()


def untimed(value):
    if isinstance(value, dict):
        return {k: untimed(v) for k, v in value.items() if k not in ('elapsedMS', 'elapsedSeconds')}
    if isinstance(value, list):
        return list(map(untimed, value))
    return value


assert untimed(frozen) == untimed(fresh)
for case in frozen['cases']:
    for run in case['runs']:
        matched = next(c for c in comparison['cases'] if c['name'] == case['name'] and c['relativeTolerance'] == run['relativeTolerance'])
        final, work = run['final'], matched['exact']['work']
        assert final['attemptedResidualEvaluations'] == work['evaluations']
        assert final['attemptedIterations'] == work['iterations']
        assert final['acceptedSteps'] == 2*work['acceptedTrials']
        assert final['rejectedSteps'] == work['rejectedTrials']
        for compact, full in zip(run['rows'], matched['exactRows']):
            assert compact['ledger'] == full['ledger']
            assert compact['events'] == full['events']
            assert compact['temperaturesK'] == [n['temperatureK'] for n in full['nodes']]
            assert compact['sections'] == [{k: s[k] for k in compact['sections'][i]} for i, s in enumerate(full['sections'])]
baseline_suite = read('baseline-frozen.json')
for case in baseline_suite['cases']:
    for run in case['runs']:
        matched = next(c for c in comparison['cases'] if c['name'] == case['name'] and c['relativeTolerance'] == run['relativeTolerance'])
        assert run['final']['attemptedResidualEvaluations'] == matched['baseline']['work']['evaluations']
        assert run['final']['attemptedIterations'] == matched['baseline']['work']['iterations']
        for compact, full in zip(run['rows'], matched['baselineRows']):
            assert compact['ledger'] == full['ledger']
            assert compact['events'] == full['events']
            assert compact['temperaturesK'] == [n['temperatureK'] for n in full['nodes']]
            assert compact['sections'] == [{k: s[k] for k in compact['sections'][i]} for i, s in enumerate(full['sections'])]
for name in ('exact-frozen-audit.json', 'exact-fresh-audit.json', 'exact-controls.json', 'exact-domain.json', 'baseline-domain.json'):
    read(name)
assert all(c['settings']['thermalJacobian'] == 'exact' for c in read('exact-controls.json')['cases'])
assert len(read('exact-domain.json')['cases']) == 36
browser = read('exact-browser.json')
assert {b['name'] for b in browser['browsers']} == {'chromium', 'webkit'}
failures = read('exact-failures.json')
nominal_reversal = next(c for c in comparison['cases'] if c['name'] == 'heat-reversal' and c['relativeTolerance'] == 1e-6)
assert failures['state'] == nominal_reversal['exactState']
assert failures['rows'] == nominal_reversal['exactRows']
assert failures['result']['work'] == nominal_reversal['exact']['work']
assert failures['result']['propertyCalls'] == nominal_reversal['exact']['propertyCalls']
assert len(failures['failures']) == failures['result']['work']['failures']
assert all(0 <= f['iteration'] <= 30 and f['faultKind'] == 'solver' for f in failures['failures'])
assert failures['converged']['maximumFluidNorm'] <= 1e-11
assert failures['converged']['maximumThermalK'] <= 1e-12
if '--qualification-only' in sys.argv[3:]:
    result = dict(passed=True, python=platform.python_version(), matrixEntries=matrix_entries,
                  maximumMatrixAbsoluteError=matrix_absolute, accountingRows=accounting_rows,
                  worstAccountingResiduals=worst, sequenceDifferences=sequence_differences)
    target.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'sequenceDifferences'}))
    sys.exit(0)
performance = read('performance.json')
assert performance['warmupPairs'] >= 1 and len(performance['pairs']) >= 5
timing = []
for name in [c['name'] for c in frozen['cases']] + ['total']:
    times = {choice: [] for choice in ('baseline', 'exact')}
    for pair in performance['pairs']:
        assert pair['order'] == (['baseline', 'exact'] if pair['pair'] % 2 == 0 else ['exact', 'baseline'])
        for choice in times:
            first = performance['pairs'][0][choice]
            for run, original in zip(pair[choice], first):
                for key in ('name', 'work', 'propertyCalls', 'stateHash', 'recordHash'):
                    assert run[key] == original[key]
                matched = next(c for c in comparison['cases'] if c['name'] == run['name'] and c['relativeTolerance'] == 1e-6)
                assert run['work'] == matched[choice]['work']
                assert run['propertyCalls'] == matched[choice]['propertyCalls']
                assert run['elapsedMS'] > 0
            times[choice].append(sum(c['elapsedMS'] for c in pair[choice] if name == 'total' or c['name'] == name))
    ratios = [a/b for a, b in zip(times['exact'], times['baseline'])]
    timing.append(dict(name=name, baselineMS=dict(median=statistics.median(times['baseline']),
        minimum=min(times['baseline']), maximum=max(times['baseline']), stdev=statistics.stdev(times['baseline'])),
        exactMS=dict(median=statistics.median(times['exact']),minimum=min(times['exact']),maximum=max(times['exact']),stdev=statistics.stdev(times['exact'])),
        pairedExactOverBaseline=dict(median=statistics.median(ratios),minimum=min(ratios),maximum=max(ratios)),
        rawBaselineMS=times['baseline'],rawExactMS=times['exact']))

result = dict(passed=True,python=platform.python_version(),assembly=dict(trials=len(assembly['trials']),groups=groups,
    entries=matrix_entries,maximumAbsoluteError=matrix_absolute,finiteDifferenceEntries=probe_entries,
    maximumFiniteDifferenceRelativeError=fd_relative,maximumFiniteDifferenceThermalKPerK=fd_thermal,
    maximumFiniteDifferenceFluidKJPerK=fd_fluid),accounting=dict(rows=accounting_rows,worst=worst),timing=timing,
    sequenceDifferences=sequence_differences,
    evidenceDigests={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.json') if p.resolve()!=target})
target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
