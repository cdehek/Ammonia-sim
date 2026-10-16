"""Record source, dependencies, wheels, compiler, artifacts and preservation."""
import hashlib,json,subprocess,platform,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));R=B.parents[2];S=Path('/workspace/coolprop-b5')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
expected=read(B.parent/'browser_eos_b4c/evidence/dependency-verification.json')['dependencies'];deps={}
for n,v in expected.items():
 p=Path('/workspace/b5-native-build/_deps')/n;files={str(f.relative_to(p)):sha(f)for f in sorted(p.rglob('*'))if f.is_file()and'.git'not in f.relative_to(p).parts};h=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest();deps[n]=dict(fileCount=len(files),pathSHA256JSON=h,match=h==v['pathSHA256JSON'])
assert all(x['match']for x in deps.values())
expectedW=read(B.parent/'browser_eos_b3/evidence/provenance.json')['wheelBinaries'];wheels={}
for tools in ['b5-tools','b5-tools72']:
 for p in sorted((Path('/workspace')/tools/'CoolProp').glob('*.so')):
  h=sha(p);wheels[str(p)]=dict(sha256=h,matchesHistorical=any(x['sha256']==h for x in expectedW.values()))
assert all(v['matchesHistorical']for v in wheels.values())
old=read(E/'starting-file-hashes.json');changed=[n for n,h in old.items()if sha(R/n)!=h]
assert not changed
versions={}
for label,cmd in [('gcc',['g++','--version']),('python',[sys.executable,'--version']),('cmake',['/workspace/b5-tools/bin/cmake','--version']),('ninja',['/workspace/b5-tools/bin/ninja','--version'])]:versions[label]=subprocess.check_output(cmd,text=True).splitlines()[0]
source=read(B.parent/'browser_eos_b4c/evidence/source-stage-candidateB.json')['trackedSourceSHA256'];sourceChanged=[n for n,h in source.items()if sha(S/n)!=h];assert not sourceChanged
out=dict(startingCommit='3622000309cacdd35aaaebbb805ae40d27c75603',branch=subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=S,text=True).strip(),sourceTree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=S,text=True).strip(),sourceRestoredToB4C=True,sourceFilesVerified=len(source),sourceMismatches=sourceChanged,dependencies=deps,wheelBinaries=wheels,versions=versions,platform=platform.platform(),binaries=read(E/'native-binaries.json'),diagnosticOnly=True,functionalRepair=False,originalTrackedFiles=len(old),changedStartingFiles=changed,acceptedContract='../browser_eos_backend/SOLVER_CONTRACT.md',loaderUnchanged=True,fullA2Qualification=False,productionIntegration=False,deployment=False)
(E/'provenance.json').write_text(json.dumps(out,indent=2)+'\n');print('provenance verified; historical files',len(old),'source',len(source),'dependencies',len(deps),'wheels',len(wheels))
