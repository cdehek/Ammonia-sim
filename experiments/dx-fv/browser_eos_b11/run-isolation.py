"""Independent clocks/full state/history/Assist and exact five-exercise exports."""
import asyncio,functools,gzip,hashlib,http.server,json,threading,traceback
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';O=B.parent/'browser_eos_b10'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{s.server_port}/experiments/dx-fv/browser_eos_b11/preview/'
# Read-only test observer installed before original scripts. Not in delivered artifact.
observer="""(()=>{let storage;Object.defineProperty(window,'AmmoniaStorage',{configurable:true,get:()=>storage,set:api=>{const create=api.createStorage;storage={...api,createStorage(...args){const model=create(...args),make=model.create;model.create=(...args)=>{const state=make(...args);window.__plantState=state;return state;};return model;}};}});})();"""
async def open_a2(p):
 await p.locator('#b10-a2-link').click();await p.wait_for_function('!!window.b10')
async def tool(p,id):
 if id=='operator-assist':
  if await p.locator('#operator-assist').is_hidden():await p.locator('#operator-assist-toggle').click()
 else:await p.locator('.plant-nav a[href="#'+id+'"]').click()
async def manage(p):
 await tool(p,'storage-training')
 if not await p.locator('.training-library').evaluate('e=>e.open'):await p.locator('.training-library summary').click()
async def download(p,id):
 async with p.expect_download() as pending:await p.locator('#'+id).click()
 d=await pending.value;return Path(await d.path()).read_bytes()
async def capture(p):
 return await p.evaluate('''async()=>{const {exact}=await import('./support/values.mjs');const hash=async v=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(exact(v)))))].map(x=>x.toString(16).padStart(2,'0')).join('');const s=window.__plantState;return {originalClock:s?.time??null,originalStateHash:await hash(s??null),originalHistoryHash:await hash(s?.history??null),originalRows:s?.rows.length??0,originalSamples:s?.history.samples.length??0,originalEvents:s?.history.events.length??0,alarm:document.getElementById('storage-alarm-summary').textContent,A2Clock:window.b10?.client?.view.clockSeconds??null,A2Session:window.b10?.client?.sessionId??null,A2SnapshotHash:await hash(window.b10?.client?.view.snapshot??null),A2HistoryHash:await hash(window.b10?.client?.view.history??null)};}''')
async def exercise(p,id):
 await manage(p);await p.locator('#training-select').select_option(id);await p.locator('#training-load').click();await p.locator('#training-answer').select_option('0');await p.locator('#training-check').click()
 if id!='startup':await p.locator('#training-disturbance').click()
 for i in range(24):
  if not await p.locator('#training-advance').is_enabled():break
  await p.locator('#training-advance').click()
 if id=='hot':
  assert 'High discharge temperature' in await p.locator('#storage-alarm-summary').inner_text()
  await tool(p,'operator-assist');assert 'High discharge temperature' in await p.locator('#operator-assist').inner_text();await manage(p)
  await p.locator('#training-restore').click();await p.locator('#training-clear').click();await p.locator('#training-advance').click()
 assert 'Objectives completed' in await p.locator('#training-status').inner_text(),id
 await manage(p);return await download(p,'training-export')
