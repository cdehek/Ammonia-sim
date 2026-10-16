"""Audit dispatch, actual raw quality, work counts, and diagnostic equivalence."""
import collections,json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import save
def read(n):return json.loads((E/n).read_text())
on=read('trace-candidateB-results.json')['rows'];off=read('trace-candidateB-off-results.json')['rows'];plain=read('trace-candidateB-uninstrumented-results.json')['rows']
assert on==off==plain
out=dict(loggingOnOffAndUninstrumentedEqual=True,rows=len(on),builds={})
for label,suffix in [('controlA',''),('candidateB',''),('candidateB','-full-vle')]:
 blocks=[];cur=None
 for line in (E/f'trace-{label}{suffix}.jsonl').read_text().splitlines():
  e=json.loads(line)
  if 'marker' in e:cur=dict(marker=e['marker'],events=[]);blocks.append(cur)
  elif cur:cur['events'].append(e)
 summary=[]
 for b in blocks:
  counts=dict(collections.Counter(e['event'] for e in b['events']));qualities=[e for e in b['events'] if e['event'] in ['superanc_quality','vle_quality']];dispatch=[e for e in b['events'] if e['event'] in ['PH_dispatch','caloric_dispatch']]
  v=dict(marker=b['marker'],eventCounts=counts,qualityDecisions=qualities,dispatch=dispatch,homogeneousEvaluations=counts.get('homogeneous_eval',0));summary.append(v)
  if label=='candidateB':
   for q in qualities:
    if q['Q']>1:assert dispatch and dispatch[-1]['phase']==5 and dispatch[-1]['homogeneous']==1
 out['builds'][label+suffix]=dict(snapshots=summary,totalHomogeneousEvaluations=sum(r['homogeneousEvaluations'] for r in summary))
before=out['builds']['controlA']['snapshots'];after=out['builds']['candidateB']['snapshots'];changes=[]
for a,b in zip(before,after):
 assert a['marker']==b['marker']
 if a['homogeneousEvaluations']!=b['homogeneousEvaluations']:changes.append(dict(marker=a['marker'],control=a['homogeneousEvaluations'],candidate=b['homogeneousEvaluations'],rawQuality=a['qualityDecisions']))
out['changedHomogeneousWork']=changes
# Compare diagnostic PH values with full matrix sample values, not just logging parity.
for label in ['controlA','candidateB']:
 expected={}
 for r in read(f'native-{label}.json')['rows']:
  for x in [r['base']]+[q['output'] for q in r['probes'] if 'output'in q]:expected[tuple(x['inputBits'])]=x['PH']
 for r in read(f'trace-{label}-results.json')['rows']:assert r['state']==expected[tuple(r['marker']['inputBits'])]
out['allSnapshotsMatchUninstrumentedScientificMatrix']=True
save(E/'trace-audit.json',out);print('Trace gates pass;',len(changes),'changed solver work counts;',len(on),'logging parity snapshots')
