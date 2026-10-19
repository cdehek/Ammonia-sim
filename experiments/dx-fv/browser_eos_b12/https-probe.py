"""Future bounded unauthenticated HTTPS probe; no login/session material retained.

No remote request happens without an explicit origin argument. This tool is only
one part of Access verification, never a privacy certification or owner-login test.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

B = Path(__file__).resolve().parent

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def valid_origin(value):
    p = urllib.parse.urlsplit(value)
    host = p.hostname or ''
    assert p.scheme == 'https' and not p.username and not p.password
    assert p.port in (None, 443) and p.path in ('', '/') and not p.query and not p.fragment
    labels = host.split('.')
    assert len(labels) in (3, 4) and labels[-2:] == ['pages', 'dev']
    assert re.fullmatch(r'ammonia-lab-research-b12[a-z0-9-]*', labels[-3])
    assert all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?', s) for s in labels)
    return 'https://' + host

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('origin', help='Actual verified B12 project or deployment origin; no placeholders')
    ap.add_argument('--output', type=Path, help='New sanitized receipt inside B12; never overwritten')
    args = ap.parse_args()
    origin = valid_origin(args.origin)
    if args.output:
        dest = args.output.resolve()
        assert dest.is_relative_to(B) and not dest.exists()
    manifest = json.loads((B / 'evidence/deployment-package-manifest.json').read_text())
    opener = urllib.request.build_opener(NoRedirect)
    rows = []
    # All existing assets plus unknown paths; no cookies, auth or redirects.
    for asset in manifest['assets'] + [{'path': '__b12_missing__.mjs'}, {'path': 'science/__b12_missing__.mjs'}]:
        path = '/' if asset['path'] == 'index.html' else '/' + asset['path']
        req = urllib.request.Request(origin + path, headers={'Accept-Encoding': 'identity', 'Cache-Control': 'no-cache'})
        try:
            response = opener.open(req, timeout=15)
        except urllib.error.HTTPError as e:
            response = e
        with response:
            status = response.code
            location = urllib.parse.urlsplit(urllib.parse.urljoin(origin, response.headers.get('Location', '')))
            auth_redirect = (status in (301, 302, 303, 307, 308)
                             and location.scheme == 'https'
                             and bool(location.hostname)
                             and location.hostname.endswith('.cloudflareaccess.com')
                             and location.path.startswith('/cdn-cgi/access/login'))
            body = response.read(2_000_001)
            exposed = 'sha256' in asset and hashlib.sha256(body).hexdigest() == asset['sha256']
            # No response bodies, headers, login URLs or identity are persisted.
            rows.append({'path': path, 'status': status, 'accessLoginRedirect': auth_redirect,
                         'refused': status in (401, 403), 'exactAssetExposed': exposed,
                         'accessDecisionRequiresIndependentReview': not auth_redirect,
                         'candidateDenial': (auth_redirect or status in (401, 403)) and not exposed})
    report = {'observedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'origin': origin, 'mode': 'unauthenticated', 'rows': rows,
              'allCandidateDenials': all(r['candidateDenial'] for r in rows),
              'ownerLoginVerified': False, 'privacyCertified': False,
              'note': 'Verify intended Access team, forbidden identity, owner login and every alias independently. 401/403 alone can be an unrelated denial.'}
    if args.output:
        with dest.open('x') as f:
            f.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if not report['allCandidateDenials']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
