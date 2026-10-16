import argparse,functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'))
ap=argparse.ArgumentParser();ap.add_argument('--performance',action='store_true');ap.add_argument('--builds',default='controlA,candidateB');args=ap.parse_args()
cases=json.loads((E/'lifecycle-controlA.json').read_text())['cases']
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   browser=getattr(pw,name).launch(timeout=30000,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']}if name=='webkit'else{}))
   try:
    for build in args.builds.split(','):
     kind='cost' if args.performance else 'lifecycle'
     target=E/f'{name}-{build}-{kind}.json'
     assert not target.exists();page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/')
     try:
      out=page.evaluate('''async({build,cases,perf})=>{
       const {loadEOS}=await import('/experiments/dx-fv/browser_eos_b4c/loader.mjs');const {lifecycle,performanceWork}=await import('/experiments/dx-fv/browser_eos_b4c/lifecycle.mjs');
       const eos=await loadEOS(build);let out;try{out={init:eos.init,...(perf?performanceWork(eos,cases):lifecycle(eos,cases))};}finally{eos.dispose();}
       if(perf){let ticks=0,last=performance.now(),maxGapMS=0;const timer=setInterval(()=>{let now=performance.now();maxGapMS=Math.max(maxGapMS,now-last);last=now;ticks++;},10),w=new Worker('/experiments/dx-fv/browser_eos_b4c/worker.mjs',{type:'module'});try{out.worker=await new Promise((resolve,reject)=>{w.onmessage=e=>resolve(e.data);w.onerror=e=>reject(Error(e.message));w.postMessage({build,cases});});out.mainThreadDuringWorker={ticks,maxGapMS};}finally{clearInterval(timer);w.terminate();}}
       return out;}''',dict(build=build,cases=cases,perf=args.performance))
      out.update(browser=name,browserVersion=browser.version,build=build,physicalIPad=False)
     except Exception as exc:out=dict(error=str(exc))
     target.write_text(json.dumps(out,indent=2)+'\n');page.close();print(name,build,'done',flush=True)
   finally:browser.close()
finally:server.shutdown()
