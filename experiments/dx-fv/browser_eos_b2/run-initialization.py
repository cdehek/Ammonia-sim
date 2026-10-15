"""Supplemental zero-exchange initialization at exact failed boundary inputs.

Original accepted source/geometry; additional declared diagnostic configurations,
never replacements for accepted operating fixtures. No integration is advanced.
"""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
sources={p.name:p.read_text() for p in (B.parent/'browser_eos_backend/accepted').glob('*.cjs')}
requests=json.loads((E/'chromium-boundary-build44.json').read_text())['rows']
if os.environ.get('B2_INIT_DETAIL'):requests=[r for r in requests if r['id'] in ['approach-30298.937123458254-liquid-0.001','approach-3500000.0-liquid-1e-05']]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   browser=getattr(p,name).launch(**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' else {}))
   try:
    for build in os.environ.get('B2_INIT_BUILDS','build30,build44').split(','):
     f=E/f'{name}-initialization{"-detail" if os.environ.get("B2_INIT_DETAIL") else ""}-{build}.json';assert not f.exists()
     page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/')
     r=page.evaluate('''async({build,requests,sources,engine,table})=>{
      const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table);
      const {loadEOS}=await import('./loader.mjs'),{createAdapter}=await import('./adapter.mjs');const eos=await loadEOS(build),adapter=createAdapter(eos,guard),cache={},rows=[];
      function require(name){const key=name.slice(2);if(cache[key])return cache[key].exports;const m={exports:{}};cache[key]=m;new Function('module','exports','require',sources[key])(m,m.exports,require);return m.exports;}
      const {createCoupledModel}=require('./coupled-model.cjs');
      try{for(const q of requests){const [p,h]=q.adapterInputs,row={id:q.id,exactSIInputs:q.exactSIInputs,adapterInputs:[p,h]};
       try{row.supportGuard=guard.ph(p,h);const requested=adapter.ph(p,h),T=requested.T+273.15;const model=createCoupledModel(adapter,{timestepGrowth:'failure-aware'});
        const state=model.create({sealed:true,refrigerantConductanceKWK:0,initial:Array.from({length:5},()=>({p,h})),thermal:{tubeProfileK:T,finProfileK:T,airInitialK:T,airLoadKW:0}});
        row.initial=model.record(state);row.initialRequestedDifferences=row.initial.sections.map(s=>({pressureBar:s.p-p,enthalpyKJkg:s.h-h,temperatureK:s.T-requested.T}));
        const before=JSON.stringify(state),work={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};try{const trial=model.trial(state,.001,work);row.pureZeroExchangeTrial={completed:true,cells:trial.cells};}catch(e){row.pureZeroExchangeTrial={completed:false,error:String(e),faultKind:e.faultKind,evidence:e.evidence};}row.pureZeroExchangeTrial.work=work;row.exactTrialStatePreserved=JSON.stringify(state)===before;
       }catch(e){row.error=String(e);row.faultKind=e.faultKind;row.evidence=e.evidence;}
       rows.push(row);}
       return {build,rows,counts:adapter.counts,linearMemory:eos.memory(),supplementalDiagnostic:true,secondsAdvanced:0};
      }finally{eos.dispose();}
     }''',dict(build=build,requests=requests,sources=sources,engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text())))
     r.update(browser=name,browserVersion=browser.version);f.write_text(json.dumps(r,indent=2)+'\n');page.close();print(name,build,'complete',flush=True)
   finally:browser.close()
finally:server.shutdown()
