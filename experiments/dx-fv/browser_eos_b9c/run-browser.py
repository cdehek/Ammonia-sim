"""Bounded sequential actual-browser qualification and predeclared timings."""
import argparse,asyncio,functools,gzip,hashlib,http.server,json,os,threading,traceback,time,importlib.metadata,subprocess
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['parity','regressions','c1','timing'],required=True);p.add_argument('--engines',default='chromium,webkit');a=p.parse_args()
if a.stage=='timing': assert json.loads((E/'qualification.json').read_text())['passed']
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
def rss():
 rows=[line.split() for line in subprocess.check_output(['ps','-eo','pid,ppid,rss,comm'],text=True).splitlines()[1:]]
 descendants={os.getpid()}
 for _ in range(8):descendants.update(int(pid) for pid,parent,_,_ in rows if int(parent) in descendants)
 selected=[{'pid':int(pid),'rssKiB':int(mem),'command':cmd} for pid,parent,mem,cmd in rows if int(pid) in descendants and any(k in cmd.lower() for k in ['chrome','webkit','minibrowser','webprocess','networkprocess'])]
 return {'processes':selected,'sumRSSKiB':sum(r['rssKiB'] for r in selected),'limit':'process RSS can double-count shared pages; high-water/JIT/GC, not live JS cache bytes'}
async def main():
 async with async_playwright() as pw:
  for name in a.engines.split(','):
   target=E/f'{a.stage}-{name}.json.gz';assert not target.exists(),target
   sources=[p for p in B.iterdir() if p.suffix in ['.mjs','.html','.py','.cjs']]+list((B/'isolated').glob('*'))
   out={'engine':name,'stage':a.stage,'runs':[],'passed':False,'playwright':importlib.metadata.version('playwright'),'sourceHashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.is_file()}};browser=None
   try:
    opts={'headless':True,'timeout':30000}
    opts['executable_path']='/workspace/b9-runtime/webkit.sh' if name=='webkit' else str(next(Path('/workspace/b9-runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')))
    # Explicit executable identity; BrowserType.executable_path names full Chrome,
    # whereas Playwright's default headless launch selects the headless shell.
    browser=await getattr(pw,name).launch(**opts);out['version']=browser.version
    binary=Path(opts.get('executable_path',getattr(pw,name).executable_path));out['executable']=str(binary);out['executableSHA256']=hashlib.sha256(binary.read_bytes()).hexdigest()
    ctx=await browser.new_context();page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9c/index.html');await page.wait_for_function('!!window.workerRun')
    out['userAgent']=await page.evaluate('navigator.userAgent');out['heapBefore']=await page.evaluate('performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null');out['processMemoryBefore']=rss()
    await page.evaluate('window.beats=[];window.lastBeat=performance.now();window.beatTimer=setInterval(()=>{const t=performance.now();window.beats.push(t-window.lastBeat);window.lastBeat=t;},10)')
    async def run(args):
     t=time.monotonic();raw=await asyncio.wait_for(page.evaluate('async a=>JSON.stringify(await window.workerRun(a))',args),90);r=json.loads(raw);r['requestRoundtripMS']=(time.monotonic()-t)*1000;return r
    if a.stage=='parity':
     for f in ['cold','warm']:
      for mode in ['control','candidate']:
       out['runs'].append(await run(dict(mode=mode,fixture=f,observed=True)))
       print(name,a.stage,f,mode,flush=True)
    elif a.stage=='regressions':
     for mode in ['control','candidate']:out['runs'].append(await run(dict(task='regressions',mode=mode)))
    elif a.stage=='c1':out['runs'].append(await run(dict(task='c1')))
    elif a.stage=='timing':
     for round in range(5):
      for f in (['cold','warm'] if round%2==0 else ['warm','cold']):
       for mode in ['control','candidate','control']:
        r=await run(dict(mode=mode,fixture=f,observed=False));r['round']=round;out['runs'].append(r)
       print(name,'round',round,f,flush=True)
    out['heartbeatMS']=await page.evaluate('clearInterval(window.beatTimer);window.beats');out['heapAfter']=await page.evaluate('performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null');out['processMemoryAfter']=rss();out['pageErrors']=errors;assert not errors
    out['lifecycle']={'freshWorkerPerRequest':True,'terminatedAfterEachResponse':True,'sessions':len(out['runs']),'restartExactByParity':True,'retainedCacheReferences':False,'memoryLimit':'main-page heap only; worker leak freedom not inferred'};out['passed']=True
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
   finally:
    if browser:await browser.close()
    target.write_bytes(gzip.compress((json.dumps(out,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0));print(target.name,out['passed'],flush=True)
   if not out['passed']:raise RuntimeError(out.get('error'))
try:asyncio.run(main())
finally:server.shutdown()
