"""B7 additive preservation receipts; historical verification is read-only."""
import argparse, hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
START='f6227de0760d81994c60497869f5c6013a9d403f'
BRANCH='research/browser-eos-b7-gatea-wasm-qualification-20261017'
def git(*args): return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x): (E/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--start',action='store_true');p.add_argument('--refs',default='remote-before.tsv');p.add_argument('--clean',action='store_true');p.add_argument('--read-only',action='store_true');a=p.parse_args()
 E.mkdir(exist_ok=True)
 assert git('branch','--show-current')==BRANCH
 assert git('merge-base',START,'HEAD')==START
 if a.start:
  assert git('rev-parse','HEAD')==START
  write('starting-files-sha256.json',{f:sha(R/f) for f in git('ls-tree','-r','--name-only',START).splitlines()})
  write('checkpoint.json',dict(start=START,tree=git('rev-parse',START+'^{tree}'),branch=BRANCH,initialClean=True,observation='Empty git status --porcelain=v1 at exact B6 HEAD before git switch -c; execution transcript. Empty workspace initially; network-enabled clone succeeded after restricted-sandbox proxy failure.'))
 original=json.loads((E/'starting-files-sha256.json').read_text())
 assert not [f for f,h in original.items() if sha(R/f)!=h]
 spec=importlib.util.spec_from_file_location('historical_audit',B.parent/'browser_eos_b5b/audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);prior=m.verify()
 assert sha(B.parent/'browser_eos_b5a/gate-a.patch')=='2f4b9e675b98a59f3846ede09b767698090083934e080bc11790b723c9d90eeb'
 assert (R/'engine.js').read_bytes()==subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:engine.js'],cwd=R)
 b6=json.loads((B.parent/'browser_eos_b6/evidence/delivery-manifest-sha256.json').read_text())
 for f,h in b6.items(): assert sha(B.parent/'browser_eos_b6'/f)==h,f
 refs=lambda n:dict(line.split()[::-1] for line in (E/n).read_text().splitlines())
 before,after=refs('remote-before.tsv'),refs(a.refs)
 assert not {k:(v,after.get(k)) for k,v in before.items() if after.get(k)!=v}
 assert set(after)-set(before)<={'refs/heads/'+BRANCH}
 if 'refs/heads/'+BRANCH in after and 'refs/heads/'+BRANCH not in before:
  assert after['refs/heads/'+BRANCH]==git('rev-parse','HEAD')
 protected=['be9eb35a4ddf5098e685182f8104685127c6a6ee','ef1562ae1680fccf3323391e9ec83788c5ae1e69','6a220dd6c94bff08e00e0107cfec71854166ede2','4e1295be9493d8bce4ca35ee0cf61accb7465226','94f77bb062b75ffebf17a1c9758d11c1adc61711','d0d11d59756c4dc32bbfdb22a5975fd6f4527e05','3622000309cacdd35aaaebbb805ae40d27c75603','e30ad9d76bc892aa355126339997d6184c8729d2','cc2ec6b54d40cabea93fa761d10a2ecab59def25','14b8b386148c687fcb549d5f17003fa9e63fbca8','26df10c1f486b60978646e9c8819fc0054cb9465','7809d08be67eab7cb9b537b1c1199b456b2da122','7c75d9538d57080a01dffbf7e06128a27e2b9ccd','75e015fd3455e75fa85074e8748bc01eb8973624','f6227de0760d81994c60497869f5c6013a9d403f','262b6092b2ed694073ad9ffd41265f44dd0b6ca0']
 for commit in protected:git('cat-file','-e',commit+'^{commit}')
 changes=git('diff',START,'--name-status').splitlines()
 assert all(x.startswith('A\texperiments/dx-fv/browser_eos_b7/') for x in changes),changes
 status=git('status','--porcelain=v1','--untracked-files=all')
 assert all('experiments/dx-fv/browser_eos_b7/' in x for x in status.splitlines()),status
 if a.clean: assert not status,status
 receipt=dict(start=START,head=git('rev-parse','HEAD'),branch=BRANCH,historicalFiles=len(original),historicalMismatches=[],protectedRemoteRefs=len(before),remoteDrift={},B6ManifestFiles=len(b6),acceptedEngineIdentical=True,changesAdditiveB7=True,**{k:prior[k] for k in ['artifacts','patches','acceptedA2']},protectedCommits=protected)
 if a.read_only and (E/'delivery-manifest-sha256.json').exists():
  for name,digest in json.loads((E/'delivery-manifest-sha256.json').read_text()).items():assert sha(B/name)==digest,name
 if not a.read_only:write('start-audit.json' if a.start else 'final-preservation.json',receipt)
 print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in receipt.items()}))
if __name__=='__main__': main()
