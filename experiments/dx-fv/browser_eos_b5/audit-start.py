"""Read-only verification of inherited artifacts, accepted closure and source."""
import hashlib,json,lzma,subprocess
from pathlib import Path
import os
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'))
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
for folder in ['browser_eos_b3','browser_eos_b4a','browser_eos_b4b','browser_eos_b4c']:
 p=B.parent/folder
 for name,v in json.loads((p/'evidence/native-binaries.json').read_text()).items():
  f=p/v['archive'];a=sha(f.read_bytes());b=sha(lzma.decompress(f.read_bytes()))
  rows.append(dict(file=str(f.relative_to(R)),archive=a,binary=b,pass_=a==v['archiveSHA256'] and b==v['sha256']))
for folder,manifest in [('browser_eos_backend','build-provenance.json'),('browser_eos_b4a','provenance.json'),('browser_eos_b4b','provenance.json'),('browser_eos_b4c','provenance.json')]:
 p=B.parent/folder
 for name,v in json.loads((p/'evidence'/manifest).read_text())['artifacts'].items():
  f=p/name;rows.append(dict(file=str(f.relative_to(R)),sha256=sha(f.read_bytes()),pass_=sha(f.read_bytes())==v['sha256']))
source=Path('/workspace/coolprop-b5')
expected=json.loads((B.parent/'browser_eos_b4c/evidence/source-stage-candidateB.json').read_text())['trackedSourceSHA256']
bad=[f for f,h in expected.items() if sha((source/f).read_bytes())!=h]
accepted={}
for f,h in json.loads((B.parent/'browser_eos_b4c/evidence/accepted-a2-verification.json').read_text())['files'].items():
 raw=subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:experiments/dx-fv/'+f],cwd=R)
 snapshot=B.parent/'browser_eos_backend/accepted'/f
 accepted[f]=dict(gitSHA256=sha(raw),snapshotSHA256=sha(snapshot.read_bytes()),pass_=sha(raw)==h==sha(snapshot.read_bytes()))
patches={str(p.relative_to(R)):sha(p.read_bytes()) for p in [B.parent/'browser_eos_backend/flash-44.patch',B.parent/'browser_eos_b4a/liquid-classification.patch',B.parent/'browser_eos_b4b/pt-cache-consistency.patch',B.parent/'browser_eos_b4c/upper-quality-classification.patch']}
out=dict(artifacts=rows,sourceHEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),sourceFiles=len(expected),sourceMismatches=bad,accepted=accepted,patches=patches)
out['allPass']=all(x['pass_'] for x in rows) and not bad and all(x['pass_'] for x in accepted.values())
(E/'preservation-verification.json').write_text(json.dumps(out,indent=2)+'\n');assert out['allPass'];print('Preservation verified',len(rows),'artifacts;',len(expected),'source files; accepted closure',len(accepted))
