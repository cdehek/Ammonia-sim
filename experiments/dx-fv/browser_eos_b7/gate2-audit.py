"""Final independent focused acceptance, retaining every broader blocker."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';read=lambda n:json.loads((E/n).read_text())
assert read('gate1-audit.json')['gate1']=='PASS'
requirements={
 'threeResolvedLiquidsAndFourUnresolved':'seven-science-audit.json',
 'original250RecordsBothPaths':'ledger-science-audit.json',
 'inheritedPropertiesAndB6LifecycleAndC1':'regression-audit.json',
 'workerParityAndRefusals':'worker-audit.json',
 'separate21AndFullVLESignedRegressions':'additional-audit.json',
 'separate21IndependentReferenceComparisons':'additional-independent-audit.json',
 'focusedC1A2Compatibility':'a2-audit.json',
}
checks={}
for name,filename in requirements.items():
 p=E/filename;d=read(filename);assert d['passed'],filename;checks[name]=dict(file=filename,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),passed=True)
for engine in ['chromium','webkit']:
 d=read(f'selection-{engine}.json');assert 'harnessError' not in d and d['result']['passed']
 assert len(read(f'performance-{engine}.json')['result']['rows'])==180
assert read('inherited-focused-audit.json')['passOriginalFocusedRequirements']
source=read('source-candidate.json')['trackedSourceSHA256'];S=Path('/workspace/b7-work/upstream')
assert all(hashlib.sha256((S/n).read_bytes()).hexdigest()==h for n,h in source.items())
assert len(read('support-attribution.json')['rows'])==14
blockers=[
 '148: unresolved historical QT refusal',
 '162: numerical homogeneous liquid return; independent physical phase unresolved',
 '164: unresolved historical QT refusal',
 '165: unresolved historical QT refusal',
 'Seven original default browser 35-bar refusals remain; no exact-boundary acceptance qualification',
 'Two inward false-acceptance hazards and inherited full-VLE boundary returns remain unqualified',
 'P1 stable-equilibrium/topology/convex-envelope dependency remains unproved',
 'Full EOS/backend and full accepted A2 qualification remain incomplete',
 'Physical Safari/iPadOS, broader fluids, critical/mixture regions and long-duration behavior untested',
 'Substantial observed main-thread initialization/sampling gaps require separate responsiveness engineering',
]
out=dict(assessment='FOCUSED BROWSER GATE A PASS',gate1='PASS',gate2='PASS',checks=checks,threeResolvedLiquids=[146,151,152],fourUnresolvedEndpoints=[148,162,164,165],remainingQualificationBlockers=blockers,scope='Limited experimental qualification of the accepted compiled Gate A algorithm through an isolated full-VLE runtime harness in Chromium and desktop WebKit. Historical general browser default path remains superancillary; no full backend, Gate B, complete A2, physical device or production qualification.',stopForEngineeringReview=True)
p=E/'acceptance.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(out['assessment'],'— Gate 1 PASS; Gate 2 PASS; broader blockers retained')
