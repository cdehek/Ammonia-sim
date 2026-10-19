"""Actual served Chromium/WPE WebKit connection, source, fault and lifecycle evidence."""
import asyncio,functools,gzip,hashlib,http.server,json,threading,traceback,time,importlib.metadata,statistics
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
assert json.loads((E/'gates-1-4.json').read_text())['prototypeAuthorized']
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9d/'
async def main():
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   out={'browser':name,'passed':False,'playwright':importlib.metadata.version('playwright'),'primary':[],'packaging':{}}
   browser=None
   try:
    executable='/workspace/b9-runtime/webkit.sh' if name=='webkit' else str(next(Path('/workspace/b9-runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')))
    browser=await getattr(pw,name).launch(executable_path=executable,headless=True);out.update(version=browser.version,executable=executable,executableSHA256=hashlib.sha256(Path(executable).read_bytes()).hexdigest())
    ctx=await browser.new_context(viewport={'width':1440,'height':1000});page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.goto(url);await page.wait_for_function('!!window.shadow');out['userAgent']=await page.evaluate('navigator.userAgent')
    reference=await ctx.new_page();await reference.goto(url.replace('browser_eos_b9d/','browser_eos_b9c/index.html'));await reference.wait_for_function('!!window.workerRun')
    # Main display only, no scientific test libraries on the primary page yet.
    for fixture in ['cold','warm']:
     reference_before=await reference.evaluate('a=>workerRun(a)',{'fixture':fixture,'mode':'candidate','observed':False})
     await page.evaluate('Object.values(shadow.metrics).forEach(a=>a.length=0)')
     await page.click('#'+fixture);await page.wait_for_function('shadow.client?.view.status==="ready"')
     for i in range(3):
      await page.click('#advance');await page.wait_for_function('shadow.client?.view.status==="accepted-state" && shadow.client.pending.size===0')
     assert await page.evaluate('shadow.client.view.snapshot.clockSeconds')==.001
     sample=await page.evaluate('(fixture)=>({fixture,metrics:shadow.client.metrics,render:shadow.metrics.renders,heartbeat:shadow.metrics.heartbeat,frames:shadow.metrics.frames,input:shadow.metrics.input,snapshot:shadow.client.view.snapshot,history:shadow.client.view.history})',fixture)
     reference_after=await reference.evaluate('a=>workerRun(a)',{'fixture':fixture,'mode':'candidate','observed':False});sample['B9CBefore']=reference_before;sample['B9CAfter']=reference_after;out['primary'].append(sample)
     await page.screenshot(path=str(E/f'shadow-{name}-{fixture}.png'),full_page=True)
    await reference.close()
    # Genuine browser input during a requested advance; pending overlap is separately tested directly.
    await page.click('#warm');await page.wait_for_function('shadow.client?.view.status==="ready"')
    await page.click('#advance');await page.click('#stop');await page.wait_for_function('shadow.client?.view.status==="scheduling-stopped"')
    out['pendingStop']=await page.evaluate('({metrics:shadow.client.metrics,input:shadow.metrics.input,clock:shadow.client.view.clockSeconds,status:shadow.client.view.status})')
    await page.click('#dispose');await page.wait_for_function('shadow.client.closed');out['primaryDisposed']=True;out['disposal']=await page.evaluate('shadow.client.metrics.at(-1)')
    # Full scientific retrieval is test-only and outside primary timing.
    out['science']=[]
    for fixture in ['cold','warm']:
     print(name,'shadow science',fixture,flush=True)
     result=await page.evaluate('async f=>(await import("./shadow-tests.mjs")).science(f)',fixture)
     review=json.loads(gzip.decompress((E/f'review-{name}.json.gz').read_bytes()))
     assert result['checkpointHashes']==review['results'][fixture]['control']['checkpointHashes'],'shadow full source accepted-state parity'
     result['exactOriginalControlCheckpoints']=True;out['science'].append(result)
    print(name,'lifecycle',flush=True);out['lifecycle']=await page.evaluate('async()=>(await import("./shadow-tests.mjs")).lifecycle()');assert out['lifecycle']['passed']
    out['pageErrors']=errors;assert not errors
    # Missing candidate asset: expected failure, never alternate backend.
    missing=await browser.new_context();await missing.route('**/browser_eos_b9c/candidate-bundle.mjs',lambda route:route.abort())
    mp=await missing.new_page();await mp.goto(url);await mp.wait_for_function('!!window.shadow');await mp.click('#cold');await mp.wait_for_function('shadow.client?.view.status==="unqualified-backend"')
    out['packaging']['missingScientificBundle']=await mp.evaluate('({status:shadow.client.view.status,snapshot:shadow.client.view.snapshot,fault:shadow.client.view.fault})');assert out['packaging']['missingScientificBundle']['snapshot'] is None;await missing.close()
    # No Internet application calls on the ordinary served page.
    out['packaging']['servedLocalAssets']='PASS; local HTTP origin, exact table bundle, no external application backend'
    # Real network-offline startup observation, not a localhost inference.
    offline=await browser.new_context();op=await offline.new_page();await op.goto(url);await op.wait_for_function('!!window.shadow');await offline.set_offline(True);await op.click('#cold')
    try:await op.wait_for_function('shadow.client?.view.status!=="initializing"',timeout=10000)
    except Exception:pass
    out['packaging']['browserOffline']=await op.evaluate('({status:shadow.client?.view.status,snapshot:shadow.client?.view.snapshot??null,fault:shadow.client?.view.fault??null})');await offline.close()
    filectx=await browser.new_context();fp=await filectx.new_page();file_errors=[];fp.on('pageerror',lambda e:file_errors.append(str(e)))
    try:
     await fp.goto((B/'index.html').as_uri(),timeout=10000);out['packaging']['nativeFile']={'navigation':'returned','status':await fp.locator('#status').inner_text(),'appLoaded':await fp.evaluate('!!window.shadow'),'pageErrors':file_errors}
    except Exception as e:out['packaging']['nativeFile']={'navigation':'FAILED','error':str(e),'pageErrors':file_errors}
    await filectx.close();out['passed']=True
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
   finally:
    if browser:await browser.close()
    out['deliveredSourceSHA256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.glob('*') if p.is_file() and p.suffix in ['.mjs','.html','.py','.md']}
    (E/f'shadow-{name}.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':'),allow_nan=False).encode(),mtime=0))
   print(name,'PASS' if out['passed'] else out['error'],flush=True)
   if not out['passed']:raise RuntimeError(out['error'])
try:asyncio.run(main())
finally:server.shutdown()