async def main():
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   binary=B/'.runtime/webkit.sh' if name=='webkit' else next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))
   browser=await getattr(pw,name).launch(executable_path=str(binary),headless=True);out={'browser':name,'version':browser.version,'passed':False,'cases':[],'training':[]}
   try:
    ctx=await browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True);await ctx.add_init_script(observer);p=await ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));await p.goto(url)
    async def record(label,before,after,plant=False,a2=False):
     if plant:assert before['originalStateHash']==after['originalStateHash'] and before['originalHistoryHash']==after['originalHistoryHash'],label
     if a2:assert before['A2SnapshotHash']==after['A2SnapshotHash'] and before['A2HistoryHash']==after['A2HistoryHash'] and before['A2Session']==after['A2Session'],label
     out['cases'].append({'case':label,'before':before,'after':after,'plantExact':plant,'A2Exact':a2})
    # 1 original only, 2 A2 only on an independently opened workstation.
    await p.locator('#storage-example').click();first=await capture(p);assert first['originalClock']==0 and first['A2Session'] is None;out['cases'].append({'case':'1 original only','state':first})
    only=await ctx.new_page();await only.goto(url);a=await capture(only);await open_a2(only);await only.evaluate('b10.initialize("cold")');b=await capture(only);await record('2 A2 only',a,b,plant=True);assert b['originalClock'] is None and b['A2Clock']==0;await only.close()
    a=await capture(p);await open_a2(p);await p.evaluate('b10.initialize("cold")');b=await capture(p);await record('3 both initialized',a,b,plant=True);initialCold=await p.evaluate('b10.client.view.snapshot.sections')
    a=await capture(p);await p.locator('#storage-step').click();b=await capture(p);await record('4 original advance with idle A2',a,b,a2=True);assert b['originalClock']>a['originalClock']
    a=b;await p.evaluate('b10.action("advance")');b=await capture(p);await record('5 A2 advance with idle original',a,b,plant=True);assert b['A2Clock']==.0001
    a=b;await tool(p,'storage-form');b=await capture(p);await record('6 switch away',a,b,plant=True,a2=True);await open_a2(p);c=await capture(p);await record('7 return',b,c,plant=True,a2=True)
    a=c;await tool(p,'operator-assist');assist=await p.locator('#operator-assist').inner_text();await p.locator('#operator-assist-close').click();await tool(p,'operator-assist');assert await p.locator('#operator-assist').inner_text()==assist;await p.locator('#operator-assist-close').click();b=await capture(p);await record('8 Assist open/close',a,b,plant=True,a2=True);out['assistText']=assist
    # Preserve actual original export bytes over A2 view operations.
    await tool(p,'storage-form');csv=await download(p,'storage-export');await tool(p,'storage-trends');history=await download(p,'storage-history-export');await open_a2(p);await p.evaluate('b10.action("latest")');await tool(p,'storage-form');assert csv==await download(p,'storage-export');await tool(p,'storage-trends');assert history==await download(p,'storage-history-export');out['originalExportByteParity']={'storageSHA256':hashlib.sha256(csv).hexdigest(),'historySHA256':hashlib.sha256(history).hexdigest()}
    # 9 actual exercise before A2 initialization on a fresh original page.
    un=await ctx.new_page();await un.goto(url);raw=await exercise(un,'startup');expected=(O/f'evidence/baseline-training/{name}-startup-evidence.json').read_bytes();assert raw==expected;assert not await un.evaluate('!!window.b10');out['cases'].append({'case':'9 startup while A2 uninitialized','byteExact':True});await un.close()
    # 10 all five complete actual exports while an A2 session exists.
    outdir=E/f'training-{name}';outdir.mkdir(exist_ok=True)
    for id in ['startup','load','restriction','tuning','hot']:
     a=await capture(p);raw=await exercise(p,id);expected=(O/f'evidence/baseline-training/{name}-{id}-evidence.json').read_bytes();(outdir/(id+'.json')).write_bytes(raw);assert raw==expected,id+' complete export bytes';b=await capture(p);await record('10 exercise '+id+' with existing A2',a,b,a2=True)
     report=json.loads(raw);out['training'].append({'exercise':id,'byteExact':True,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'samples':len(report['history']['samples']),'events':len(report['history']['events']),'completedAt':report['attempt']['endedAt'],'allObjectives':all(g['met'] for g in report['attempt']['goals'])})
    # 11 genuine A2 numerical refusal: local stale display, no original alarm or mutation.
    await open_a2(p);await p.evaluate('b10.action("dispose")');a=await capture(p)
    fault=await p.evaluate('''async()=>{const {Client}=await import('./client.mjs');window.__fault=new Client(v=>b10.update(v),{test:true});await __fault.request('initialize',{fixture:'numerical'});const r=await __fault.request('advance');return {response:r,display:b10.root.querySelector('#status').textContent,displayClock:__fault.view.snapshot.clockSeconds,history:__fault.view.history.length};}''');assert not fault['response']['success'] and fault['response']['snapshot'] is None and 'STALE' in fault['display'];b=await capture(p);await record('11 numerical refusal leaves original exact',a,b,plant=True);out['fault']=fault
    await p.evaluate('__fault.dispose()');a=await capture(p);await p.locator('#storage-step').click();b=await capture(p);assert b['originalClock']>a['originalClock'];out['cases'].append({'case':'12 original operates after A2 disposal','before':a,'after':b})
    await p.evaluate('b10.initialize("cold")');b=await capture(p);assert b['A2Clock']==0 and b['A2Session']!=first['A2Session'];assert await p.evaluate('b10.client.view.history.length')==1;assert await p.evaluate('b10.client.view.snapshot.sections')==initialCold;out['cases'].append({'case':'13 clean independent restart','state':b})
    # 14 trusted original controls during actual worker computation/playback.
    await p.locator('#storage-example').click();await p.evaluate('b10.initialize("warm")');await p.evaluate('''()=>{window.__ack=[];for(const id of ['storage-start','storage-pause'])document.getElementById(id).addEventListener('click',e=>__ack.push({id,trusted:e.isTrusted,ackMS:performance.now()-e.timeStamp,pending:b10.client.pending.size,originalClock:__plantState.time}));window.__pending=b10.action('advance');}''');await p.locator('#storage-start').click();await p.evaluate('__pending');await p.wait_for_timeout(350);await p.locator('#storage-pause').click();b=await capture(p);assert b['originalClock']>0 and b['A2Clock']==.0001;out['cases'].append({'case':'14 original controls and playback during worker computation','state':b,'acks':await p.evaluate('__ack')});await p.screenshot(path=str(E/f'isolation-{name}.png'),full_page=True)
    # Actual worker startup error is caught without pausing ongoing original playback.
    fail=await ctx.new_page();await fail.route('**/preview/worker.mjs*',lambda r:r.abort());await fail.goto(url);await fail.locator('#storage-example').click();await fail.locator('#storage-start').click();await open_a2(fail);await fail.locator('#b10-a2-shadow #cold').click();await fail.wait_for_function('b10.client?.view.status==="lost"');await fail.wait_for_timeout(350);assert not await fail.locator('#storage-pause').is_disabled();out['workerInitError']={'status':await fail.evaluate('b10.client.view.status'),'originalClock':await fail.locator('#storage-clock').inner_text(),'originalStillRunning':True};await fail.locator('#storage-pause').click();await fail.close()
    assert not errors;out['pageErrors']=errors;out['passed']=True
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
   finally:
    await browser.close();(E/f'isolation-{name}.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),mtime=0))
   print(name,'PASS' if out['passed'] else out['error'],flush=True)
   if not out['passed']:raise RuntimeError(out['error'])
try:asyncio.run(main())
finally:s.shutdown()
