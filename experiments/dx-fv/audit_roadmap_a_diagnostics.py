"""A0 independent stdlib audit of captured evaluations and declared balances.

Usage: python audit_roadmap_a_diagnostics.py report.json probes.jsonl.gz audit.json
No JavaScript solver, property engine, or diagnostic comparator is imported.
"""
import gzip
import hashlib
import json
import math
import platform
import sys
from pathlib import Path


def close(a, b, absolute=1e-12, relative=1e-11):
    assert math.isfinite(a) and math.isfinite(b)
    assert abs(a-b) <= absolute + relative*max(abs(a), abs(b)), (a, b)


def physical_network():
    length = .003/(math.pi*.020**2/4)
    tube_capacity = 7850*math.pi/4*(.024**2-.020**2)*length*.470
    fin_plan = math.pi/4*(.080**2-.024**2)
    fin_capacity = 1910*fin_plan*.0002*2700*.900
    tube_g = math.pi*.024*(length-1910*.0002)*50/1000
    fin_g = 1910*(2*fin_plan+math.pi*.080*.0002)*50/1000
    capacities = [v/5 for _ in range(5) for v in (tube_capacity, fin_capacity)]+[6*.718]
    links = [(10, 2*i, tube_g/5) for i in range(5)]
    links += [(10, 2*i+1, fin_g/5) for i in range(5)]
    links += [(2*i+1, 2*i, 2/5) for i in range(5)]
    return capacities, links


def exact_columns(context, capacities, links):
    # Independent assembly from energy balance incidence, not recorded matrices.
    assert len(context['physicalScales']) == 21
    assert context['stageSeconds'] > 0
    assert min(abs(context['stageWeight']-.5), abs(context['stageWeight']-(1-(2-math.sqrt(2)))/(2-(2-math.sqrt(2))))) < 1e-15
    for i, capacity in enumerate(capacities):
        close(context['thermalCapacitiesKJK'][i], capacity)
        close(context['physicalScales'][10+i], capacity*1e-12/1e-11)
    rates = [[0.0]*11 for _ in range(11)]
    for f, t, g in links:
        for row, sign in ((f, -1), (t, 1)):
            rates[row][f] += sign*g/capacities[f]
            rates[row][t] -= sign*g/capacities[t]
    for cell in range(5):
        rates[2*cell][2*cell] -= .12/capacities[2*cell]
    tau = context['stageSeconds']*context['stageWeight']
    columns = []
    for col in range(11):
        column = [0.0]*21
        for row in range(11):
            column[10+row] = ((1 if row == col else 0)-tau*rates[row][col])/context['physicalScales'][10+row]
        if col < 10 and col % 2 == 0:
            column[col+1] = -tau*.12/capacities[col]/context['physicalScales'][col+1]
        # Internal exchanges cancel in the physical combined-energy derivative.
        energy_rows = list(range(1, 10, 2))+list(range(10, 21))
        close(sum(column[row]*context['physicalScales'][row] for row in energy_rows), 1.0)
        columns.append(column)
    return columns


table = json.loads((Path(__file__).resolve().parents[2]/'properties.json').read_text())


def inverse_temperature(p, h):
    logs = list(map(math.log, table['p']))
    i = next((i for i in range(len(logs)-1) if logs[i+1] > math.log(p)), len(logs)-2)
    w = (math.log(p)-logs[i])/(logs[i+1]-logs[i])
    a, b = table['sat'][i:i+2]
    sat_t, hf, hg = (a[j]+w*(b[j]-a[j]) for j in (0, 1, 4))
    if hf-1e-8 <= h <= hg+1e-8:
        return sat_t
    vapor = h > hg
    axis = table['sh' if vapor else 'sc']
    rows = table['vapor' if vapor else 'liquid']
    for j in range(len(axis)-1):
        if any(rows[k][m] is None for k in (i, i+1) for m in (j, j+1)):
            continue
        left = rows[i][j][0]+w*(rows[i+1][j][0]-rows[i][j][0])
        right = rows[i][j+1][0]+w*(rows[i+1][j+1][0]-rows[i][j+1][0])
        if min(left, right)-1e-8 <= h <= max(left, right)+1e-8:
            offset = axis[j]+(h-left)/(right-left)*(axis[j+1]-axis[j])
            return sat_t+(offset if vapor else -offset)
    raise AssertionError('No supported table segment')


