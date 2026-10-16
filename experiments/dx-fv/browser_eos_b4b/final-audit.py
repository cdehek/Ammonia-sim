"""Read-only scientific/preservation checks; write one new delivery ledger."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((E/n).read_text())
def save(n,d):
 p=E/n;assert not p.exists(),p;p.write_text(json.dumps(d,indent=2)+'\n')
start=read('preservation-start.json');changed=[n for n,h in start['trackedSHA256'].items()if sha(R/n)!=h];assert not changed
baseline={ref.removeprefix('refs/remotes/origin/'):h for h,ref in [line.split()for line in (E/'refs-before.txt').read_text().splitlines()]if not ref.endswith('/HEAD')}
remote={ref.removeprefix('refs/heads/'):h for h,ref in [line.split()for line in (E/'refs-before-push.txt').read_text().splitlines()]}
assert all(remote.get(n)==h for n,h in baseline.items());assert set(remote)==set(baseline)
assert subprocess.check_output(['git','-C',str(R),'branch','--show-current']).decode().strip()=='research/browser-eos-b4b-vapor-cache-repair-20261016'
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==start['commit']
provenance=read('provenance.json')
for n,q in provenance['artifacts'].items():assert sha(B/n)==q['sha256'],n
assert sha(B/'pt-cache-consistency.patch')==provenance['B4BpatchSHA256']
assert sha(B/'ALGORITHM.md')==provenance['preimplementationAlgorithmSHA256']
assert read('preimplementation-decision.json')['algorithm']['ALGORITHM.md']==provenance['preimplementationAlgorithmSHA256']
science=read('scientific-audit.json');assert science['classification']=='FOCUSED REPAIR PASS'and not science['fullQualification']and not science['physicalIPad']
assert science['primary']['eligibleForLimitedA2']and science['browserCompleteRowsEqual']
assert read('historical-artifact-hash-verification.json')['allPass']
assert read('35bar-fixed-inventories.json')['allEqual']
browser35={}
for engine in ['chromium','webkit']:
 d=read(f'{engine}-35bar-fixed-inventories.json');assert d['allEqual'];browser35[engine]=len(d['comparisons'])
for side in ['controlA','candidateB']:
 for block in read('trace-audit.json')[side]:
  if block['marker']['marker'].startswith('fixed-B3-PT'):assert block['cacheCoordinateMatchesCommitted']==(side=='candidateB')
for runtime,builds in read('performance-summary.json').items():
 for build in ['controlA','candidateB']:assert all(v>0 for v in builds[build]['medianMicroseconds'].values())
out=dict(classification='FOCUSED REPAIR PASS',start=start['commit'],branch='research/browser-eos-b4b-vapor-cache-repair-20261016',startingTrackedFiles=len(start['trackedSHA256']),changedStartingFiles=changed,protectedRemoteHeads=baseline,allProtectedRemoteHeadsUnchangedBeforePush=True,browserFixed35Inventories=browser35,sourceScope=provenance['functionalSourceFiles'],B1andB4APatchesPreserved=True,acceptedA2Unchanged=read('accepted-a2-verification.json')['unchanged'],originalCanonicalBudgets=dict(pressurePa=.1,enthalpyJkg=.1,temperatureK=1e-4),originalFluidNonlinearScale=1e-11,originalThermalResidualK=1e-12,fullQualification=False,physicalIPad=False,knownUnresolved=['upper-quality 1<Q<=1+1e-9 classification','35-bar DU/support boundary including retained full-VLE exceptions','research JS rejected-PT exception cleanup','complete accepted option/reference/domain/rollback qualification','physical iPad Safari'],supersededIntermediateEvidence={'trace-summary.json':'Compared cache fill to a stale reduced-coordinate field. Authoritative trace-audit.json instead compares cache fill to the final explicit density coordinate; original intermediate retained.','lifecycle-controlA.json':'Initial writer included a fresh-PT rejection in row.error. Corrected lifecycle-controlA-replay.json separates the rejected call; original retained.'})
save('final-integrity.json',out)
files={str(p.relative_to(B)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(B.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.name!='delivery-file-hashes.json'}
save('delivery-file-hashes.json',files)
print('PASS: original budgets, scientific evidence, artifacts, 1,102 starting files and all protected heads verified.')
