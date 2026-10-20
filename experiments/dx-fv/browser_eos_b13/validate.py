"""Review gate: verify preservation, retained hash identity, evidence and deliverables."""
import gzip,hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
commands=[['python3',str(B/'audit.py')],['node',str(B/'verify-results.mjs')],['python3',str(B/'analyze.py')],['timeout','30','node','--max-old-space-size=512',str(B/'contracts.mjs')],['python3',str(B/'verify-protected.py')]]
for cmd in commands:
 p=subprocess.run(cmd,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
 assert p.returncode==0,(cmd,p.stdout.decode()[-1000:],p.stderr.decode()[-2000:])
required=['README.md','B12_OWNER_COMMISSIONING_RETROSPECTIVE.md','ENGINEERING_REPORT.md','MECHANICS_REPORT.md','SCIENTIFIC_BASELINE_AND_PROVENANCE.md','HORIZON_PROBE_PROTOCOL.md','TIME_STEP_AND_CONVERGENCE_ANALYSIS.md','PROPERTY_EVALUATION_PROFILE.md','JACOBIAN_AND_TRBDF2_PROFILE.md','PHYSICAL_DOMAIN_AND_PHASE_ANALYSIS.md','CONSERVATION_AND_ROLLBACK.md','SOLVER_PERFORMANCE_RESULTS.md','LONG_HORIZON_FEASIBILITY.md','QUALIFICATION_GAPS.md','NEXT_SOLVER_MILESTONE_PROPOSAL.md']
assert all((B/p).is_file() for p in required)
a=json.loads((E/'analysis.json').read_text());assert a['maxActualHorizonSeconds']==.01
for f,r in a['results'].items():
 assert r['stop'] is None and r['seconds']==.01
 assert r['jacobianBuilds']==r['linearSolves']==r['corrections']
 assert r['observed']['profile']['calls']['stage']==6*r['attempts']
 assert r['derivativeOutcomes']=={'used':21*r['corrections']}
 assert len(r['propertyRangesByInterval'])==7 and len(r['observed']['profileIntervals'])==6
 assert r['growthHistory']['nonlinearFailures']==0
 for key,v in r['conservation'].items():assert v<(1e-8 if 'Mass' in key or 'mass' in key else 1e-6)
 for x in r['intervals']:assert x['actual']==x['requested'] and x['end']<=.01
p=json.loads((E/'baseline-parity.json').read_text());assert p['retainedCanonicalScienceAndAttemptHashesIndependentlyRecomputed'];assert all(c['acceptedA2SameEngineBitExact'] and c['canonicalObservedScienceBitExact'] and c['canonicalObservedAttemptsBitExact'] for c in p['checks'])
budget=json.loads((E/'budget-termination-warm-010.jsonl.exit.json').read_text());assert budget['terminationKind']=='cpu-budget-signal' and not budget['complete'];assert budget['lastObservedAcceptedSeconds']>budget['lastCheckpointSeconds']
status=json.loads((B/'milestone-status.json').read_text());assert status['decision']=='B13-A0 DIAGNOSTIC CHARACTERIZATION PASS' and not status['deployment'] and not status['productionMerge']
result=dict(passed=True,sourcePreservation=True,protectedRefsAndPR3=True,baselineSameEngineBitExact=True,canonicalAndObservedThrough001Exact=True,canonicalReceiptHashesIndependentlyRecomputed=True,normalHorizonSeconds=.01,normalHorizonQualified=False,conservation=True,domainRefusalAndEarlierProgressPreserved=True,externalCPUBudgetTermination=True,requiredReports=len(required),noDeployment=True)
(E/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
