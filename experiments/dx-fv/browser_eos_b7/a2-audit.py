"""Bounded existing C1 subset; retain its assertions, no full A2 qualification."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';rows=[]
for engine in ['chromium','webkit']:
 d=json.loads((E/f'a2-{engine}.json').read_text());assert 'harnessError' not in d and d['result']['passed']
 for run in d['result']['a2']:
  result=run['result'];assert result['passed'] and not result['fullA2Qualification'] and len(result['rows'])==5
  for r in result['rows']:
   row=dict(engine=engine,errorExperiment=run['label'],scenario=r['scenario'])
   if r['scenario']=='A-supported':assert r['exactAcceptedMatch'];row['exactAcceptedMatch']=True
   elif r['scenario']=='real-browser-boundary':
    assert r['everyRejectedTrialRollback'];row.update(persistent=r['persistent'],rejectedTrials=r['trialFailures'],everyRejectedTrialRollback=True)
    if r['persistent']:
     assert r['acceptedRollback'] and r['identityPreserved'] and r['floor']==1e-9 and len(r['attempts'])==20
     sizes=[z['trialSeconds'] for z in r['attempts']];assert all(y==x/2 for x,y in zip(sizes,sizes[1:]));assert sizes[-1]==1.9073486328125e-9
     row.update(exactAcceptedRollback=True,identityPreserved=True,attempts=20,halvings=19,floor=1e-9)
   else:
    assert r['scenario']=='D-physical-thermal-exit' and r['acceptedRollback'] and r['limit'] in [200,400]
    assert r['candidateStop']['kind']=='domain' and r['candidateStop']['evidence']['confirmed'];row.update(temperatureLimitK=r['limit'],independentThermalExitConfirmed=True)
   if 'record' in r:
    rec=r['record'];assert abs(rec['massResidualKg'])<1e-8 and abs(rec['combinedEnergyResidualKJ'])<1e-6
    assert all(abs(s['massKg'])<1e-8 and abs(s['energyKJ'])<1e-6 for s in rec['sectionResiduals'])
    row['massResidualKg']=rec['massResidualKg'];row['combinedEnergyResidualKJ']=rec['combinedEnergyResidualKJ']
   rows.append(row)
files={}
for name in ['a2-subset.cjs','science.mjs','evidence/c1-harness-provenance.json']:
 p=B.parent/'browser_eos_b6'/name;files['browser_eos_b6/'+name]=hashlib.sha256(p.read_bytes()).hexdigest()
out=dict(passed=True,rows=rows,scenariosPerEngine=10,sourceIdentities=files,originalC1AndAcceptedA2DependenciesUnchanged=True,fullA2Qualification=False,scope='Existing supported pair, transient/persistent real property fault experiments, exact rollback, genuine thermal exits. Actual PT fault uses explicitly labeled harness dispatch injection; no Gate B endpoint properties substituted.')
p=E/'a2-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Bounded C1 A2 compatibility PASS; 10 scenarios per engine')
