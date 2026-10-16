"""Seal B6 delivery bytes without embedding a self-referential commit hash."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(E/n).write_text(json.dumps(x,indent=2)+'\n')
assert json.loads((E/'verification.json').read_text())['assessment']=='FOCUSED LOADER REPAIR PASS'
assert json.loads((E/'final-preservation.json').read_text())['mismatches']==[]
assert sha(B/'loader.mjs')==json.loads((E/'performance-source-identity.json').read_text())['finalLoaderSHA256']
sources={str(p.relative_to(B)):sha(p) for p in B.rglob('*') if p.is_file() and 'evidence' not in p.relative_to(B).parts and '__pycache__' not in p.parts}
write('source-manifest-sha256.json',sources)
manifest=E/'delivery-manifest-sha256.json'
allfiles={str(p.relative_to(B)):sha(p) for p in sorted(B.rglob('*')) if p.is_file() and p!=manifest and '__pycache__' not in p.parts}
write(manifest.name,allfiles)
print(len(sources),'source/report hashes;',len(allfiles),'delivery file hashes sealed')
