"""Limited accepted scientific assertions; this is not full A2 qualification."""
import json,os,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import save
def read(n):return json.loads((E/n).read_text())
assert read('focused-gate.json')['eligibleForLimitedA2'] and read('boundary-gate.json')['eligibleForLimitedA2']
out=dict(cases={},zeroExchange={},conservationMaxima={},fullQualification=False);failures=[]
keys=['acceptedSteps','rejectedSteps','accuracyRejectedSteps','eventRejectedSteps','domainRejectedSteps','attemptedResidualEvaluations','attemptedIterations','attemptedLinearSolves']
for engine in ['chromium','webkit']:
 for case in ['cold','warm','feed-step','heat-reversal']:
  a=read(f'{engine}-A2-{case}-controlA.json');b=read(f'{engine}-A2-{case}.json')
  for label,d in [('controlA',a),('candidateB',b)]:
   if 'error'in d or not d.get('completedAllSelectedSamples'):failures.append(dict(engine=engine,case=case,label=label,error=d.get('error','incomplete')));continue
   for row in d['rows']:
    r=row['record'];assert r['stop']is None and r['lastResidual']<=1e-11 and r['lastTimeError']<=1 and all(t['error']<=1 for t in r['trace'])
    for k,v in row['conservation'].items():
     out['conservationMaxima'][k]=max(out['conservationMaxima'].get(k,0),v)
     assert v<(1e-8 if 'Mass' in k or k=='massKg' else 1e-6)
  if 'rows' not in a or 'rows' not in b:continue
  ra=a['rows'][-1]['record'];rb=b['rows'][-1]['record'];assert a['settings']==b['settings']
  out['cases'][engine+'-'+case]=dict(completedSeconds=rb['seconds'],settingsUnchanged=True,controlWork={k:ra[k] for k in keys},candidateWork={k:rb[k] for k in keys},workDelta={k:rb[k]-ra[k] for k in keys},eventsChanged=ra['events']!=rb['events'],controlEvents=ra['events'],candidateEvents=rb['events'],controlCounts=a['rows'][-1]['counts'],candidateCounts=b['rows'][-1]['counts'],controlOutlets=ra['outlet'],candidateOutlets=rb['outlet'],candidateLastResidual=rb['lastResidual'],candidateMaxTemporalError=max(t['error'] for t in rb['trace']))
 for case in ['zero','vapor-zero','upper-vapor-zero']:
  data={}
  for label,suffix in [('controlA','-controlA'),('candidateB','')]:
   d=read(f'{engine}-A2-{case}{suffix}.json');assert 'error' not in d
   for r in d['rows']:
    assert 'error' not in r and r['trial']['completed'] and r['trial']['errorNorm']<=1e-11 and r['exactTrialStatePreserved'] and 'scientificCheck' in r['trial']
   data[label]=dict(exactTrialStatePreserved=True,errorNorm=d['rows'][0]['trial']['errorNorm'],work=d['rows'][0]['trial']['work'],counts=d['counts'])
  out['zeroExchange'][engine+'-'+case]=data
out.update(failures=failures,passOriginalLimitedScientificRequirements=not failures,acceptedDependencyClosure=read('accepted-a2-verification.json'))
save(E/'A2-audit.json',out);print('Limited A2 gates',not failures,'cases',len(out['cases']),'zero-exchange pairs',len(out['zeroExchange']));assert not failures
