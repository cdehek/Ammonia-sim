"""Read-only historical preservation audit. Writes B11 receipts only."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
START='a49c5c4ade306fe02117139cf81c30a59727a7b1'
PINS={'A2':'be9eb35a4ddf5098e685182f8104685127c6a6ee','B9C':'b67afb3215075b2ec82bef376d39e03953dc0da2','B9D':'20ddac46423a7a742af19ac415ef8796cf3a429f','B10':START,'original':'262b6092b2ed694073ad9ffd41265f44dd0b6ca0'}
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
if __name__=='__main__':
 E.mkdir(exist_ok=True)
 files=git('ls-tree','-rz',START).split(b'\0');hashes={};blobs={}
 # One batch request preserves binary content and avoids thousands of subprocesses.
 entries=[x.decode().split('\t') for x in files if x]
 proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for meta,p in entries:
  blob=meta.split()[2];proc.stdin.write((blob+'\n').encode());proc.stdin.flush()
  h=proc.stdout.readline();size=int(h.split()[2]);raw=proc.stdout.read(size);assert proc.stdout.read(1)==b'\n'
  assert (R/p).read_bytes()==raw,p
  hashes[p]=sha(raw);blobs[p]=blob
 proc.stdin.close();proc.wait()
 if (E/'starting-files-sha256.json').exists():assert json.loads((E/'starting-files-sha256.json').read_text())==hashes
 else:
  assert git('rev-parse','HEAD').decode().strip()==START
  assert not git('status','--porcelain','--untracked-files=no')
  save('starting-files-sha256.json',hashes);save('starting-git-blobs.json',blobs)
  (E/'local-refs-before.txt').write_bytes(git('for-each-ref','--format=%(refname) %(objectname)'))
 accepted=json.loads((B.parent/'browser_eos_b10/evidence/accepted-source-manifest.json').read_text())
 for p,v in accepted.items():assert (R/v['snapshot']).read_bytes()==git('show',PINS['A2']+':'+p)
 for key in PINS:git('cat-file','-e',PINS[key]+'^{commit}')
 old=(E/'local-refs-before.txt').read_text().splitlines()
 for line in old:
  ref,value=line.split();assert git('rev-parse',ref).decode().strip()==value or ref=='refs/heads/research/b11-portable-ipad-preview-20261019',ref
 changed=git('diff','--name-only',START).decode().splitlines()
 assert all(p.startswith('experiments/dx-fv/browser_eos_b11/') for p in changed)
 save('preservation.json',{'passed':True,'historicalFiles':len(hashes),'allStartingTrackedBytesUnchanged':True,'acceptedClosureFiles':len(accepted),'protectedPins':PINS,'historicalRefsUnchanged':True,'tags':git('tag').decode().splitlines(),'changesConfinedToB11':True})
 print('PASS',len(hashes),'starting files;',len(accepted),'accepted scientific closure files')
