"""Exercise original accepted five-section A2 sources by dependency injection.

Each sample is persisted. This does not rewrite references or alter solver limits.
"""
import functools,http.server,json,os,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
for name in ['chromium','webkit']:
    q=json.loads((E/f'{name}-synthetic-build44.json').read_text())
    assert all(r['converged'] for r in q['rows']), 'Synthetic gate failed'
class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.wasm':'application/wasm'}
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
sources={p.name:p.read_text() for p in (B/'accepted').glob('*.cjs')}
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   browser=getattr(p,name).launch(headless=True,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE') else {}))
   try:
    for case in ['cold','warm','load-step','feed-step','heat-reversal']:
     for tol in [1e-6,1e-7,1e-8]:
      f=E/f'{name}-coupled-{case}-{tol}.json'
      if f.exists():continue
      context=browser.new_context();page=context.new_page()
      page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/');page.wait_for_function('!!window.b1')
      print(name,case,tol,'start',flush=True)
      started=time.monotonic()
      report={'browser':name,'browserVersion':browser.version,'case':case,'relativeTolerance':tol,'build':'build44',
        'sourceCommit':'be9eb35a4ddf5098e685182f8104685127c6a6ee','physicalIPad':False,'rows':[],
        'selection':{'thermalJacobian':'finite-difference','timestepGrowth':'failure-aware'}}
      try:
       result=page.evaluate('''async ({sources,engine,table,caseName,tol})=>{
        const cache={};function require(name){const key=name.startsWith('./')?name.slice(2):name;if(cache[key])return cache[key].exports;
          if(!sources[key])throw Error('Unexpected original-model import '+name);const m={exports:{}};cache[key]=m;new Function('module','exports','require',sources[key])(m,m.exports,require);return m.exports;}
        const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table);
        const e=await b1.loadEOS('build44');const {createAdapter}=await import('./adapter.mjs');const adapter=createAdapter(e,guard);
        const F=require('coupled-fixtures.cjs'),c=F.cases().find(c=>c.name===caseName);
        const attempts=[];const model=require('coupled-model.cjs').createCoupledModel(adapter,{...F.accuracyOptions(tol),trace:true,thermalJacobian:'finite-difference',timestepGrowth:'failure-aware'},a=>{
          if(a.accepted===false||a.failure)attempts.push(a);
        });
        const s=model.create(c.config);window.coupled={model,s,e,adapter,attempts};
        return {initial:model.record(s),samples:c.samples,settings:model.record(s).settings,initialTable:c.config.initial.map(v=>guard.ph(v.p,v.h)),init:e.init};
       }''',{'sources':sources,'engine':(R/'engine.js').read_text(),'table':json.loads((R/'properties.json').read_text()),'caseName':case,'tol':tol})
       report.update(result);f.write_text(json.dumps(report,indent=2)+'\n')
       for t in result['samples']:
        record=page.evaluate('''t=>{const {model,s,adapter,e,attempts}=coupled;const start=performance.now();const record=model.advance(s,t-s.seconds);return {record,elapsedMS:performance.now()-start,counts:{...adapter.counts},linearMemory:e.memory(),failedAttempts:attempts.splice(0)};}''',t)
        report['rows'].append(record);report['elapsedSeconds']=time.monotonic()-started
        f.write_text(json.dumps(report,indent=2)+'\n')
        print(name,case,tol,t,'reached',record['record']['seconds'],'stop',record['record']['stop'],flush=True)
        if record['record']['stop'] is not None:break
       report['completedAllSamples']=len(report['rows'])==len(result['samples']) and report['rows'][-1]['record']['stop'] is None
       report['finalStateDiagnostics']=page.evaluate('''()=>{const {s,adapter,e}=coupled;return {rejectionTrace:s.rejectionTrace,trace:s.trace,counts:adapter.counts,linearMemory:e.memory()};}''')
       page.evaluate('coupled.e.dispose()')
      except Exception as exc:report['harnessError']=str(exc);report['completedAllSamples']=False
      finally:
       report['elapsedSeconds']=time.monotonic()-started;f.write_text(json.dumps(report,indent=2)+'\n');context.close()
   finally:browser.close()
finally:server.shutdown()
