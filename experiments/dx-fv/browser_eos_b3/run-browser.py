"""Focused real desktop-engine experiment, local server only, no hosting."""
import functools,http.server,json,os,threading,time,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B3_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   options={'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE') else {}
   try: browser=getattr(pw,name).launch(timeout=30000,**options)
   except Exception as e:
    (E/f'{name}-launch-failure.json').write_text(json.dumps(dict(error=str(e)),indent=2)+'\n');continue
   try:
    for build in ['official8','build30','build44','official72']:
     target=E/f'{name}-{build}.json';assert not target.exists(),target
     page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/',timeout=30000)
     t=time.monotonic()
     try:
      # A JS deadline catches cooperative failures; the shell applies a hard
      # 600-second process deadline even if synchronous WASM stalls.
      result=page.evaluate('''async ({build,requests,references,engine,table})=>{
       const {loadEOS}=await import('./loader.mjs');const {run}=await import('../browser_eos_b3/browser.mjs');
       const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table);
       const eos=await loadEOS(build);try{return {init:eos.init,...run(eos,requests,references,guard)};}finally{eos.dispose();}
      }''',dict(build=build,requests=json.loads((B/'inputs.json').read_text()),references=json.loads((E/'native-wheel8.json').read_text())['rows'],engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text())))
      result.update(browser=name,browserVersion=browser.version,build=build,elapsedSeconds=time.monotonic()-t,physicalIPad=False)
      target.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
      print(name,build,len(result['rows']),round(time.monotonic()-t,2),flush=True)
     except Exception as e:
      target.with_suffix('.failure.json').write_text(json.dumps(dict(error=str(e),traceback=traceback.format_exc()),indent=2)+'\n')
     finally:page.close()
   finally:browser.close()
finally:server.shutdown()