report_path, archive_path, output_path = map(Path, sys.argv[1:4])
repository_root = Path(__file__).resolve().parents[2]
assert not output_path.resolve().is_relative_to(repository_root), 'Audit output must be outside the repository.'
assert output_path.resolve() not in (report_path.resolve(), archive_path.resolve()), 'Do not overwrite source evidence.'
report = json.loads(report_path.read_text())
assert report['passed'] and report['diagnosticOnly']
assert report['runtime'].startswith('v22.')
assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == report['archive']['sha256']
capacities, links = physical_network()
counts = dict(trials=0, derivativeProbes=0, thermalColumns=0, quantizationPoints=0, failedProbes=0, branchRejected=0)
seen = set()
max_derivative_error = 0.0
max_inverse_discrepancy = 0.0
max_kelvin_conversion_effect = 0.0
actions = dict(pairs=0,nearClosurePairs=0,maximumAcceptedDisplacementDefectK=0.0,maximumNearClosureDefectK=0.0)
ph_probe_metrics = {kind: dict(probes=0,maximumTemperatureDifferenceErrorK=0.0,
    maximumTemperatureDerivativeError=0.0,maximumStageClosureDifferenceK=0.0)
    for kind in ('pressure', 'enthalpy')}
for line in gzip.open(archive_path, 'rt'):
    trial = json.loads(line)
    counts['trials'] += 1
    seen.add((trial['case'], trial['tolerance'], trial['bucket']))
    for expected, node in zip(capacities, trial['spec']['thermal']['nodes']):
        close(expected, node['capacityKJK'])
    for g in trial['spec']['conductancesKWK']:
        close(g, .12)
    contexts, iterations, all_iterations = {}, {}, {}
    thermal_probes = {}
    case = next(c for c in report['cases'] if c['name'] == trial['case'] and c['tolerance'] == trial['tolerance'])
    for event in trial['attempt']['events']:
        sid = event.get('solveId')
        if event['type'] == 'iteration':
            if event.get('context'):
                contexts[sid] = event['context']
            iterations[sid] = event
            all_iterations[sid, event['iteration']] = event
            assert event['fluidNorm'] == max(map(abs, event['residual'][:10]))
            assert event['thermalNorm'] == max(map(abs, event['residual'][10:]))
            if event['status'] == 'converged':
                assert max(map(abs, event['residual'])) <= 1e-11
        elif event['type'] == 'derivative':
            counts['derivativeProbes'] += 1
            assert event['actualPerturbation'] == event['perturbedCoordinate']-event['originalCoordinate']
            assert event['perturbedCoordinate'] == event['originalCoordinate']+event['step']
            assert abs(event['step']) == event['epsilon']*2**(-event['shrink'])
            assert ('residual' in event) == (event['outcome'] != 'probe-failed')
            counts['failedProbes'] += event['outcome'] == 'probe-failed'
            counts['branchRejected'] += event['outcome'] == 'branch-rejected'
            if event['kind'] in ph_probe_metrics and event['outcome'] == 'used':
                cell = event['column']//2
                context, base = contexts[sid], iterations[sid]
                ph = base['states'][cell]
                p, h = ph['p'], ph['h']
                if event['kind'] == 'pressure':
                    p = event['perturbedCoordinate']
                else:
                    h = event['perturbedCoordinate']
                ideal_delta_t = inverse_temperature(p, h)-inverse_temperature(ph['p'], ph['h'])
                tau_g = context['stageSeconds']*context['stageWeight']*.12
                row = 10+2*cell
                used_delta_t = -(event['residual'][row]-base['residual'][row])*context['physicalScales'][row]/tau_g
                error = used_delta_t-ideal_delta_t
                metric = ph_probe_metrics[event['kind']]
                metric['probes'] += 1
                metric['maximumTemperatureDifferenceErrorK'] = max(metric['maximumTemperatureDifferenceErrorK'], abs(error))
                metric['maximumTemperatureDerivativeError'] = max(metric['maximumTemperatureDerivativeError'], abs(error/event['step']))
                stage_error = abs(tau_g*error/capacities[2*cell])
                if stage_error > metric['maximumStageClosureDifferenceK']:
                    metric['maximumStageClosureDifferenceK'] = stage_error
                    metric['worstStageProbe'] = dict(case=trial['case'], tolerance=trial['tolerance'], startSeconds=trial['attempt']['startSeconds'],
                        stageSeconds=context['stageSeconds'],stageWeight=context['stageWeight'],cell=cell,step=event['step'],
                        usedTemperatureDifferenceK=used_delta_t,algebraicTemperatureDifferenceK=ideal_delta_t)
            if event['kind'] == 'thermal-energy' and event['outcome'] == 'used':
                counts['thermalColumns'] += 1
                col = event['column']-10
                assert 0 <= col < 11
                context, base = contexts[sid], iterations[sid]
                thermal_probes.setdefault((sid, event['iteration']), {})[col] = event
                expected = exact_columns(context, capacities, links)[col]
                for row, (probe, previous, exact) in enumerate(zip(event['residual'], base['residual'], expected)):
                    measured = (probe-previous)/event['step']
                    if exact == 0:
                        assert measured == 0, (col, row, measured)
                    if row >= 10:
                        physical_error = abs(measured-exact)*context['physicalScales'][row]*capacities[col]/capacities[row-10]
                        max_derivative_error = max(max_derivative_error, physical_error)
                        assert physical_error <= case['stats']['columns'][col]['maximumThermalTemperatureDerivativeError']+1e-12
        elif event['type'] == 'line-search' and event['outcome'] in ('accepted', 'not-reduced'):
            assert (event['nextError'] < event['previousError']) == (event['outcome'] == 'accepted')
    for (sid, iteration_index), probes in thermal_probes.items():
        following = thermal_probes.get((sid, iteration_index+1))
        if len(probes) != 11 or following is None or len(following) != 11:
            continue
        context = contexts[sid]
        base = all_iterations[sid, iteration_index]
        exact = exact_columns(context, capacities, links)
        defect = [0.0]*11
        for col, probe in probes.items():
            displacement = following[col]['originalCoordinate']-probe['originalCoordinate']
            for row in range(11):
                measured = (probe['residual'][10+row]-base['residual'][10+row])/probe['step']
                defect[row] += (measured-exact[col][10+row])*displacement*context['physicalScales'][10+row]/capacities[row]
        maximum = max(map(abs, defect))
        actions['pairs'] += 1
        actions['maximumAcceptedDisplacementDefectK'] = max(actions['maximumAcceptedDisplacementDefectK'], maximum)
        closure = max(abs(base['residual'][10+i])*context['physicalScales'][10+i]/capacities[i] for i in range(11))
        if closure < 1e-10 and base['fluidNorm'] <= 1e-11:
            actions['nearClosurePairs'] += 1
            actions['maximumNearClosureDefectK'] = max(actions['maximumNearClosureDefectK'], maximum)
    for point in trial['quantRows']:
        counts['quantizationPoints'] += 1
        context = contexts[point['solveId']]
        independent_t = inverse_temperature(point['p'], point['h'])
        max_inverse_discrepancy = max(max_inverse_discrepancy, abs(independent_t-point['exactT']))
        close(independent_t, point['exactT'], absolute=2e-12, relative=0)
        delta = point['exactT']-point['T']
        shift = context['stageSeconds']*context['stageWeight']*.12*delta
        kelvin_delta = (point['exactT']+273.15)-(point['T']+273.15)
        max_kelvin_conversion_effect = max(max_kelvin_conversion_effect,
            abs(context['stageSeconds']*context['stageWeight']*.12*(kelvin_delta-delta)/capacities[2*point['cell']]))
        close(shift, point['exchangeShiftKJ'], absolute=1e-24)
        close(-shift/capacities[2*point['cell']], point['thermalShiftK'], absolute=1e-24)
        iteration = all_iterations[point['solveId'], point['iteration']]
        row = 10+2*point['cell']
        close(iteration['residual'][row]*context['physicalScales'][row]/capacities[2*point['cell']], point['currentK'], absolute=1e-24)
