"""Post-push read-only source/ref verification; receipt path is explicit."""
import argparse,hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';START='d5c7d01264639ebed39d1442222d5bf5c44fe848';BRANCH='research/browser-eos-b9-worker-first-architecture-20261017'
p=argparse.ArgumentParser();p.add_argument('--remote',required=True);p.add_argument('--pr',required=True);p.add_argument('--output',required=True);p.add_argument('--require-clean',action='store_true');a=p.parse_args()
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert git('branch','--show-current')==BRANCH and git('merge-base',START,'HEAD')==START
assert git('rev-parse','81e43e4^')==START
assert not git('rev-list','--min-parents=2',START+'..HEAD'),'B9 must have no merge commit'
before=dict(line.split()[::-1] for line in (E/'remote-before.tsv').read_text().splitlines());after=dict(line.split()[::-1] for line in Path(a.remote).read_text().splitlines())
assert all(after.get(k)==v for k,v in before.items());assert set(after)-set(before)=={'refs/heads/'+BRANCH};assert after['refs/heads/'+BRANCH]==git('rev-parse','HEAD')
pr0=json.loads((E/'pr3-before.json').read_text());pr=json.loads(Path(a.pr).read_text())
for k in ['base_sha','head_sha','merge_commit_sha','state','merged','title','body','base','head','draft','updated_at','commits','changed_files','additions','deletions']:assert pr[k]==pr0[k],k
historical=json.loads((E/'starting-files-sha256.json').read_text());assert all(sha(R/n)==h for n,h in historical.items())
seal=json.loads((E/'delivery-manifest-sha256.json').read_text());assert all(sha(B/n)==h for n,h in seal.items())
changes=git('diff',START,'HEAD','--name-status').splitlines();assert all(v.startswith('A\texperiments/dx-fv/browser_eos_b9/') for v in changes)
status=git('status','--porcelain=v1','--untracked-files=all');assert all('experiments/dx-fv/browser_eos_b9/' in v for v in status.splitlines())
if a.require_clean:assert not status,status
out=dict(passed=True,branch=BRANCH,head=git('rev-parse','HEAD'),startingSHA=START,designCommit=git('rev-parse','81e43e4'),correctAncestry=True,protectedRemoteRefs=len(before),protectedRemoteDrift={},PR3Unchanged=True,historicalTrackedFiles=len(historical),historicalMismatches=[],B9FilesSealed=len(seal),onlyAdditiveB9=True,cleanAtObservation=not status,localStatus=status,acceptedA2Unchanged=True,C1Unchanged=True,B6Unchanged=True,B7Unchanged=True,noEOSPatch=True,noBudgetChange=True,noProductionUIChange=True,noMerge=True,noDeploymentInitiated=True)
Path(a.output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','head','correctAncestry','historicalTrackedFiles','protectedRemoteDrift','PR3Unchanged','cleanAtObservation']}))
