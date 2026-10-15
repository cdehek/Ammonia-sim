import os
import functools,http.server,json,os,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   options={'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE') else {}
   try:browser=getattr(p,name).launch(**options)
   except Exception as e:(E/f'{name}-unavailable.json').write_text(json.dumps({'error':str(e)},indent=2));continue
   try:
    for build in ['official8','build30','build44','official72']:
     f=E/f'{name}-phase-{build}.json'
     if f.exists():continue
     page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/')
     start=time.monotonic()
     result=page.evaluate('''async ({build,requests})=>{const {loadEOS}=await import('./loader.mjs');const {investigate}=await import('../browser_eos_b2/phase.mjs');const eos=await loadEOS(build);try{return {init:eos.init,...investigate(eos,requests)};}finally{eos.dispose();}}''',{'build':build,'requests':json.loads((B/'inputs.json').read_text())})
     result.update(browser=name,browserVersion=browser.version,build=build,elapsedSeconds=time.monotonic()-start,physicalIPad=False)
     f.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');page.close();print(name,build,len(result['rows']),flush=True)
   finally:browser.close()
finally:server.shutdown()
