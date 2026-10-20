"""Reproduce/verify the root-layout Worker upload ZIP; no Cloudflare operations.

Uses the existing B12 stage.build, then independently hashes its 14 assets against
the evidence committed at the owner-specified B12 checkpoint. Standard library only.
"""
import argparse
import io
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

from stage import B, R, IDENTITY, build, canonical, require, sha

CHECKPOINT = 'f66566af56bf14beb822b5b8951f74e488b01f1e'
NAME = 'cloudflare-worker-static-upload.zip'
STAMP = (2026, 10, 20, 0, 0, 0)
EVIDENCE = ['staging-original-manifest.json', 'hosting-wrapper-manifest.json',
            'staged-deployment-manifest.json', 'staging-sha256.json']

def sealed_evidence():
    values = []
    for name in EVIDENCE:
        raw = (B / 'evidence' / name).read_bytes()
        pinned = subprocess.check_output(['git', 'show', CHECKPOINT + ':experiments/dx-fv/browser_eos_b12/evidence/' + name], cwd=R)
        require(raw == pinned, 'Existing evidence changed: ' + name)
        values.append(json.loads(raw))
    original, wrapper, staged, seal = values
    require(seal['manifests'] == {p: sha((B / 'evidence' / p).read_bytes()) for p in EVIDENCE[:3]}, 'Manifest seal mismatch')
    require(original['packageIdentity'] == staged['originalB11PackageIdentity'] == IDENTITY, 'Original identity mismatch')
    require(staged['assetCount'] == 14 and len(staged['assets']) == 14, 'Expected 14 assets')
    expected = {a['path']: a for a in staged['assets']}
    require(len(expected) == 14 and 'index.html' in expected and '404.html' in expected, 'Root assets missing')
    require(expected['404.html']['sha256'] == seal['root404SHA256'], '404 hash mismatch')
    require(staged['assets'] == sorted(original['assets'] + wrapper['addedAssets'], key=lambda a: a['path']), '13+1 evidence mismatch')
    return values

def verify_assets(root, staged):
    require(root.is_dir() and not root.is_symlink(), 'Invalid asset folder')
    require(not any(p.is_symlink() for p in root.rglob('*')), 'Symlink in assets')
    paths = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(paths == {a['path'] for a in staged['assets']}, 'Asset folder has extra/missing files')
    for a in staged['assets']:
        raw = (root / a['path']).read_bytes()
        require(len(raw) == a['bytes'] and sha(raw) == a['sha256'], 'Asset SHA-256/length mismatch: ' + a['path'])

def archive_bytes(root, staged):
    verify_assets(root, staged)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_STORED) as z:
        for a in sorted(staged['assets'], key=lambda a: a['path']):
            entry = zipfile.ZipInfo(a['path'], STAMP)
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            z.writestr(entry, (root / a['path']).read_bytes())
    raw = out.getvalue()
    verify_archive(raw, staged)
    return raw

def verify_archive(raw, staged):
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names = [a['path'] for a in sorted(staged['assets'], key=lambda a: a['path'])]
            require(z.namelist() == names and len(names) == 14, 'ZIP must contain exactly 14 sorted root-layout asset members')
            require(z.comment == b'', 'Unexpected ZIP comment')
            for a in staged['assets']:
                entry = z.getinfo(a['path'])
                require(not entry.is_dir() and entry.create_system == 3 and entry.external_attr >> 16 == 0o100644,
                        'Unexpected ZIP entry type/mode')
                require(entry.date_time == STAMP and entry.compress_type == zipfile.ZIP_STORED and entry.extra == b'',
                        'ZIP metadata is not reproducible')
                require(not entry.flag_bits & 1, 'Encrypted ZIP forbidden')
                data = z.read(entry)
                require(len(data) == a['bytes'] and sha(data) == a['sha256'], 'ZIP asset hash mismatch: ' + a['path'])
    except (zipfile.BadZipFile, EOFError, RuntimeError) as error:
        raise ValueError('Invalid/corrupt ZIP') from error

def verify_checksum(raw, expected_sha):
    require(sha(raw) == expected_sha, 'External ZIP SHA-256 mismatch')

def fresh_archive():
    original, wrapper, staged, seal = sealed_evidence()
    parent = B / '.runtime/staging'
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='worker-upload-', dir=parent) as td:
        root = Path(td) / 'assets'
        generated = build(root)
        for name, value in zip(EVIDENCE[:3], generated):
            require(canonical(value) == (B / 'evidence' / name).read_bytes(), 'Stage result differs from sealed evidence')
        raw = archive_bytes(root, staged)
    return raw, staged

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verify', type=Path, help='Verify an existing ZIP against sealed assets and the external checksum')
    args = ap.parse_args()
    if args.verify:
        raw = args.verify.read_bytes()
        verify_checksum(raw, (B / (NAME + '.sha256')).read_text().split()[0])
        verify_archive(raw, sealed_evidence()[2])
        print('PASS: ZIP checksum, root layout and every sealed asset')
        return
    raw, staged = fresh_archive()
    target = B / NAME
    checksum = B / (NAME + '.sha256')
    require(not target.is_symlink() and not checksum.is_symlink(), 'Refusing symlinked package output')
    target.write_bytes(raw)
    checksum.write_text(sha(raw) + '  ' + NAME + '\n')
    report = {'schema': 1, 'packagingCheckpoint': CHECKPOINT, 'filename': NAME,
              'zipSHA256': sha(raw), 'zipBytes': len(raw), 'archiveRoot': 'index.html; no enclosing directory',
              'entries': staged['assets'], 'assetCount': 14, 'originalB11PackageIdentity': IDENTITY,
              'hostingWrapperIdentity': staged['hostingWrapperIdentity'],
              'stagedManifestSHA256': sha((B / 'evidence/staged-deployment-manifest.json').read_bytes()),
              'compression': 'ZIP_STORED', 'fixedTimestamp': list(STAMP),
              'scientificOrWorkstationBytesModified': 0, 'workerScriptAdded': False,
              'cloudflareAccountOperationsPerformed': False, 'deployedIdentityVerified': False}
    (B / 'evidence/worker-upload-package.json').write_bytes(canonical(report))
    print('PASS:', NAME, sha(raw), len(raw), 'bytes; 14 exact assets')

if __name__ == '__main__':
    main()
