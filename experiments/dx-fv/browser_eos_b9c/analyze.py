"""Independent exact browser evidence comparison and property-sequence projection."""
import gzip,json,struct,statistics,argparse,math
from pathlib import Path
B=Path(__file__).resolve().parent; E=B/'evidence'
def read(n):return json.loads(gzip.decompress((E/n).read_bytes()))
def save(n,v):(E/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def number(v):return struct.unpack('>d',bytes.fromhex(v['f64']))[0] if isinstance(v,dict) and set(v)=={'f64'} else v
def plain(v):
 if isinstance(v,list):return [plain(x) for x in v]
 if isinstance(v,dict):return number(v) if set(v)=={'f64'} else {k:plain(x) for k,x in v.items()}
 return v
def compare_properties(a,b):
 # a,b remain bit encodings. No float conversion enters an equality decision.
 assert a['section']==b['section']
 assert a['stageCount']==b['stageCount'] and a['trialCount']==b['trialCount']
 assert len(a['boundaries'])==len(b['boundaries'])
 hits=set();retained={};requests={'inlet':0,'outlet':0};misses={'inlet':0,'outlet':0};outside=0
 for x,y in zip(a['boundaries'],b['boundaries']):
  assert {k:v for k,v in x.items() if k!='realPH'}=={k:v for k,v in y.items() if k!='realPH'}
  if number(x['stage']) is None:outside+=1;assert x['realPH']==y['realPH'];continue
  side=x['side'];requests[side]+=1;key=(x['stage']['f64'],side)
  state={k:x[k] for k in ['p','h','value'] if k in x}
  if number(y['realPH'])==1:retained[key]=state;misses[side]+=1
  else:
   assert number(y['realPH'])==0 and state==retained[key],'omitted input/result differs'
   hits.add(y['id']['f64'])
 dropped=[p for p in a['properties'] if isinstance(p['request'],dict) and p['request'].get('f64') in hits]
 assert len(dropped)==2*len(hits)
 grouped={}
 for p in dropped:grouped.setdefault(p['request']['f64'],[]).append(p['method'])
 for i in hits:assert grouped[i]==['ph','sat']
 projected=[p for p in a['properties'] if not(isinstance(p['request'],dict) and p['request'].get('f64') in hits)]
 assert projected==b['properties'],'other property order/input/output/throw changed'
 pa,pb=plain(a),plain(b)
 return {'passed':True,'stages':pa['stageCount'],'trials':pa['trialCount'],'logicalStageBoundaryRequests':requests,'candidateMisses':misses,'successfulHits':len(hits),'realPHControl':pa['public'].get('ph',0),'realPHCandidate':pb['public'].get('ph',0),'realPHReduction':pa['public'].get('ph',0)-pb['public'].get('ph',0),'section':pa['section'],'publicSATControl':pa['public'].get('sat',0),'publicSATCandidate':pb['public'].get('sat',0),'nestedSATControl':pa['counts'].get('lexical.sat',0)-pa['public'].get('sat',0),'nestedSATCandidate':pb['counts'].get('lexical.sat',0)-pb['public'].get('sat',0),'canonicalRecoveryControl':pa['public'].get('stateMVU',0),'canonicalRecoveryCandidate':pb['public'].get('stateMVU',0),'nonStageBoundaryRequests':outside,'nonStagePHControl':sum(p['method']=='ph' and p['stage'] is None for p in pa['properties']),'nonStagePHCandidate':sum(p['method']=='ph' and p['stage'] is None for p in pb['properties']),'thrownControl':sum('error' in p for p in pa['properties']),'thrownCandidate':sum('error' in p for p in pb['properties']),'projectedPropertySequenceExact':True,'eachOmittedInputAndResultExact':True}
p=argparse.ArgumentParser();p.add_argument('--performance',action='store_true');args=p.parse_args()
if not args.performance:
 summary={'passed':True,'engines':{}}
 for engine in ['chromium','webkit']:
  parity=read('parity-'+engine+'.json.gz');assert parity['passed'];rows={}
  historical=json.loads(gzip.decompress((B.parent/'browser_eos_b9b/evidence'/('baseline-'+engine+'.json.gz')).read_bytes()))
  for f in ['cold','warm']:
   a,b=[r for r in parity['runs'] if r['fixture']==f];old=next(r for r in historical['runs'] if r['fixture']==f)
   assert a['science']==b['science'] and a['scienceHash']==b['scienceHash']==old['scienceHash']
   assert a['checkpointHashes']==b['checkpointHashes']==old['checkpointHashes']
   assert a['componentHashes']==b['componentHashes']
   for k in ['residuals','linear','solves']:assert a['evidence'][k]==b['evidence'][k]
   prop=compare_properties(a['evidence'],b['evidence']);assert prop['successfulHits']==prop['realPHReduction']
   assert prop['stages']==(54 if f=='cold' else 120)
   assert a['work']['residuals']==(2914 if f=='cold' else 7710)
   rows[f]={'exactScience':True,'savedB9BBaselineExact':True,'scienceSHA256':a['scienceHash'],'componentHashes':a['componentHashes'],'work':a['work'],'property':prop,'conservation':a['audits']}
  reg=read('regressions-'+engine+'.json.gz');assert reg['passed'];a,b=reg['runs'];regrows={}
  assert a['property']==b['property'] and a['invalidUpdates']==b['invalidUpdates']
  for x,y in zip(a['cases'],b['cases']):
   assert {k:v for k,v in x.items() if k!='evidence'}=={k:v for k,v in y.items() if k!='evidence'},x['name']
   ea,eb=x['evidence'],y['evidence']
   for k in ['logicalBoundaryHash','section','stageCount','trialCount','boundaryRequests','stageRequests','thrown']:assert ea[k]==eb[k],(x['name'],k)
   assert number(ea['public'].get('ph',{'f64':'0000000000000000'}))-number(eb['public'].get('ph',{'f64':'0000000000000000'}))==number(eb['stageHits'])
   regrows[x['name']]={'exactScience':True,'controlProperties':plain(ea),'candidateProperties':plain(eb),'componentHashes':x['componentHashes']}
  failure=read('c1-'+engine+'.json.gz');assert failure['passed'] and failure['runs'][0]['passed']
  summary['engines'][engine]={'fixtures':rows,'regressions':regrows,'propertyCases':len(a['property']),'invalidUpdates':len(a['invalidUpdates']),'C1UnmodifiedPass':True,'backendGuardPass':a['rejectedBackend'] and b['rejectedBackend']}
 save('qualification.json',summary);print('Exact science, projected properties, boundary/phase and C1 qualification PASS')
else:
 result={}
 for engine in ['chromium','webkit']:
  data=read('timing-'+engine+'.json.gz');assert data['passed'];rows={};parity=read('parity-'+engine+'.json.gz')
  for f in ['cold','warm']:
   runs=[r for r in data['runs'] if r['fixture']==f];expected=next(r for r in parity['runs'] if r['fixture']==f)['scienceHash']
   assert len(runs)==15 and all(r['scienceHash']==expected for r in runs)
   values={};pairs=[]
   for mode in ['control','candidate']:
    v=[r for r in runs if r['mode']==mode]
    def stat(v):return {'median':statistics.median(v),'min':min(v),'max':max(v),'stdev':statistics.stdev(v) if len(v)>1 else 0,'samples':v}
    values[mode]={'advanceMS':stat([sum(t['advanceMS'] for t in r['timing']) for r in v]),'initializationMS':stat([r['initializationMS'] for r in v]),'tableAndFactoryConstructionMS':stat([r['constructionMS'] for r in v]),'extraRecordMS':stat([sum(t['recordMS'] for t in r['timing']) for r in v]),'roundtripMS':stat([r['requestRoundtripMS'] for r in v])}
   for i in range(5):
    v=[r for r in runs if r['round']==i];assert [r['mode'] for r in v]==['control','candidate','control']
    times=[sum(t['advanceMS'] for t in r['timing']) for r in v];baseline=(times[0]+times[2])/2;pairs.append({'round':i,'beforeMS':times[0],'candidateMS':times[1],'afterMS':times[2],'bracketMS':baseline,'deltaMS':times[1]-baseline,'reductionPercent':100*(baseline-times[1])/baseline})
   consistent=all(p['reductionPercent']>0 for p in pairs)
   rows[f]={'values':values,'paired':pairs,'medianPairedReductionPercent':statistics.median(p['reductionPercent'] for p in pairs),'improvementMeasured':consistent,'decision':'meaningful improvement in all five matched brackets' if consistent else 'mixed/noisy matched evidence','diagnosticAdvanceMS':{r['mode']:sum(t['advanceMS'] for t in r['timing']) for r in parity['runs'] if r['fixture']==f},'diagnosticScopesMS':{r['mode']:plain(r['evidence']['times']) for r in parity['runs'] if r['fixture']==f}}
  beats=data['heartbeatMS'];result[engine]={'fixtures':rows,'heartbeat':{'medianMS':statistics.median(beats),'maxMS':max(beats),'samples':len(beats)},'heapBefore':data['heapBefore'],'heapAfter':data['heapAfter'],'version':data['version'],'lifecycle':data['lifecycle']}
 save('performance-summary.json',result);print('Matched performance evidence analyzed; all timed scientific hashes exact')
