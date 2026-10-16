"""Replay fixed browser inventories through both libraries and the unchanged guard."""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4B_EVIDENCE',B/'evidence'))
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright()as pw:
  for engine in ['chromium','webkit']:
   inputs=[]
   for origin in ['controlA','candidateB']:
    for row in json.loads((E/f'{engine}-{origin}-focused.json').read_text())['rows']:
     if row['args'][0]==3500000.:inputs.append(dict(origin=origin,id=row['id'],input=row['inventories']['C']['input']['values']))
   browser=getattr(pw,engine).launch(**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']}if engine=='webkit'else{}));page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/')
   try:
    result=page.evaluate('''async({inputs,engine,table})=>{
     const {loadEOS}=await import('/experiments/dx-fv/browser_eos_b4b/loader.mjs'),{createAdapter}=await import('/experiments/dx-fv/browser_eos_backend/adapter.mjs');const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table),rows=[];
     for(const build of ['controlA','candidateB']){const eos=await loadEOS(build),adapter=createAdapter(eos,guard);try{for(const q of inputs){const x=q.input,row={...q,build};try{row.DU=eos.evaluate({mode:'DU',args:[x.rho,x.u]});}catch(e){row.rawError=String(e);}try{row.adapter=adapter.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){row.adapterError=String(e);}rows.push(row);}}finally{eos.dispose();}}
     return {rows};}''',dict(inputs=inputs,engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text())))
    rows=result['rows'];comparisons=[]
    for a in [r for r in rows if r['build']=='controlA']:
     b=next(r for r in rows if r['build']=='candidateB'and r['id']==a['id']and r['origin']==a['origin']);comparisons.append(dict(id=a['id'],origin=a['origin'],rawEqual=a.get('DU')==b.get('DU')and a.get('rawError')==b.get('rawError'),guardEqual=a.get('adapter')==b.get('adapter')and a.get('adapterError')==b.get('adapterError')))
    result.update(comparisons=comparisons,allEqual=all(r['rawEqual']and r['guardEqual']for r in comparisons),browser=engine,browserVersion=browser.version)
    p=E/f'{engine}-35bar-fixed-inventories.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');assert result['allEqual'];print(engine,len(comparisons),'fixed inventories identical raw/guard behavior',flush=True)
   finally:page.close();browser.close()
finally:server.shutdown()
