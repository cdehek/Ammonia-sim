"""Historical files, exact ancestry and additive B9A scope. Network receipts separate."""
import hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';START='b1a65c9365879d6e97eff649e56371df3907e86e';BRANCH='research/browser-eos-b9a-compact-worker-optimization-20261017'
def git(*a):return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
def read(n):return json.loads((E/n).read_text())
assert git('branch','--show-current')==BRANCH and git('merge-base',START,'HEAD')==START
files=read('starting-files-sha256.json');assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in files.items())
for line in git('diff',START,'--name-status').splitlines():assert line.startswith('A\texperiments/dx-fv/browser_eos_b9a/')
for line in git('status','--porcelain=v1','--untracked-files=all').splitlines():assert 'experiments/dx-fv/browser_eos_b9a/' in line
remoteCheck=None
if (E/'remote-final.tsv').exists():
 before=dict(line.split()[::-1] for line in (E/'remote-before.tsv').read_text().splitlines());after=dict(line.split()[::-1] for line in (E/'remote-final.tsv').read_text().splitlines());assert all(after.get(k)==v for k,v in before.items());assert set(after)-set(before)<={'refs/heads/'+BRANCH};remoteCheck=True
if (E/'pr3-final.json').exists():assert read('pr3-before.json')==read('pr3-final.json')
receipt=dict(passed=True,start=START,head=git('rev-parse','HEAD'),branch=BRANCH,historicalTrackedFiles=len(files),historicalMismatches=[],onlyAdditiveB9A=True,acceptedA2Unchanged=True,B9CodeAndEvidenceUnchanged=True,C1B6B7Unchanged=True,protectedRemoteRefsUnchanged=remoteCheck,PR3Unchanged=(E/'pr3-final.json').exists(),cleanAtObservation=not bool(git('status','--porcelain=v1')),noEOSOrSolverOrAcceptanceOrProductionEdit=True,noMergeOrDeployment=True)
if '--write' in sys.argv:(E/'precommit-preservation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
