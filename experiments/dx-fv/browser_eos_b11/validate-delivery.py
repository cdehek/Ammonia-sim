"""Read-only completeness/parity validation of retained B11 receipts."""
import gzip,json,subprocess
from pathlib import Path
from audit import B,R
required=['README.md','ENGINEERING_REPORT.md','MECHANICS_REPORT.md','PREVIEW_PACKAGING_DESIGN.md','ASSET_MANIFEST.md','SOURCE_AND_BUILD_AUDIT.md','SERVER_AND_ORIGIN_COMPATIBILITY.md','SCIENTIFIC_PARITY_MATRIX.md','ORIGINAL_WORKSTATION_REGRESSION.md','TRAINING_EXPORT_PARITY.md','BROWSER_PERFORMANCE.md','OFFLINE_COMPATIBILITY.md','PHYSICAL_IPAD_REVIEW.md','PREVIEW_HOSTING_HANDOFF.md','FAILURE_AND_LIFECYCLE.md','PROTECTED_REFS_AND_PR3_AUDIT.md','build.py','preview.zip','preview.zip.sha256','milestone-status.json','milestone-status.csv']
assert all((B/p).is_file() for p in required)
E=B/'evidence'
def read(p):
 f=E/p;return json.loads(gzip.decompress(f.read_bytes()) if p.endswith('.gz') else f.read_text())
for browser in ['chromium','webkit']:
 for name in ['integration','review','isolation']:assert read(f'{name}-{browser}.json.gz')['passed']
 for name in ['portability','performance']:assert read(f'{name}-{browser}.json')['passed']
 for row in read(f'integration-{browser}.json.gz')['science']:assert row['exactSavedB10AcceptedStateRecordAndAttempts'] and [x['clock'] for x in row['rows']]==[0,.0001,.0005,.001]
 rows=read(f'isolation-{browser}.json.gz')['training'];assert len(rows)==5 and all(r['byteExact'] for r in rows)
 for row in rows:
  assert (E/f'training-{browser}/{row["exercise"]}.json').read_bytes()==(B.parent/f'browser_eos_b10/evidence/baseline-training/{browser}-{row["exercise"]}-evidence.json').read_bytes()
 assert len(list(E.glob(f'integration-{browser}-*.png')))>=8
assert not read('regression-comparison.json')['newRequiredSuiteRegressions']
assert read('source-integrity.json')['passed'] and read('reproducibility.json')['passed'] and read('preservation.json')['passed']
status=json.loads((B/'milestone-status.json').read_text());assert status['independent']['physicalIPad']=='AWAITING USER' and status['gates']['G_deployment_authorization']=='NO-GO' and status['normalA2HorizonSeconds']==.001
prefix='experiments/dx-fv/browser_eos_b11/'
assert all(x.startswith(prefix) for x in subprocess.check_output(['git','diff','--name-only','a49c5c4ade306fe02117139cf81c30a59727a7b1'],cwd=R).decode().splitlines())
print('PASS: required artifacts, both browsers, all ten full exports, exact saved B10 parity, screenshots and independent status boundaries')
