"""Complete B4C source/artifact identities, preserving every inherited byte."""
import hashlib,json,lzma,os,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));S=Path('/workspace/coolprop-b4c')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((E/n).read_text())
def cmd(*a):return subprocess.check_output(a).decode().strip()
def save(n,x):p=E/n;assert not p.exists();p.write_text(json.dumps(x,indent=2)+'\n')
start=read('preservation-start.json');changed=[n for n,h in start['trackedSHA256'].items() if sha(R/n)!=h];assert not changed
before=read('source-stage-controlA.json')['trackedSourceSHA256'];after=read('source-stage-candidateB.json')['trackedSourceSHA256'];different=[n for n,h in before.items() if after[n]!=h];assert different==['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp']
assert all(sha(S/n)==h for n,h in after.items())
name=different[0];a=(S/name).read_text();a=a.replace('Q > 1 + 1e-9 || (Q > 1 && (other == iHmolar || other == iSmolar || other == iUmolar))','Q > 1 + 1e-9');assert hashlib.sha256(a.encode()).hexdigest()==before[name]
assert cmd('git','-C',str(S),'rev-parse','HEAD')=='ae81610e7d23efc57f9d051c8e70a4d66e87537f'
assert before['src/Solvers.cpp']==after['src/Solvers.cpp'];assert before['src/Backends/Helmholtz/FlashRoutines.cpp']==after['src/Backends/Helmholtz/FlashRoutines.cpp']
for label,v in read('native-binaries.json').items():
 p=B/v['archive'];assert sha(p)==v['archiveSHA256'] and hashlib.sha256(lzma.decompress(p.read_bytes())).hexdigest()==v['sha256']
dependencies=read('dependency-verification-attempt.json');assert all(v['match'] for v in dependencies.values())
save('dependency-verification.json',dict(allNineMatch=True,dependencies=dependencies))
oldLoader=(B.parent/'browser_eos_b4b/loader.mjs').read_text();loader=(B/'loader.mjs').read_text();expected=oldLoader.replace("controlA:'./vendor/controlA',rebuiltA:'./vendor/controlA'","controlA:'../browser_eos_b4b/vendor/candidateB',rebuiltA:'./vendor/controlA'").replace('Unknown isolated B4B build','Unknown isolated B4C build');assert expected==loader
artifacts={str(p.relative_to(B)):dict(bytes=p.stat().st_size,sha256=sha(p)) for directory in ['vendor','artifacts'] for p in sorted((B/directory).rglob('*')) if p.is_file()}
save('provenance.json',dict(startCommit=start['commit'],branch=cmd('git','-C',str(R),'branch','--show-current'),upstreamCommit=cmd('git','-C',str(S),'rev-parse','HEAD'),upstreamTree=cmd('git','-C',str(S),'rev-parse','HEAD^{tree}'),functionalFiles=different,sourceBeforeSHA256={n:before[n] for n in different},sourceAfterSHA256={n:after[n] for n in different},inheritedFlashSHA256=after['src/Backends/Helmholtz/FlashRoutines.cpp'],unchangedGenericSolversSHA256=after['src/Solvers.cpp'],patchSHA256=sha(B/'upper-quality-classification.patch'),algorithmSHA256=sha(B/'ALGORITHM.md'),preimplementation=read('preimplementation-decision.json'),nativeBinaries=read('native-binaries.json'),scientificNativeControl='../browser_eos_b4b/artifacts/libCoolProp-candidateB.so.xz',scientificBrowserControl='../browser_eos_b4b/vendor/candidateB',matchedPerformanceControls='newly rebuilt controlA native/WASM; complete scientific equivalence independently verified',buildVersions=read('build-versions.json'),dependencies='dependency-verification.json',artifacts=artifacts,startingTrackedFiles=len(start['trackedSHA256']),changedStartingFiles=changed,loaderExceptionHandlingUnchanged=True,EOSAndFluidDataUnchanged=True,acceptedA2=read('accepted-a2-verification.json'),fullQualification=False,physicalIPad=False,deployment=False))
print('All inherited bytes, source scope, native archives, loader preservation and artifact hashes verified')
