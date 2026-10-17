"""Independently verify inherited dependency file digests before WASM compilation."""
import hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;D=Path(sys.argv[1]);E=B/'evidence'
expected=json.loads((B.parent/'browser_eos_b3/evidence/provenance.json').read_text())['dependencies']
rows={}
for n,old in expected.items():
 p=D/n
 tree={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file() and '.git' not in f.relative_to(p).parts}
 digest=hashlib.sha256(json.dumps(tree,sort_keys=True).encode()).hexdigest()
 commit=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip() if (p/'.git').exists() else None
 rows[n]=dict(fileCount=len(tree),pathSHA256JSON=digest,commit=commit,expected=old,match=len(tree)==old['fileCount'] and digest==old['pathSHA256JSON'] and commit==old['commit'])
out=dict(dependencies=rows,allNineMatch=all(x['match'] for x in rows.values()))
t=E/'dependency-verification.json';assert not t.exists();t.write_text(json.dumps(out,indent=2)+'\n')
assert out['allNineMatch'],rows
print('All nine dependency contents and Git pins match')
