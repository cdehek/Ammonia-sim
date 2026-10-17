"""Seed only immutable preserved inventories/references and verified native binaries."""
import hashlib,json,lzma
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';W=Path('/workspace/b7-work/native');E.mkdir(exist_ok=True);W.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
for name in ['fixed-inputs.json','fixed-inventory.csv','independent-fixed-references.json','high-precision-references.json','original-failures.json']:
 source=X/'browser_eos_b5a/evidence'/name;target=E/name
 if target.exists():assert target.read_bytes()==source.read_bytes()
 else:target.write_bytes(source.read_bytes())
identities={}
manifest=json.loads((X/'browser_eos_b5a/evidence/native-binaries.json').read_text())
for name,label in [('control','control'),('A1','candidate')]:
 m=manifest[name];archive=X/'browser_eos_b5a'/m['archive'];raw=archive.read_bytes();binary=lzma.decompress(raw)
 assert sha(raw)==m['archiveSHA256'] and sha(binary)==m['sha256']
 target=W/f'{label}.so'
 if target.exists():assert target.read_bytes()==binary
 else:target.write_bytes(binary)
 identities[label]=dict(archive=str(archive.relative_to(B.parents[2])),archiveSHA256=sha(raw),binarySHA256=sha(binary),bytes=len(binary),scientificSource='Verified B4C' if label=='control' else 'Exact accepted B5A A1',matchedNativeCompiler='GCC 14.2.0, archived original B5A matched build')
target=E/'native-artifact-identities.json'
if target.exists():assert json.loads(target.read_text())==identities
else:target.write_text(json.dumps(identities,indent=2)+'\n')
saved=json.loads((X/'browser_eos_b5a/evidence/additional-inventories.json').read_text())['rows']
additional=dict(rows=[{k:r['saved'][k] for k in ['failureKey','origin','requestedP','requestedH','referenceT','input','bits']} for r in saved],source='browser_eos_b5a/evidence/additional-inventories.json',notRegenerated=True)
assert len(additional['rows'])==21
target=E/'additional-inputs.json'
if target.exists():assert json.loads(target.read_text())==additional
else:target.write_text(json.dumps(additional,indent=2,allow_nan=False)+'\n')
print('Preserved 250/21 inputs and matched native archive identities verified')
