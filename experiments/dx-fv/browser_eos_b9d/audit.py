"""B9D provenance; never writes historical files."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
START='b67afb3215075b2ec82bef376d39e03953dc0da2'; A2='be9eb35a4ddf5098e685182f8104685127c6a6ee'
def git(*a): return subprocess.check_output(['git',*a],cwd=R)
def sha(b): return hashlib.sha256(b).hexdigest()
def save(n,v): (E/n).write_text(json.dumps(v,indent=2)+'\n')
assert git('rev-parse','HEAD').decode().strip()==START
assert not git('diff',START,'--name-only')
files=git('ls-tree','-r','--name-only',START).decode().splitlines()
manifest={n:sha((R/n).read_bytes()) for n in files}
assert all((R/n).read_bytes()==git('show',START+':'+n) for n in files)
save('starting-files-sha256.json',manifest)
accepted=json.loads((B.parent/'browser_eos_b9c/evidence/accepted-source-manifest.json').read_text())
for path,v in accepted.items(): assert (R/v['snapshot']).read_bytes()==git('show',A2+':'+path)
save('accepted-source-manifest.json',accepted)
proto=json.loads((B.parent/'browser_eos_b9c/evidence/prototype-source-manifest.json').read_text())
for variant,v in proto.items(): assert sha((B.parent/'browser_eos_b9c'/(variant+'-bundle.mjs')).read_bytes())==v['bundleSHA256']
save('optimized-source-manifest.json',{'pinnedCommit':START,'bundles':proto,'wrapperSHA256':sha((B.parent/'browser_eos_b9c/table-only.cjs').read_bytes()),'patchSHA256':sha((B.parent/'browser_eos_b9c/BOUNDARY_PH_PROTOTYPE.patch').read_bytes())})
checks={}
prior=json.loads((B.parent/'browser_eos_b9c/evidence/gate0.json').read_text())
for folder,v in prior['sourceChecks'].items():
 names=git('ls-tree','-r','--name-only',v['commit'],'--','experiments/dx-fv/'+folder+'/').decode().splitlines()
 assert all((R/n).read_bytes()==git('show',v['commit']+':'+n) for n in names)
 checks[folder]={'commit':v['commit'],'files':len(names),'exact':True}
for v in prior['canonicalCheckpoints'].values(): assert git('cat-file','-t',v).strip()==b'commit'
assert git('rev-parse','origin/feature/operator-workstation-bottom-panel-20261014').decode().strip()=='262b6092b2ed694073ad9ffd41265f44dd0b6ca0'
for n in ['remote','local']: (E/(n+'-refs-before.txt')).write_bytes(Path('/tmp/b9d-'+n+'-before.txt').read_bytes())
save('gate0.json',{'passed':True,'start':START,'branch':git('branch','--show-current').decode().strip(),'cleanStartingTrackedTree':True,'historicalFiles':len(files),'acceptedClosureFiles':len(accepted),'checks':checks,'checkpoints':prior['canonicalCheckpoints'],'originalC1B6B7EvidenceByteExact':True,'operatorPinned':True,'tags':git('tag').decode().splitlines()})
print('Gate 0 PASS',len(files),len(accepted))
