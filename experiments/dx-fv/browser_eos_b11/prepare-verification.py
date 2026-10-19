"""Derive B11 test adapters; original test/assertion bodies remain unchanged."""
import hashlib,json,difflib
from pathlib import Path
B=Path(__file__).resolve().parent;O=B.parent/'browser_eos_b10';receipts=[]
def emit(n,text):
 old=(O/n).read_text();(B/n).write_text(text);receipts.append({'path':n,'source':'B10/'+n,'sourceSHA256':hashlib.sha256(old.encode()).hexdigest(),'derivedSHA256':hashlib.sha256(text.encode()).hexdigest(),'diff':''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True)))})
for n in ['review.html','review-worker.mjs','reference-worker.mjs']:
 emit(n,(O/n).read_text())
n='bridge-tests.mjs';s=(O/n).read_text()
for x in ['client.mjs','snapshot.mjs','view.mjs','worker.mjs']:s=s.replace("'./"+x+"'","'./preview/"+x+"'")
emit(n,s)
# Mechanical exact copy is test-only; never a runtime dependency.
(B/'isolated').mkdir(exist_ok=True);(B/'isolated/coupled-model.cjs').write_bytes((O/'isolated/coupled-model.cjs').read_bytes())
for n in ['run-integration.py','run-isolation.py','run-render.py','run-scientific-review.py']:
 s=(O/n).read_text();s=s.replace('/experiments/dx-fv/browser_eos_b10/','/experiments/dx-fv/browser_eos_b11/preview/')
 if n=='run-scientific-review.py':s=s.replace('browser_eos_b11/preview/review.html','browser_eos_b11/review.html')
 s=s.replace('import("./bridge-tests.mjs")','import("../bridge-tests.mjs")').replace("new Worker('./reference-worker.mjs'","new Worker('../reference-worker.mjs'")
 s=s.replace("'**/browser_eos_b9c/candidate-bundle.mjs'","'**/preview/science/candidate-bundle.mjs'")
 s=s.replace("'**/browser_eos_b10/worker.mjs*'","'**/preview/worker.mjs*'")
 s=s.replace("url+'artifacts/pinned-workstation.html'","url+'../../browser_eos_b10/artifacts/pinned-workstation.html'")
 s=s.replace("(B/'index.html').as_uri()","(B/'preview/index.html').as_uri()")
 s=s.replace("import('../browser_eos_b9/values.mjs')","import('./support/values.mjs')")
 s=s.replace("(E/f'baseline-training/","(O/f'evidence/baseline-training/")
 s=s.replace("B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'","B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';O=B.parent/'browser_eos_b10'")
 if n=='run-integration.py':
  # Compare entire exactly encoded accepted state/record and every attempt with saved B10.
  marker="r['exactSavedControl']=True;"
  s=s.replace(marker,"b10=json.loads(gzip.decompress((O/f'evidence/integration-{name}.json.gz').read_bytes()));prior=next(v for v in b10['science'] if v['fixture']==fixture);assert r['checkpointHashes']==prior['checkpointHashes'];assert r['fullAcceptedDetails']==prior['fullAcceptedDetails'];assert r['attemptsHash']==prior['attemptsHash'];r['exactSavedB10AcceptedStateRecordAndAttempts']=True;"+marker)
 emit(n,s)
# A static root that serves only packaged assets for candidate requests.
n='run-original.cjs';s=(O/n).read_text();s=s.replace("path.resolve(R,'.'+pathname)","path.resolve(mode==='baseline'?root:path.join(B,'preview'),'.'+pathname)")
s=s.replace("!file.startsWith(R+path.sep)","!file.startsWith(B+path.sep)")
emit(n,s)
(B/'evidence/test-adapter-derivation.json').write_text(json.dumps(receipts,indent=2)+'\n')
