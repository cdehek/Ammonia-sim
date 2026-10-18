"""Deliverable/source seal; no measurement reruns, writes only B9B receipts."""
import hashlib,json,subprocess,gzip
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
required=['README.md','PROFILING_DESIGN.md','NONLINEAR_WORK_CENSUS.md','PROPERTY_EVALUATION_AUDIT.md','JACOBIAN_AND_LINE_SEARCH_COST.md','COLD_VS_WARM_DIFFICULTY.md','INSTRUMENTATION_OVERHEAD.md','BROWSER_PERFORMANCE_MATRIX.md','OPTIMIZATION_HYPOTHESES.md','ENGINEERING_REPORT.md','MECHANICS_REPORT.md']
assert all((B/n).is_file() for n in required)
assert json.loads((E/'scientific-parity.json').read_text())['passed']
for engine in ['chromium','webkit']:
 for stage in ['baseline','passive','matrix','validation','failure']:
  v=json.loads(gzip.decompress((E/f'{stage}-{engine}.json.gz').read_bytes()));assert v['passed']
 for r in json.loads((E/'scientific-parity.json').read_text())['engines'][engine].values():assert r['savedFullScientificRowsAndObserverAttemptsExact']
manifest={}
for n in ['profile.mjs','diagnostic-bundle.mjs','worker.mjs','run-browser.py','failure-copy.mjs','run-node.mjs','isolated/engine.js','isolated/coupled-model.cjs']:
 p=B/n;manifest[n]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
for n in ['accepted-bundle.mjs','service.mjs','values.mjs']:
 p=B.parent/'browser_eos_b9'/n;manifest['../browser_eos_b9/'+n]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
(E/'measurement-source-manifest.json').write_text(json.dumps(dict(files=manifest,originalSource='be9eb35a4ddf5098e685182f8104685127c6a6ee',scienceReference='355db28d853817e1931295d6ec2f007876d53f90',finalMatrix='matrix-*.json.gz',excluded='All superseded-* and *harness-failed* receipts',sourceCopyStatus='Profiling-only; not accepted A2'),indent=2)+'\n')
files={}
for p in sorted(B.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name in ['deliverables-manifest.json','postpush.json','postpush-audit.json','remote-postpush.tsv','pr3-postpush.json']:continue
 files[str(p.relative_to(B))]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
(E/'deliverables-manifest.json').write_text(json.dumps(dict(requiredDeliverables=required,files=files,selfHashExcluded=True,postpushReceiptsExcluded=True,revision='pre-final-commit'),indent=2)+'\n')
print('Sealed',len(files),'B9B files; mandatory deliverables and final browser receipts PASS')
