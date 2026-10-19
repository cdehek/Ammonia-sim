"""Matched sequential B10/B11 measurements; exact same bounded workload each time."""
import asyncio,functools,http.server,json,threading,time,traceback,resource,subprocess
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start()
def memory():
 # Sum browser/driver descendant RSS, including shared pages; coarse observation only.
 rows=subprocess.check_output(['ps','-eo','pid=,ppid=,rss=,comm=']).decode().splitlines();table=[r.split(None,3) for r in rows];import os
 ids={os.getpid()}
 for _ in range(8):ids|={int(p) for p,pp,rss,n in table if int(pp) in ids}
 processes=[{'name':n,'rssKiB':int(rss)} for p,pp,rss,n in table if int(p) in ids and int(p)!=os.getpid() and n!='ps']
 return {'processes':processes,'totalRSSKiB':sum(p['rssKiB'] for p in processes),'limit':'Browser/driver descendants; shared pages may be counted more than once; no worker heap isolation'}
async def run():
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   binary=B/'.runtime/webkit.sh' if name=='webkit' else next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))
   browser=await getattr(pw,name).launch(executable_path=str(binary),headless=True);out={'browser':name,'version':browser.version,'passed':False,'samples':[],'viewport':[1440,1000],'sequential':True}
   try:
    for round in range(2):
     for fixture in ['cold','warm']:
      pair=[]
      for mode in (['B10','B11'] if round==0 else ['B11','B10']):
       ctx=await browser.new_context(viewport={'width':1440,'height':1000});await ctx.add_init_script((B/'performance-probe.js').read_text());p=await ctx.new_page()
       path='browser_eos_b10/' if mode=='B10' else 'browser_eos_b11/preview/'
       row={'mode':mode,'fixture':fixture,'round':round};t=time.perf_counter();await p.goto(f'http://127.0.0.1:{s.server_port}/experiments/dx-fv/'+path);await p.wait_for_function('AmmoniaStartup.ready');row['navigationToOriginalReadyMS']=(time.perf_counter()-t)*1000
       assert await p.evaluate('!window.b10');t=time.perf_counter();await p.locator('#storage-example').click();row['originalInitializeMS']=(time.perf_counter()-t)*1000;row['originalModelCreateMS']=await p.evaluate('__probe.data.originalModelCreateMS.at(-1)')
       t=time.perf_counter();await p.locator('#b10-a2-link').click();await p.wait_for_function('!!window.b10');row['lazyPanelMS']=(time.perf_counter()-t)*1000
       await p.locator('#b10-a2-shadow #'+fixture).click();await p.wait_for_function('b10.client?.view.status==="ready"');row['session']=await p.evaluate('b10.metrics.sessions.at(-1)');row['initialization']=await p.evaluate('b10.client.metrics[0]');row['memoryReady']=memory()
       await p.locator('#storage-start').click();await p.evaluate('__probe.reset()');t=time.perf_counter();await p.evaluate('window.__advance=b10.action("advance")');switch=time.perf_counter();await p.locator('.plant-nav a[href="#plant-diagnostics"]').click();row['switchDuringComputeMS']=(time.perf_counter()-switch)*1000
       await p.locator('[data-component="compressor"]').click();await p.evaluate('__advance');await p.locator('#b10-a2-link').click()
       for i in range(2):await p.evaluate('b10.action("advance")')
       row['threeAdvanceWithToolsMS']=(time.perf_counter()-t)*1000;await p.locator('#storage-pause').click();row['workerMetrics']=await p.evaluate('b10.client.metrics');row['renderMS']=await p.evaluate('b10.metrics.renders');row['observations']=await p.evaluate('__probe.read()');row['memoryAfter']=memory();row['clock']=await p.evaluate('b10.client.view.clockSeconds');assert row['clock']==.001
       snap=await p.evaluate('b10.client.view.snapshot');row['scientificSnapshot']={k:snap[k] for k in ['clockSeconds','sections','nodes','flows','totals','conservation','numerics']}
       t=time.perf_counter();await p.evaluate('b10.action("dispose")');row['disposeMS']=(time.perf_counter()-t)*1000;await p.evaluate('f=>b10.initialize(f)',fixture);row['restart']=await p.evaluate('b10.metrics.sessions.at(-1)');await p.evaluate('b10.action("dispose")');row['resources']=await p.evaluate('b10.resources');assert not row['resources']['heartbeatActive'] and not row['resources']['frameActive'];out['samples'].append(row);pair.append(row);await ctx.close();print(name,round,fixture,mode,'measured',flush=True)
      assert pair[0]['scientificSnapshot']==pair[1]['scientificSnapshot']
    out['passed']=True
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
   finally:
    await browser.close();(E/f'performance-{name}.json').write_text(json.dumps(out,indent=2)+'\n')
   if not out['passed']:raise RuntimeError(out['error'])
try:asyncio.run(run())
finally:s.shutdown()
