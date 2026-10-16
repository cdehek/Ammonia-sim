"""B6 preservation audit. Never writes outside B6; no source/build intervention."""
import argparse, hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
START='75e015fd3455e75fa85074e8748bc01eb8973624'
TARGET='research/browser-eos-b6-rejected-pt-loader-repair-20261016'
def git(*a): return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x): (E/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--start',action='store_true');ap.add_argument('--refs',default='remote-refs-before.tsv');ap.add_argument('--clean',action='store_true');a=ap.parse_args()
 assert git('branch','--show-current')==TARGET
 assert git('merge-base',START,'HEAD')==START
 if a.start:
  assert git('rev-parse','HEAD')==START
  paths=git('ls-tree','-r','--name-only',START).splitlines()
  hashes={p:sha(R/p) for p in paths};write('starting-files-sha256.json',hashes)
  write('checkpoint.json',dict(start=START,branch=TARGET,startingTree=git('rev-parse',START+'^{tree}'),initialCleanObservation='Empty git status --porcelain=v1 immediately after detached checkout, before branch creation; recorded in execution transcript.',initialCloneAttempt='Default network sandbox could not reach proxy; explicit network permission clone succeeded. No pre-existing checkout.'))
 hashes=json.loads((E/'starting-files-sha256.json').read_text());bad=[p for p,h in hashes.items() if sha(R/p)!=h];assert not bad,bad
 spec=importlib.util.spec_from_file_location('prior',B.parent/'browser_eos_b5b/audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);prior=m.verify()
 assert (R/'engine.js').read_bytes()==subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:engine.js'],cwd=R)
 assert sha(B.parent/'browser_eos_b4c/vendor/candidateB/coolprop.wasm')=='8c690c741d33d26f758a825ed5e4043af50cfc52a1e8587d8a5fb93732c026c5'
 refs=lambda p:dict(line.split()[::-1] for line in p.read_text().splitlines())
 before,after=refs(E/'remote-refs-before.tsv'),refs(E/a.refs)
 drift={k:[v,after.get(k)] for k,v in before.items() if after.get(k)!=v};assert not drift,drift
 assert set(after)-set(before)<={'refs/heads/'+TARGET}
 changes=git('diff',START,'--name-status').splitlines();assert all(x.startswith('A\texperiments/dx-fv/browser_eos_b6/') for x in changes),changes
 status=git('status','--porcelain=v1','--untracked-files=all');assert all('experiments/dx-fv/browser_eos_b6/' in x for x in status.splitlines()),status
 if a.clean: assert not status,status
 receipt=dict(start=START,head=git('rev-parse','HEAD'),branch=TARGET,historicalFiles=len(hashes),mismatches=bad,protectedRemoteRefs=len(before),drift=drift,acceptedEngineIdentical=True,allChangesAdditiveB6=True,**{k:prior[k] for k in ['artifacts','patches','acceptedA2','protectedCommits']})
 write('start-audit.json' if a.start else 'final-preservation.json',receipt)
 print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in receipt.items()}))
if __name__=='__main__':main()
