"""Final scientific and preservation audit; leaves protected refs untouched."""
import hashlib,json,os,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'))
def read(n):return json.loads((E/n).read_text())
start=read('preservation-start.json');changed=[n for n,h in start['trackedSHA256'].items() if hashlib.sha256((R/n).read_bytes()).hexdigest()!=h];assert not changed
branch=subprocess.check_output(['git','branch','--show-current'],cwd=R).decode().strip();assert branch=='research/browser-eos-b4c-upper-quality-repair-20261016'
assert read('focused-gate.json')['eligibleForLimitedA2'] and read('boundary-gate.json')['eligibleForLimitedA2']
assert read('A2-audit.json')['passOriginalLimitedScientificRequirements'] and read('default-equilibrium-audit.json')['passOriginalRequirements']
assert read('upper-quality-native-before-after.json')['allCandidateCanonicalPass']
for engine in ['chromium','webkit']:
 assert read(engine+'-upper-quality-inventories.json')['allCandidateCanonicalPass']
 # Exact original signed input bits, independent of any returned phase label.
 a=read(engine+'-controlA-focused.json')['rows'];b=read(engine+'-candidateB-focused.json')['rows']
 for x,y in zip(a,b):
  assert x['id']==y['id'] and x['args']==y['args'] and x['base']['inputBits']==y['base']['inputBits']
  assert [(q['axis'],q['step'],q['output']['inputBits']) for q in x['probes']]==[(q['axis'],q['step'],q['output']['inputBits']) for q in y['probes']]
assert read('trace-audit.json')['loggingOnOffAndUninstrumentedEqual']
assert read('35bar-fixed-inventories.json')['allEqual']
assert read('provenance.json')['loaderExceptionHandlingUnchanged']
def refs(p):return {line.split()[1]:line.split()[0] for line in p.read_text().splitlines()}
before=refs(E/'refs-before.txt');after=refs(E/'refs-before-push.txt');assert all(after.get(n)==h for n,h in before.items())
out=dict(classification='FOCUSED REPAIR PASS',branch=branch,start=start['commit'],startingTrackedFiles=len(start['trackedSHA256']),changedStartingFiles=changed,allOriginalInputAndSignedProbeBitsPreserved=True,protectedHeadsUnchanged=True,protectedHeads=before,patchSHA256=read('provenance.json')['patchSHA256'],allFocusedScientificGatesPass=True,reportedRejectedAuditorAttempt='boundary-gate-attempt1.json; homogeneous DU Q=10000 sentinel misinterpreted by first auditor',reportedDiscardedTiming='performance-native-*-contended-do-not-use.json',retainedOutsideScopeFailures=dict(fullVLE35bar=read('boundary-gate.json')['fullVLE']['candidateB']['canonicalFailures'],rejectedPTLoaderUnchanged=True,physicalIPadUntested=True,fullA2QualificationPending=True),productionUIAcceptedResearchUntouched=True,deployment=False,engineeringApprovalRequiredBeforeNextMilestone=True)
p=E/'final-integrity.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Final audit passes:',len(start['trackedSHA256']),'historical files unchanged; all focused gates pass; protected heads unchanged')
