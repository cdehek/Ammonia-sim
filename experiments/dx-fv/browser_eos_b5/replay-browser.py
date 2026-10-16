"""Unmodified B4C/B4B loaders and adapter, identical cross-runtime inventories."""
import functools,http.server,json,threading,os
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));H=B.parent/'browser_eos_b4c/evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
inputs=json.loads((E/'fixed-inputs.json').read_text())
ph=[]
for engine in ['chromium','webkit']:
 for r in json.loads((H/(engine+'-candidateB-focused.json')).read_text())['rows']:
  if r['args'][0]==3500000:ph.append(dict(engine=engine,id=r['id'],args=r['args'],historical=r['base']['state']))
try:
 with sync_playwright() as pw:
  for engine in ['chromium','webkit']:
   try:
    browser=getattr(pw,engine).launch(executable_path='/usr/bin/chromium' if engine=='chromium' else '/workspace/b5-webkit.sh',**({'args':['--no-sandbox']}if engine=='chromium'else{}))
    page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/')
    result=page.evaluate('''async({inputs,ph,engine,table})=>{
     const {loadEOS}=await import('/experiments/dx-fv/browser_eos_b4c/loader.mjs'),{createAdapter}=await import('/experiments/dx-fv/browser_eos_backend/adapter.mjs');
     const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table),rows=[],phRows=[];
     const bits=x=>{const b=new ArrayBuffer(8),d=new DataView(b);d.setFloat64(0,x);return d.getBigUint64(0).toString(16).padStart(16,'0');};
     for(const build of ['controlA','candidateB']){const eos=await loadEOS(build),adapter=createAdapter(eos,guard);
      try{for(const q of inputs){if(q.fullVLE)continue;const x=q.input.values,row={key:q.key,build,inputBits:Object.fromEntries(Object.entries(x).map(([k,v])=>[k,bits(v)]))};
       try{row.DU=eos.evaluate({mode:'DU',args:[x.rho,x.u]});row.bits=Object.fromEntries(Object.entries(row.DU).map(([k,v])=>[k,bits(v)]));}catch(e){row.rawError=String(e);}
       try{row.adapter=adapter.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){row.adapterError=String(e);row.faultKind=e.faultKind;}
       rows.push(row);
      }
      for(const q of ph){const row={...q,build};try{row.PH=eos.evaluate({mode:'PH',args:q.args});}catch(e){row.error=String(e);}phRows.push(row);}
      }finally{eos.dispose();}}
     return {rows,phRows,fullVLE:'Not exposed by the preserved browser binding; native comparison retained separately.'};
    }''',dict(inputs=inputs,ph=[x for x in ph if x['engine']==engine],engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text())))
    result.update(browser=engine,version=browser.version);page.close();browser.close()
   except Exception as ex:result=dict(browser=engine,setupError=str(ex))
   (E/(engine+'-fixed-replay.json')).write_text(json.dumps(result,indent=2)+'\n');print(engine,len(result.get('rows',[])),result.get('setupError','completed'),flush=True)
finally:server.shutdown()
