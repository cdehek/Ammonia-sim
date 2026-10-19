"""Sequential matched served cases. No original clocks, physics or assertions altered."""
import asyncio,functools,gzip,hashlib,http.server,json,threading,time,traceback,os
from pathlib import Path
import psutil
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{s.server_port}/experiments/dx-fv/'
probe="""(()=>{const data={heartbeat:[],frames:[],clicks:[],tools:[],originalModelCreateMS:[]};let storage;Object.defineProperty(window,'AmmoniaStorage',{configurable:true,get:()=>storage,set:api=>{const make=api.createStorage;storage={...api,createStorage(...args){const model=make(...args),create=model.create;model.create=(...args)=>{const t=performance.now(),state=create(...args);data.originalModelCreateMS.push(performance.now()-t);return state;};return model;}};}});let beat=performance.now(),frame=null,last=null;const timer=setInterval(()=>{const t=performance.now();data.heartbeat.push(t-beat);beat=t;},10);const tick=t=>{if(last!==null)data.frames.push(t-last);last=t;frame=requestAnimationFrame(tick);};frame=requestAnimationFrame(tick);const click=e=>data.clicks.push({id:e.composedPath().find(x=>x.id)?.id,trusted:e.isTrusted,ackMS:performance.now()-e.timeStamp,pending:window.b10?.client?.pending.size??window.shadow?.client?.pending.size??0});document.addEventListener('click',click,true);document.addEventListener('ammonia-console-change',e=>data.tools.push({tool:e.detail.tool,atMS:performance.now()}));window.__probe={data,reset(){for(const a of Object.values(data))a.length=0;beat=performance.now();last=null;},read(){return {data,heap:performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null,nav:performance.getEntriesByType('navigation').map(n=>({domContentLoaded:n.domContentLoadedEventEnd,load:n.loadEventEnd,responseEnd:n.responseEnd}))};}};window.addEventListener('pagehide',()=>{clearInterval(timer);cancelAnimationFrame(frame);document.removeEventListener('click',click,true);},{once:true});})();"""
def memory():
 values=[]
 for p in psutil.Process().children(recursive=True):
  try:values.append({'name':p.name(),'rss':p.memory_info().rss})
  except psutil.Error:pass
 return {'processes':values,'totalRSS':sum(p['rss'] for p in values),'scope':'This runner browser/driver descendants; shared pages may be counted; no worker heap isolation'}
