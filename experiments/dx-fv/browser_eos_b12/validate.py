"""Validate blocked-delivery completeness and truthful status boundaries locally."""
import csv
import io
import json
from pathlib import Path

B = Path(__file__).resolve().parent
required = ['README', 'DEPLOYMENT_ARCHITECTURE', 'CLOUDFLARE_PROJECT_ISOLATION',
            'ACCESS_CONTROL_REVIEW', 'EXACT_B11_ARTIFACT_AUDIT', 'STATIC_HOSTING_CONFIGURATION',
            'HTTPS_AND_ASSET_VERIFICATION', 'DEPLOYMENT_EXECUTION', 'SCIENTIFIC_PARITY_MATRIX',
            'WORKSTATION_PRESERVATION', 'BROWSER_HTTPS_RESULTS', 'IPAD_OWNER_HANDOFF',
            'SECURITY_AND_LIMITATIONS', 'ENGINEERING_REPORT', 'MECHANICS_REPORT',
            'OWNER_ACTION_CHECKLIST', 'QUALIFICATION_BACKLOG', 'REMOVAL_AND_ROLLBACK']
assert all((B / (p + '.md')).is_file() for p in required)
assert (B / 'QUALIFICATION_BACKLOG.md').read_bytes() == (B.parent / 'browser_eos_b10/QUALIFICATION_BACKLOG.md').read_bytes()
status = json.loads((B / 'milestone-status.json').read_text())
assert status['classification'] == 'B12 PARTIAL / BLOCKED'
assert status['actualDeploymentURL'] is None and status['actualDeploymentId'] is None
assert status['independent']['physicalIPad'] == 'AWAITING OWNER DEVICE REVIEW'
assert status['normalA2IntervalsSeconds'] == [.0001, .0004, .0005]
assert status['normalA2HorizonSeconds'] == .001
deployment = json.loads((B / 'evidence/deployment.json').read_text())
assert not deployment['cloudflareAccountActionsPerformed'] and not deployment['projectCreated']
assert deployment['url'] is None and deployment['uploadedAssetCount'] == 0
access = json.loads((B / 'evidence/access-tests.json').read_text())
assert access['status'] == 'NOT CONFIGURED' and access['actualNetworkReceipts'] == []
https = json.loads((B / 'evidence/https-browser-results.json').read_text())
assert https['chromium'] == https['webkit'] == 'NOT TESTED'
assert not https['localhostSubstitutedForHTTPS']
for p in ['artifact-audit.json', 'preservation.json', 'retained-b11-results.json']:
    assert json.loads((B / 'evidence' / p).read_text())['passed']
rows = list(csv.DictReader(io.StringIO((B / 'milestone-status.csv').read_text())))
assert {r['decision']: r['status'] for r in rows} == status['decisions']
for name in ['staging-tests.json', 'followup-preservation.json']:
    assert json.loads((B / 'evidence' / name).read_text())['passed']
plan = json.loads((B / 'hosting-plan.json').read_text())
assert plan['hostingWrapperExceptionApproved'] and plan['exactStaticRoot'] == '.runtime/staging/approved-preview'
assert plan['actualPagesResponseBehavior'] == 'UNVERIFIED UNTIL DEPLOYMENT'
assert status['followup404']['approvedAdditionalFiles'] == ['404.html']
assert status['followup404']['cloudflareProjectCreationOrUploadAuthorized'] is False
baseline = json.loads(__import__('subprocess').check_output(['git', 'show', '1ab61278159a51fb3f86bb817ea1f03b049443d8:experiments/dx-fv/browser_eos_b12/milestone-status.json'], cwd=B.parents[2]))
assert status['decisions'] == baseline['decisions'] and status['classification'] == baseline['classification']
from worker_upload import NAME, sealed_evidence, verify_archive, verify_checksum
zipraw = (B / NAME).read_bytes()
verify_checksum(zipraw, (B / (NAME + '.sha256')).read_text().split()[0])
verify_archive(zipraw, sealed_evidence()[2])
assert json.loads((B / 'evidence/worker-upload-tests.json').read_text())['passed']
assert status['workerUploadHandoff']['zipSHA256'] == __import__('hashlib').sha256(zipraw).hexdigest()
assert not status['workerUploadHandoff']['cloudflareAccountOperationsPerformed']
print('PASS: required deliverables, preserved backlog, machine tracker and honest blocked/untested boundaries')
