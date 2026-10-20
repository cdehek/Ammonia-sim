"""Lossless gzip only; retained scientific JSON content is not changed."""
from pathlib import Path
import gzip,hashlib,json
B=Path(__file__).resolve().parent;E=B/'evidence';manifest={}
for name in ['chromium-science.json']:
 p=E/name;q=E/(name+'.gz')
 if not p.exists():continue
 assert not q.exists();raw=p.read_bytes();z=gzip.compress(raw,mtime=0);assert gzip.decompress(z)==raw;q.write_bytes(z)
 manifest[name]={'compressed':q.name,'originalBytes':len(raw),'compressedBytes':len(z),'originalSHA256':hashlib.sha256(raw).hexdigest(),'compressedSHA256':hashlib.sha256(z).hexdigest(),'lossless':True};p.unlink()
if manifest:(E/'lossless-compaction.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
