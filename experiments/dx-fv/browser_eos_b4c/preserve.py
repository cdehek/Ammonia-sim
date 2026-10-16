"""Read-only historical verification and exact upper-quality inventory extraction."""
import hashlib,json,lzma,subprocess
from pathlib import Path
import os
B=Path(__file__).resolve().parent; R=B.parents[2]; E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence')); H=B.parent/'browser_eos_b4b'
def sha(data): return hashlib.sha256(data).hexdigest()
def write(name,data):
 p=E/name; assert not p.exists(),p; p.write_text(json.dumps(data,indent=2)+'\n')
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only','d0d11d59756c4dc32bbfdb22a5975fd6f4527e05'],cwd=R).decode().splitlines()
write('preservation-start.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=R).decode().strip(),trackedSHA256={n:sha((R/n).read_bytes()) for n in tracked}))
checks=[]
for folder in ['browser_eos_b3','browser_eos_b4a','browser_eos_b4b']:
 p=B.parent/folder
 for name,v in json.loads((p/'evidence/native-binaries.json').read_text()).items():
  f=p/v['archive']; data=f.read_bytes(); raw=lzma.decompress(data)
  assert sha(data)==v['archiveSHA256'] and sha(raw)==v['sha256'],f
  checks.append(dict(file=str(f.relative_to(R)),archiveSHA256=sha(data),binarySHA256=sha(raw)))
for folder,manifest,key in [('browser_eos_backend','build-provenance.json','artifacts'),('browser_eos_b4a','provenance.json','artifacts'),('browser_eos_b4b','provenance.json','artifacts')]:
 p=B.parent/folder
 for name,v in json.loads((p/'evidence'/manifest).read_text())[key].items():
  f=p/name; assert sha(f.read_bytes())==v['sha256'],f
  checks.append(dict(file=str(f.relative_to(R)),sha256=v['sha256']))
write('historical-identities.json',dict(checks=checks,allPass=True,patches={str(p.relative_to(R)):sha(p.read_bytes()) for p in [B.parent/'browser_eos_backend/flash-44.patch',B.parent/'browser_eos_b4a/liquid-classification.patch',H/'pt-cache-consistency.patch']}))
out={}
for runtime,file in [('native','native-candidateB.json'),('chromium','chromium-candidateB-focused.json'),('webkit','webkit-candidateB-focused.json')]:
 data=json.loads((H/'evidence'/file).read_text()); bases=[]; touches=[]; snapshots=[]
 for r in data['rows']:
  ident=r['request']['id'] if runtime=='native' else r['id']
  base=r['base']; state=base['PH']['values'] if runtime=='native' else base['state']
  request=r['request'] if runtime=='native' else dict(id=ident,mode='PH',args=r['args'])
  def invalid(s): return 1<s['Q']<=1+1e-9
  if invalid(state): bases.append(dict(request=request,base=base,inventories=r['inventories'],originalSignedProbes=r['probes']))
  if invalid(state): snapshots.append(dict(id=ident,sample='base',data=base))
  for q in r['probes']:
   v=q.get('output',{}); ps=v.get('PH',{}).get('values') if runtime=='native' else v.get('state')
   if not ps: continue
   if invalid(ps): snapshots.append(dict(id=ident,sample=dict(axis=q['axis'],step=q['step']),data=v))
   if runtime=='native' and q.get('samePhysicalBranch') and base['physicalPhase']=='gas' and (invalid(state) or invalid(ps)):
    touches.append(dict(id=ident,request=request,base=base,probe=q))
 out[runtime]=dict(source=str((H/'evidence'/file).relative_to(R)),sourceSHA256=sha((H/'evidence'/file).read_bytes()),invalidBaseCount=len(bases),invalidBases=bases,samePhysicalVaporTouches=touches,invalidSnapshots=snapshots)
write('original-upper-quality-inventory.json',out)
print({k:dict(baseCount=v['invalidBaseCount'],sameVaporTouches=len(v['samePhysicalVaporTouches']),invalidSnapshots=len(v['invalidSnapshots'])) for k,v in out.items()})
