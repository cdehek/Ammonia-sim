"""B10 read-only provenance audit; run before functional implementation."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
START='20ddac46423a7a742af19ac415ef8796cf3a429f'
OP='262b6092b2ed694073ad9ffd41265f44dd0b6ca0'
A2='be9eb35a4ddf5098e685182f8104685127c6a6ee'
B9C='b67afb3215075b2ec82bef376d39e03953dc0da2'
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def sha(v):return hashlib.sha256(v).hexdigest()
def save(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
assert git('rev-parse','HEAD').decode().strip()==START
assert git('branch','--show-current').decode().strip()=='research/b10-operator-workstation-shadow-hookup-20261018'
assert not git('diff','--name-only',START)
files=git('ls-tree','-r','--name-only',START).decode().splitlines()
hashes={p:sha((R/p).read_bytes()) for p in files}
assert all(sha(git('show',START+':'+p))==v for p,v in hashes.items())
save('starting-files-sha256.json',hashes)
accepted=json.loads((B.parent/'browser_eos_b9d/evidence/accepted-source-manifest.json').read_text())
for p,v in accepted.items():assert (R/v['snapshot']).read_bytes()==git('show',A2+':'+p)
save('accepted-source-manifest.json',accepted)
checks={}
prior=json.loads((B.parent/'browser_eos_b9c/evidence/gate0.json').read_text())
for folder,v in prior['sourceChecks'].items():
 names=git('ls-tree','-r','--name-only',v['commit'],'--','experiments/dx-fv/'+folder+'/').decode().splitlines()
 assert all((R/n).read_bytes()==git('show',v['commit']+':'+n) for n in names)
 checks[folder]={'commit':v['commit'],'files':len(names),'exact':True}
for folder,commit in [('browser_eos_b9c',B9C),('browser_eos_b9d',START)]:
 names=git('ls-tree','-r','--name-only',commit,'--','experiments/dx-fv/'+folder+'/').decode().splitlines()
 assert all((R/n).read_bytes()==git('show',commit+':'+n) for n in names)
 checks[folder]={'commit':commit,'files':len(names),'exact':True}
assert git('rev-parse','origin/feature/operator-workstation-bottom-panel-20261014').decode().strip()==OP
assert git('rev-parse','origin/research/browser-eos-b9d-hardening-hookup-readiness-20261018').decode().strip()==START
opfiles=git('ls-tree','-r','--name-only',OP).decode().splitlines()
save('operator-source-manifest.json',{p:{'sha256':sha(git('show',OP+':'+p)),'gitBlob':git('rev-parse',OP+':'+p).decode().strip()} for p in opfiles})
(E/'local-refs-before.txt').write_bytes(git('for-each-ref','--format=%(refname) %(objectname)'))
save('gate0.json',{'passed':True,'start':START,'cleanStartingTrackedTree':True,'historicalFiles':len(files),'acceptedClosureFiles':len(accepted),'sourceChecks':checks,'operatorCommit':OP,'operatorFiles':len(opfiles),'tags':git('tag').decode().splitlines(),'scope':'baseline build/browser receipts follow architecture, before functional implementation'})
print('Gate 0 source PASS',len(files),'historical files;',len(opfiles),'operator files')
