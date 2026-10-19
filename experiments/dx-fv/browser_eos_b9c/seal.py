"""Hash research artifacts and installed runtimes without rebuilding anything."""
import hashlib,json,platform,subprocess,importlib.metadata
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
runtime={'python':platform.python_version(),'platform':platform.platform(),'node':json.loads(subprocess.check_output(['node','-p','JSON.stringify({version:process.version,versions:process.versions})'],text=True)),'playwright':importlib.metadata.version('playwright'),'binaries':{},'sources':{str(p.relative_to(R)):sha(p) for p in B.rglob('*') if p.is_file() and p.suffix in ['.mjs','.cjs','.py','.html']},'physicalIPad':False,'noEOSRebuild':True}
for pattern in ['chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell','chromium-*/chrome-linux64/chrome','webkit-*/minibrowser-wpe/bin/MiniBrowser','webkit-*/minibrowser-wpe/lib/libWPEWebKit-*.so*']:
 for p in Path('/workspace/b9-runtime/browsers').glob(pattern):
  if p.is_file():runtime['binaries'][str(p)]=sha(p)
p=Path('/workspace/b9-runtime/webkit.sh');runtime['binaries'][str(p)]=sha(p)
(E/'runtime-manifest.json').write_text(json.dumps(runtime,indent=2)+'\n')
# Exclude the manifest itself; later remote-receipt commits may append receipts.
manifest={str(p.relative_to(B)):sha(p) for p in B.rglob('*') if p.is_file() and p.name!='deliverables-manifest.json' and '__pycache__' not in p.parts}
(E/'deliverables-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Runtime and deliverables sealed:',len(manifest),'files')