async def main():
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   binary=B/'.runtime/webkit.sh' if name=='webkit' else next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))
   browser=await getattr(pw,name).launch(executable_path=str(binary),headless=True);out={'browser':name,'version':browser.version,'rounds':[],'passed':False}
   try:
    for round in range(2):
     for fixture in ['cold','warm']:
      rows=[]
      for mode in ['A','B','C_D','E']:
       ctx=await browser.new_context(viewport={'width':1440,'height':1000});await ctx.add_init_script(probe);p=await ctx.new_page();path='browser_eos_b10/artifacts/pinned-workstation.html' if mode=='A' else 'browser_eos_b9d/' if mode=='E' else 'browser_eos_b10/'
       start=time.perf_counter();await p.goto(base+path);startupMS=(time.perf_counter()-start)*1000;row={'case':mode,'fixture':fixture,'round':round,'navigationRoundtripMS':startupMS}
       if mode!='E':
        t=time.perf_counter();await p.locator('#storage-example').click();row['originalInitializationRoundtripMS']=(time.perf_counter()-t)*1000;row['originalModelCreationMS']=await p.evaluate('__probe.data.originalModelCreateMS.at(-1)')
        if mode in ['A','B']:
         await p.evaluate('__probe.reset()');t=time.perf_counter();await p.locator('.plant-nav a[href="#storage-form"]').click();row['toolSwitchRoundtripMS']=(time.perf_counter()-t)*1000
         await p.locator('#storage-step').click();await p.wait_for_timeout(100);row['observations']=await p.evaluate('__probe.read()');row['originalClock']=await p.locator('#storage-clock').inner_text();row['A2Absent']=await p.evaluate('!window.b10');rows.append(row);await ctx.close();continue
        t=time.perf_counter();await p.locator('#b10-a2-link').click();await p.wait_for_function('!!window.b10');row['lazyPanelOpenRoundtripMS']=(time.perf_counter()-t)*1000
        await p.evaluate('f=>b10.initialize(f)',fixture);await p.evaluate('__probe.reset()');await p.wait_for_timeout(150)
        idle={'case':'C','fixture':fixture,'round':round,'startup':row,'session':await p.evaluate('b10.metrics.sessions.at(-1)'),'initialize':await p.evaluate('b10.client.metrics[0]'),'observations':await p.evaluate('__probe.read()'),'memory':memory(),'originalClock':await p.locator('#storage-clock').inner_text(),'A2Clock':await p.evaluate('b10.client.view.clockSeconds')};rows.append(idle)
        await p.locator('#storage-start').click();await p.evaluate('__probe.reset()');start=time.perf_counter()
        # True pending worker, trusted original tool input, then return to A2.
        await p.evaluate('window.__advance=b10.action("advance")');t=time.perf_counter();await p.locator('.plant-nav a[href="#plant-diagnostics"]').click();row['toolSwitchDuringComputeMS']=(time.perf_counter()-t)*1000;await p.locator('[data-component="compressor"]').click();await p.evaluate('__advance');await p.locator('#b10-a2-link').click()
        for i in range(2):await p.evaluate('b10.action("advance")')
        row['threeAdvanceRoundtripMS']=(time.perf_counter()-start)*1000;await p.locator('#storage-pause').click();row.update(case='D',metrics=await p.evaluate('b10.client.metrics'),render=await p.evaluate('b10.metrics.renders'),session=await p.evaluate('b10.metrics.sessions.at(-1)'),originalClock=await p.locator('#storage-clock').inner_text(),A2Clock=await p.evaluate('b10.client.view.clockSeconds'))
        snapshot=await p.evaluate('b10.client.view.snapshot');row['snapshotCore']={k:snapshot[k] for k in ['clockSeconds','sections','nodes','flows','totals','conservation']};row['observations']=await p.evaluate('__probe.read()');row['memory']=memory()
        start=time.perf_counter();await p.evaluate('b10.action("dispose")');row['disposeRoundtripMS']=(time.perf_counter()-start)*1000;row['dispose']=await p.evaluate('b10.client.metrics.at(-1)');await p.evaluate('f=>b10.initialize(f)',fixture);row['restart']=await p.evaluate('b10.metrics.sessions.at(-1)');await p.evaluate('b10.action("dispose")');rows.append(row)
       else:
        await p.wait_for_function('!!window.shadow');await p.evaluate('f=>shadow.initialize(f)',fixture);await p.evaluate('__probe.reset()');start=time.perf_counter()
        for i in range(3):await p.evaluate('shadow.action("advance")')
        row['threeAdvanceRoundtripMS']=(time.perf_counter()-start)*1000;row['metrics']=await p.evaluate('shadow.client.metrics');snapshot=await p.evaluate('shadow.client.view.snapshot');row['snapshotCore']={k:snapshot[k] for k in ['clockSeconds','sections','nodes','flows','totals','conservation']};row['observations']=await p.evaluate('__probe.read()');row['memory']=memory();await p.evaluate('shadow.action("dispose")');rows.append(row)
       await ctx.close()
      d=next(r for r in rows if r['case']=='D');e=next(r for r in rows if r['case']=='E');assert d['snapshotCore']==e['snapshotCore'] and d['A2Clock']==.001
      ref=await browser.new_page();await ref.goto(base+'browser_eos_b9c/');await ref.wait_for_function('!!window.workerRun');bare=await ref.evaluate('a=>workerRun(a)',{'fixture':fixture,'mode':'candidate','observed':False});await ref.close();saved=json.loads(gzip.decompress((E/f'review-{name}.json.gz').read_bytes()));assert bare['scienceHash']==saved['results'][fixture]['control']['scienceHash'] and saved['results'][fixture]['savedB9CMatch'];rows.append({'case':'bareB9C','result':bare});out['rounds'].append({'round':round,'fixture':fixture,'matchedScience':True,'cases':rows});print(name,round,fixture,'PASS',flush=True)
    out['passed']=True
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
   finally:
    await browser.close();(E/f'performance-{name}.json').write_text(json.dumps(out,indent=2)+'\n')
   if not out['passed']:raise RuntimeError(out['error'])
try:asyncio.run(main())
finally:s.shutdown()
