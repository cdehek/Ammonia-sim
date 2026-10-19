"""Deterministic preservation and separate-manifest checks for the approved stage."""
import json
import subprocess
from stage import B, R, FOLLOWUP, IDENTITY, ZIP_SHA, canonical, original_package, sha, require
from verify import preservation

subprocess.check_call(['git', 'merge-base', '--is-ancestor', FOLLOWUP, 'HEAD'], cwd=R)
preservation()  # hashes protected B11 history; does not run numerical/browser tests
original_files, original = original_package()
paths = ['staging-original-manifest.json', 'hosting-wrapper-manifest.json', 'staged-deployment-manifest.json']
o, w, d = [json.loads((B / 'evidence' / p).read_bytes()) for p in paths]
require(o == original, 'Original staging manifest does not describe exact B11')
require(w['hostingWrapperIdentity'] == sha(canonical({k: v for k, v in w.items() if k != 'hostingWrapperIdentity'})), 'Wrapper identity mismatch')
require(w['originalManifestSHA256'] == sha(canonical(o)) and w['originalFilesModified'] == 0, 'Wrapper linkage mismatch')
extra = {'path': '404.html', 'bytes': len((B / 'hosting/404.html').read_bytes()), 'mime': 'text/html', 'sha256': sha((B / 'hosting/404.html').read_bytes())}
require(w['addedAssets'] == [extra], 'More than the approved 404 file added')
require(d['assets'] == sorted(o['assets'] + [extra], key=lambda a: a['path']) and d['assetCount'] == 14, 'Combined asset set mismatch')
require(d['originalB11PackageIdentity'] == w['originalB11PackageIdentity'] == IDENTITY, 'Canonical science identity changed')
require(d['hostingWrapperIdentity'] == w['hostingWrapperIdentity'], 'Combined wrapper identity mismatch')
receipts = json.loads((B / 'evidence/staging-sha256.json').read_bytes())
require(receipts['manifests'] == {p: sha((B / 'evidence' / p).read_bytes()) for p in paths}, 'Manifest hash receipt mismatch')
require(receipts['root404SHA256'] == extra['sha256'] and receipts['originalB11ZIP_SHA256'] == ZIP_SHA, 'Artifact receipt mismatch')
baseline_manifest = subprocess.check_output(['git', 'show', FOLLOWUP + ':experiments/dx-fv/browser_eos_b12/evidence/deployment-package-manifest.json'], cwd=R)
require((B / 'evidence/deployment-package-manifest.json').read_bytes() == baseline_manifest, 'Original B12 deployment manifest overwritten')
require({a['path']: a for a in o['assets']} == {a['path']: {k: a[k] for k in ['path', 'bytes', 'mime', 'sha256']} for a in json.loads(baseline_manifest)['assets']}, 'Original file hashes changed')
changed = subprocess.check_output(['git', 'diff', '--name-only', FOLLOWUP], cwd=R).decode().splitlines()
untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=R).decode().splitlines()
require(all(p.startswith('experiments/dx-fv/browser_eos_b12/') for p in changed + untracked), 'Follow-up change outside B12')
tests = json.loads((B / 'evidence/staging-tests.json').read_bytes())
require(tests['passed'] and tests['actualCloudflarePages'] == 'NOT VERIFIED; NO DEPLOYMENT', 'Local test boundaries changed')
report = {'passed': True, 'followupStartingCommit': FOLLOWUP, 'allHistoricalB11TrackedFilesUnchanged': 3438,
          'originalB11ZIP_SHA256': ZIP_SHA, 'originalB11PackageIdentity': IDENTITY,
          'originalFilesVerifiedUnchanged': len(original_files), 'addedStagedFiles': ['404.html'],
          'originalB12DeploymentManifestUnchanged': True, 'followupChangesConfinedToB12': True,
          'hostingWrapperIdentity': w['hostingWrapperIdentity'], 'root404SHA256': extra['sha256'],
          'a2WorkerServiceClientAndBackendBytes': 'UNCHANGED; fail-closed source preserved',
          'actualCloudflarePages': 'NOT VERIFIED; NO DEPLOYMENT', 'cloudflareProjectOrUploadActions': False,
          'largeNumericalOrBrowserSuitesRerun': False, 'privateAccessAndPublicationGatesChanged': False}
(B / 'evidence/followup-preservation.json').write_bytes(canonical(report))
print('PASS: original B11/manifest/source unchanged; only approved 404 in separate staging manifests; B12-only diff')
