"""Bounded replay; decode immutable B5 inputs, serve unchanged control assets."""
import functools,http.server,json,os,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';H=B.parent/'browser_eos_b5/evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
failures=json.loads((H/'original-failures.json').read_text())['rows']
controls=[r for r in json.loads((H/'fixed-inputs.json').read_text()) if r['key'] in ['webkit-ledger-69','webkit-ledger-76']]
args=dict(falseAcceptanceControls=controls,sweep=json.loads((H/'boundary-sweep.json').read_text())['rows'],engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text()))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   args['fixtures']=[r for r in failures if r['runtime']==name]
   start=time.monotonic()
   try:
    browser=getattr(pw,name).launch(executable_path=os.environ.get(name.upper()+'_PATH','/usr/bin/chromium' if name=='chromium' else '/workspace/b5b-browsers/webkit-2336/pw_run.sh'),timeout=30000,**({'args':['--no-sandbox']} if name=='chromium' else {}))
    page=browser.new_page();page.set_default_timeout(45000);page.goto(f'http://127.0.0.1:{server.server_port}/')
    out=page.evaluate("async args=>{const {run}=await import('/experiments/dx-fv/browser_eos_b5b/browser.mjs');return run(args);}",args)
    out.update(browser=name,version=browser.version,elapsedSeconds=time.monotonic()-start)
    page.close();browser.close()
   except Exception as e:out=dict(browser=name,setupError=str(e),elapsedSeconds=time.monotonic()-start)
   (E/(name+'-replay.json')).write_text(json.dumps(out,indent=2)+'\n');print(name,len(out.get('rows',[])),out.get('setupError','completed'),flush=True)
finally:server.shutdown()
