"""Gated static M/U/V test using original accepted Newton source, unchanged."""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2]
class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.wasm':'application/wasm'}
    def log_message(self,*args):pass
summary=json.loads((B/'evidence/precision-summary-8.0.0.json').read_text())
assert all(next(r for r in summary if r['file']==f'{browser}-build44.json')['standaloneScreenPass'] for browser in ['chromium','webkit'])
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
sources={n:(B/'accepted'/n).read_text() for n in ['implicit.cjs','coupled-implicit.cjs']}
targets=json.loads((B.parent/'browser_eos_precision/evidence/native-contract.json').read_text())['targets']
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   browser=getattr(p,name).launch(headless=True,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE') else {}))
   try:
    for build in ['official8','build30','build44','official72']:
     f=B/'evidence'/f'{name}-synthetic-{build}.json'
     if f.exists():continue
     context=browser.new_context();page=context.new_page()
     page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/');page.wait_for_function('!!window.b1')
     result=page.evaluate('''async({build,sources,targets})=>{
       const l={exports:{}};new Function('module','exports',sources['implicit.cjs'])(l,l.exports);
       const n={exports:{}};new Function('module','exports','require',sources['coupled-implicit.cjs'])(n,n.exports,key=>{if(key!=='./implicit.cjs')throw Error(key);return l.exports;});
       const {synthetic}=await import('../browser_eos_precision/synthetic.mjs');
       const e=await b1.loadEOS(build);try{return {build,init:e.init,...synthetic(e,targets,n.exports.coupledNewton),linearMemory:e.memory()};}finally{e.dispose();}
     }''',{'build':build,'sources':sources,'targets':targets})
     result.update(browser=name,browserVersion=browser.version,physicalIPad=False,solverSourceCommit='be9eb35a4ddf5098e685182f8104685127c6a6ee',nineSectionCaution='Original accepted Newton numerical algorithm is generic. Its diagnostic split is hardcoded at ten fluid rows; N=9 norms must be read from full residuals. No exact thermal Jacobian supplied. Coupled A2 is five sections only.')
     f.write_text(json.dumps(result,indent=2)+'\n');print(name,build,sum(r['converged'] for r in result['rows']),'/',len(result['rows']),flush=True);context.close()
   finally:browser.close()
finally:server.shutdown()
