"""Read-only historical audit. Outputs are confined to B16."""
from pathlib import Path
import hashlib, json, subprocess, sys, platform, shutil, os
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
START='eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35'
BRANCH='research/b16-desktop-worker-performance-20261020'
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def digest(raw): return hashlib.sha256(raw).hexdigest()
def save(name,value): (E/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def audit(label):
 assert git('branch','--show-current').decode().strip()==BRANCH
 git('merge-base','--is-ancestor',START,'HEAD')
 inv={}; p=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for row in git('ls-tree','-rz',START).split(b'\0'):
  if not row: continue
  meta,path=row.decode().split('\t'); blob=meta.split()[2]
  p.stdin.write((blob+'\n').encode());p.stdin.flush();header=p.stdout.readline().split()
  raw=p.stdout.read(int(header[2]));assert p.stdout.read(1)==b'\n'
  assert (R/path).read_bytes()==raw,path
  inv[path]={'blob':blob,'sha256':digest(raw),'bytes':len(raw)}
 p.stdin.close();assert p.wait()==0
 changes=git('diff','--name-only',START).decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines()
 assert all(x.startswith('experiments/dx-fv/browser_eos_b16/') for x in changes),changes
 prior=B.parent/'browser_eos_b15'; manifest=json.loads((prior/'evidence/build-manifest.json').read_text())
 for name,v in manifest['builds'].items():assert digest((prior/(name+'-bundle.mjs')).read_bytes())==v['sha256']
 assert (prior/'control-bundle.mjs').read_bytes()==git('show','b67afb3215075b2ec82bef376d39e03953dc0da2:experiments/dx-fv/browser_eos_b9c/candidate-bundle.mjs')
 seals=json.loads((prior/'evidence/delivery-sha256.json').read_text())
 for path,v in seals.items():assert digest((prior/path).read_bytes())==v,path
 a2=json.loads((B.parent/'browser_eos_b9c/evidence/accepted-source-manifest.json').read_text())
 for path,v in a2.items():assert digest((R/v['snapshot']).read_bytes())==v['sha256'] and (R/v['snapshot']).read_bytes()==git('show','be9eb35a4ddf5098e685182f8104685127c6a6ee:'+path)
 assert 'satP,statePT:(p,T,kind)=>statePT(p,T,kind),statePX' in (prior/'candidate-bundle.mjs').read_text()
 valid=json.loads((prior/'evidence/validation.json').read_text());assert valid['passed'] and valid['finalCandidateScientificMismatches']==0
 result={'passed':True,'startingSHA':START,'historicalFileCount':len(inv),'historicalBytesUnchanged':True,'allChangesB16Only':True,'b15SealedFiles':len(seals),'frozenBuilds':manifest['builds'],'acceptedA2ClosureFiles':len(a2),'originalTableAndAllHistoricalB12FilesUnchanged':True,'publicInterfaceFixPresent':True,'b15ExactEquivalenceReceipt':valid,'headAtAudit':git('rev-parse','HEAD').decode().strip(),'initialCheckpoint':'Exact B15 branch HEAD and empty git status observed before B16 creation; no AGENTS.md found.'}
 save(label+'-source-audit.json',result)
 if label=='initial':save('historical-files.json',inv)
 else:assert json.loads((E/'historical-files.json').read_text())==inv
 print(json.dumps(result,indent=2))
if __name__=='__main__':audit(sys.argv[1] if len(sys.argv)>1 else 'initial')
