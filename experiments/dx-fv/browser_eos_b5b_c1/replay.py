"""Bounded real browser control/candidate and accepted A2 failure integration."""
import functools,http.server,json,os,threading,time,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';H=B.parent/'browser_eos_b5/evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.wasm':'application/wasm'}
    def log_message(self,*a):pass
failures=json.loads((H/'original-failures.json').read_text())['rows']
controls=[r for r in json.loads((H/'fixed-inputs.json').read_text()) if r['key'] in ['webkit-ledger-69','webkit-ledger-76']]
requests=json.loads((B.parent/'browser_eos_b4c/evidence/native-candidateB.json').read_text())['rows']
focused=[r['request'] for r in requests if r['request']['id'] in ['B1-liquid-precision','B1-vapor-regression','approach-30298.937123458254-liquid-0.001','diagnostic-quality-band-799999.9981754856-hg-9.9e-10']]
args=dict(falseAcceptanceControls=controls,sweep=json.loads((H/'boundary-sweep.json').read_text())['rows'],engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text()),
          sources={p.name:p.read_text() for p in (B/'a2').glob('*.cjs')},controlSources={p.name:p.read_text() for p in (B.parent/'browser_eos_backend/accepted').glob('*.cjs')},a2Tests=(B/'a2-tests.cjs').read_text(),focusedRequests=focused)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in os.environ.get('C1_ENGINES','chromium,webkit').split(','):
   args['fixtures']=[r for r in failures if r['runtime']==name];start=time.monotonic();out={}
   try:
    browser=getattr(pw,name).launch(executable_path=os.environ.get(name.upper()+'_PATH','/usr/bin/chromium' if name=='chromium' else '/workspace/c1-browsers/webkit-2336/pw_run.sh'),timeout=30000,**({'args':['--no-sandbox']} if name=='chromium' else {}))
    page=browser.new_page();page.set_default_timeout(90000);page.goto(f'http://127.0.0.1:{server.server_port}/')
    out=page.evaluate("async args=>{const {run}=await import('/experiments/dx-fv/browser_eos_b5b_c1/browser.mjs');return run(args);}",args)
    out.update(browser=name,version=browser.version,physicalIPad=False)
    page.close();browser.close()
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc(),passed=False)
   out.update(elapsedSeconds=time.monotonic()-start)
   (E/(name+'-replay.json')).write_text(json.dumps(out,indent=2)+'\n');print(name,out.get('passed'),out.get('error','completed'),flush=True)
finally:server.shutdown()
