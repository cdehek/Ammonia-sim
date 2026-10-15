"""Record source/toolchain/artifact identities; never inspect credentials."""
from pathlib import Path
import hashlib,json,platform,subprocess
B=Path(__file__).resolve().parent
S=Path('/workspace/coolprop-b1');D=Path('/workspace/b1-runtime/build30/_deps');SDK=Path('/workspace/emsdk-b1')
def run(args,cwd=None):return subprocess.check_output(args,cwd=cwd,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(path):
    files={}
    for p in sorted(path.rglob('*')):
        if p.is_file() and '.git' not in p.relative_to(path).parts:
            files[str(p.relative_to(path))]=sha(p)
    return {'files':len(files),'sha256OfSortedPathHashJSON':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
deps={}
for p in sorted(D.glob('*-src')):
    g=p/'.git'
    deps[p.name]={'sourceTree':tree(p)}
    if g.exists():deps[p.name].update(commit=run(['git','rev-parse','HEAD'],p),trackedStatus=run(['git','status','--porcelain=v1','--untracked-files=no'],p),submodules=run(['git','submodule','status','--recursive'],p))
    else:deps[p.name]['archivePin']='See exact URL and SHA256 in upstream-dependencies.cmake'
tracked=run(['git','ls-tree','-r','--name-only','HEAD'],S).splitlines()
manifest={n:sha(S/n) for n in tracked}
original=run(['git','show','HEAD:src/Backends/Helmholtz/FlashRoutines.cpp'],S)+'\n'
(B/'source').mkdir(exist_ok=True)
(B/'source/FlashRoutines-original.cpp').write_text(original)
(B/'source/FlashRoutines-44.cpp').write_bytes((S/'src/Backends/Helmholtz/FlashRoutines.cpp').read_bytes())
for src,dst in [('cmake/dependencies.cmake','upstream-dependencies.cmake'),('CMakeLists.txt','upstream-CMakeLists.txt'),('LICENSE','LICENSE-CoolProp.txt')]:
    (B/'source'/dst).write_bytes((S/src).read_bytes())
generated={str(p.relative_to(S)):sha(p) for p in sorted((S/'include').glob('*.h')) if str(p.relative_to(S)) not in manifest}
tools={}
for rel in ['upstream/emscripten/emcc.py','upstream/emscripten/emscripten-version.txt','upstream/bin/clang','upstream/bin/wasm-ld','upstream/bin/wasm-opt','node/22.16.0_64bit/bin/node']:
    p=SDK/rel
    if p.exists():tools[rel]={'sha256':sha(p),'bytes':p.stat().st_size}
data={'upstreamRepository':'https://github.com/CoolProp/CoolProp.git','upstreamCommit':run(['git','rev-parse','HEAD'],S),
 'upstreamGitTree':run(['git','rev-parse','HEAD^{tree}'],S),'sourceDiff':run(['git','diff','--','src/Backends/Helmholtz/FlashRoutines.cpp'],S),
 'trackedSourceStatus':run(['git','status','--porcelain=v1','--untracked-files=no'],S),'originalFlashSHA256':sha(B/'source/FlashRoutines-original.cpp'),
 'experimentalFlashSHA256':sha(B/'source/FlashRoutines-44.cpp'),'patchedTrackedSourceFiles':manifest,'generatedHeaders':generated,
 'dependencies':deps,'emsdkRepository':'https://github.com/emscripten-core/emsdk.git','emsdkCommit':run(['git','rev-parse','HEAD'],SDK),
 'emscripten':run([str(SDK/'upstream/emscripten/emcc'),'--version']),'clang':run([str(SDK/'upstream/bin/clang'),'--version']),
 'toolHashes':tools,'cmake':run(['/workspace/b1-runtime/python/bin/cmake','--version']),
 'ninja':run(['/workspace/b1-runtime/python/bin/ninja','--version']),'python':platform.python_version(),
 'artifacts':{str(p.relative_to(B)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted((B/'vendor').glob('*/*'))},
 'officialArtifacts':{str(p.relative_to(B.parent)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted((B.parent/'browser_eos/vendor').glob('*.*/*')) if p.suffix in ['.js','.wasm']},
 'buildType':'Release','generator':'Ninja','parallelJobs':2,
 'flagsEvidence':['evidence/compile-commands.json','evidence/CMakeCache.txt','source/upstream-CMakeLists.txt'],
 'initialBuild':'unmodified full source compile, then patch/recompile only FlashRoutines.cpp and relink; identical flags/dependencies',
 'rebuild':'A separate empty object directory compiles all translation units again with explicit CPM source overrides pointing to identical dependency files.',
 'versionWarning':'Both experimental artifacts report upstream 8.0.0/revision. The external manifest and distinct build30/build44 paths identify the experimental modification; never identify build44 by version alone.'}
(B/'evidence/build-provenance.json').write_text(json.dumps(data,indent=2)+'\n')
print(data['upstreamCommit'],data['originalFlashSHA256'],data['experimentalFlashSHA256'])
