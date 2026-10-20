"""Bounded ZIP reproducibility, layout, SHA-256 and rejection checks. No network."""
import io
from pathlib import Path
import tempfile
import warnings
import zipfile

from stage import B, canonical, sha
from worker_upload import NAME, STAMP, fresh_archive, sealed_evidence, verify_archive, verify_assets, verify_checksum

def main():
    first, staged = fresh_archive()
    second, _ = fresh_archive()
    assert first == second == (B / NAME).read_bytes()
    checksum = (B / (NAME + '.sha256')).read_text().split()
    assert checksum == [sha(first), NAME]
    verify_checksum(first, checksum[0])
    verify_archive(first, sealed_evidence()[2])
    with zipfile.ZipFile(io.BytesIO(first)) as z:
        members = [(p, z.read(p)) for p in z.namelist()]
    refused = []
    def reject(name, action):
        try:
            action()
        except ValueError:
            refused.append(name)
        else:
            raise AssertionError('Corruption accepted: ' + name)
    def changed_zip(rows, symlink=None):
        out = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_STORED) as z:
                for p, data in rows:
                    e = zipfile.ZipInfo(p, STAMP)
                    e.create_system = 3
                    e.external_attr = (0o120777 if p == symlink else 0o100644) << 16
                    z.writestr(e, data)
        return out.getvalue()
    def verify(rows, **kw):
        verify_archive(changed_zip(rows, **kw), staged)
    reject('missing asset', lambda: verify(members[:-1]))
    reject('unapproved extra file', lambda: verify(members + [('extra.txt', b'extra')]))
    reject('enclosing folder instead of root index.html', lambda: verify([('preview/' + p, d) for p, d in members]))
    reject('duplicate member', lambda: verify(members + [members[0]]))
    reject('path traversal', lambda: verify([('../index.html' if p == 'index.html' else p, d) for p, d in members]))
    reject('symlink member', lambda: verify(members, symlink='worker.mjs'))
    for name in ['science/candidate-bundle.mjs', 'worker.mjs', '404.html']:
        rows = [(p, bytes([d[0] ^ 1]) + d[1:] if p == name else d) for p, d in members]
        reject('changed bytes with valid CRC: ' + name, lambda: verify(rows))
    reject('truncated archive', lambda: verify_archive(first[:100], staged))
    reject('external checksum mismatch', lambda: verify_checksum(first + b'corruption', checksum[0]))
    with tempfile.TemporaryDirectory(prefix='verify-extraction-', dir=B / '.runtime/staging') as td:
        root = Path(td)
        with zipfile.ZipFile(io.BytesIO(first)) as z:
            z.extractall(root)  # Only after exact known-member verification above.
        verify_assets(root, staged)
        (root / 'worker.mjs').write_bytes(b'corrupt')
        reject('corrupt extracted asset', lambda: verify_assets(root, staged))
    report = {'passed': True, 'scope': 'Packaging only; no runtime, browser, scientific or Cloudflare campaign',
              'independentFreshStageBuilds': 2, 'byteIdenticalZIPs': True,
              'zipSHA256': sha(first), 'rootIndexHTML': True, 'memberCount': len(members),
              'preservedNestedPaths': [p for p, _ in members if '/' in p],
              'all14FilesMatchExistingEvidence': True, 'externalChecksumMatches': True,
              'corruptionRejections': refused, 'cloudflareAccountOperations': False}
    (B / 'evidence/worker-upload-tests.json').write_bytes(canonical(report))
    print('PASS: two identical fresh ZIP builds; 14 exact root assets;', len(refused), 'rejection cases')

if __name__ == '__main__':
    main()
