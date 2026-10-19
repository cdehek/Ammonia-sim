"""Bounded packaging and loopback HTTP checks, NOT Cloudflare or browser tests."""
from functools import partial
from html.parser import HTMLParser
from http.client import HTTPConnection
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading

from stage import B, OLD, build, canonical, original_package, sha, verify_directory

class StaticHTML(HTMLParser):
    def handle_starttag(self, tag, attrs):
        assert tag in {'html', 'meta', 'title', 'h1', 'p'}, tag
        assert dict(attrs) in ({}, {'lang': 'en'}, {'charset': 'utf-8'}), attrs

class StrictStatic(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, '.mjs': 'text/javascript', '.js': 'text/javascript'}
    def log_message(self, *args):
        pass

class PagesRoutingEmulator(StrictStatic):
    """Only the documented missing-path distinction; not Cloudflare implementation."""
    def send_error(self, code, message=None, explain=None):
        if code != 404:
            return super().send_error(code, message, explain)
        root = Path(self.directory)
        wrapper = root / '404.html'
        body = (wrapper if wrapper.is_file() else root / 'index.html').read_bytes()
        self.send_response(404 if wrapper.is_file() else 200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

def exercise(root, handler, assets, label, expected_missing, expected_body=None):
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(handler, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    rows = []
    def request(method, path):
        c = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
        try:
            c.request(method, path)
            response = c.getresponse()
            body = response.read()
            return response.status, response.getheader('Content-Type', '').split(';')[0], body
        finally:
            c.close()
    try:
        for a in assets:
            path = '/' if a['path'] == 'index.html' else '/' + a['path']
            status, mime, body = request('GET', path)
            assert status == 200 and sha(body) == a['sha256'] and len(body) == a['bytes']
            assert mime == a['mime'], (path, mime)
            rows.append({'method': 'GET', 'path': path, 'status': status, 'mime': mime, 'sha256': sha(body), 'matchesManifest': True})
        for path in ['/__missing__', '/__missing__.mjs', '/__missing-worker__.js',
                     '/science/__missing__.mjs', '/support/__missing__.mjs',
                     '/__missing__.css', '/__missing__.json', '/science/__missing__.mjs?probe=404']:
            for method in ['GET', 'HEAD']:
                status, mime, body = request(method, path)
                assert status == expected_missing, (label, path, status)
                assert method != 'HEAD' or body == b''
                if method == 'GET' and expected_body is not None:
                    assert body == expected_body
                rows.append({'method': method, 'path': path, 'status': status, 'mime': mime,
                             'bodySHA256': sha(body), 'applicationHTMLServed': method == 'GET' and body == (OLD / 'preview/index.html').read_bytes()})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return {'label': label, 'scope': 'Actual loopback HTTP transport; local handler only', 'rows': rows, 'passed': True}

def main():
    staging = B / '.runtime/staging'
    staging.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='checks-', dir=staging) as td:
        root = Path(td)
        a = build(root / 'first')
        b = build(root / 'second')
        assert all(canonical(x) == canonical(y) for x, y in zip(a, b))
        files, original = original_package()
        wrapper = (B / 'hosting/404.html').read_bytes()
        StaticHTML().feed(wrapper.decode('utf-8'))
        assert b'404' in wrapper and b'<script' not in wrapper and b'http' not in wrapper
        complete = {**files, '404.html': wrapper}
        verify_directory(root / 'first', complete)
        refusals = []
        def rejected(name, action):
            try:
                action()
            except ValueError:
                refusals.append(name)
            else:
                raise AssertionError('Expected fail-closed packaging refusal: ' + name)
        rejected('existing stage cannot be overwritten', lambda: build(root / 'first'))
        rejected('B11 directory cannot be a staging target', lambda: build(OLD / 'preview'))
        alias = root / 'alias'
        alias.symlink_to(root / 'second', target_is_directory=True)
        rejected('symlinked staging parent rejected', lambda: build(alias / 'new-output'))
        alias.unlink()
        target = root / 'first/science/candidate-bundle.mjs'
        raw = target.read_bytes()
        target.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        rejected('changed scientific bundle rejected', lambda: verify_directory(root / 'first', complete))
        target.write_bytes(raw)
        extra = root / 'first/_headers'
        extra.write_text('unauthorized extra file')
        rejected('unapproved extra file rejected', lambda: verify_directory(root / 'first', complete))
        extra.unlink()
        target = root / 'first/404.html'
        target.write_bytes(b'changed')
        rejected('changed wrapper rejected', lambda: verify_directory(root / 'first', complete))
        target.write_bytes(wrapper)
        verify_directory(root / 'first', complete)
        observations = [
            exercise(OLD / 'preview', PagesRoutingEmulator, original['assets'],
                     'UNWRAPPED: documented Pages fallback EMULATION negative control', 200,
                     (OLD / 'preview/index.html').read_bytes()),
            exercise(root / 'first', PagesRoutingEmulator, a[2]['assets'],
                     'WRAPPED: documented Pages 404 routing EMULATION', 404, wrapper),
            exercise(root / 'first', StrictStatic, a[2]['assets'],
                     'WRAPPED: ordinary strict Python static server (no Pages emulation)', 404)]
        report = {'schema': 1, 'passed': True, 'scope': 'Targeted packaging and loopback HTTP only',
                  'reproducibleStages': 2, 'originalAssetsUnchanged': 13, 'approvedExtraFiles': ['404.html'],
                  'newRuntimeDependencies': 0, 'packagingRefusals': refusals,
                  'allStagedManifestsMatchCommittedEvidence': all(canonical(v) == (B / 'evidence' / n).read_bytes() for n, v in zip(
                      ['staging-original-manifest.json', 'hosting-wrapper-manifest.json', 'staged-deployment-manifest.json'], a)),
                  'httpObservations': observations, 'actualCloudflarePages': 'NOT VERIFIED; NO DEPLOYMENT',
                  'realHTTPSBrowserTests': 'NOT RUN', 'numericalSuites': 'NOT RERUN',
                  'a2FailClosedRuntimeSource': 'UNCHANGED; no new runtime claim'}
        assert report['allStagedManifestsMatchCommittedEvidence']
        (B / 'evidence/staging-tests.json').write_bytes(canonical(report))
        print('PASS: reproducible 13+1 stage, packaging refusals, real loopback GET/HEAD 404s; Cloudflare behavior UNVERIFIED')

if __name__ == '__main__':
    main()
