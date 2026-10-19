"""Bounded packaging verification; never executes or changes a physical model."""
import gzip, hashlib, json, subprocess, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as XML

B = Path(__file__).resolve().parent
R = B.parents[2]
E = B / 'evidence'
MANIFEST = E / 'delivery-sha256.json'
CHECK = '--check-only' in sys.argv

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(name):
    p = E / name
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_text())

required = ['README', 'B10_INTEGRATION_ARCHITECTURE', 'WORKSTATION_SOURCE_DERIVATION',
            'SHADOW_PANEL_DESIGN', 'TWO_MODEL_ISOLATION', 'WORKER_AND_SESSION_PROTOCOL',
            'FIELD_AND_UNITS_MAPPING', 'SCIENTIFIC_PARITY_MATRIX', 'FAILURE_AND_ROLLBACK',
            'ORIGINAL_WORKSTATION_REGRESSION', 'TRAINING_EXPORT_PARITY', 'BROWSER_UI_RESULTS',
            'PERFORMANCE_AND_RESPONSIVENESS', 'OFFLINE_AND_IPAD_LIMITATIONS',
            'ENGINEERING_REPORT', 'MECHANICS_REPORT', 'QUALIFICATION_BACKLOG',
            'PROTECTED_REFS_AND_PR3_AUDIT']
assert all((B / (name + '.md')).is_file() for name in required)
build = read('build-manifest.json')
assert digest(B / 'index.html') == build['derivedSHA256']
assert digest(B / 'artifacts/pinned-workstation.html') == build['originalSHA256']
assert digest(B.parent / 'browser_eos_b9c/candidate-bundle.mjs') == build['scientificBundleSHA256']
assert build['reversibleToExactOriginal'] and build['existingFunctionBodiesUnchanged']

# The later sequential WebKit baseline has its own receipt; the original sealed
# baseline is retained byte-for-byte rather than overwritten or reinterpreted.
checkpoint = '4362b79d54ada6b8b34ebf3d9820471de78fc499'
prefix = str(B.relative_to(R)) + '/evidence/'
old = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', checkpoint, '--',
                              prefix + 'baseline-webkit', prefix + 'baseline-webkit.log'], cwd=R).decode().splitlines()
for name in old:
    kept = name.replace('baseline-webkit', 'baseline-webkit-pre-implementation', 1)
    assert (R / kept).read_bytes() == subprocess.check_output(['git', 'show', checkpoint + ':' + name], cwd=R)

exports = []
for browser in ['chromium', 'webkit']:
    for family in ['review', 'integration', 'isolation']:
        assert read(f'{family}-{browser}.json.gz')['passed']
    perf = read(f'performance-{browser}.json')
    assert perf['passed'] and len(perf['rounds']) == 4
    for row in perf['rounds']:
        assert row['matchedScience']
        assert {c['case'] for c in row['cases']} == {'A', 'B', 'C', 'D', 'E', 'bareB9C'}
    for row in read(f'isolation-{browser}.json.gz')['training']:
        candidate = E / f'training-{browser}' / (row['exercise'] + '.json')
        original = E / 'baseline-training' / f"{browser}-{row['exercise']}-evidence.json"
        assert candidate.read_bytes() == original.read_bytes()
        assert digest(candidate) == row['sha256']
        exports.append(str(candidate.relative_to(B)))
    baseline = read(f'baseline-{browser}/results.json')
    candidate = read(f'candidate-{browser}/results.json')
    assert [r['suite'] for r in baseline] == [r['suite'] for r in candidate]
    assert all(a['code'] != 0 or b['code'] == 0 for a, b in zip(baseline, candidate))
    assert sum(r['code'] == 0 for r in candidate) == (19 if browser == 'chromium' else 8)

render = read('independent-render.json')
assert len(render) == 2
assert all(x['passed'] and x['independentFormulaChecks'] and len(x['rows']) == 16 for x in render)
tracker = json.loads((B / 'milestone-status.json').read_text())
assert tracker['classification'] == 'B10 OPERATOR WORKSTATION SHADOW HOOK-UP PASS'
assert [r['id'] for r in tracker['decisions']] == list('ABCDEFGHIJKLMNOP')
assert tracker['productionMerge'] == tracker['plantBackend'] == 'NO-GO'
with zipfile.ZipFile(B / 'milestone-status.xlsx') as z:
    assert z.testzip() is None
    for name in z.namelist():
        XML.fromstring(z.read(name))
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    rows = XML.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('m:sheetData/m:row', ns)
    assert len(rows) == 17

screenshots = sorted(E.glob('integration-*.png')) + sorted(E.glob('isolation-*.png'))
assert len(screenshots) >= 24
assert all(p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') for p in screenshots)
out = {'passed': True, 'requiredReports': len(required), 'completeExportPairsExact': len(exports),
       'screenshotFiles': len(screenshots), 'scienceAndLifecycleReceiptsPassed': True,
       'matchedPerformanceCases': 'A/B/C/D/E + bare B9C; two rounds/fixture/browser',
       'independentRenderFormulaChecks': True, 'xlsxXMLAndDecisionRowsValid': True,
       'originalHTMLAndDerivedHTMLAndScientificBundleHashesExact': True,
       'sealedPreImplementationWebKitReceiptsExact': len(old),
       'scope': 'packaging checks only; completed expensive suites not rerun'}
if not CHECK:
    (E / 'delivery-validation.json').write_text(json.dumps(out, indent=2) + '\n')
names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard',
                                 '--', str(B.relative_to(R))], cwd=R).decode().splitlines()
paths = sorted({R / name for name in names} - {MANIFEST})
hashes = {str(p.relative_to(B)): digest(p) for p in paths}
if CHECK:
    assert hashes == json.loads(MANIFEST.read_text())['files'], 'Delivery file set/hash changed'
else:
    MANIFEST.write_text(json.dumps({'algorithm': 'SHA-256',
        'scope': 'Every nonignored B10 delivery file except this self manifest; Git seals the manifest',
        'files': hashes}, indent=2) + '\n')
print(json.dumps({**out, 'deliveryFileHashesExact': len(hashes), 'checkOnly': CHECK}, indent=2))
