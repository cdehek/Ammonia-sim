"""Independently audit every archived failed Newton history (stdlib only)."""
import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

summary=json.loads(Path(sys.argv[1]).read_text())
archive=Path(sys.argv[2])
assert summary['passed']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==summary['failedHistory']['sha256']
counts=Counter()
derivatives=line_searches=0
for line in gzip.open(archive,'rt'):
    trial=json.loads(line)
    iterations={}
    for event in trial['events']:
        if event['type']=='iteration':
            r=event['residual']
            assert event['fluidNorm']==max(map(abs,r[:10]))
            assert event['thermalNorm']==max(map(abs,r[10:]))
            assert abs(r[event['dominantIndex']])==max(map(abs,r))
            iterations[event['solveId']]=event
        elif event['type']=='derivative':
            derivatives+=1
            assert abs(event['step'])==event['epsilon']*2**(-event['shrink'])
            assert event['epsilon']>0
        elif event['type']=='line-search':
            line_searches+=1
            assert 2**(-28)<=event['factor']<=1
            if event['outcome']=='accepted':assert event['nextError']<event['previousError']
            elif event['outcome']=='not-reduced':assert not event['nextError']<event['previousError']
        elif event['type']=='solve-failed':
            counts[(trial['case'],trial['tolerance'])]+=1
            last=event['lastIteration']
            if last is not None:
                assert last==iterations[event['solveId']]
                assert max(map(abs,last['residual']))>1e-11
                if 'iteration budget' in event['message']:assert last['iteration']==30
for case in summary['cases']:
    assert counts[(case['name'],case['tolerance'])]==case['stats']['failedNewton']
    assert case['stats']['maxConvergedThermalResidualK']<=1e-12
assert sum(counts.values())==len(summary['failedNewtonAttempts'])
result=dict(passed=True,source='Independent Python stdlib diagnostic integrity audit',failedNewtonHistories=sum(counts.values()),
            derivativeProbesAudited=derivatives,lineSearchProbesAudited=line_searches,
            archiveSHA256=summary['failedHistory']['sha256'])
Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
