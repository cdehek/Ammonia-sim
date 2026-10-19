"""Actual derived workstation, source/render, failure and viewport receipts."""
import asyncio,functools,gzip,hashlib,http.server,json,threading,traceback
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{s.server_port}/experiments/dx-fv/browser_eos_b10/'
async def main():
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   binary=B/'.runtime/webkit.sh' if name=='webkit' else next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))
   browser=await getattr(pw,name).launch(executable_path=str(binary),headless=True);out={'browser':name,'version':browser.version,'passed':False,'primary':[]}
   try:
    ctx=await browser.new_context(viewport={'width':1440,'height':1000},has_touch=True);p=await ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    await p.goto(url);assert await p.evaluate('AmmoniaStartup.ready && !window.b10');out['inactiveLazy']=True
    await p.locator('#b10-a2-link').click();await p.wait_for_function('!!window.b10');assert await p.locator('#b10-a2-shadow').evaluate('e=>e.closest("#console-content")!==null')
    assert await p.locator('#storage-clock').inner_text()=='0.0 s simulated';out['actualConsoleMount']=True
    for fixture in ['cold','warm']:
     await p.locator('#b10-a2-shadow #'+fixture).click();await p.wait_for_function('b10.client?.view.status==="ready"')
     for i in range(3):
      await p.locator('#b10-a2-shadow #advance').click();await p.wait_for_function('b10.client.view.status==="accepted-state"&&b10.client.pending.size===0')
     assert await p.evaluate('b10.client.view.snapshot.clockSeconds')==.001
     out['primary'].append(await p.evaluate('fixture=>({fixture,metrics:b10.client.metrics,ui:b10.metrics,snapshot:b10.client.view.snapshot,history:b10.client.view.history})',fixture))
     await p.screenshot(path=str(E/f'integration-{name}-{fixture}.png'),full_page=True)
    out['science']=[];saved=json.loads((B.parent/'browser_eos_b9d/evidence/shadow-summary.json').read_text())['browsers'][name]['science'];review=json.loads((B.parent/'browser_eos_b9d/evidence/review-summary.json').read_text())[name]['fixtures']
    for fixture in ['cold','warm']:
     print(name,'source/render',fixture,flush=True);r=await p.evaluate('async f=>(await import("./bridge-tests.mjs")).science(f)',fixture)
     reference=await p.evaluate('''f=>new Promise((resolve,reject)=>{const w=new Worker('./reference-worker.mjs',{type:'module'});w.onmessage=e=>{w.terminate();e.data.ok?resolve(e.data.result):reject(Error(e.data.error));};w.onerror=e=>{w.terminate();reject(Error(e.message));};w.postMessage(f);})''',fixture)
     assert reference['scienceHash']==review[fixture]['hash'];assert r['checkpointHashes']==reference['checkpointHashes']==next(v for v in saved if v['fixture']==fixture)['checkpointHashes'];assert r['attemptsHash']==reference['attemptsHash'];r['exactSavedControl']=True;r['allOriginalAttemptDiagnosticsExact']=True;r['reference']=reference;out['science'].append(r)
    print(name,'lifecycle',flush=True);out['lifecycle']=await p.evaluate('async()=>(await import("./bridge-tests.mjs")).lifecycle()');assert out['lifecycle']['passed']
    # Check source and all view conversions against real accepted data.
    await p.evaluate('b10.initialize("warm")');await p.evaluate('b10.action("advance")');await p.locator('#b10-a2-shadow #units').select_option('US')
    out['conversions']=await p.evaluate('''async()=>{const {convert,format,get}=await import('./view.mjs');const s=b10.client.view.snapshot;const cells=[...b10.root.querySelectorAll('[data-reading]')];for(const c of cells){if(c.textContent!==format(convert(get(s,c.dataset.reading),c.dataset.conversion,true)))throw Error('conversion '+c.dataset.reading);}return {cells:cells.length,pressureFormula:(s.sections[0].pressureBarAbsolute-1.01325)*14.503773773,temperatureF:s.sections[0].temperatureC*1.8+32,deltaF:s.sections[0].superheatK*1.8,nullableQuality:s.sections.map(s=>s.quality)};}''')
    await p.locator('#b10-a2-shadow #units').select_option('SI');out['viewports']=[]
    for label,w,h in [('desktop',1440,1000),('landscape',1024,768),('portrait',768,1024)]:
     await p.set_viewport_size({'width':w,'height':h});await p.locator('#b10-a2-link').click()
     r=await p.evaluate('''()=>({overflow:document.documentElement.scrollWidth>innerWidth,touch:[...b10.root.querySelectorAll('button,select')].every(e=>{const r=e.getBoundingClientRect();return r.height>=44&&r.width>=44;}),tableScroll:(()=>{const e=b10.root.querySelector('.scroll');return {client:e.clientWidth,scroll:e.scrollWidth};})(),originalControl:(()=>{const r=document.getElementById('storage-start').getBoundingClientRect(),c=document.getElementById('operator-console').getBoundingClientRect();return r.bottom<c.top;})(),duplicateIDs:(()=>{const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return ids.length-new Set(ids).size;})()})''')
     assert not r['overflow'] and r['touch'] and r['originalControl'] and r['duplicateIDs']==0
     await p.locator('#console-expand').click();await p.screenshot(path=str(E/f'integration-{name}-{label}-expanded.png'));await p.locator('#b10-a2-shadow .scroll').first.scroll_into_view_if_needed();await p.screenshot(path=str(E/f'integration-{name}-{label}-instruments.png'));await p.locator('#b10-a2-shadow #latest').focus();await p.keyboard.press('Escape');assert await p.locator('#operator-console').get_attribute('data-size')=='partial'
     await p.screenshot(path=str(E/f'integration-{name}-{label}.png'));await p.keyboard.press('Escape');assert await p.locator('#operator-console').get_attribute('data-size')=='collapsed'
     assert await p.locator('#b10-a2-link').evaluate('e=>e===document.activeElement');r.update(label=label,width=w,height=h,escape=True,focusReturn=True);out['viewports'].append(r)
    await p.locator('#b10-a2-link').click();await p.evaluate('b10.action("dispose")');out['disposedResources']=await p.evaluate('b10.resources');assert not out['disposedResources']['heartbeatActive'] and not out['disposedResources']['frameActive']
    out['boundedRestarts']=await p.evaluate('''async()=>{const rows=[];for(let i=0;i<5;i++){await b10.initialize('cold');const id=b10.client.sessionId;const pending=b10.action('advance');const dispose=b10.action('dispose');await Promise.all([pending,dispose]);if(!b10.client.closed||b10.client.pending.size)throw Error('dangling pending disposal');rows.push({id,clock:b10.client.view.clockSeconds,resources:b10.resources});}return rows;}''');assert len(set(r['id'] for r in out['boundedRestarts']))==5
    await p.evaluate('''async()=>{await b10.initialize('warm');window.__terminatingAdvance=b10.action('advance').catch(()=>{});window.addEventListener('pagehide',()=>sessionStorage.setItem('B10-test-pagehide',JSON.stringify(b10.resources)),{once:true});}''');await p.goto(url+'artifacts/pinned-workstation.html');out['pageTermination']=json.loads(await p.evaluate('sessionStorage.getItem("B10-test-pagehide")'));assert out['pageTermination']['ended'] and out['pageTermination']['pending']==0 and not out['pageTermination']['heartbeatActive'] and not out['pageTermination']['frameActive']
    # Missing scientific module and real browser offline: expected explicit failures.
    missing=await browser.new_context();await missing.route('**/browser_eos_b9c/candidate-bundle.mjs',lambda r:r.abort());mp=await missing.new_page();await mp.goto(url);await mp.locator('#b10-a2-link').click();await mp.wait_for_function('!!window.b10');await mp.locator('#b10-a2-shadow #cold').click();await mp.wait_for_function('b10.client?.view.status==="unqualified-backend"');out['missingModule']=await mp.evaluate('({status:b10.client.view.status,snapshot:b10.client.view.snapshot,error:b10.client.view.fault})');assert out['missingModule']['snapshot'] is None;await missing.close()
    off=await browser.new_context();op=await off.new_page();await op.goto(url);await op.locator('#b10-a2-link').click();await op.wait_for_function('!!window.b10');await off.set_offline(True);await op.locator('#b10-a2-shadow #cold').click()
    try:await op.wait_for_function('b10.client?.view.status!=="initializing"',timeout=10000)
    except Exception:pass
    out['offline']=await op.evaluate('({status:b10.client?.view.status,snapshot:b10.client?.view.snapshot??null})');await off.close()
    fp=await browser.new_page()
    try:
     await fp.goto((B/'index.html').as_uri(),timeout=10000);await fp.locator('#b10-a2-link').click();await fp.wait_for_timeout(300);out['nativeFile']={'originalReady':await fp.evaluate('AmmoniaStartup.ready'),'A2Loaded':await fp.evaluate('!!window.b10'),'panelText':await fp.locator('#b10-a2-shadow').inner_text()}
    except Exception as e:out['nativeFile']={'error':str(e)}
    out['errors']=errors;assert not errors;out['passed']=True
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
   finally:
    await browser.close();(E/f'integration-{name}.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),mtime=0))
   print(name,'PASS' if out['passed'] else out['error'],flush=True)
   if not out['passed']:raise RuntimeError(out['error'])
try:asyncio.run(main())
finally:s.shutdown()
