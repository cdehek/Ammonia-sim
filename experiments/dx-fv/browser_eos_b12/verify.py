"""Read-only source/package checks; receipts and optional extraction stay in B12.

Run from any directory: python3 path/to/browser_eos_b12/verify.py [--extract]
No historical script is executed: several of them write historical evidence.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

B = Path(__file__).resolve().parent
R = B.parents[2]
OLD = B.parent / 'browser_eos_b11'
E = B / 'evidence'
START = '909de1579051bfadca0e282adf93eaedc0e24b9c'
PREFIX = 'experiments/dx-fv/browser_eos_b12/'
ZIP_SHA = 'a642fe22078e7637f9e5c12ce0efbc6f8b7de317da3853b6a52b03452a3ee078'
IDENTITY = 'b7803a5bf93ddc102c7367b80e7dc4c620c21daec0dbad6ef1a988161e3a2914'
PINS = {'A2': 'be9eb35a4ddf5098e685182f8104685127c6a6ee',
        'B9C': 'b67afb3215075b2ec82bef376d39e03953dc0da2',
        'B9D': '20ddac46423a7a742af19ac415ef8796cf3a429f',
        'B10': 'a49c5c4ade306fe02117139cf81c30a59727a7b1',
        'B11': START, 'original': '262b6092b2ed694073ad9ffd41265f44dd0b6ca0'}

def git(*a):
    return subprocess.check_output(['git', *a], cwd=R)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def save(name, obj):
    E.mkdir(exist_ok=True)
    (E / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def batch_blobs(entries):
    proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=R,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for spec, path in entries:
            proc.stdin.write((spec + '\n').encode())
            proc.stdin.flush()
            header = proc.stdout.readline().split()
            assert len(header) == 3 and header[1] == b'blob', (spec, header)
            raw = proc.stdout.read(int(header[2]))
            assert proc.stdout.read(1) == b'\n'
            yield path, header[0].decode(), raw
    finally:
        proc.stdin.close()
        proc.stdout.close()
        assert proc.wait() == 0

def preservation():
    git('merge-base', '--is-ancestor', START, 'HEAD')
    assert git('branch', '--show-current').decode().strip() == 'research/b12-private-https-ipad-preview-20261019'
    for value in PINS.values():
        git('cat-file', '-e', value + '^{commit}')
    entries = []
    for row in git('ls-tree', '-rz', START).split(b'\0'):
        if row:
            meta, path = row.decode().split('\t')
            assert meta.split()[1] == 'blob'
            entries.append((meta.split()[2], path))
    inventory = {}
    for path, blob, raw in batch_blobs(entries):
        assert (R / path).read_bytes() == raw, path
        inventory[path] = {'gitBlob': blob, 'sha256': sha(raw), 'bytes': len(raw)}
    baseline = E / 'historical-tracked-files.json'
    if baseline.exists():
        assert json.loads(baseline.read_text()) == inventory
    else:
        assert git('rev-parse', 'HEAD').decode().strip() == START
        save(baseline.name, inventory)
    changed = git('diff', '--name-only', START).decode().splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').decode().splitlines()
    assert all(p.startswith(PREFIX) for p in changed + untracked)
    accepted = json.loads((B.parent / 'browser_eos_b10/evidence/accepted-source-manifest.json').read_text())
    for path, item in accepted.items():
        assert (R / item['snapshot']).read_bytes() == git('show', PINS['A2'] + ':' + path)
    save('preservation.json', {'passed': True, 'historicalFiles': len(inventory),
                              'protectedPins': PINS, 'acceptedClosureFiles': len(accepted),
                              'allHistoricalBytesUnchanged': True, 'changesConfinedToB12': True})

def artifact(extract):
    raw_zip = (OLD / 'preview.zip').read_bytes()
    assert sha(raw_zip) == ZIP_SHA
    assert (OLD / 'preview.zip.sha256').read_text().split()[0] == ZIP_SHA
    mraw = (OLD / 'preview/asset-manifest.json').read_bytes()
    assert sha(mraw) == 'b3aaf9f7a33ba1b8e591e8ed00dc4dca8c6432cbb2dd89426db461452fbe46be'
    m = json.loads(mraw)
    assert m['packageIdentity'] == IDENTITY
    unhashed = {k: v for k, v in m.items() if k != 'packageIdentity'}
    assert sha((json.dumps(unhashed, sort_keys=True, indent=2) + '\n').encode()) == IDENTITY
    assert m['pins'] == {k: v for k, v in PINS.items() if k != 'B11'}
    assets = m['assets'] + [{'path': 'asset-manifest.json', 'sha256': sha(mraw),
                             'bytes': len(mraw), 'mime': 'application/json'}]
    expected = {a['path']: a for a in assets}
    assert len(expected) == 13
    assert {p.relative_to(OLD / 'preview').as_posix() for p in (OLD / 'preview').rglob('*') if p.is_file()} == set(expected)
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:
        assert len(z.namelist()) == len(expected)
        assert set(z.namelist()) == {'preview/' + p for p in expected}
        for item in z.infolist():
            path = PurePosixPath(item.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert item.external_attr >> 16 == 0o100644
            p = path.relative_to('preview').as_posix()
            data = z.read(item)
            assert data == (OLD / 'preview' / p).read_bytes()
            assert sha(data) == expected[p]['sha256'] and len(data) == expected[p]['bytes']
            if extract:
                dest = B / '.runtime/extracted/preview' / p
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
    if extract:
        root = B / '.runtime/extracted/preview'
        assert (root / 'index.html').is_file()
        assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == set(expected)
        for p, item in expected.items():
            assert sha((root / p).read_bytes()) == item['sha256']
    for a in m['assets']:
        data = (OLD / 'preview' / a['path']).read_bytes()
        for change in reversed(a['relocations']):
            assert data.count(change['to'].encode()) == change['count']
            data = data.replace(change['to'].encode(), change['from'].encode())
        assert data == git('show', a['sourceCommit'] + ':' + a['sourcePath'])
        assert sha(data) == a['sourceSHA256']
        assert git('rev-parse', a['sourceCommit'] + ':' + a['sourcePath']).decode().strip() == a['sourceGitBlob']
    bundle = (OLD / 'preview/science/candidate-bundle.mjs').read_bytes()
    assert bundle == git('show', PINS['B9C'] + ':experiments/dx-fv/browser_eos_b9c/candidate-bundle.mjs')
    operator = json.loads(git('show', PINS['B10'] + ':experiments/dx-fv/browser_eos_b10/evidence/operator-source-manifest.json'))
    for path, blob, raw in batch_blobs([(PINS['original'] + ':' + p, p) for p in operator]):
        assert blob == operator[path]['gitBlob'] and sha(raw) == operator[path]['sha256']
    text = (OLD / 'preview/index.html').read_text().replace('./panel.mjs', '/experiments/dx-fv/browser_eos_b10/panel.mjs')
    text = re.sub(r'<script data-b10="(?:mount|bootstrap)">.*?</script>', '', text, flags=re.S)
    entry = " 'b10-a2-shadow':[$('b10-a2-shadow'),'A2 — Five-Section Evaporator Research'],\n"
    assert text.count(entry) == 1
    original = git('show', PINS['original'] + ':index.html')
    assert text.replace(entry, '').encode() == original
    for p in (OLD / 'preview').rglob('*.mjs'):
        for spec in re.findall(r"(?:from\s*|new URL\()'([^']+)'", p.read_text()):
            if spec.startswith('.'):
                target = (p.parent / spec).resolve()
                assert target.is_relative_to((OLD / 'preview').resolve()) and target.is_file()
    save('deployment-package-manifest.json', {'schema': 1, 'sourceCommit': START,
        'zipRepositoryPath': 'experiments/dx-fv/browser_eos_b11/preview.zip',
        'zipSHA256': ZIP_SHA, 'packageIdentity': IDENTITY, 'staticRootInZip': 'preview/',
        'assets': assets, 'totalBytes': sum(a['bytes'] for a in assets)})
    save('artifact-audit.json', {'passed': True, 'zipSHA256': ZIP_SHA, 'packageIdentity': IDENTITY,
        'assetCount': len(assets), 'sourceDerivationsVerified': len(m['assets']),
        'originalSourceFilesVerified': len(operator), 'originalHTMLSHA256': sha(original),
        'scientificBundleSHA256': sha(bundle), 'extractedAndVerified': extract,
        'scienceGenerated': False, 'remoteDeploymentVerified': False})

def retained_results():
    seal = json.loads((OLD / 'evidence/delivery-sha256.json').read_text())
    for p, digest in seal.items():
        assert sha((OLD / p).read_bytes()) == digest, p
    def read(p):
        raw = (OLD / 'evidence' / p).read_bytes()
        return json.loads(gzip.decompress(raw) if p.endswith('.gz') else raw)
    training = []
    for browser in ['chromium', 'webkit']:
        for name in ['integration', 'review', 'isolation']:
            assert read(f'{name}-{browser}.json.gz')['passed']
        for name in ['portability', 'performance']:
            assert read(f'{name}-{browser}.json')['passed']
        for row in read(f'integration-{browser}.json.gz')['science']:
            assert row['exactSavedB10AcceptedStateRecordAndAttempts']
            assert [x['clock'] for x in row['rows']] == [0, .0001, .0005, .001]
        rows = read(f'isolation-{browser}.json.gz')['training']
        assert len(rows) == 5 and all(r['byteExact'] for r in rows)
        for row in rows:
            data = (OLD / f'evidence/training-{browser}/{row["exercise"]}.json').read_bytes()
            assert data == (B.parent / f'browser_eos_b10/evidence/baseline-training/{browser}-{row["exercise"]}-evidence.json').read_bytes()
            training.append({'browser': browser, 'exercise': row['exercise'], 'bytes': len(data), 'sha256': sha(data)})
    assert not read('regression-comparison.json')['newRequiredSuiteRegressions']
    save('retained-b11-results.json', {'passed': True, 'scope': 'Revalidated committed B11 receipts; no new browser execution',
        'sealedFilesVerified': len(seal), 'scienceCheckpoints': [0, .0001, .0005, .001],
        'trainingExports': training, 'realHTTPSBrowserTests': 'NOT TESTED',
        'physicalIPad': 'AWAITING OWNER DEVICE REVIEW', 'historicalWebKit': 'PARTIAL'})

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--extract', action='store_true')
    args = ap.parse_args()
    preservation()
    artifact(args.extract)
    retained_results()
    print('PASS: protected bytes, exact ZIP/assets/source derivation, retained B11 science/training evidence')
