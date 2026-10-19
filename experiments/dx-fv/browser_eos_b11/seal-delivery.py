"""Hash every nonignored B11 delivery file; --check verifies without executing science."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
from audit import B,R,sha
ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
prefix=B.relative_to(R).as_posix()+'/'
files=sorted(set(subprocess.check_output(['git','ls-files','-co','--exclude-standard','--',prefix],cwd=R).decode().splitlines()))
seal=B/'evidence/delivery-sha256.json'
manifest={p[len(prefix):]:sha((R/p).read_bytes()) for p in files if (R/p).is_file() and (R/p)!=seal}
asset=json.loads((B/'preview/asset-manifest.json').read_text())
for a in asset['assets']:assert sha((B/'preview'/a['path']).read_bytes())==a['sha256']
with zipfile.ZipFile(B/'preview.zip') as z:
 assert {n.removeprefix('preview/'):z.read(n) for n in z.namelist()}=={p.relative_to(B/'preview').as_posix():p.read_bytes() for p in (B/'preview').rglob('*') if p.is_file()}
assert (B/'preview.zip.sha256').read_text().split()[0]==sha((B/'preview.zip').read_bytes())
if args.check:assert json.loads(seal.read_text())==manifest,'Delivery seal mismatch'
else:seal.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print('PASS',len(manifest),'delivery file hashes; complete ZIP and runtime assets verified')
