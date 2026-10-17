"""Verify every inherited tracked byte before compilation; apply preserved A1 once."""
import argparse,hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(s,*a):return subprocess.check_output(['git','-C',str(s),*a],text=True).strip()
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--apply-a1',action='store_true');p.add_argument('--label',default='control');a=p.parse_args();s=a.source
assert run(s,'rev-parse','HEAD')=='ae81610e7d23efc57f9d051c8e70a4d66e87537f'
assert run(s,'rev-parse','HEAD^{tree}')=='ca49b8c34df0dae93dcc7fe07e2815a10d967662'
expected=json.loads((X/'browser_eos_b4c/evidence/source-stage-candidateB.json').read_text())['trackedSourceSHA256']
before={n:sha(s/n) for n in expected};assert before==expected,[n for n in expected if before[n]!=expected[n]]
patch=X/'browser_eos_b5a/gate-a.patch'
assert sha(patch)=='2f4b9e675b98a59f3846ede09b767698090083934e080bc11790b723c9d90eeb'
if a.apply_a1:
 run(s,'apply','--check',str(patch));run(s,'apply',str(patch))
after={n:sha(s/n) for n in expected}
changed=[n for n in expected if before[n]!=after[n]]
if a.apply_a1:
 assert set(changed)=={'src/Backends/Helmholtz/VLERoutines.h','src/Backends/Helmholtz/VLERoutines.cpp','src/Backends/Helmholtz/FlashRoutines.cpp'}
 accepted=json.loads((X/'browser_eos_b5a/evidence/source-stage-A1.json').read_text())['trackedSourceSHA256']
 assert after==accepted
 assert subprocess.run(['git','-C',str(s),'apply','--check',str(patch)],capture_output=True).returncode!=0
 run(s,'apply','--reverse','--check',str(patch))
for n in ['browser_eos_backend/flash-44.patch','browser_eos_b4a/liquid-classification.patch','browser_eos_b4b/pt-cache-consistency.patch','browser_eos_b4c/upper-quality-classification.patch']:
 run(s,'apply','--reverse','--check',str(X/n))
out=dict(upstream=run(s,'rev-parse','HEAD'),tree=run(s,'rev-parse','HEAD^{tree}'),source=str(s),label=a.label,trackedSourceSHA256=after,files=len(after),changedFromB4C=changed,exactAcceptedManifest=True,gateAPatchSHA256=sha(patch),gateAAppliedExactlyOnce=a.apply_a1,inheritedPatchesReverseApplicable=True,untracked=run(s,'ls-files','--others','--exclude-standard'))
target=E/f'source-{a.label}.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
print(a.label,len(after),'source hashes match; differences from B4C:',changed)
