"""Bounded actual browser runs; refuses to overwrite evidence."""
import argparse,functools,http.server,json,os,threading,hashlib,subprocess,platform,importlib.metadata,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
ap=argparse.ArgumentParser();ap.add_argument('--stage',default='a');ap.add_argument('--engines',default='chromium,webkit');ap.add_argument('--replicas',type=int,default=2);args=ap.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
cases=json.loads((B.parent/'browser_eos_b4c/evidence/lifecycle-controlA.json').read_text())['cases']
fixtures=json.loads((E/'historical-rejected-pt.json').read_text())
try:
 with sync_playwright() as pw:
  for name in args.engines.split(','):
   for replica in range(args.replicas):
    target=E/f'gate-{args.stage}-{name}-{replica}.json';assert not target.exists(),target
    console=[];out={};browser=None
    try:
     exe=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium') if name=='chromium' else os.environ.get('WEBKIT_PATH','/workspace/b6-browsers/webkit-2336/b6-wpe.sh')
     browser=getattr(pw,name).launch(executable_path=exe,timeout=30000)
     page=browser.new_page();page.on('console',lambda m:console.append(dict(type=m.type,text=m.text)));page.on('pageerror',lambda e:console.append(dict(type='pageerror',text=str(e))))
     page.goto(f'http://127.0.0.1:{server.server_port}/',timeout=30000)
     if args.stage=='a':
      results=[]
      for kind in ['historical','diagnostic']:
       results.append(page.evaluate("async a=>{const {run}=await import('/experiments/dx-fv/browser_eos_b6/gate-a.mjs');return run(a.kind,a.cases,a.fixtures);}",dict(kind=kind,cases=cases,fixtures=[v for v in fixtures if v['engine']==name])))
      out['runs']=results
     else:
      out['result']=page.evaluate("async a=>{const {run}=await import('/experiments/dx-fv/browser_eos_b6/gate-b.mjs');return run(a);}",dict(engine=name))
     out.update(browser=name,browserVersion=browser.version,replica=replica,executable=exe,userAgent=page.evaluate('navigator.userAgent'),physicalIPad=False)
    except Exception as exc:out['harnessError']=str(exc)
    finally:
     if browser:browser.close()
     out['console']=console;target.write_text(json.dumps(out,indent=2)+'\n');print(target.name,'ERROR' if 'harnessError' in out else 'complete',flush=True)
finally:server.shutdown()
