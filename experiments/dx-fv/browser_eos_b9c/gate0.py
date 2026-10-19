"""Read-only scientific identity audit; receipts are confined to B9C."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'; E.mkdir(exist_ok=True)
START='ec2df3f9ee3efd7faef3d129282ad1dd7bdc896f'; A2='be9eb35a4ddf5098e685182f8104685127c6a6ee'
def git(*a): return subprocess.check_output(['git',*a],cwd=R)
def sha(b): return hashlib.sha256(b).hexdigest()
def save(n,v): (E/n).write_text(json.dumps(v,indent=2)+'\n')
assert git('rev-parse','HEAD').decode().strip()==START
assert not git('diff',START,'--name-only')
files=git('ls-tree','-r','--name-only',START).decode().splitlines()
historical={n:sha((R/n).read_bytes()) for n in files}
assert all((R/n).read_bytes()==git('show',START+':'+n) for n in files)
save('starting-files-sha256.json',historical)
manifest=json.loads((B.parent/'browser_eos_b9b/evidence/accepted-source-manifest.json').read_text())
for original,v in manifest.items():
 raw=(R/v['snapshot']).read_bytes()
 assert raw==git('show',A2+':'+original) and sha(raw)==v['sha256']
save('accepted-source-manifest.json',manifest)
checks={}
for folder,commit in [('browser_eos_b9','b1a65c9365879d6e97eff649e56371df3907e86e'),('browser_eos_b9a','355db28d853817e1931295d6ec2f007876d53f90'),('browser_eos_b9b',START),('browser_eos_b5b_c1','7809d08be67eab7cb9b537b1c1199b456b2da122'),('browser_eos_b6','f6227de0760d81994c60497869f5c6013a9d403f'),('browser_eos_b7','429ce020128763454324529cc1c7640cf1f474e8')]:
 names=git('ls-tree','-r','--name-only',commit,'--','experiments/dx-fv/'+folder+'/').decode().splitlines()
 assert names and all((R/n).read_bytes()==git('show',commit+':'+n) for n in names)
 checks[folder]={'commit':commit,'files':len(names),'exact':True}
checkpoints={'A2':A2,'B5A':'cc2ec6b54d40cabea93fa761d10a2ecab59def25','B5AGateB':'14b8b386148c687fcb549d5f17003fa9e63fbca8','C1':'7809d08be67eab7cb9b537b1c1199b456b2da122','C2':'7c75d9538d57080a01dffbf7e06128a27e2b9ccd','C2P1':'75e015fd3455e75fa85074e8748bc01eb8973624','B6':'f6227de0760d81994c60497869f5c6013a9d403f','B7':'429ce020128763454324529cc1c7640cf1f474e8','B8':'d5c7d01264639ebed39d1442222d5bf5c44fe848','B9':'b1a65c9365879d6e97eff649e56371df3907e86e','B9A':'355db28d853817e1931295d6ec2f007876d53f90','B9B':START,'operatorUI':'262b6092b2ed694073ad9ffd41265f44dd0b6ca0'}
for v in checkpoints.values(): assert git('cat-file','-t',v).strip()==b'commit'
save('gate0.json',dict(start=START,branch=git('branch','--show-current').decode().strip(),cleanBeforeAdditions=True,historicalFiles=len(files),acceptedFiles=len(manifest),sourceChecks=checks,canonicalCheckpoints=checkpoints,C2Correction={'supplied':'7c75d9538d57080a01dffbf7e06128a27c75603','canonical':checkpoints['C2'],'authority':'browser_eos_b8/PROTECTED_CHECKPOINT_AUDIT.md plus live ref and Git object'},historicalScientificEvidencePreserved=True))
print('Gate 0 PASS:',len(files),'historical files;',len(manifest),'accepted files')
