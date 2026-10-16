import functools,http.server,json,os,threading
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'))
requests=json.loads((E/'shared-controlA.json').read_text())['rows']
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   browser=getattr(pw,name).launch(timeout=30000,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' else {}))
   try:
    for build in ['controlA','candidateB']:
     target=E/f'{name}-{build}-shared.json';assert not target.exists();page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/')
     try:
      result=page.evaluate('''async({build,requests})=>{const {loadEOS}=await import('/experiments/dx-fv/browser_eos_b4c/loader.mjs');const {sharedCallers}=await import('/experiments/dx-fv/browser_eos_b4c/shared-callers.mjs');const eos=await loadEOS(build);try{return sharedCallers(eos,requests);}finally{eos.dispose();}}''',dict(build=build,requests=requests));result.update(browser=name,browserVersion=browser.version,build=build)
     except Exception as exc:result=dict(error=str(exc))
     target.write_text(json.dumps(result,indent=2)+'\n');page.close();print(name,build,'shared complete',flush=True)
   finally:browser.close()
finally:server.shutdown()
