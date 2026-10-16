"""Focused desktop Chromium/WPE WebKit, local loopback only. Hard shell deadline."""
import os
import argparse,functools,http.server,json,os,threading,time,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'))
ap=argparse.ArgumentParser();ap.add_argument('--builds',default='control44,liquid44');ap.add_argument('--primary-only',action='store_true');ap.add_argument('--performance',action='store_true');ap.add_argument('--references',default='native-control44.json');args=ap.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.wasm':'application/wasm'}
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
references=json.loads((E/args.references).read_text())['rows'];requests=[r['request']for r in references]
if args.primary_only:requests=[q for q in requests if q['args']==[30298.937123458254,98904.56398938334]]
historical=json.loads((B.parent/'browser_eos_b3/evidence/chromium-build44.json').read_text())['rows']
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   options={'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE') else {}
   try:browser=getattr(pw,name).launch(timeout=30000,**options)
   except Exception as exc:
    f=E/f'{name}-launch-failure.json';assert not f.exists();f.write_text(json.dumps(dict(error=str(exc)),indent=2)+'\n');continue
   try:
    for build in args.builds.split(','):
     kind='performance' if args.performance else 'primary' if args.primary_only else 'focused'
     f=E/f'{name}-{build}-{kind}.json';assert not f.exists();page=browser.new_page();start=time.monotonic()
     try:
      page.goto(f'http://127.0.0.1:{server.server_port}/',timeout=30000)
      out=page.evaluate('''async({build,requests,references,historical,engine,table,perf})=>{
       const {loadEOS}=await import('/experiments/dx-fv/browser_eos_b4a/loader.mjs');
       const {run,performanceWork}=await import('/experiments/dx-fv/browser_eos_b4a/browser.mjs');
       const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table);
       const eos=await loadEOS(build);try{return {init:eos.init,...(perf?performanceWork(eos,requests):run(eos,requests,references,historical,guard))};}finally{eos.dispose();}
      }''',dict(build=build,requests=requests,references=references,historical=historical,engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text()),perf=args.performance))
      out.update(browser=name,browserVersion=browser.version,build=build,elapsedSeconds=time.monotonic()-start,physicalIPad=False)
      f.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(name,build,kind,'complete',flush=True)
     except Exception as exc:f.write_text(json.dumps(dict(error=str(exc),traceback=traceback.format_exc()),indent=2)+'\n')
     finally:page.close()
   finally:browser.close()
finally:server.shutdown()
