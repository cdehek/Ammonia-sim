"""Serve unchanged repository assets and execute bounded diagnostic browser calls."""
import functools,http.server,json,threading
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'))
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
inputs=json.loads((E/'fixed-inputs.json').read_text());unique={tuple(r['input']['bits'][k]for k in ['rho','u']):r for r in inputs}
args=dict(inputs=list(unique.values()),sweep=json.loads((E/'boundary-sweep.json').read_text())['rows'],referenceInventories=json.loads((E/'reference-inventories.json').read_text()),guardFixtures=[r for r in json.loads((E/'original-failures.json').read_text())['rows']if r['runtime']=='chromium'],engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text()))
try:
 with sync_playwright()as pw:
  for name in ['chromium','webkit']:
   browser=getattr(pw,name).launch(executable_path='/usr/bin/chromium'if name=='chromium'else'/workspace/b5-webkit.sh',**({'args':['--no-sandbox']}if name=='chromium'else{}));page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/')
   result=page.evaluate("async args=>{const {run}=await import('/experiments/dx-fv/browser_eos_b5/browser-diagnostics.mjs');return run(args);}",args);result.update(browser=name,version=browser.version)
   (E/(name+'-diagnostics.json')).write_text(json.dumps(result,indent=2)+'\n');print(name,len(result['lifecycle']),'lifecycle',len(result['boundary']),'boundary',flush=True);page.close();browser.close()
finally:server.shutdown()
