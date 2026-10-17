"""Collect bounded external logs and final source/tool identities, never archives."""
import hashlib,importlib.metadata,json,platform,shutil
from pathlib import Path
B=Path(__file__).resolve().parent;W=Path('/workspace/b7-work');E=B/'evidence';L=E/'logs';L.mkdir(exist_ok=True)
def copy(source,target):
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==source.read_bytes(),str(target)
 else:shutil.copyfile(source,target)
for p in sorted(W.glob('*.log')):copy(p,L/p.name)
for p in sorted((B.parent/'browser_eos_b4c/vendor/notices').glob('*')):copy(p,B/'vendor/notices'/p.name)
copy(W/'webkit.sh',E/'webkit-launcher.sh');copy(W/'upstream/LICENSE',B/'vendor/CoolProp-LICENSE.txt')
source=W/'upstream';tracked=json.loads((E/'source-candidate.json').read_text())['trackedSourceSHA256']
files={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.is_file() and '.git' not in p.relative_to(source).parts}
assert all(files[n]==h for n,h in tracked.items())
snapshot=dict(trackedFiles=len(tracked),allSourceFilesSHA256=files,generatedOrUntracked={n:h for n,h in files.items() if n not in tracked},exactA1TrackedManifest=True)
p=E/'source-final-complete.json'
if p.exists():assert json.loads(p.read_text())==snapshot
else:p.write_text(json.dumps(snapshot,indent=2)+'\n')
toolPaths=['emsdk/upstream/bin/clang','emsdk/upstream/bin/wasm-ld','emsdk/upstream/emscripten/emcc.py','emsdk/upstream/emscripten/emcc','emsdk/upstream/emscripten/src/lib/libexceptions.js','emsdk/upstream/emscripten/system/lib/libcxxabi/src/cxa_exception_emscripten.cpp']
runtime=dict(python=platform.python_version(),packages={n:importlib.metadata.version(n) for n in ['CoolProp','cmake','ninja','numpy','playwright','mpmath']},tools={n:hashlib.sha256((W/n).read_bytes()).hexdigest() for n in toolPaths},nativeArchives='Verified matched native B5A control/A1 archives; actual fresh/reused C API replay in B7. No new native compile.',browserVersions={n:json.loads((E/f'activation-{n}.json').read_text())['browserVersion'] for n in ['chromium','webkit']})
p=E/'runtime-final.json';assert not p.exists();p.write_text(json.dumps(runtime,indent=2)+'\n')
print('External logs, licenses, all source/generated files and final tool identities retained')
