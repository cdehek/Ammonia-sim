"""Apply only the reviewed caloric upper-quality dispatch at both decision sites."""
import difflib,hashlib,json,subprocess,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));S=Path(sys.argv[1]);name='src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp'
old=json.loads((E/'source-stage-controlA.json').read_text())['trackedSourceSHA256']
assert all(hashlib.sha256((S/n).read_bytes()).hexdigest()==h for n,h in old.items())
assert (E/'preimplementation-thermodynamics.json').exists()
assert (E/'preimplementation-decision.json').exists()
p=S/name;before=p.read_text();anchor='} else if (Q > 1 + 1e-9) {'
assert before.count(anchor)==2
after=before.replace(anchor,'} else if (Q > 1 + 1e-9 || (Q > 1 && (other == iHmolar || other == iSmolar || other == iUmolar))) {')
patch=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
target=B/'upper-quality-classification.patch'
if target.exists():assert target.read_text()==patch
else:target.write_text(patch)
subprocess.run(['git','-C',str(S),'apply','--check',str(target)],check=True)
subprocess.run(['git','-C',str(S),'apply',str(target)],check=True)
current={n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in old}
assert [n for n in old if current[n]!=old[n]]==[name]
assert (S/name).read_text().replace('Q > 1 + 1e-9 || (Q > 1 && (other == iHmolar || other == iSmolar || other == iUmolar))','Q > 1 + 1e-9')==before
stage=E/'source-stage-candidateB.json';assert not stage.exists();stage.write_text(json.dumps(dict(trackedSourceSHA256=current,onlyChangedFile=name,patchSHA256=hashlib.sha256(patch.encode()).hexdigest(),inheritedPatchesPreservedExactly=True),indent=2)+'\n')
print(patch)
