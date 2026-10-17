"""Only the verified three A1 files enter the common incremental build tree."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';W=Path('/workspace/b7-work')
control=json.loads((E/'source-control.json').read_text())['trackedSourceSHA256'];candidate=json.loads((E/'source-candidate.json').read_text())['trackedSourceSHA256']
for n,h in control.items():assert hashlib.sha256((W/'upstream'/n).read_bytes()).hexdigest()==h,n
changed=[n for n in candidate if candidate[n]!=control[n]];assert len(changed)==3
for n in changed:(W/'upstream'/n).write_bytes((W/'candidate'/n).read_bytes())
for n,h in candidate.items():assert hashlib.sha256((W/'upstream'/n).read_bytes()).hexdigest()==h,n
(E/'source-transition.json').write_text(json.dumps(dict(commonBuildSource=str(W/'upstream'),changed=changed,completeCandidateManifestMatch=True,unchangedFiles=1779,reason='Reuse unchanged objects under identical toolchain, paths and dependencies.'),indent=2)+'\n')
print('Common build source matches independently reconstructed exact A1')
