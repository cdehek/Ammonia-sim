"""Explicit API retrieval costs on frozen workloads. Outer timeout 180s."""
import argparse,functools,gzip,http.server,json,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2]
p=argparse.ArgumentParser();p.add_argument('--tag',default='');args=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   target=B/'evidence'/f'retrieval-{name}{args.tag}.json.gz';assert not target.exists();opts=dict(headless=True,timeout=30000)
   if name=='webkit':opts['executable_path']='/workspace/b9-runtime/webkit.sh'
   browser=getattr(pw,name).launch(**opts)
   try:
    page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9a/index.html');out=json.loads(page.evaluate("async()=>JSON.stringify(await(await import('./retrieval.mjs')).run())"));out.update(engine=name,browserVersion=browser.version);assert out['passed'];target.write_bytes(gzip.compress(json.dumps(out).encode(),mtime=0));print(name,'retrieval PASS',flush=True)
   finally:browser.close()
finally:server.shutdown()
