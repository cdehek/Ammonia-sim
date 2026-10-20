"""Content seal for reviewable B14 deliverables, excludes itself and runtime data."""
import argparse,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;dest=B/'evidence/delivery-sha256.json';p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');a=p.parse_args()
files={str(f.relative_to(B)):hashlib.sha256(f.read_bytes()).hexdigest()for f in sorted(B.rglob('*'))if f.is_file()and f!=dest and not any(x in ['.runtime','__pycache__']for x in f.relative_to(B).parts)}
if a.verify:assert files==json.loads(dest.read_text());print('PASS: B14 delivery content seal')
else:dest.write_text(json.dumps(files,indent=2)+'\n');print('Sealed',len(files),'B14 deliverables')
