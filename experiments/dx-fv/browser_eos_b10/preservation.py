"""Final B10-only scope, historical hashes, protected refs and PR identity."""
import hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';START='20ddac46423a7a742af19ac415ef8796cf3a429f';BRANCH='research/b10-operator-workstation-shadow-hookup-20261018';PREFIX='experiments/dx-fv/browser_eos_b10/'
def git(*args):return subprocess.check_output(['git',*args],cwd=R).decode().strip()
def remote(p):return {line.split()[1]:line.split()[0] for line in p.read_text().splitlines()}
assert git('branch','--show-current')==BRANCH
before=json.loads((E/'starting-files-sha256.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==v for p,v in before.items())
assert git('merge-base','HEAD',START)==START
for line in git('diff','--name-status',START).splitlines():
 kind,name=line.split('\t');assert kind=='A' and name.startswith(PREFIX),(kind,name)
for name in git('ls-files','--others','--exclude-standard').splitlines():assert name.startswith(PREFIX),name
refs0=remote(E/'remote-refs-before.txt');refs1=remote(E/'remote-refs-final.txt');assert all(refs1.get(k)==v for k,v in refs0.items())
assert set(refs1)-set(refs0)<={'refs/heads/'+BRANCH}
local0={line.split()[0]:line.split()[1] for line in (E/'local-refs-before.txt').read_text().splitlines()};local1={line.split()[0]:line.split()[1] for line in git('for-each-ref','--format=%(refname) %(objectname)').splitlines()}
assert all(local1.get(k)==v for k,v in local0.items() if k!='refs/heads/'+BRANCH)
assert set(local1)-set(local0)<={'refs/remotes/origin/'+BRANCH}
p0=json.loads((E/'pr3-before.json').read_text());p1=json.loads((E/'pr3-final.json').read_text())
keys=['url','number','title','body','state','merged','draft','base','base_sha','head','head_sha','head_repo_full_name','merge_commit_sha','updated_at','closed_at','merged_at'];assert all(p0[k]==p1[k] for k in keys)
out={'passed':True,'historicalFilesExact':len(before),'protectedRemoteRefsExact':len(refs0),'protectedLocalRefsExact':len(local0)-1,'PR3IdentityBodyStatusExact':True,'onlyB10Additions':True,'exactB9DAncestry':True,'auditedCommit':git('rev-parse','HEAD'),'branch':BRANCH,'merge':False,'deployment':False,'scientificModification':False,'newScientificBackend':False,'physicalPlantConnection':False}
if '--check-only' not in sys.argv:(E/'preservation-final.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