for case in report['cases']:
    assert case['settings']['nonlinearTolerance'] == 1e-11
    assert case['settings']['thermalResidualK'] == 1e-12
    assert case['settings']['maxIterations'] == 30
    assert case['settings']['relativeTolerance'] == case['tolerance']
    assert case['settings']['maxStep'] == (0.125 if case['tolerance'] <= 1e-8 else 0.25 if case['tolerance'] <= 1e-7 else 0.5)
    assert case['observationalEquivalence']['passed'] and case['observationalEquivalence']['mutatedDetachedProbeCopies']
    assert all(column['probes'] > 0 for column in case['stats']['columns'])
    assert case['stats']['maximumConvergedThermalClosureK'] <= 1e-12
    assert case['stats']['storage']['selectedAttempts'] == sum(1 for name, tol, _ in seen if (name, tol) == (case['name'], case['tolerance']))
    attempts = case['stats']['attempts']
    assert sum(a['evaluations'] for a in attempts) == case['work']['evaluations']
    assert sum(a['iterations'] for a in attempts) == case['work']['iterations']
    assert sum(a['linearSolves'] for a in attempts) == case['work']['linearSolves']
    assert sum(bool(a['failure'] or a['rejectionReason']) for a in attempts) == case['rejectedTrials']
    assert sum(not (a['failure'] or a['rejectionReason']) for a in attempts) == case['acceptedTrials']
    regrowth = dict(solverFailures=0, nextAttemptHalved=0, sameStateRepeatedFailures=0, successfulRetryFollowedByGrowth=0, grownProposalFailed=0)
    for i, a in enumerate(attempts):
        previous = attempts[i-1] if i else None
        following = attempts[i+1] if i+1 < len(attempts) else None
        if a['failure'] == 'solver':
            regrowth['solverFailures'] += 1
            if following and following['startSeconds'] == a['startSeconds']:
                regrowth['nextAttemptHalved'] += following['trialSeconds'] == a['trialSeconds']/2
                regrowth['sameStateRepeatedFailures'] += following['failure'] == 'solver'
        if not (a['failure'] or a['rejectionReason']) and previous and previous['failure'] == 'solver' and previous['startSeconds'] == a['startSeconds'] and following and following['startSeconds'] > a['startSeconds'] and following['trialSeconds'] > a['trialSeconds']:
            regrowth['successfulRetryFollowedByGrowth'] += 1
            regrowth['grownProposalFailed'] += following['failure'] == 'solver'
    assert regrowth == case['regrowth']
    for r in case['records']:
        assert abs(r['massResidualKg']) < 1e-8
        assert all(abs(r[key]) < 1e-6 for key in ('refrigerantEnergyResidualKJ', 'thermalEnergyResidualKJ', 'combinedEnergyResidualKJ'))
        assert all(abs(n['residualKJ']) < 1e-6 for n in r['nodes'])
        assert all(abs(s['massKg']) < 1e-8 and abs(s['energyKJ']) < 1e-6 for s in r['sectionResiduals'])
