"""Extract exact B11 into a NEW B12-only stage, verify, add only approved 404.

Standard library only. No build, serving, Cloudflare operations or asset rewrites.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

B = Path(__file__).resolve().parent
R = B.parents[2]
OLD = B.parent / 'browser_eos_b11'
START = '909de1579051bfadca0e282adf93eaedc0e24b9c'
FOLLOWUP = '1ab61278159a51fb3f86bb817ea1f03b049443d8'
ZIP_SHA = 'a642fe22078e7637f9e5c12ce0efbc6f8b7de317da3853b6a52b03452a3ee078'
IDENTITY = 'b7803a5bf93ddc102c7367b80e7dc4c620c21daec0dbad6ef1a988161e3a2914'
MANIFEST_SHA = 'b3aaf9f7a33ba1b8e591e8ed00dc4dca8c6432cbb2dd89426db461452fbe46be'

def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def git_blob(path):
    return subprocess.check_output(['git', 'show', START + ':experiments/dx-fv/browser_eos_b11/' + path], cwd=R)

def original_package():
    raw = (OLD / 'preview.zip').read_bytes()
    require(sha(raw) == ZIP_SHA and raw == git_blob('preview.zip'), 'B11 ZIP differs from committed authorized artifact')
    require((OLD / 'preview.zip.sha256').read_text().split()[0] == ZIP_SHA, 'B11 ZIP checksum receipt mismatch')
    mraw = (OLD / 'preview/asset-manifest.json').read_bytes()
    require(sha(mraw) == MANIFEST_SHA, 'B11 asset manifest mismatch')
    m = json.loads(mraw)
    require(m['packageIdentity'] == IDENTITY, 'B11 package identity mismatch')
    require(sha(canonical({k: v for k, v in m.items() if k != 'packageIdentity'})) == IDENTITY,
            'B11 canonical identity recomputation failed')
    assets = [{k: a[k] for k in ['path', 'bytes', 'mime', 'sha256']} for a in m['assets']]
    assets.append({'path': 'asset-manifest.json', 'bytes': len(mraw), 'mime': 'application/json', 'sha256': sha(mraw)})
    expected = {a['path']: a for a in assets}
    require(len(expected) == 13 and '404.html' not in expected, 'Unexpected original asset set')
    files = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        require(len(z.infolist()) == 13 and set(z.namelist()) == {'preview/' + p for p in expected}, 'ZIP file set mismatch')
        for p, a in expected.items():
            entry = z.getinfo('preview/' + p)
            require(entry.external_attr >> 16 == 0o100644, 'Unexpected ZIP mode')
            data = z.read(entry)
            require(data == (OLD / 'preview' / p).read_bytes() == git_blob('preview/' + p), 'Original asset is not committed B11: ' + p)
            require(sha(data) == a['sha256'] and len(data) == a['bytes'], 'Original hash/size mismatch: ' + p)
            files[p] = data
    for a in m['assets']:
        if a['path'] == 'science/candidate-bundle.mjs':
            pinned = subprocess.check_output(['git', 'show', m['pins']['B9C'] + ':experiments/dx-fv/browser_eos_b9c/candidate-bundle.mjs'], cwd=R)
            require(files[a['path']] == pinned, 'Scientific B9C identity mismatch')
    original = {'schema': 1, 'kind': 'ORIGINAL B11 ONLY', 'sourceCommit': START,
                'zipSHA256': ZIP_SHA, 'packageIdentity': IDENTITY, 'assetManifestSHA256': MANIFEST_SHA,
                'assets': sorted(assets, key=lambda a: a['path']), 'assetCount': 13}
    return files, original

def verify_directory(root, files):
    require(not root.is_symlink() and root.is_dir(), 'Not a real staging directory')
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'Symlink forbidden in stage')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    require(actual == set(files), 'Unexpected or missing staged file')
    # Also reject empty/unexpected directories: deploy only the sealed static tree.
    expected_dirs = {parent for p in files for parent in Path(p).parents if str(parent) != '.'}
    require({p.relative_to(root) for p in root.rglob('*') if p.is_dir()} == expected_dirs, 'Unexpected staged directory')
    for path, raw in files.items():
        require((root / path).read_bytes() == raw, 'Staged bytes changed: ' + path)

def build(root):
    root = root.absolute()
    runtime = B / '.runtime/staging'
    require(not any(p.is_symlink() for p in [root, *root.parents] if p.is_relative_to(B)),
            'Symlinked staging paths are forbidden')
    require(root.resolve().is_relative_to(runtime.resolve()) and root.resolve() != runtime.resolve(),
            'Staging must be inside B12 .runtime/staging, never the original extracted folder')
    require(not root.exists() and not root.is_symlink(), 'Use a NEW staging path; existing output is never overwritten')
    files, original = original_package()
    wrapper = (B / 'hosting/404.html').read_bytes()
    root.mkdir(parents=True)
    for p, raw in files.items():
        dest = root / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    verify_directory(root, files)
    # The sole authorized extra asset; the original ZIP, manifest and copy stay sealed.
    (root / '404.html').write_bytes(wrapper)
    combined = {**files, '404.html': wrapper}
    verify_directory(root, combined)
    extra = {'path': '404.html', 'bytes': len(wrapper), 'mime': 'text/html', 'sha256': sha(wrapper)}
    hosting = {'schema': 1, 'kind': 'B12 HOSTING WRAPPER ONLY', 'originalB11PackageIdentity': IDENTITY,
               'originalManifestSHA256': sha(canonical(original)),
               'approvedException': 'Owner follow-up: one static root 404.html in NEW B12 staging only',
               'followupStartingCommit': FOLLOWUP, 'addedAssets': [extra], 'originalFilesModified': 0}
    hosting['hostingWrapperIdentity'] = sha(canonical(hosting))
    deployment = {'schema': 1, 'kind': 'B12 STAGED DEPLOYMENT; NOT THE B11 CANONICAL PACKAGE',
                  'originalB11PackageIdentity': IDENTITY, 'hostingWrapperIdentity': hosting['hostingWrapperIdentity'],
                  'assets': sorted(original['assets'] + [extra], key=lambda a: a['path']),
                  'assetCount': 14, 'totalBytes': sum(len(raw) for raw in combined.values())}
    return original, hosting, deployment

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path, help='NEW directory inside browser_eos_b12/.runtime/staging')
    args = ap.parse_args()
    original, hosting, deployment = build(args.out)
    for name, value in [('staging-original-manifest.json', original), ('hosting-wrapper-manifest.json', hosting),
                        ('staged-deployment-manifest.json', deployment)]:
        (B / 'evidence' / name).write_bytes(canonical(value))
    receipts = {'schema': 1, 'originalB11ZIP_SHA256': ZIP_SHA, 'originalB11PackageIdentity': IDENTITY,
                'manifests': {name: sha((B / 'evidence' / name).read_bytes()) for name in
                              ['staging-original-manifest.json', 'hosting-wrapper-manifest.json', 'staged-deployment-manifest.json']},
                'root404SHA256': hosting['addedAssets'][0]['sha256'], 'originalFilesVerifiedUnchanged': 13,
                'extraFiles': ['404.html'], 'cloudflareResponseBehavior': 'NOT VERIFIED; NO DEPLOYMENT'}
    (B / 'evidence/staging-sha256.json').write_bytes(canonical(receipts))
    print('PASS: 13 exact committed B11 assets + one static 404.html in NEW B12 stage')

if __name__ == '__main__':
    main()
