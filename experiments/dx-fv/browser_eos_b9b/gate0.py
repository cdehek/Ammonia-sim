"""Read-only checkpoint/source audit. Writes receipts only under B9B."""
import hashlib,json,subprocess,shutil,sys,importlib.metadata
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'; E.mkdir(exist_ok=True)
START='355db28d853817e1931295d6ec2f007876d53f90'; A2='be9eb35a4ddf5098e685182f8104685127c6a6ee'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
assert git('merge-base',START,'HEAD').decode().strip()==START
files=git('ls-tree','-r','--name-only',START).decode().splitlines()
historical={n:sha((R/n).read_bytes()) for n in files}
assert all((R/n).read_bytes()==git('show',START+':'+n) for n in files)
save('starting-files-sha256.json',historical)
manifest=json.loads((B.parent/'browser_eos_b9a/evidence/accepted-source-manifest.json').read_text())
for original,v in manifest.items():assert (R/v['snapshot']).read_bytes()==git('show',A2+':'+original)
save('accepted-source-manifest.json',manifest)
checks={}
for folder,commit in [('browser_eos_b9','b1a65c9365879d6e97eff649e56371df3907e86e'),('browser_eos_b5b_c1','7809d08be67eab7cb9b537b1c1199b456b2da122'),('browser_eos_b6','f6227de0760d81994c60497869f5c6013a9d403f'),('browser_eos_b7','429ce020128763454324529cc1c7640cf1f474e8')]:
 prefix='experiments/dx-fv/'+folder+'/'
 names=git('ls-tree','-r','--name-only',commit,'--',prefix).decode().splitlines()
 assert all((R/n).read_bytes()==git('show',commit+':'+n) for n in names)
 checks[folder]={'commit':commit,'files':len(names),'exact':True}
for n in ['remote-before.tsv','pr3-before.json']:shutil.copyfile('/tmp/b9b-'+n,E/n)
save('gate0.json',dict(start=START,head=git('rev-parse','HEAD').decode().strip(),branch=git('branch','--show-current').decode().strip(),initialCleanAtStart=True,historicalFiles=len(files),acceptedFiles=len(manifest),originalGitChecks=checks,node=subprocess.check_output(['node','--version'],text=True).strip(),systemChromium=subprocess.check_output(['chromium','--version'],text=True).strip(),playwright=importlib.metadata.version('playwright'),webkit='pending runtime setup; must be recorded before measurement',profilers=['Chromium CDP Profiler (capability to be tested)','WebKit Playwright protocol: capability to be tested','Node inspector CPU profiler'],noRebuild=True))
print('Gate 0 source identities verified:',len(files),'historical files;',len(manifest),'A2 files')
