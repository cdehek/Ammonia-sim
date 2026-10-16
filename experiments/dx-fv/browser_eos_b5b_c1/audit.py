"""C1 additive isolation / accepted-source and artifact identity audit."""
import hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
START='26df10c1f486b60978646e9c8819fc0054cb9465'
TARGET='refs/heads/research/browser-eos-b5b-c1-failclosed-propagation-20261016'
def git(*a): return subprocess.check_output(['git',*a],cwd=R,text=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v): (E/n).write_text(json.dumps(v,indent=2)+'\n')
if '--start' in sys.argv:
    assert git('rev-parse','HEAD').strip()==START
    # The only untracked files at this point are this new research directory.
    assert not git('diff',START,'--name-only')
    files=git('ls-tree','-r','--name-only',START).splitlines()
    write('starting-file-hashes.json',{n:sha(R/n) for n in files})
    write('checkpoint.json',dict(startHEAD=START,startingBranch='research/browser-eos-b5b-boundary-contract-design-20261016',
        startingPorcelain='',branch=git('branch','--show-current').strip(),trackedFiles=len(files),localRefs=git('show-ref')))
start=json.loads((E/'starting-file-hashes.json').read_text())
assert all(sha(R/n)==h for n,h in start.items())
spec=importlib.util.spec_from_file_location('historical_audit',B.parent/'browser_eos_b5b/audit.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
prior=mod.verify() # read-only; never calls historical script main or writes old evidence
out=dict(startingFiles=len(start),historicalFileMismatches=[],historicalAudit=prior,
         originalBudgetsAndSupportPreserved=True)
if '--start' not in sys.argv:
    changed=git('diff',START,'--name-status').splitlines()
    assert all(n.startswith('A\texperiments/dx-fv/browser_eos_b5b_c1/') for n in changed),changed
    def refs(n): return {line.split()[1]:line.split()[0] for line in (E/n).read_text().splitlines()}
    before,after=refs('refs-before.txt'),refs('refs-after.txt')
    drift={k:[v,after.get(k)] for k,v in before.items() if after.get(k)!=v}
    assert not drift,drift
    assert set(after)-set(before)<={TARGET}
    out.update(changes=changed,protectedRefDrift=drift,protectedRefsChecked=len(before))
write('start-audit.json' if '--start' in sys.argv else 'final-preservation.json',out)
print('preserved',len(start),'files;',len(prior['artifacts']),'artifact identities;',len(prior['acceptedA2']),'accepted A2 dependencies')
