"""Matched 30/44 worker cost. Run only after scientific workers have exited."""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
sources={p.name:p.read_text() for p in (B.parent/'browser_eos_backend/accepted').glob('*.cjs')}
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   browser=getattr(p,name).launch(**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' else {}))
   try:
    for build in (['build30','build44'] if name=='chromium' else ['build44','build30']):
     f=E/f'{name}-coupled-cost-{build}.json';assert not f.exists()
     page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b2/')
     r=page.evaluate('''async data=>{const worker=new Worker('./coupled-cost-worker.mjs',{type:'module'}),gaps=[];let prev=performance.now();const timer=setInterval(()=>{let now=performance.now();gaps.push(now-prev);prev=now;},50);try{const result=await new Promise((resolve,reject)=>{worker.onmessage=e=>resolve(e.data);worker.onerror=e=>reject(Error(e.message));worker.postMessage(data);});return {result,pageMaxTimerGapMS:Math.max(0,...gaps),gaps};}finally{clearInterval(timer);worker.terminate();}}''',dict(build=build,sources=sources,engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text())))
     r.update(browser=name,browserVersion=browser.version)
     if name=='chromium':r['pageCDPHeapAfterWorker']=page.context.new_cdp_session(page).send('Runtime.getHeapUsage')
     f.write_text(json.dumps(r,indent=2)+'\n');page.close();print(name,build,'complete',flush=True)
   finally:browser.close()
finally:server.shutdown()
