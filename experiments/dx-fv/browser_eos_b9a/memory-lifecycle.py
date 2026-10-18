"""Bounded cache, explicit diagnostic retrieval, disposal and navigation. Outer 240s."""
import argparse,functools,http.server,json,threading,time,psutil
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent; R=B.parents[2]
p=argparse.ArgumentParser();p.add_argument('--tag',default='');args=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  driver=psutil.Process(pw._impl_obj._connection._transport._proc.pid)
  for name in ['chromium','webkit']:
   target=B/'evidence'/f'memory-{name}{args.tag}.json';assert not target.exists()
   opts=dict(headless=True,timeout=30000)
   if name=='webkit':opts['executable_path']='/workspace/b9-runtime/webkit.sh'
   browser=getattr(pw,name).launch(**opts);rows=[];cycles=[]
   for mode in ['A','B','C']:
    context=browser.new_context();page=context.new_page();page.set_default_timeout(30000);url=f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9a/index.html';page.goto(url)
    def sample(label):
     processes=[]
     for child in driver.children(recursive=True):
      try:processes.append(dict(pid=child.pid,rssBytes=child.memory_info().rss))
      except psutil.Error:pass
     return dict(mode=mode,label=label,summedBrowserChildRSSBytes=sum(p['rssBytes'] for p in processes),processCount=len(processes),heap=page.evaluate('performance.memory?({used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}):null'))
    rows.append(sample('page-ready'))
    for cycle in range(3):
     init=page.evaluate("""async mode=>{const {Client}=await import('./client.mjs');window.memoryClient=new Client(mode);const r=await memoryClient.request('initialize',{fixture:'cold'});if(!r.success)throw Error(r.error.message);return {clock:r.clock,version:r.acceptedVersion};}""",mode)
     rows.append(sample(f'{cycle}-initialized'))
     result=page.evaluate("""async ({mode,stress})=>{let approximateCacheJSONBytes=0;const samples=[];for(const duration of [.0001,.0004,.0005]){const r=await memoryClient.request('advance',{duration});if(!r.success)throw Error(r.error.message);approximateCacheJSONBytes+=new TextEncoder().encode(JSON.stringify(r.result)).length;}
     if(stress){for(let i=0;i<8;i++){const r=await memoryClient.request('diagnostics');if(!r.success)throw Error('diagnostics');const bytes=new TextEncoder().encode(JSON.stringify(r.result)).length;approximateCacheJSONBytes+=bytes;samples.push({type:'fullDiagnostics',serviceMS:r.timing.serviceMS,roundtripMS:r.clientTiming.roundtripMS,bytes});}
     while(memoryClient.sequence<256){const r=await memoryClient.request(mode==='A'?'snapshot':'snapshotCompact');if(!r.success)throw Error('snapshot cache');approximateCacheJSONBytes+=new TextEncoder().encode(JSON.stringify(r.result)).length;}
     const r=await memoryClient.request('advance',{duration:.0001});if(r.success||r.clock!==.001)throw Error('cache exhaustion changed physics');return {cacheEntries:256,exhausted:r.error,clock:r.clock,approximateCacheJSONBytes,samples};}
     return {clock:.001,approximateCacheJSONBytes,samples};}""",dict(mode=mode,stress=cycle==0))
     rows.append(sample(f'{cycle}-active-cache'))
     disposed=page.evaluate('async()=>await memoryClient.dispose()');assert disposed['success'];page.evaluate('window.memoryClient=null');page.wait_for_timeout(100);rows.append(sample(f'{cycle}-disposed'));cycles.append(dict(mode=mode,cycle=cycle,init=init,result=result,disposed=disposed['result']))
    page.locator('#initialize').click();page.wait_for_function("document.querySelector('#status').textContent.startsWith('ready')");page.evaluate("document.querySelector('#advance').click()");page.goto('about:blank');page.goto(url);assert page.locator('#status').inner_text()=='Not initialized';rows.append(sample('navigation-new-page'));context.close()
   out=dict(passed=True,engine=name,browserVersion=browser.version,observations=rows,cycles=cycles,navigationWithPendingWork=True,inFlightState='unknown; destroyed disposable session; not solver rollback',exactWireOrHeapBytes=False,workerHeapIsolated=False,leakFreedomProved=False,limitation='RSS sums shared pages; GC/process high-water not worker allocations; estimated cache bytes omit overhead, requests and initial result')
   target.write_text(json.dumps(out,indent=2)+'\n');browser.close();print(name,'memory complete',flush=True)
finally:server.shutdown()