replay_probes = 0
assert len(report.get('targetedReplays', [])) == 6, 'Run the --replay phase before this audit.'
for replay in report['targetedReplays']:
    assert replay['passed'] and replay['startSeconds'] == 1 and replay['trialSeconds'] in (.5, .025)
    contexts, bases = {}, {}
    columns_seen = set()
    for event in replay['events']:
        sid = event.get('solveId')
        if event['type'] == 'iteration':
            if event.get('context'):
                contexts[sid] = event['context']
            bases[sid] = event
        if event['type'] == 'derivative' and event['kind'] == 'thermal-energy' and event['outcome'] == 'used':
            replay_probes += 1
            col = event['column']-10
            columns_seen.add(col)
            context = contexts[sid]
            exact = exact_columns(context, capacities, links)[col]
            for row in range(11):
                measured = (event['residual'][10+row]-bases[sid]['residual'][10+row])/event['step']
                error = abs(measured-exact[10+row])*context['physicalScales'][10+row]*capacities[col]/capacities[row]
                assert error <= replay['columns']['maximumThermalTemperatureDerivativeError']+1e-12
    assert columns_seen == set(range(11))
memory = report.get('memoryComparison')
if memory is not None:
    assert memory['passed']
    for key in ('runtime', 'stateHash', 'recordsHash', 'counts', 'work'):
        assert memory['original'][key] == memory['observed'][key]
    assert memory['differenceKiB'] == memory['observed']['maximumResidentSetKiB']-memory['original']['maximumResidentSetKiB']
    assert memory['observed']['payload']['probeVectors'] > 0
    assert memory['original']['payload']['probeVectors'] == 0
result = dict(passed=True,python=platform.python_version(),method='Independent Python stdlib geometry/balance/inversion audit',
              counts=counts,maximumArchivedThermalDerivativeError=max_derivative_error,
              maximumIndependentInverseDifferenceK=max_inverse_discrepancy,archiveSHA256=report['archive']['sha256'],
              maximumExplicitKelvinConversionSensitivityDifferenceK=max_kelvin_conversion_effect,
              derivativeDefectOnObservedAcceptedDisplacements=actions,
              matchedProbePHCouplingDiscrepancy=ph_probe_metrics,
              targetedReplaysAudited=len(report['targetedReplays']),targetedReplayThermalColumns=replay_probes,
              limitation='Probe-level audit covers selected archived trials; full-run aggregates and equivalence are asserted by the JS harness. Regrowth/work arithmetic covers all attempts.')
output_path.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
