"""Read-only baseline audit; all output belongs to B13."""
import hashlib, json, subprocess, importlib.util
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'; E.mkdir(exist_ok=True)
START='e6779247eec9a39350a39551eec1740f06097aeb'
PINS=dict(A2='be9eb35a4ddf5098e685182f8104685127c6a6ee',B9C='b67afb3215075b2ec82bef376d39e03953dc0da2',B9D='20ddac46423a7a742af19ac415ef8796cf3a429f',B10='a49c5c4ade306fe02117139cf81c30a59727a7b1',B11='909de1579051bfadca0e282adf93eaedc0e24b9c',B12=START)
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def save(n,d): (E/n).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def run():
 assert git('branch','--show-current').decode().strip()=='research/b13-dx-fv-horizon-diagnostics-20261019'
 git('merge-base','--is-ancestor',START,'HEAD')
 for p in PINS.values(): git('cat-file','-e',p+'^{commit}')
 inventory={}
 proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for row in git('ls-tree','-rz',START).split(b'\0'):
  if not row: continue
  meta,path=row.decode().split('\t'); blob=meta.split()[2]
  proc.stdin.write((blob+'\n').encode());proc.stdin.flush()
  header=proc.stdout.readline().split();raw=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'
  assert (R/path).read_bytes()==raw,path
  inventory[path]={'blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
 proc.stdin.close();assert proc.wait()==0
 prefix='experiments/dx-fv/browser_eos_b13/'
 paths=git('diff','--name-only',START).decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines()
 assert all(p.startswith(prefix) for p in paths),paths
 manifest=json.loads((B.parent/'browser_eos_b9c/evidence/accepted-source-manifest.json').read_text())
 for path,v in manifest.items():
  raw=(R/v['snapshot']).read_bytes();assert hashlib.sha256(raw).hexdigest()==v['sha256'];assert raw==git('show',PINS['A2']+':'+path)
 for p in ['candidate-bundle.mjs','diagnostic-candidate-bundle.mjs','control-bundle.mjs','isolated/coupled-model.cjs']:
  path='experiments/dx-fv/browser_eos_b9c/'+p;assert (R/path).read_bytes()==git('show',PINS['B9C']+':'+path)
 assert (B.parent/'browser_eos_b11/preview/science/candidate-bundle.mjs').read_bytes()==(B.parent/'browser_eos_b9c/candidate-bundle.mjs').read_bytes()
 save('source-preservation.json',dict(passed=True,startingCommit=START,pins=PINS,historicalFileCount=len(inventory),allHistoricalBytesUnchanged=True,acceptedA2Closure=manifest,b9cExact=True,changesConfinedToB13=True,startingWorktreeClean=True,startingCleanEvidence='Observed git status --porcelain empty before branch creation; HEAD and B12 origin both exact requested SHA.'))
 save('historical-files.json',inventory)
 spec=importlib.util.spec_from_file_location('b12verify',B.parent/'browser_eos_b12/verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.E=E
 m.artifact(False);m.retained_results()
 print('PASS: all B12 bytes, A2 14-file closure, B9C bundles, B11/B12 package and retained checkpoints')
if __name__=='__main__':run()
