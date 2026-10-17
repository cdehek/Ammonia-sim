"""Bounded coarse process/heap observations, after timing work. Timeout 120s."""
import argparse,functools,http.server,json,os,threading,time
from pathlib import Path
import psutil
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2]
p=argparse.ArgumentParser();p.add_argument('--tag',default='');a=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  driver=psutil.Process(pw._impl_obj._connection._transport._proc.pid)
  for name in ['chromium','webkit']:
   opts=dict(headless=True,timeout=30000)
   if name=='webkit':opts['executable_path']='/workspace/b9-runtime/webkit.sh'
   browser=getattr(pw,name).launch(**opts);page=browser.new_page();page.set_default_timeout(30000)
   url=f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9/index.html';page.goto(url)
   def sample(label):
    processes=[]
    for child in driver.children(recursive=True):
     try:processes.append(dict(pid=child.pid,rssBytes=child.memory_info().rss))
     except psutil.Error:pass
    return dict(label=label,summedBrowserChildRSSBytes=sum(v['rssBytes'] for v in processes),processCount=len(processes),pageHeap=page.evaluate('performance.memory?({used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize,limit:performance.memory.jsHeapSizeLimit}):null'))
   rows=[sample('page-ready')];cycles=[]
   for mode in ['main','worker']:
    for cycle in range(3):
     init=page.evaluate("""async mode=>{const {Client}=await import('./client.mjs');window.memoryClient=new Client(mode);const r=await memoryClient.request('initialize',{fixture:'cold'});if(!r.success)throw Error(r.error.message);return {clock:r.clock,version:r.acceptedVersion};}""",mode)
     rows.append(sample(f'{mode}-{cycle}-initialized'))
     result=page.evaluate("""async()=>{const a=await memoryClient.request('advance',{duration:.0001});const d=await memoryClient.request('diagnostics');const disposed=await memoryClient.dispose();return {success:a.success,clock:a.clock,acceptedVersion:a.acceptedVersion,diagnosticHeap:d.result.heap,disposed:disposed.result};}""")
     assert result['success'] and result['clock']==.0001
     page.evaluate('window.memoryClient=null');page.wait_for_timeout(100)
     rows.append(sample(f'{mode}-{cycle}-disposed'));cycles.append(dict(mode=mode,cycle=cycle,initial=init,result=result))
   # Exercise the actual panel's pagehide/unmount path with a pending worker solve.
   page.locator('#initialize').click();page.wait_for_function("document.querySelector('#status').textContent.startsWith('ready')")
   page.evaluate("document.querySelector('#advance').click()")
   page.goto('about:blank');page.goto(url);assert page.locator('#status').inner_text().startswith('Not initialized')
   rows.append(sample('navigation-new-page-no-session'))
   out=dict(passed=True,engine=name,browserVersion=browser.version,observations=rows,cycles=cycles,navigationWithPendingWork=True,lastKnownPanelClockBeforeNavigation=0,inFlightAcceptedState='unknown; disposable session terminated',uniquePhysicalMemoryClaim=False,workerThreadHeapSeparatelyAvailable=False,forcedGC=False,leakFreedomProved=False,scope='Sum of current browser child RSS includes shared pages more than once; OS process grouping, allocator and GC high-water effects prevent unique worker attribution. Page heap is coarse Chromium-only API. Desktop WebKit is not iPad.')
   (B/'evidence'/f'memory-{name}{a.tag}.json').write_text(json.dumps(out,indent=2)+'\n');browser.close();print(name,'memory/lifecycle observations complete',flush=True)
finally:server.shutdown()
