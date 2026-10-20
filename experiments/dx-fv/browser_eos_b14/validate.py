"""Milestone integrity and interpretation checks; no new simulation campaign."""
import gzip,hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(n):return json.loads((E/(n+'.json')).read_text())
def run(*args):
 p=subprocess.run(args,cwd=B,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 assert p.returncode==0,p.stdout+p.stderr
 return p.stdout
checks=[]
for f in ['cold','warm']:
 for i in range(1,4):
  c=f'canonical-{f}-r{i}';o=f'observed-{f}-r{i}'+('-fixed'if f=='cold'and i==1 else'')
  run('node','verify.mjs',c,o);checks.append(dict(canonical=c,observed=o,passed=True))
for s in ['added','fine']:
 run('node','verify.mjs','canonical-warm-'+s,'observed-warm-'+s);checks.append(dict(schedule=s,passed=True))
run('node','verify-baseline.mjs');run('node','analyze.mjs');run('node','final-analysis.mjs');run('python3','audit.py');run('python3','verify-protected.py')
a=read('analysis');event=read('transition-bracket')['event'];assert event['direction']=='cooling'and event['boundary']=='vapor'and event['section']==0
assert event['bracketStartSeconds']<event['seconds']<event['bracketEndSeconds']<=.01
for f,n,evals,ph,jacs in [('cold',32,5272,5028,235),('warm',86,19380,17416,867)]:
 v=a['fixtures'][f];assert v['acceptedPhysicalSubsteps']==n and v['calls']['residual']==evals and v['advanceCounts']['property.ph']==ph
 assert v['calls']['jacobian']==jacs and v['newton']['failed']==0 and v['newton']['allUnitLineSearch']and v['newton']['allFirstPositiveDerivative']
 assert all(c['counts'].get('property.ph',0)==0 for c in v['columnTotals'][10:])
 assert all(c['positiveFirstOnly']for c in v['columnTotals'])
 t=read('temporal-'+f);assert all(len(e['terms'])==31 and e['bitExact']for e in t);assert all(max(x['normalized']for x in e['terms']if x['coordinate']=='thermal-energy')<1 for e in t)
 assert read('conservation-'+f)['passed']
 init=[json.loads(x)for x in gzip.open(E/('initialization-'+f+'.jsonl.gz'),'rt')];c=[json.loads(x)for x in gzip.open(E/('canonical-'+f+'-r1.jsonl.gz'),'rt')];assert next(x for x in init if x['type']=='checkpoint')['scienceHash']==next(x for x in c if x['type']=='checkpoint')['scienceHash']
assert all(r['comparisons'][-1]['maximumToleranceRatio']<1 and r['conservation']['passed']for r in a['boundaries'])
assert read('external-budget-validation')['passed'];assert json.loads(gzip.decompress((E/'domain-and-rollback.json.gz').read_bytes()))['passed']
expected=['README.md','RESEARCH_DESIGN_AND_GATE_0.md','ENGINEERING_REPORT.md','MECHANICS_REPORT.md','SCIENTIFIC_SOURCE_AND_PROVENANCE.md','WARM_PHASE_TRANSITION_RECONSTRUCTION.md','TEMPORAL_ERROR_DECOMPOSITION.md','OUTPUT_BOUNDARY_SENSITIVITY.md','JACOBIAN_COLUMN_COST_ANALYSIS.md','RESIDUAL_ASSEMBLY_AND_ALLOCATION.md','PH_INVERSION_COST_ANALYSIS.md','CONSERVATION_AND_ROLLBACK.md','INSTRUMENTATION_EQUIVALENCE.md','PERFORMANCE_MEASUREMENT_LIMITATIONS.md','QUALIFICATION_GAPS.md','NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md']
assert all((B/f).is_file()for f in expected)
assert read('source-preservation')['historicalBytesUnchanged']
status=json.loads((B/'milestone-status.json').read_text());assert status['classification']=='B14-A0 PHASE/JACOBIAN DIAGNOSTIC PASS'
# Source/run bounds and receipts; failed setup and deliberate timeout are separate evidence.
exits=[]
for p in E.glob('*.exit.json'):
 x=json.loads(p.read_text());name=p.stem
 if name=='observed-cold-r1.exit':assert x['returncode']==1 and x['lastCheckpointSeconds']is None and 'Anchor drift'in x['stderr']
 elif name=='external-budget-witness.exit':assert x['timedOut']and x['terminationKind']=='external-wall-budget'
 else:assert x['returncode']==0
 if 'lastCheckpointSeconds'in x and x['lastCheckpointSeconds']is not None:assert x['lastCheckpointSeconds']<=.01
 exits.append(dict(file=p.name,returncode=x['returncode']))
result=dict(passed=True,classification=status['classification'],exactPairComparisons=checks,all31TermEstimatesExact=True,allNormalNewtonAndDerivativeChecks=True,allAcceptedConservationChecks=True,originalA2Baseline=True,domainRollbackAndExternalTerminationDistinct=True,requiredReports=len(expected),processReceipts=exits,remainingUncertainties=status['unresolved'])
(E/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: exact pairs, estimator/column/PH/conservation/failure evidence and protected sources')
