"""Seal all B7 artifacts except the inherently self-referential manifest itself."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;p=B/'evidence/delivery-manifest-sha256.json';assert not p.exists()
files={str(f.relative_to(B)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(B.rglob('*')) if f.is_file() and f!=p}
p.write_text(json.dumps(files,indent=2)+'\n');print('Sealed',len(files),'B7 files')
