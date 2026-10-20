"""Read-only Git-object provenance; writes only inside B15."""
import hashlib,json,subprocess,importlib.util,platform,os,sys
sys.dont_write_bytecode=True
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
START='71608010fe49946dc542a4d85dff315c875274ad'
PINS=dict(A2='be9eb35a4ddf5098e685182f8104685127c6a6ee',B9C='b67afb3215075b2ec82bef376d39e03953dc0da2',B9D='20ddac46423a7a742af19ac415ef8796cf3a429f',B10='a49c5c4ade306fe02117139cf81c30a59727a7b1',B11='909de1579051bfadca0e282adf93eaedc0e24b9c',B12='e6779247eec9a39350a39551eec1740f06097aeb',B13='eddb2e7add904238162ead68ef9e2c1b8874f04d',B14=START)
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def save(n,v): (E/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def run():
 assert git('branch','--show-current').decode().strip()=='research/b15-vapor-ph-bracket-reuse-20261020'
 git('merge-base','--is-ancestor',START,'HEAD')
 assert git('rev-parse','origin/research/b14-phase-jacobian-diagnostics-20261019').decode().strip()==START
 for v in PINS.values():git('cat-file','-e',v+'^{commit}')
 inv={};p=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for row in git('ls-tree','-rz',START).split(b'\0'):
  if not row:continue
  meta,path=row.decode().split('\t');blob=meta.split()[2]
  p.stdin.write((blob+'\n').encode());p.stdin.flush();h=p.stdout.readline().split();raw=p.stdout.read(int(h[2]));assert p.stdout.read(1)==b'\n'
  assert (R/path).read_bytes()==raw,path
  inv[path]=dict(blob=blob,sha256=sha(raw),bytes=len(raw))
 p.stdin.close();assert p.wait()==0
 changes=git('diff','--name-only',START).decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines()
 assert all(x.startswith('experiments/dx-fv/browser_eos_b15/') for x in changes),changes
 m=json.loads((B.parent/'browser_eos_b9c/evidence/accepted-source-manifest.json').read_text());assert len(m)==14
 for path,v in m.items():
  raw=(R/v['snapshot']).read_bytes();assert sha(raw)==v['sha256'];assert raw==git('show',PINS['A2']+':'+path)
 for name in ['candidate-bundle.mjs','diagnostic-candidate-bundle.mjs','control-bundle.mjs','isolated/coupled-model.cjs']:
  path='experiments/dx-fv/browser_eos_b9c/'+name;assert (R/path).read_bytes()==git('show',PINS['B9C']+':'+path)
 seals=json.loads((B.parent/'browser_eos_b14/evidence/delivery-sha256.json').read_text())
 for path,d in seals.items():assert sha((B.parent/'browser_eos_b14'/path).read_bytes())==d,path
 prior=json.loads((B.parent/'browser_eos_b13/evidence/delivery-sha256.json').read_text())
 for path,d in prior.items():assert sha((B.parent/'browser_eos_b13'/path).read_bytes())==d,path
 spec=importlib.util.spec_from_file_location('b12verify',B.parent/'browser_eos_b12/verify.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.E=E;mod.artifact(False);mod.retained_results()
 save('source-preservation.json',dict(passed=True,baseline=START,pins=PINS,historicalFileCount=len(inv),acceptedA2Closure=m,b9cIdentity=True,b14SealedFiles=len(seals),historicalBytesUnchanged=True,changesConfinedToB15=True,initialHeadAndCleanTree='Exact detached B14 HEAD and empty git status observed before branch creation; no AGENTS.md found'))
 save('historical-files.json',inv)
 print('PASS: protected Git blobs, 14-file closure, B9C, B14 sealed receipts and B12 package')
if __name__=='__main__':run()
