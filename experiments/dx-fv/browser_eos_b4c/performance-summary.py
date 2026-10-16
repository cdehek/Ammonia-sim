"""Matched descriptive costs only; discarded contended samples are never used."""
import json,os,statistics
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'))
def read(n):return json.loads((E/n).read_text())
def summarize(rows):
 return {k:dict(medianMicroseconds=statistics.median(r['elapsedMS']*1000/r['calls'] for r in rows if r['group']==k),calls=sum(r['calls'] for r in rows if r['group']==k),exceptions=sum(len(r['errors']) for r in rows if r['group']==k)) for k in sorted({r['group'] for r in rows})}
out=dict(native={},browser={},A2Cold={},physicalIPad=False,timingAcceptanceThreshold=None,wholeSimulatorSlowdownClaim=False)
for label in ['controlA','candidateB']:
 d=read(f'performance-native-{label}.json');out['native'][label]=dict(groups=summarize(d['rows']),initializationMS=d['initializationMS'],maxRSSKiB=d['maxRSSKiB'])
for runtime in ['chromium','webkit']:
 for label,build in [('controlA','rebuiltA'),('candidateB','candidateB')]:
  d=read(f'{runtime}-{build}-cost.json');assert 'error'not in d and 'error'not in d['worker']
  out['browser'][runtime+'-'+label]=dict(groups=summarize(d['rows']),workerGroups=summarize(d['worker']['result']['rows']),init=d['init'],workerInit=d['worker']['result']['init'],linearMemoryBytes=d['memoryBytes'],workerLinearMemoryBytes=d['worker']['result']['memoryBytes'],heartbeat=d['mainThreadDuringWorker'],jsHeap=d['jsHeap'],browserVersion=d['browserVersion'])
  a=read(f'{runtime}-A2-cold-perf-{label}.json');assert a['completedAllSelectedSamples'] and 'error'not in a
  out['A2Cold'][runtime+'-'+label]=dict(completedSeconds=.2,advanceElapsedMS=sum(r['elapsedMS'] for r in a['rows']),elapsedMSWithSetup=a['elapsedSeconds']*1000,counts=a['rows'][-1]['counts'],work={k:a['rows'][-1]['record'][k] for k in ['acceptedSteps','rejectedSteps','attemptedResidualEvaluations','attemptedIterations']})
out['additionalB4CCostRatios']={}
for runtime in ['native','chromium','webkit']:
 a=out['native']['controlA']['groups'] if runtime=='native' else out['browser'][runtime+'-controlA']['groups'];b=out['native']['candidateB']['groups'] if runtime=='native' else out['browser'][runtime+'-candidateB']['groups']
 out['additionalB4CCostRatios'][runtime]={k:b[k]['medianMicroseconds']/v['medianMicroseconds'] for k,v in a.items()}
assert all(v['exceptions']==0 for d in out['native'].values() for v in d['groups'].values())
assert all(v['exceptions']==0 for d in out['browser'].values() for key in ['groups','workerGroups'] for v in d[key].values())
out['measurementNotes']=['Five 150ms rounds per microbenchmark group, medians; full updates/getters, not pure kernel time.','Control/candidate native and WASM rebuilt with matched toolchains/flags. Full scientific controls also match archived B4B exactly.','Authoritative timings ran serially after scientific campaigns and compilers. First native timing pair overlapped A2 zero-exchange and is retained as contended-do-not-use.','A2 cold performance is a separate matched end-to-end replay. Other A2 scientific-run wall times are not cumulative performance evidence.','One cold timing per runtime/build is descriptive, not a statistical speed guarantee.','B4A/B4B historical ratios are different workloads; no multiplied cumulative slowdown is reported.','Internal homogeneous evaluation counts are native source traces; browser adapter counts are public interface calls, not internal Newton counts.']
p=E/'performance-summary.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Matched performance summary; no property/worker exceptions')
