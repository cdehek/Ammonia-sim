"""Reconstruct preliminary source identity without retaining duplicate registries."""
from pathlib import Path
import hashlib,json
V=Path(__file__).resolve().parent;B=V.parent;m=json.loads((V/'build-manifest.json').read_text())
for n,x in m['builds'].items():
 raw=(B/(n+'-bundle.mjs')).read_text()
 if 'candidate'in n:
  a='satP,statePT:(p,T,kind)=>statePT(p,T,kind),statePX';assert raw.count(a)==1;raw=raw.replace(a,'satP,statePT,statePX')
 assert hashlib.sha256(raw.encode()).hexdigest()==x['sha256'],n
 if n=='candidate':assert raw==(V/'candidate-bundle.mjs').read_text()
print('PASS: all preliminary registry source hashes reproducibly reconstructed')
