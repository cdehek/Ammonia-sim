"""Seal review artifacts; omit only the seal itself and ignored runtime/cache files."""
import argparse,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;target=B/'evidence/delivery-sha256.json'
ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');a=ap.parse_args()
files={p.relative_to(B).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(B.rglob('*')) if p.is_file() and p!=target and not any(k in p.relative_to(B).parts for k in ['.runtime','__pycache__'])}
if a.verify:assert files==json.loads(target.read_text()),'B13 artifact seal mismatch'
else:target.write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
print(('Verified' if a.verify else 'Sealed'),len(files),'B13 review artifacts')
