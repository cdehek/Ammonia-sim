"""Read-only Git/worktree/ref audit. --write adds a B9B receipt only."""
import hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';START='355db28d853817e1931295d6ec2f007876d53f90';BRANCH='research/browser-eos-b9b-solver-property-profiling-20261017'
def git(*a):return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
files=json.loads((E/'starting-files-sha256.json').read_text())
assert git('branch','--show-current')==BRANCH
assert git('merge-base',START,'HEAD')==START
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in files.items())
changes=git('diff',START,'--name-status').splitlines()
assert all(line.startswith('A\texperiments/dx-fv/browser_eos_b9b/') for line in changes)
for line in git('status','--porcelain=v1','--untracked-files=all').splitlines():assert 'experiments/dx-fv/browser_eos_b9b/' in line
remote=None;pr=None;prMetadataChanges=[]
remotePath=E/('remote-postpush.tsv' if (E/'remote-postpush.tsv').exists() else 'remote-final.tsv')
if remotePath.exists():
 before={l.split()[1]:l.split()[0] for l in (E/'remote-before.tsv').read_text().splitlines()};after={l.split()[1]:l.split()[0] for l in remotePath.read_text().splitlines()}
 assert all(after.get(k)==v for k,v in before.items())
 assert set(after)-set(before)<={'refs/heads/'+BRANCH}
 remote=dict(protectedUnchanged=True,protectedRefCount=len(before),tags=sum(k.startswith('refs/tags/') for k in before),onlyAllowedAddedRef=True,ownRemoteHead=after.get('refs/heads/'+BRANCH))
prPath=E/('pr3-postpush.json' if (E/'pr3-postpush.json').exists() else 'pr3-final.json')
if prPath.exists():
 before=json.loads((E/'pr3-before.json').read_text());after=json.loads(prPath.read_text())
 # GitHub embeds repository-global pushed_at in each PR's head/base repo.
 # An authorized research-branch push changes these, without changing the PR.
 # Normalize ONLY these two fields; assert every other API field unchanged.
 for side in ['head','base']:
  a=before[side]['repo'].pop('pushed_at');b=after[side]['repo'].pop('pushed_at')
  if a!=b:prMetadataChanges.append(dict(path=side+'.repo.pushed_at',before=a,after=b,meaning='Repository-global research push timestamp; not PR identity'))
 assert before==after;pr=True
receipt=dict(passed=True,start=START,head=git('rev-parse','HEAD'),branch=BRANCH,exactStartingAncestry=True,historicalTrackedFiles=len(files),historicalByteMismatches=[],onlyAdditiveB9B=True,acceptedA2Unchanged=True,B9B9AC1B6B7UIProductionUnchanged=True,protectedRemoteRefs=remote,PR3Unchanged=pr,PR3NonIdentityRepoMetadataChanges=prMetadataChanges,cleanAtObservation=not bool(git('status','--porcelain=v1')),noNumericalSolverOrEOSOrAcceptanceModification=True,noProductionIntegration=True,noMergeOrDeployment=True)
if '--write' in sys.argv:(E/'preservation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
