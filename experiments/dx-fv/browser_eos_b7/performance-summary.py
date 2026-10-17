"""Descriptive repeated browser measurements; never ratio failure to success."""
import json,statistics
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';read=lambda p:json.loads(p.read_text());rows=[];engines={}
for engine in ['chromium','webkit']:
 d=read(E/f'performance-{engine}.json');assert 'harnessError' not in d;d=d['result']
 for full in [False,True]:
  for group in sorted({r['group'] for r in d['rows']}):
   blocks={id:[r for r in d['rows'] if r['id']==id and r['fullVLE']==full and r['group']==group] for id in ['rebuiltB4C','gateA']}
   summarize=lambda records:dict(rounds=len(records),medianUS=statistics.median(r['usPerCall'] for r in records),minUS=min(r['usPerCall'] for r in records),maxUS=max(r['usPerCall'] for r in records),calls=sum(r['calls'] for r in records),rawReturned=sum(r['counts']['accepted'] for r in records),refused=sum(r['counts']['rejected'] for r in records))
   def signatures(records):return {tuple((r['accepted']>0,r['rejected']>0) for r in z['outcomes']) for z in records}
   control,candidate=summarize(blocks['rebuiltB4C']),summarize(blocks['gateA']);comparable=signatures(blocks['rebuiltB4C'])==signatures(blocks['gateA'])
   rows.append(dict(engine=engine,fullVLE=full,group=group,control=control,candidate=candidate,comparableOutcomes=comparable,descriptiveMedianRatio=candidate['medianUS']/control['medianUS'] if comparable else None,ratioExclusion=None if comparable else 'Different raw return/refusal outcomes; failure-to-success ratio is not meaningful'))
 init={}
 for id in ['rebuiltB4C','gateA']:
  samples=[r for r in d['initialization'] if r['id']==id];init[id]=dict(samples=len(samples),medianTotalMS=statistics.median(r['init']['totalMS'] for r in samples),medianFirstFactoryMS=statistics.median(r['init']['firstFactoryMS'] for r in samples),maxFirstFactoryMS=max(r['init']['firstFactoryMS'] for r in samples),initialLinearMemoryBytes=sorted({r['init']['initialLinearMemoryBytes'] for r in samples}),readyLinearMemoryBytes=sorted({r['init']['readyLinearMemoryBytes'] for r in samples}))
 worker=read(E/f'workers-{engine}.json')['result']
 heaps=[r['heap']['used'] for r in d['rows'] if r.get('heap')]
 engines[engine]=dict(initialization=init,linearMemoryObserved=sorted({r['memory'] for r in d['rows']}),jsHeapRangeBytes=[min(heaps),max(heaps)] if heaps else None,maximumMainThreadCampaignHeartbeatGapMS=d['maximumHeartbeatGapMS'],maximumWorkerCampaignHeartbeatGapMS=worker['maximumHeartbeatGapMS'],workerLatencyMS={r['id']:r['latencyMS'] for r in worker['rows']},latencySamplesPerBuild=1,initIncludesArtifactIntegrityChecks=True,responsivenessConcern='Synchronous module factory and bounded main-thread sampling produce substantial observed timer gaps; worker gaps are also retained. Numerical correctness is separate. No smooth-response guarantee.')
out=dict(rows=rows,engines=engines,roundsPerPropertyGroup=5,rawReturnedIsNotPhysicalQualification=True,workerLatencyNotSpeedup=True,physicalSafariOrIPad=False,heapAndLinearMemoryAreNotLeakProof=True)
p=E/'performance-summary.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(engines,indent=2))
