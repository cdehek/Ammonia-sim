"""Reproducible descriptive summaries; no timing exclusions or inferred populations."""
from pathlib import Path
import json,statistics as s,gzip,hashlib
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(name):
 p=E/(name+'.json')
 return json.loads(p.read_text() if p.exists() else gzip.decompress((E/(name+'.json.gz')).read_bytes()))
def q(values,p):
 values=sorted(values);i=(len(values)-1)*p;lo=int(i);return values[lo]+(values[min(lo+1,len(values)-1)]-values[lo])*(i-lo)
def stats(v):
 return {'n':len(v),'median':s.median(v),'min':min(v),'max':max(v),'iqr':q(v,.75)-q(v,.25),'p95':q(v,.95)} if v else {'n':0}
def pairs(rows,key,get,check=None):
 variants=['control','candidate']
 if any(r['variant'].startswith('count-')for r in rows):variants=['count-control','count-candidate']
 p=[]
 for pair in sorted(set(r['pair']for r in rows)):
  a,b=[next(r for r in rows if r['pair']==pair and r['variant']==v)for v in variants]
  if check:assert check(a)==check(b),(key,pair,'scientific mismatch')
  aa,bb=get(a),get(b);p.append({'pair':pair,'controlMS':aa,'candidateMS':bb,'savedMS':aa-bb,'improvementPercent':(aa-bb)/aa*100})
 return {'case':key,'pairs':p,'controlMS':stats([x['controlMS']for x in p]),'candidateMS':stats([x['candidateMS']for x in p]),'savedMS':stats([x['savedMS']for x in p]),'improvementPercent':stats([x['improvementPercent']for x in p]),'candidateFasterPairs':sum(x['savedMS']>0 for x in p)}
summary={'allValidSamplesRetained':True,'statisticalScope':'descriptive session pairs on one host; no outlier trimming, population CI, allocation inference or universal speedup','node':{},'worker':{},'micro':{},'sensitivity':{}}
if (E/'node-primary.json').exists():
 node=read('node-primary')
 for w in [0,2]:
  for f in ['cold','warm']:
   rows=[r for r in node if r['warmups']==w and r['kind']==f]
   for metric in ['wallMS','cpuMS']:
    k=f'{f}-warmups{w}-{metric}';summary['node'][k]=pairs(rows,k,lambda r:r['scopes']['compute'][metric],lambda r:{k:v for k,v in r['result'].items() if k not in ['intervals','advanceCounts']})
 for kind in ['vapor','twoPhase','mixed']:
  summary['micro']['node-'+kind]=pairs([r for r in node if r['kind']=='ph'],kind,lambda r:r['result'][kind]['wallMS'],lambda r:r['result'][kind]['checksum'])
 for campaign in ['counters','jitless']:
  if not (E/('node-'+campaign+'.json')).exists():continue
  for f in ['cold','warm']:
   rows=[r for r in read('node-'+campaign) if r['kind']==f];k=campaign+'-'+f;summary['sensitivity'][k]=pairs(rows,k,lambda r:r['scopes']['compute']['wallMS'],lambda r:{k:v for k,v in r['result'].items()if k not in ['intervals','advanceCounts']})
worker=read('chromium-performance')['rows']
for w in [0,2]:
 for f in ['cold','warm']:
  rows=[r for r in worker if r['primary'] and r['warmups']==w and r['fixture']==f]
  for metric in ['computeMS','serviceMS','roundtripMS']:
   k=f'{f}-warmups{w}-{metric}';summary['worker'][k]=pairs(rows,k,lambda r:r['advance'][metric],lambda r:r['checksum'])
  if f=='warm':
   k=f'warm-transition-0.005-to-0.01-warmups{w}';summary['worker'][k]=pairs(rows,k,lambda r:r['advance']['intervals'][-1]['wallMS'],lambda r:r['checksum'])
for schedule in ['added','fine']:
 for f in ['cold','warm']:
  rows=[r for r in worker if r['schedule']==schedule and r['fixture']==f];k=f'{f}-{schedule}';summary['worker'][k]=pairs(rows,k,lambda r:r['advance']['computeMS'],lambda r:r['checksum'])
micro=read('chromium-micro')['rows']
for kind in ['vapor','twoPhase','mixed']:summary['micro']['worker-'+kind]=pairs(micro,kind,lambda r:r['result'][kind]['wallMS'],lambda r:r['result'][kind]['checksum'])
summary['lifecycle']={}
for v in ['control','candidate']:
 rows=[r for r in worker if r['primary'] and r['warmups']==0 and r['variant']==v]
 life={}
 for name,fn in {'constructMS':lambda r:r['constructMS'],'readyMS':lambda r:r['readyMS'],'initialSnapshotRoundtripMS':lambda r:r['init']['roundtripMS'],'assetVerificationMS':lambda r:r['init']['assetVerificationMS'],'importMS':lambda r:r['init']['importMS'],'tableMS':lambda r:r['init']['tableMS'],'initializeMS':lambda r:r['init']['initializeMS'],'disposeMS':lambda r:r['disposalMS'],'handlerMS':lambda r:r['advance']['handlerMS'],'textAssignmentMS':lambda r:r['advance']['textAssignmentMS'],'projectionMS':lambda r:r['advance']['projectionMS'],'mainPostMS':lambda r:r['advance']['mainPostMS'],'dispatchToWorkerMS':lambda r:r['advance']['dispatchToWorkerMS'],'returnDeliveryMS':lambda r:r['advance']['returnDeliveryMS']}.items():life[name]=stats([fn(r)for r in rows])
 for category in ['ping','echo']:
  for metric in ['roundtripMS','serviceMS','handlerMS','mainPostMS','returnDeliveryMS']:
   life[category+'-'+metric]=stats([m[metric]for r in rows for m in r[category]])
 life['workerPostMS']=stats([t for r in rows for t in r['postCosts'].values()])
 life['responsiveness']={k:stats([d for r in rows for d in r['responsiveness'][k]])for k in ['delaysMS','inputAcknowledgementMS','toolSwitchMS']}
 life['longTasks']=[t for r in rows for t in r['responsiveness']['longTasks']]
 summary['lifecycle'][v]=life
# Hypothetical mix: arithmetic weighted means of paired absolute deltas per pair.
# Mixes count whole cold/warm bounded requests, not time/energy duty cycles.
summary['hypotheticalMixes']={}
for w in [0,2]:
 cold=summary['worker'][f'cold-warmups{w}-computeMS']['pairs'];warm=summary['worker'][f'warm-warmups{w}-computeMS']['pairs']
 for label,weight in [('cold-heavy',.9),('balanced',.5),('warm-heavy',.1)]:
  p=[]
  for c,v in zip(cold,warm):
   aa=weight*c['controlMS']+(1-weight)*v['controlMS'];bb=weight*c['candidateMS']+(1-weight)*v['candidateMS'];p.append({'controlMS':aa,'candidateMS':bb,'savedMS':aa-bb,'percent':(aa-bb)/aa*100})
  summary['hypotheticalMixes'][f'{label}-warmups{w}']={'coldRequestFraction':weight,'n':len(p),'medianPairedSavedMS':s.median(x['savedMS']for x in p),'medianPairedPercent':s.median(x['percent']for x in p),'planningOnly':True}
summary['workerSamples']=len(worker);summary['workerMicroSamples']=len(micro)
(E/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Summarized all valid paired samples; strict same-runtime checksums/digests match')
