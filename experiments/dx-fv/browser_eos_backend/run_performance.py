"""Identical desktop worker workloads, fresh-context startup and memory evidence."""
import functools,http.server,json,os,platform,threading
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
    # Reverse the build order in WebKit to reduce a consistent order bias.
    for build in (['official8','build30','build44','official72'] if name=='chromium' else ['official72','build44','build30','official8']):
     f=B/'evidence'/f'{name}-performance-{build}.json'
     if f.exists():continue
     result={'build':build,'browser':name,'browserVersion':browser.version,'physicalIPad':False,'platform':platform.platform(),'startup':[]}
     for run in range(3):
      context=browser.new_context();page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/');page.wait_for_function('!!window.b1')
      result['startup'].append(page.evaluate('''async build=>{const e=await b1.loadEOS(build);try{return {init:e.init,linearMemory:e.memory()};}finally{e.dispose();}}''',build));context.close()
     context=browser.new_context();page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/');page.wait_for_function('!!window.b1')
     result['worker']=page.evaluate('''async({build,requests})=>{
       const worker=new Worker('./worker.mjs',{type:'module'}),gaps=[];let previous=performance.now();
       const timer=setInterval(()=>{const now=performance.now();gaps.push(now-previous);previous=now;},50);
       try{const result=await new Promise((resolve,reject)=>{worker.onmessage=e=>resolve(e.data);worker.onerror=e=>reject(Error(e.message));worker.postMessage({build,requests});});return {result,gaps,maxTimerGapMS:Math.max(0,...gaps),hidden:document.hidden,userAgent:navigator.userAgent};}
       finally{clearInterval(timer);worker.terminate();}
     }''',{'build':build,'requests':requests})
     if name=='chromium':result['pageHeap']=context.new_cdp_session(page).send('Runtime.getHeapUsage')
     f.write_text(json.dumps(result,indent=2)+'\n');print(name,build,'worker',result['worker']['result']['ok'],flush=True);context.close()
   finally:browser.close()
finally:server.shutdown()
