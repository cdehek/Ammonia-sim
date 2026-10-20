"""B16 artifact content seal, excluding only itself and ignored runtime caches."""
from pathlib import Path
import json,hashlib,sys
B=Path(__file__).resolve().parent;dest=B/'evidence/delivery-sha256.json'
files={str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(B.rglob('*'))if p.is_file()and p!=dest and not any(x in ['.runtime','__pycache__']for x in p.relative_to(B).parts)}
if '--verify' in sys.argv:assert json.loads(dest.read_text())==files;print('PASS: B16 delivery content seal')
else:dest.write_text(json.dumps(files,indent=2)+'\n');print('Sealed',len(files),'B16 files')
