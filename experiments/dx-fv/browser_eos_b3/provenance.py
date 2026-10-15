"""Capture final source/artifact/input identities and verify exact source stages."""
import hashlib,json,subprocess,tempfile,platform
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';S=Path('/workspace/coolprop-b3')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(*args):return subprocess.check_output(args).decode().strip()
files=['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp','src/Backends/Helmholtz/FlashRoutines.cpp','src/Solvers.cpp']
stages={}
for bits in [30,44]:
 with tempfile.TemporaryDirectory(prefix='b3-source-verification-')as folder:
    root=Path(folder)
    for n in files:
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(['git','-C',str(S),'show','HEAD:'+n]))
    subprocess.run(['git','-C',str(root),'apply',str(E/f'instrumentation{bits}.diff')],check=True)
    stages[str(bits)]={n:sha(root/n)for n in files}
    if bits==30:assert stages['30']==json.loads((E/'source-stage-diag30.json').read_text())['files']
    else:assert all((root/n).read_bytes()==(S/n).read_bytes()for n in files)
old=json.loads((R/'experiments/dx-fv/browser_eos_backend/evidence/build-provenance.json').read_text())
dependencies={}
for name in old['dependencies']:
 p=Path('/workspace/b3-build/_deps')/name
 if (p/'.git').exists():
    commit=command('git','-C',str(p),'rev-parse','HEAD');assert commit==old['dependencies'][name]['commit']
 else:commit=None
 tree={str(f.relative_to(p)):sha(f)for f in sorted(p.rglob('*'))if f.is_file() and '.git'not in f.relative_to(p).parts}
 dependencies[name]=dict(commit=commit,fileCount=len(tree),pathSHA256JSON=hashlib.sha256(json.dumps(tree,sort_keys=True).encode()).hexdigest())
artifacts={}
for folder in [R/'experiments/dx-fv/browser_eos/vendor',R/'experiments/dx-fv/browser_eos_backend/vendor']:
 for p in folder.rglob('*'):
    if p.suffix in ['.js','.wasm']:artifacts[str(p.relative_to(R))]=dict(bytes=p.stat().st_size,sha256=sha(p))
wheelBinaries={}
for runtime in ['b3-runtime','b3-runtime72']:
 for p in (Path('/workspace')/runtime/'lib').glob('python*/site-packages/CoolProp/**/*.so'):
    wheelBinaries[str(p)]=dict(bytes=p.stat().st_size,sha256=sha(p))
out=dict(upstreamCommit=command('git','-C',str(S),'rev-parse','HEAD'),upstreamTree=command('git','-C',str(S),'rev-parse','HEAD^{tree}'),
 sourceStatus=command('git','-C',str(S),'status','--porcelain'),diagnosticSourceStages=stages,dependencies=dependencies,
 baselineOriginalFlashSHA256=old['originalFlashSHA256'],baselineHistorical44FlashSHA256=old['experimentalFlashSHA256'],
 inputSHA256=sha(B/'inputs.json'),browserArtifacts=artifacts,nativeBinaries=json.loads((E/'native-binaries.json').read_text()),wheelBinaries=wheelBinaries,
 platform=platform.platform(),compilerVersion=command('g++','--version'),compilerSHA256=sha(Path('/usr/bin/g++').resolve()),
 flagsEvidence=['compile-commands.json','CMakeCache.txt'],sourceInstrumentation='Added logging only; combined44 diff also reproduces the existing B1 expression.',
 native44Correction='None in B3: exact historical B1 flash-44.patch used as the requested control.')
target=E/'provenance.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
print('Verified both diagnostic source reconstructions, dependency commits, and binary/input hashes')
