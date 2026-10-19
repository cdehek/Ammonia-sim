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
print('PASS: required deliverables, preserved backlog, machine tracker and honest blocked/untested boundaries')
