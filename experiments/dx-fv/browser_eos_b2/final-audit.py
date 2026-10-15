"""Integrity audit, explicitly separate from failed backend qualification."""
import os,json,hashlib,subprocess,struct
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checkpoint=json.loads((B/'evidence/checkpoint.json').read_text())
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='research/browser-eos-b2-qualification-20261015'
assert all(sha(R/name)==digest for name,digest in checkpoint['files'].items())
changed=subprocess.check_output(['git','diff','--name-only',checkpoint['startingCommit']],cwd=R,text=True).splitlines()
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
assert all(name.startswith('experiments/dx-fv/browser_eos_b2/') for name in changed+untracked)
for name in ['coupled-test.cjs','coupled-controls.cjs','coupled-domain-test.cjs','coupled-browser.cjs','roadmap-a1.cjs','roadmap-a2.cjs','audit_coupled_results.py','audit_roadmap_a2.py']:
 assert (B/name).read_bytes()==subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:experiments/dx-fv/'+name],cwd=R)
for name,digest in checkpoint['acceptedSource']['sha256'].items():assert sha(B.parent/'browser_eos_backend/accepted'/name)==digest
for name in ['engine.js','properties.json']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show',f'be9eb35a4ddf5098e685182f8104685127c6a6ee:{name}'],cwd=R)
environment=json.loads((E/'environment.json').read_text())
for name,entry in environment['sourceSnapshots'].items():
 assert sha(B/name)==entry['sha256']
phase=json.loads((E/'phase-summary.json').read_text());assert all(phase['engineEquality'].values()) and all(phase['controlEqualsOfficial'].values())
assert len(phase['builds'])==8 and all(len(r['errors'])==0 and r['rows']==236 for r in phase['builds'])
inputs=json.loads((B/'inputs.json').read_text());transported=0
for browser in ['chromium','webkit']:
 for build in ['official8','build30','build44','official72']:
  rows=json.loads((E/f'{browser}-phase-{build}.json').read_text())['rows']
  assert len(rows)==len(inputs)==236
  for q,expected in zip(rows,inputs):
   assert q['id']==expected['id'] and q['args']==expected['args'] and q['inputBits']==expected['inputBits']
   assert [struct.pack('>d',x).hex() for x in q['args']]==q['inputBits']
   for s in [q['base']]+[p['output'] for p in q['probes']]:
    assert [struct.pack('>d',s[k]).hex() for k in ['p','h']]==s['inputBits'];transported+=1
boundary=[]
for browser in ['chromium','webkit']:
 d=json.loads((E/f'{browser}-boundary-build44.json').read_text());assert len(d['rows'])==8
 assert sum(r['canonicalCompatibilityPass'] for r in d['rows'])==1
 assert all(r['exactSIInputs']==r['adapterRoundTripSI'] for r in d['rows'])
 boundary.append({'browser':browser,'pass':1,'fail':7})
roots=json.loads((E/'boundary-native-roots.json').read_text());assert all(r['referencePass'] for r in roots['rows'])
for r in roots['rows']:assert all(r['referenceHomogeneousDerivatives'][k]>0 for k in ['cp','cv','kappa'])
science=json.loads((E/'independent-scientific-audit.json').read_text())
assert all(r['conservationPass'] for r in science['operating'])
assert all(not r['rollbackFailures'] and r['maxAcceptedTemporalError']<=1 for r in science['historyAudits'])
assert all(r['status']=='PASS' for r in science['contractConservation'])
suite=json.loads((E/'suite-summary.json').read_text())
assert len(suite['coreAssertionGroups'])==36 and all(r['status']=='PASS' for r in suite['coreAssertionGroups'])
assert len(suite['domainWithIsolatedPTMapping'])==6 and all(r['status']=='PASS' and r['cases']==36 for r in suite['domainWithIsolatedPTMapping'])
correction=json.loads((E/'phase-classification-correction.json').read_text())
assert len(correction['comparisons'])==8 and all(r['physicalOutputSnapshotsExactlyUnchanged'] and r['newPhase2DerivativeSnapshots']==80 for r in correction['comparisons'])
catalog=json.loads((E/'catalog-integrity.json').read_text())
assert catalog['passed'] and len(catalog['sourceSHA256'])==77 and len(catalog['blocks'])==19
terminal=json.loads((E/'independent-terminal-audit.json').read_text())
assert len(terminal['rows'])==30 and all('error' not in r for r in terminal['rows'])
performance=json.loads((E/'performance-summary.json').read_text())
assert len(performance['standalone'])==4 and len(performance['coupled'])==4
assert all(r['workerOK'] and all(g['failures']==0 for g in r['groups'].values()) for r in performance['standalone'])
assert all(not r['error'] and not r['failedRows'] and not r['missingCases'] and all(c['allTargetsReached'] and c['repeatedWorkExactlyMatches'] for c in r['cases'].values()) for r in performance['coupled'])
report={'integrityPass':True,'qualification':'BLOCKED','backendScientificPass':False,'protectedB1Files':len(checkpoint['files']),'onlyB2Additions':True,'acceptedDependencySnapshots':12,'acceptedSuiteSourceCopies':8,'source30MatchesOfficial8':True,'browserPhaseMatricesExactlyEqual':True,'canonicalRegression':boundary,'independentStableLiquidRoots':len(roots['rows']),'completedOperatingAudits':len(science['operating']),'historyAudits':len(science['historyAudits']),'physicalIPadTested':False}
report.update(rootGuardAndTableMatchAccepted=True,selectedCoreGroupsPassed=36,domainCasesPassedWithExplicitPTMapping=216,contractHistoryConservationAudits=len(science['contractConservation']),rollbackChecks=sum(r['rollbackChecks'] for r in science['historyAudits']),unexecutedSuitePaths=[r['name'] for r in suite['otherAcceptedInventory'] if r['status'].startswith('NOT RUN')])
report.update(allRequiredScientificSuiteComplete=False,exactBinary64PhaseInputsVerified=transported,catalogSourceDataStringsVerified=77,independentTerminalStates=30,matchedPropertyMeasurements=4,matchedCoupledMeasurements=4,offlineOutcomes={name:[dict(browser=r['browser'],completed=sum(b['ok'] for b in r['builds']),attempted=len(r['builds']),errors=[b['error'] for b in r['builds'] if not b['ok']]) for r in rows] for name,rows in performance['offline'].items()})
(E/'final-integrity-audit.json').write_text(json.dumps(report,indent=2)+'\n')
manifest={str(p.relative_to(B)):sha(p) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence-hashes.json'}
(E/'evidence-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(report,indent=2))
