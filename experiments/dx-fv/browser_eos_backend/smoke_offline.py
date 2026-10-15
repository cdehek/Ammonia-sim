"""Desktop smoke of the standalone artifact with offline contexts + stopped origin."""
import functools,http.server,json,os,sys,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve();disabled=False;blocked=0
emulate_offline='--origin-only' not in sys.argv
class Handler(http.server.SimpleHTTPRequestHandler):
 extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.wasm':'application/wasm'}
 def log_message(self,*args):pass
 def do_GET(self):
  global blocked
  if disabled:blocked+=1;self.send_error(503);return
  super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
requests=json.loads((root/'experiments/dx-fv/browser_eos/inputs.json').read_text())['requests']
inputs=json.loads((root/'experiments/dx-fv/browser_eos_precision/inputs.json').read_text());inputs['cases']=inputs['cases'][:1]
report=[]
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   disabled=False
   browser=getattr(p,name).launch(headless=True,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE') else {}))
   context=browser.new_context();url=f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/'
   row={'browser':name,'browserVersion':browser.version,'physicalIPad':False,'builds':[]}
   try:
    page=context.new_page();page.goto(url);page.click('#offline');page.wait_for_function("document.querySelector('#status').textContent.includes('service worker controls')",timeout=120000)
    row['preparation']=page.locator('#status').inner_text();page.close();disabled=True;context.set_offline(emulate_offline)
    for build in ['official8','build30','build44','official72']:
     page=context.new_page()
     try:
      page.goto(url);page.wait_for_function('!!window.b1')
      result=page.evaluate('''async({build,requests,inputs})=>{
       const worker=new Worker('./worker.mjs',{type:'module'});
       try{return await new Promise((resolve,reject)=>{worker.onmessage=e=>resolve(e.data);worker.onerror=e=>reject(Error(e.message));worker.postMessage({build,requests,inputs});});}
       finally{worker.terminate();}
      }''',{'build':build,'requests':requests,'inputs':inputs})
      row['builds'].append({'build':build,'freshPage':True,'freshWorker':True,'contextOffline':emulate_offline,'originDisabled':True,'result':result})
     except Exception as exc:row['builds'].append({'build':build,'error':str(exc)})
     finally:page.close()
     print(name,build,'offline complete',flush=True)
   except Exception as exc:row['error']=str(exc)
   finally:context.close();browser.close()
   row['blockedOriginRequests']=blocked;report.append(row)
finally:server.shutdown()
f=B/'evidence'/(sys.argv[2] if len(sys.argv)>2 else 'ipad-offline-smoke.json');assert not f.exists();f.write_text(json.dumps(report,indent=2)+'\n')
