"""Pinned B9 browser dependencies in B10/.runtime; no host package edits."""
import hashlib,importlib.metadata,json,os,subprocess,sys,urllib.request
from pathlib import Path
B=Path(__file__).resolve().parent; W=B/'.runtime'; D=W/'debs';D.mkdir(parents=True,exist_ok=True)
assert importlib.metadata.version('playwright')=='1.62.0'
pins=json.loads((B.parent/'browser_eos_b4a/evidence/provenance.json').read_text())['browserExtraDebs']
for name,digest in pins.items():
 folder='libm/libmanette' if name.startswith('libmanette') else 'h/hyphen' if name.startswith('libhyphen') else 'h/harfbuzz' if name.startswith('libharfbuzz') else 'libg/libglvnd'
 p=D/name
 if not p.exists():
  with urllib.request.urlopen('https://deb.debian.org/debian/pool/main/'+folder+'/'+name,timeout=40) as response:p.write_bytes(response.read())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 subprocess.run(['dpkg-deb','-x',str(p),str(W/'sysroot')],check=True)
s=(B.parent/'browser_eos_b4c/evidence/webkit-launcher.sh').read_text().replace('/workspace/b4c-browsers',str(W/'browsers')).replace('/workspace/b4c-sysroot',str(W/'sysroot'))
p=W/'webkit.sh';p.write_text(s);p.chmod(0o755)
print('Pinned shared libraries extracted; launcher ready')
