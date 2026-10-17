"""Seal additive B9 artifacts, excluding only this manifest and Python caches."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;target=B/'evidence/delivery-manifest-sha256.json'
rows={str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(B.rglob('*')) if p.is_file() and p!=target and '__pycache__' not in p.parts}
target.write_text(json.dumps(rows,indent=2)+'\n');print('sealed',len(rows),'B9 files')
