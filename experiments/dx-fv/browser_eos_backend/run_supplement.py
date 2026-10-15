"""Extra single-phase derivative screening in both actual desktop engines."""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2]
class Handler(http.server.SimpleHTTPRequestHandler):
 extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.wasm':'application/wasm'}
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
requests=json.loads((B.parent/'browser_eos/inputs.json').read_text())['requests']
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   browser=getattr(p,name).launch(headless=True,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE') else {}))
   try:
    for build in ['official8','build30','build44','official72']:
     f=B/'evidence'/f'{name}-supplement-{build}.json'
     if f.exists():continue
     context=browser.new_context();page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/');page.wait_for_function('!!window.b1')
     result=page.evaluate('''async({build,requests})=>{const {screenOther}=await import('./screen_other_states.mjs');const e=await b1.loadEOS(build);try{return {build,...screenOther(e,requests)};}finally{e.dispose();}}''',{'build':build,'requests':requests})
     result.update(browser=name,browserVersion=browser.version,physicalIPad=False);f.write_text(json.dumps(result,indent=2)+'\n');print(name,build,len(result['rows']),'rows',sum('error' in r for r in result['rows']),'errors',flush=True);context.close()
   finally:browser.close()
finally:server.shutdown()
