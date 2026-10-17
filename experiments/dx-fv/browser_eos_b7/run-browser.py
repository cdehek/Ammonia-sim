"""Bounded actual Chromium/desktop WebKit execution; retain failed attempts."""
import argparse,functools,http.server,json,math,os,threading,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
def json_safe(value):
 # The original B6 synthetic validation cases actually execute NaN/Infinity.
 # Preserve those observations in strict JSON with explicit representation tags;
 # never substitute a finite value into a scientific input or execution.
 if isinstance(value,float) and not math.isfinite(value):return {'nonfiniteBinary64':str(value)}
 if isinstance(value,dict):return {k:json_safe(v) for k,v in value.items()}
 if isinstance(value,list):return [json_safe(v) for v in value]
 return value
p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--engines',default='chromium,webkit');p.add_argument('--tag',default='');a=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in a.engines.split(','):
   target=E/f'{a.stage}-{name}{a.tag}.json';assert not target.exists(),target
   browser=None;out={};logs=[]
   try:
    opts=dict(timeout=30000,headless=True)
    if name=='webkit':opts['executable_path']='/workspace/b7-work/webkit.sh'
    browser=getattr(pw,name).launch(**opts);page=browser.new_page();page.set_default_timeout(120000)
    page.on('console',lambda m:logs.append(dict(type=m.type,text=m.text)))
    page.on('pageerror',lambda e:logs.append(dict(type='pageerror',text=str(e))))
    page.goto(f'http://127.0.0.1:{server.server_port}/',timeout=30000)
    out['result']=page.evaluate("async args=>{const {run}=await import('/experiments/dx-fv/browser_eos_b7/browser.mjs');return run(args);}",dict(engine=name,stage=a.stage))
    out.update(engine=name,browserVersion=browser.version,userAgent=page.evaluate('navigator.userAgent'),physicalSafariOrIPad=False)
   except Exception as ex:out.update(harnessError=str(ex),traceback=traceback.format_exc())
   finally:
    if browser:browser.close()
    out['console']=logs;target.write_text(json.dumps(json_safe(out),indent=2,allow_nan=False)+'\n');print(target.name,'ERROR' if 'harnessError' in out else 'complete',flush=True)
finally:server.shutdown()
