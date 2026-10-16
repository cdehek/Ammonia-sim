"""Bounded unchanged browser controls; never writes historical evidence."""
import functools,http.server,json,os,threading,time,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];X=B.parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'))
def read(p):return json.loads(p.read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.wasm':'application/wasm'}
 def log_message(self,*a):pass
fixed=read(X/'browser_eos_b5/evidence/fixed-inputs.json')
args=dict(sweep=read(X/'browser_eos_b5/evidence/boundary-sweep.json')['rows'],
 falseAcceptanceControls=[r for r in fixed if r['key'] in ['webkit-ledger-69','webkit-ledger-76']],
 endpoints=[r for r in fixed if r['key'] in ['native-ledger-148','native-ledger-162','native-ledger-164','native-ledger-165']],
 engine=(R/'engine.js').read_text(),table=read(R/'properties.json'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
args['origins']=[]
focused=read(X/'browser_eos_b4c/evidence/webkit-candidateB-focused.json')['rows']
for f in args['falseAcceptanceControls']:
 q=next(r for r in focused if r['id']==f['id']);args['origins'].append(dict(key=f['key'],requestBits=q['inputBits'],inventoryBits=f['input']['bits']))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in os.environ.get('C2_ENGINES','chromium,webkit').split(','):
   args['fixtures']=[r for r in read(X/'browser_eos_b5/evidence/original-failures.json')['rows'] if r['runtime']==name]
   start=time.perf_counter();out={}
   try:
    browser=getattr(pw,name).launch(executable_path=os.environ.get(name.upper()+'_PATH','/usr/bin/chromium' if name=='chromium' else '/workspace/c2-browsers/webkit-2336/pw_run.sh'),timeout=30000,**({'args':['--no-sandbox']} if name=='chromium' else {}))
    page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/')
    originOnly=bool(os.environ.get('C2_ORIGINS_ONLY'))
    out=page.evaluate("async args=>{const m=await import('/experiments/dx-fv/browser_eos_b5b_c2/browser.mjs');return m[args.originOnly?'origins':'run'](args);}",{**args,'originOnly':originOnly})
    out.update(browser=name,version=browser.version,physicalIPad=False)
    if originOnly:
     out['historicalExactMatch']=True
     page.close();browser.close()
     out['elapsedSeconds']=time.perf_counter()-start
     p=E/(name+'-origins.json');assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(name,'origins exact',flush=True)
     continue
    old=read(X/f'browser_eos_b5b/evidence/{name}-replay.json')
    for group in ['rows','falseAcceptance']:
     for row,prior in zip(out[group],old[group]):
      assert row['input']['bits']==prior['input']['bits'];assert row['raw']['bits']==prior['raw']['bits']
      assert ('adapter' in row)==('adapter' in prior)
    assert len(out['rows'])==7 and all('error'in r for r in out['rows'])
    assert all('adapter'in r for r in out['falseAcceptance'])
    assert sum('adapter'in r for r in out['c1'])==2
    out['historicalExactMatch']=True
    page.close();browser.close()
   except Exception as ex:out.update(error=str(ex),traceback=traceback.format_exc())
   out['elapsedSeconds']=time.perf_counter()-start
   p=E/(name+'-replay.json');assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(name,out.get('historicalExactMatch'),out.get('error','completed'),flush=True)
finally:server.shutdown()
