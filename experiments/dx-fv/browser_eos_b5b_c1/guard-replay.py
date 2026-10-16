"""Bounded supplemental strict lower/temperature and actual loader refusal."""
import functools,http.server,json,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
args=dict(engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text()))
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   start=time.monotonic();browser=getattr(pw,name).launch(executable_path='/usr/bin/chromium' if name=='chromium' else '/workspace/c1-browsers/webkit-2336/pw_run.sh',timeout=30000,**({'args':['--no-sandbox']} if name=='chromium' else {}))
   page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/');out=page.evaluate("async args=>{const {run}=await import('/experiments/dx-fv/browser_eos_b5b_c1/guards.mjs');return run(args);}",args)
   out.update(version=browser.version,elapsedSeconds=time.monotonic()-start);(B/'evidence'/(name+'-guards.json')).write_text(json.dumps(out,indent=2)+'\n');browser.close();print(name,out['passed'])
finally:server.shutdown()
