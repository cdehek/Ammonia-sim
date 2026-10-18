"""Independent removal audit of every allowed observation insertion."""
import json,re,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
manifest=json.loads((E/'accepted-source-manifest.json').read_text());receipts={}
for name in ['coupled-model.cjs','engine.js']:
 original=next((R/v['snapshot']).read_text() for v in manifest.values() if Path(v['snapshot']).name==name)
 s=(B/'isolated'/name).read_text()
 if name=='coupled-model.cjs':
  s,n=re.subn(r'\n/\* B9B observation \*/ const __b9bEnd=globalThis\.__b9b\.enter\("[^"]+",[^\n]+\);try\{\n','',s);assert n==10
  s,n=re.subn(r'\n\}finally\{__b9bEnd\(\);\}/\* B9B observation \*/\n','',s);assert n==10
  s=s.replace('globalThis.__b9b.cache(key,properties.has(key));','').replace("globalThis.__b9b.note('state-install',[start,dt]);",'')
 else:
  s,n=re.subn(r'globalThis\.__b9b\.count\("internal\.[^"]+"\);','',s);assert n==8
  s=s.replace('globalThis.__b9b.count(target>=f-eps&&target<=g+eps?"inverse.mixture":"inverse.single-phase");','')
 assert s==original,'An original byte changed: '+name
 receipts[name]=dict(exactOriginalRestored=True,sha256=hashlib.sha256(s.encode()).hexdigest())
(E/'observational-removal-audit.json').write_text(json.dumps(dict(passed=True,files=receipts,noOriginalExpressionChanged=True,limitation='Insertion identity is necessary but not sufficient: runtime scientific/decision/property-sequence and failure parity are verified separately'),indent=2)+'\n')
print('All declared observation insertions removed -> exact accepted source bytes')
