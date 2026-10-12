"""Audit preserved evidence and report the stop decision without further solves."""
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
evidence = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()
assert not target.is_relative_to(root)
preserved = json.loads((evidence / 'preserved-files.json').read_text())
for name, digest in preserved.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
properties = json.loads((evidence / 'property-tests.json').read_text())
eos = json.loads((evidence / 'property-eos.json').read_text())
assert properties['passed'] and eos['propertyTestsPassed'] and eos['generalSaturationImprovement']

def errors(points):
    result = {}
    for kind in ('linear', 'candidate'):
        values = [r[kind+'ErrorK'] for r in points]
        result[kind] = dict(maximumAbsolute=max(map(abs, values)),
                           rms=math.sqrt(statistics.mean(v*v for v in values)))
    return result

sat = errors(eos['saturationSamples'])
regions = {name:errors(points) for name, points in eos['regionSamples'].items()}
for field, row in [('saturationAccuracy', sat)]:
    for kind, values in row.items():
        for key, value in values.items():assert abs(value-eos[field][kind][key]) < 1e-14
for name, row in regions.items():
    for kind, values in row.items():
        for key, value in values.items():assert abs(value-eos['regionAccuracy'][name][kind][key]) < 1e-14
regressions = [name for name, row in regions.items()
               if any(row['candidate'][key] > row['linear'][key]+1e-10 for key in ('maximumAbsolute','rms'))]
assert regressions == ['liquid'], regressions
worst = max(eos['regionSamples']['liquid'],key=lambda r:abs(r['candidateErrorK']))
matched = next(r for r in properties['states'] if r['kind']=='liquid' and r['p']==worst['p'] and r['h']==worst['h'])
assert matched['baselineRecovery']['energyResidual'] == matched['candidateRecovery']['energyResidual']
result = dict(evidenceAuditPassed=True, candidateQualified=False, stopRequired=True,
    existingFilesPreserved=len(preserved), regionRegressions=regressions,
    saturationAccuracy=sat,regionAccuracy=regions,worstLiquid={**worst,**matched},
    propertyProbeCount=len(properties['saturation']),stateProbeCount=len(properties['states']),
    originalPhaseGateChanged=False,trajectoryRunsPerformed=False,committed=False,pushed=False,
    interpretation='Candidate preserved and rejected at focused liquid-PH accuracy gate; event/cost/fixture runs held under user stop instruction.')
target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['evidenceAuditPassed','candidateQualified','stopRequired','existingFilesPreserved','regionRegressions']}))
