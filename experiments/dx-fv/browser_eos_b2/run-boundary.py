import os
"""Exact additional boundary regression, unchanged canonical equations/budgets."""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
q=json.loads((E/'chromium-phase-build44.json').read_text())
requests=[r for r in q['rows'] if r['id'].startswith('approach-') and r.get('base',{}).get('state',{}).get('Q',0)<0 and r['base']['phase']==6]
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   opts={'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' else {}
   browser=getattr(p,name).launch(**opts)
   try:
    for build in ['build30','build44']:
     page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/')
     result=page.evaluate('''async ({requests,build,engine,table})=>{
      const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table);
      const {loadEOS}=await import('./loader.mjs');const {createAdapter}=await import('./adapter.mjs');const eos=await loadEOS(build),adapter=createAdapter(eos,guard),rows=[];
      try{for(const q of requests){const [P,H]=q.args,p=P/1e5,h=H/1000,V=.003/5,row={id:q.id,exactSIInputs:q.args,adapterInputs:[p,h],adapterRoundTripSI:[p*1e5,h*1000],inputBits:q.inputBits};
       try{row.guard=guard.ph(p,h);row.PH=adapter.ph(p,h);const M=row.PH.rho*V,U=M*h-100*p*V;row.inventory={M,V,U};row.recovered=adapter.stateMVU(M,V,U,p);row.differences={pressureBar:row.recovered.p-p,enthalpyKJkg:row.recovered.h-h,temperatureK:row.recovered.T-row.PH.T};row.canonicalCompatibilityPass=Math.abs(row.differences.pressureBar)<=1e-6&&Math.abs(row.differences.enthalpyKJkg)<=1e-4&&Math.abs(row.differences.temperatureK)<=1e-4;
       }catch(e){row.error=String(e);row.canonicalCompatibilityPass=false;}rows.push(row);}
       return {rows,counts:adapter.counts,linearMemory:eos.memory()};
      }finally{eos.dispose();}
     }''',dict(requests=requests,build=build,engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text())))
     result.update(browser=name,browserVersion=browser.version,build=build,limits=dict(pressureBar=1e-6,enthalpyKJkg=1e-4,temperatureK=1e-4),additionalRegression=True)
     f=E/f'{name}-boundary-{build}.json';assert not f.exists();f.write_text(json.dumps(result,indent=2)+'\n');page.close();print(name,build,len(result['rows']),sum(r['canonicalCompatibilityPass'] for r in result['rows']),flush=True)
   finally:browser.close()
finally:server.shutdown()
