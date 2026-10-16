"""Finalize binary, tool, source, input and preservation identities."""
import hashlib,importlib.metadata,json,os,platform,shutil,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'));S=Path('/workspace/coolprop-b4a')
def command(*a):return subprocess.check_output(a).decode().strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
start=json.loads((E/'preservation-start.json').read_text());changed=[p for p,h in start['trackedSHA256'].items()if sha(R/p)!=h];assert not changed,changed
artifacts={str(p.relative_to(B)):dict(bytes=p.stat().st_size,sha256=sha(p))for folder in ['artifacts','vendor']for p in sorted((B/folder).rglob('*'))if p.is_file()}
native={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in Path('/workspace/b4a-native-artifacts').glob('*.so')}
versions=dict(platform=platform.platform(),python=platform.python_version(),compiler=command('g++','--version'),compilerSHA256=sha(Path(shutil.which('g++')).resolve()),cmake=command('/workspace/b4a-tools/cmake/data/bin/cmake','--version'),ninja=command('/workspace/b4a-tools/bin/ninja','--version'),emsdkCommit=command('git','-C','/workspace/emsdk-b4a','rev-parse','HEAD'),emcc=command('/workspace/emsdk-b4a/upstream/emscripten/emcc','--version'),clang=command('/workspace/emsdk-b4a/upstream/bin/clang','--version'),SDKNode=command('/workspace/emsdk-b4a/node/22.16.0_64bit/bin/node','--version'),packages={n:importlib.metadata.version(n)for n in ['CoolProp','numpy','playwright','cmake','ninja']})
deb={p.name:sha(p)for p in Path('/workspace/b4a-debs').glob('*.deb')}
out=dict(start='4e1295be9493d8bce4ca35ee0cf61accb7465226',branch=command('git','-C',str(R),'branch','--show-current'),upstreamCommit=command('git','-C',str(S),'rev-parse','HEAD'),upstreamTree=command('git','-C',str(S),'rev-parse','HEAD^{tree}'),patchSHA256=sha(B/'liquid-classification.patch'),B1patchSHA256=sha(B.parent/'browser_eos_backend/flash-44.patch'),algorithmSHA256=sha(B/'ALGORITHM.md'),versions=versions,dependencyEvidence='dependency-verification.json',artifacts=artifacts,nativeUncompressed=native,browserExtraDebs=deb,originalTrackedFiles=len(start['trackedSHA256']),changedOriginalFiles=changed,inputB3SHA256=sha(B.parent/'browser_eos_b3/inputs.json'),acceptedA2Verification='accepted-a2-verification.json',sourceStages=['source-stage-control44.json','source-stage-liquid44.json','source-stage-diagnostic44.json'],fullQualification=False,physicalIPad=False)
target=E/'provenance.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
print('Original tracked files unchanged:',len(start['trackedSHA256']),'artifacts:',len(artifacts))
