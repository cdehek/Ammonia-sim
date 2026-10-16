"""Verify history, source ownership and preserved artifacts; publish build identities."""
import hashlib,json,lzma,os,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4B_EVIDENCE',B/'evidence'));S=Path('/workspace/coolprop-b4b')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(*a):return subprocess.check_output(a).decode().strip()
def save(n,d):
 p=E/n;assert not p.exists(),p;p.write_text(json.dumps(d,indent=2)+'\n')
start=json.loads((E/'preservation-start.json').read_text());changed=[p for p,h in start['trackedSHA256'].items()if sha(R/p)!=h];assert not changed
verified=[]
for folder,filename,key in [('browser_eos_backend','build-provenance.json','artifacts'),('browser_eos_b4a','provenance.json','artifacts'),('browser_eos_b3','provenance.json','browserArtifacts')]:
 p=B.parent/folder/'evidence'/filename;d=json.loads(p.read_text())
 for n,q in d[key].items():
  f=(R/n)if folder=='browser_eos_b3'else p.parent.parent/n
  assert sha(f)==q['sha256'],f;verified.append(dict(file=str(f.relative_to(R)),sha256=q['sha256']))
 if folder=='browser_eos_backend':
  for n,q in d['officialArtifacts'].items():
   f=B.parent/n;assert sha(f)==q['sha256'];verified.append(dict(file=str(f.relative_to(R)),sha256=q['sha256']))
  assert sha(p.parent.parent/'source/FlashRoutines-original.cpp')==d['originalFlashSHA256']
  assert sha(p.parent.parent/'source/FlashRoutines-44.cpp')==d['experimentalFlashSHA256']
  stage=json.loads((E/'source-stage-controlA.json').read_text())['trackedSourceSHA256'];different=[n for n,h in d['patchedTrackedSourceFiles'].items()if stage[n]!=h]
  assert different==['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp']
  raw=subprocess.check_output(['git','-C',str(S),'show','HEAD:'+different[0]]);assert hashlib.sha256(raw).hexdigest()==d['patchedTrackedSourceFiles'][different[0]]
for m in [B.parent/'browser_eos_b3/evidence/native-binaries.json',B.parent/'browser_eos_b4a/evidence/native-binaries.json',E/'native-binaries.json']:
 for n,q in json.loads(m.read_text()).items():
  f=m.parent.parent/q['archive'];raw=lzma.decompress(f.read_bytes());assert sha(f)==q['archiveSHA256']and hashlib.sha256(raw).hexdigest()==q['sha256'];verified.append(dict(file=str(f.relative_to(R)),sha256=q['archiveSHA256'],binarySHA256=q['sha256']))
old=json.loads((B.parent/'browser_eos_b3/evidence/provenance.json').read_text())['wheelBinaries']
for path,q in old.items():
 root='/workspace/b4b-tools72/CoolProp'if'b3-runtime72'in path else'/workspace/b4b-tools/CoolProp';p=Path(root)/Path(path).name;assert sha(p)==q['sha256'];verified.append(dict(referenceWheel=str(p),sha256=q['sha256']))
control=json.loads((E/'source-stage-controlA.json').read_text())['trackedSourceSHA256'];candidate=json.loads((E/'source-stage-candidateB.json').read_text())['trackedSourceSHA256'];functional=[n for n in control if candidate[n]!=control[n]];assert functional==['src/Backends/Helmholtz/FlashRoutines.cpp']
assert all(sha(S/n)==h for n,h in candidate.items())
assert cmd('git','-C',str(S),'rev-parse','HEAD')=='ae81610e7d23efc57f9d051c8e70a4d66e87537f'
artifacts={str(p.relative_to(B)):dict(bytes=p.stat().st_size,sha256=sha(p))for directory in ['vendor','artifacts']for p in sorted((B/directory).rglob('*'))if p.is_file()}
save('historical-artifact-hash-verification.json',dict(checks=verified,allPass=True,trackedFilesUnchanged=len(start['trackedSHA256'])))
save('provenance.json',dict(start=start['commit'],branch=cmd('git','-C',str(R),'branch','--show-current'),upstreamCommit=cmd('git','-C',str(S),'rev-parse','HEAD'),upstreamTree=cmd('git','-C',str(S),'rev-parse','HEAD^{tree}'),functionalSourceFiles=functional,originalSourceSHA256={n:control[n]for n in functional},patchedSourceSHA256={n:candidate[n]for n in functional},B4AclassifierSHA256=candidate['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp'],unchangedGenericSolversSHA256=candidate['src/Solvers.cpp'],B1patchSHA256=sha(B.parent/'browser_eos_backend/flash-44.patch'),B4ApatchSHA256=sha(B.parent/'browser_eos_b4a/liquid-classification.patch'),B4BpatchSHA256=sha(B/'pt-cache-consistency.patch'),preimplementationAlgorithmSHA256=sha(B/'ALGORITHM.md'),buildVersions=json.loads((E/'build-versions.json').read_text()),dependencies='dependency-verification.json',nativeBinaries='native-binaries.json',artifacts=artifacts,changedOriginalFiles=changed,originalTrackedFiles=len(start['trackedSHA256']),acceptedA2='accepted-a2-verification.json',sameEOSReference=True,fullQualification=False,physicalIPad=False))
print('Historical hashes, original tracked files, source scope and new binary provenance verified.')
