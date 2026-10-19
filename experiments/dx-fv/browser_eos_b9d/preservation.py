"""Read-only preservation assertions, B9D-only receipts; remote snapshot supplied externally."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';START='b67afb3215075b2ec82bef376d39e03953dc0da2'
def git(*a):return subprocess.check_output(['git',*a],cwd=R).decode().strip()
def refs(path):return {line.split()[1]:line.split()[0] for line in path.read_text().splitlines()}
before=json.loads((E/'starting-files-sha256.json').read_text())
assert all(hashlib.sha256((R/n).read_bytes()).hexdigest()==v for n,v in before.items())
assert git('merge-base','HEAD',START)==START
prefix='experiments/dx-fv/browser_eos_b9d/'
for line in git('diff','--name-status',START).splitlines():
 kind,name=line.split('\t');assert kind=='A' and name.startswith(prefix),(kind,name)
for name in git('ls-files','--others','--exclude-standard').splitlines():assert name.startswith(prefix),name
original=refs(E/'remote-refs-before.txt');now=refs(E/'remote-refs-final.txt')
assert all(now.get(k)==v for k,v in original.items()),'Protected remote ref changed'
allowed='refs/heads/research/browser-eos-b9d-hardening-hookup-readiness-20261018'
assert set(now)-set(original)<={allowed}
localBefore={line.split()[0]:line.split()[1] for line in (E/'local-refs-before.txt').read_text().splitlines()}
localNow={line.split()[0]:line.split()[1] for line in git('for-each-ref','--format=%(refname) %(objectname)').splitlines()}
assert all(localNow.get(k)==v for k,v in localBefore.items() if k!=allowed),'Protected local ref changed'
prior=json.loads((E/'pr3-before.json').read_text());current=json.loads((E/'pr3-final.json').read_text())
keys=['url','number','title','body','state','merged','draft','base','base_sha','head','head_sha','head_repo_full_name','merge_commit_sha','updated_at','closed_at','merged_at']
assert all(current[k]==prior[k] for k in keys),'PR #3 changed'
assert git('rev-parse','origin/feature/operator-workstation-bottom-panel-20261014')=='262b6092b2ed694073ad9ffd41265f44dd0b6ca0'
checks={'passed':True,'historicalFilesByteExact':len(before),'exactB9CAncestry':True,'onlyB9DAdditions':True,'protectedRemoteRefsUnchanged':len(original),'protectedLocalRefsUnchanged':len(localBefore)-1,'newRefsAllowed':[allowed],'PR3IdentityStatusTitleBodyUnchanged':True,'acceptedA2Unchanged':True,'originalB9CUnchanged':True,'operatorWorkstationUnchanged':True,'demoCandidateUnchanged':True,'productionMainUnchanged':True,'C1B6B7Unchanged':True,'EOSRepair':False,'newPropertyAcceptance':False,'merge':False,'deployment':False,'currentCommitAtAudit':git('rev-parse','HEAD')}
(E/'preservation-final.json').write_text(json.dumps(checks,indent=2)+'\n')
print('Preservation PASS:',len(before),'historical files;',len(original),'protected refs; PR #3 unchanged')
