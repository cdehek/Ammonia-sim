"""Real browsers against a copy OUTSIDE repository; root/nested, origins and failures."""
import asyncio,functools,http.server,ipaddress,json,os,shutil,socket,tempfile,threading,time,traceback
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;E=B/'evidence'
async def wait(p,expression,timeout=30):
 deadline=time.monotonic()+timeout
 while not await p.evaluate(expression):
  if time.monotonic()>deadline:raise TimeoutError(expression)
  await asyncio.sleep(.05)
async def run():
 with tempfile.TemporaryDirectory(prefix='b11-independent-') as td:
  root=Path(td);shutil.copytree(B/'preview',root/'root');shutil.copytree(B/'preview',root/'nested/review/b11')
  requests=[]
  class Handler(http.server.SimpleHTTPRequestHandler):
   extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript'}
   def end_headers(self):
    # This allows original inline scripts/styles, same-origin imports/fetch/worker, data images.
    self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; worker-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'")
    super().end_headers()
   def log_message(self,fmt,*args):requests.append({'path':self.path,'status':args[1] if len(args)>1 else None})
  servers=[]
  for folder in ['root','nested']:
   s=http.server.ThreadingHTTPServer(('0.0.0.0',0),functools.partial(Handler,directory=str(root/folder)));threading.Thread(target=s.serve_forever,daemon=True).start();servers.append(s)
  try:
   async with async_playwright() as pw:
    for name in ['chromium','webkit']:
     binary=B/'.runtime/webkit.sh' if name=='webkit' else next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))
     browser=await getattr(pw,name).launch(executable_path=str(binary),headless=True);out={'browser':name,'version':browser.version,'independentCopyOutsideCheckout':True,'cases':[],'passed':False}
     try:
      for label,port,prefix in [('root',servers[0].server_port,'/'),('nested',servers[1].server_port,'/review/b11/')]:
       ctx=await browser.new_context(viewport={'width':1024,'height':768},has_touch=True);p=await ctx.new_page();urls=[];errors=[]
       p.on('request',lambda r:urls.append(r.url));p.on('pageerror',lambda e:errors.append(str(e)))
       url=f'http://127.0.0.1:{port}{prefix}';await p.goto(url);assert await p.evaluate('AmmoniaStartup.ready&&!window.b10')
       await p.locator('#b10-a2-link').click();await wait(p,'!!window.b10')
       states=[]
       for fixture in ['cold','warm']:
        r=await p.evaluate('f=>b10.initialize(f)',fixture);assert r['success'];times=[r['clockSeconds']]
        for i in range(3):
         r=await p.evaluate('b10.action("advance")');assert r['success'];times.append(r['clockSeconds'])
        assert times==[0,.0001,.0005,.001]
        d=await p.evaluate('b10.action("diagnostics")');assert d['success']
        states.append({'fixture':fixture,'times':times,'diagnostics':d['result'],'snapshot':await p.evaluate('b10.client.view.snapshot')})
        await p.evaluate('b10.action("dispose")')
       await p.evaluate('b10.initialize("cold")');assert await p.evaluate('b10.client.view.clockSeconds')==0;await p.evaluate('b10.action("dispose")')
       assert all(u.startswith(url) for u in urls),urls
       assert not any('/browser_eos_b' in u or '/workspace' in u for u in urls)
       assert not errors,errors
       await p.screenshot(path=str(E/f'portable-{name}-{label}-1024x768.png'))
       out['cases'].append({'case':label,'passed':True,'requests':urls,'errors':errors,'states':states,'restart':True,'CSP':'same-origin + original inline scripts/styles; no unsafe-eval'})
       await ctx.close()
      url=f'http://127.0.0.1:{servers[0].server_port}/'
      # Existing fully loaded worker is a different mode from offline startup.
      ctx=await browser.new_context();p=await ctx.new_page();await p.goto(url);await p.locator('#b10-a2-link').click();await wait(p,'!!window.b10');await p.evaluate('b10.initialize("cold")');await ctx.set_offline(True)
      existing=[]
      for i in range(3):
       r=await p.evaluate('b10.action("advance")');assert r['success'];existing.append(r['clockSeconds'])
      assert existing==[.0001,.0005,.001];await p.evaluate('b10.action("dispose")')
      restart=await p.evaluate('async()=>{try{await b10.initialize("cold");}catch(e){}return {status:b10.view.status,snapshot:b10.view.snapshot,error:b10.view.fault};}')
      assert restart['snapshot'] is None and restart['status'] in ['lost','unqualified-backend']
      await p.locator('#storage-example').click();await p.locator('#storage-step').click();out['cases'].append({'case':'offline-existing-session','existingWorkerThreeAdvances':existing,'offlineFreshRestart':restart,'originalOperationContinues':await p.locator('#storage-clock').inner_text(),'qualification':'Existing loaded localhost worker only; not offline startup/cache/PWA or HTTPS-disconnected proof'});await ctx.close()
      for mode in ['missing','corrupt','offline-before-worker','offline-before-panel']:
       ctx=await browser.new_context();p=await ctx.new_page();await p.goto(url)
       if mode=='offline-before-panel':await ctx.set_offline(True)
       await p.locator('#b10-a2-link').click()
       if mode=='offline-before-panel':
        await p.wait_for_timeout(500);result=await p.evaluate('({loaded:!!window.b10,text:document.getElementById("b10-a2-shadow").textContent,originalReady:AmmoniaStartup.ready})');assert not result['loaded'];out['cases'].append({'case':mode,**result});await ctx.close();continue
       await wait(p,'!!window.b10')
       if mode=='missing':await ctx.route('**/science/candidate-bundle.mjs',lambda r:r.abort())
       if mode=='corrupt':await ctx.route('**/science/candidate-bundle.mjs',lambda r:r.fulfill(status=200,content_type='text/javascript',body='export const corrupt=true;'))
       if mode.startswith('offline'):await ctx.set_offline(True)
       await p.locator('#b10-a2-shadow #cold').click();await wait(p,'b10.view.status!=="initializing"')
       result=await p.evaluate('({status:b10.view.status,snapshot:b10.view.snapshot,error:b10.view.fault,originalReady:AmmoniaStartup.ready})')
       assert result['snapshot'] is None and result['status'] in ['lost','unqualified-backend'] and result['originalReady']
       out['cases'].append({'case':mode,**result});await ctx.close()
      fp=await browser.new_page()
      try:
       await fp.goto((root/'root/index.html').as_uri(),timeout=10000);await fp.locator('#b10-a2-link').click();await fp.wait_for_timeout(500)
       out['file']=await fp.evaluate('({originalReady:AmmoniaStartup.ready,loaded:!!window.b10,text:document.getElementById("b10-a2-shadow").textContent})')
      except Exception as e:out['file']={'error':str(e)}
      await fp.close()
      # Actual non-loopback origin, same container only. No claim of external device reachability.
      candidates=socket.gethostbyname_ex(socket.gethostname())[2];ip=next((x for x in candidates if ipaddress.ip_address(x).is_private and not ipaddress.ip_address(x).is_loopback),None)
      if ip:
       p=await browser.new_page();response=await p.goto(f'http://{ip}:{servers[0].server_port}/')
       out['privateNetworkTransport']={'origin':p.url,'httpStatus':response.status,'originalReady':await p.evaluate('!!window.AmmoniaStartup?.ready'),'bodyExcerpt':(await p.locator('body').inner_text())[:200],'scope':'Same cloud host non-loopback path only; not an owner-network device test'}
       await p.close()
      else:out['privateNetworkTransport']={'untested':'No non-loopback private address available'}
      # Deliver only our own copied static bytes on reserved .invalid HTTP origin.
      # This tests genuine browser origin policy, never accesses a blocked destination,
      # and is explicitly NOT server/LAN reachability evidence or synthetic science.
      from urllib.parse import urlsplit
      ctx=await browser.new_context()
      async def own_static(route):
       path=urlsplit(route.request.url).path.lstrip('/') or 'index.html';file=(root/'root'/path).resolve()
       if not file.is_relative_to((root/'root').resolve()) or not file.is_file():return await route.fulfill(status=404,body='Missing local test asset')
       mime={'.mjs':'text/javascript','.html':'text/html','.css':'text/css','.json':'application/json'}.get(file.suffix,'application/octet-stream')
       await route.fulfill(status=200,content_type=mime,body=file.read_bytes(),headers={'Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; worker-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'"})
      await ctx.route('http://b11-origin-policy.invalid/**',own_static)
      p=await ctx.new_page();await p.goto('http://b11-origin-policy.invalid/');await p.locator('#b10-a2-link').click();await wait(p,'!!window.b10');await p.locator('#b10-a2-shadow #cold').click();await wait(p,'b10.view.status!=="initializing"')
      out['privateHTTP']=await p.evaluate('({origin:location.origin,secureContext:isSecureContext,subtle:!!crypto.subtle,randomUUID:typeof crypto.randomUUID,status:b10.view.status,snapshot:b10.view.snapshot,error:b10.view.fault,originalReady:AmmoniaStartup.ready})')
      out['privateHTTP']['scope']='Reserved HTTP .invalid origin with locally fulfilled exact package bytes; browser origin-policy test ONLY, no actual network reachability claim'
      assert not out['privateHTTP']['secureContext'] and out['privateHTTP']['snapshot'] is None and out['privateHTTP']['status']=='unqualified-backend'
      await p.locator('#storage-example').click();await p.locator('#storage-step').click();out['privateHTTP']['originalOperationClock']=await p.locator('#storage-clock').inner_text();await ctx.close()
      out['physicalIPad']='AWAITING USER DEVICE REVIEW';out['peerDeviceReachability']='UNTESTED: no second device in owner network';out['HTTPS']='Static requirements inspected; no HTTPS host deployed/tested';out['serviceWorker']='Absent; offline PWA not implemented';out['passed']=True
     except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
     finally:
      await browser.close();(E/f'portability-{name}.json').write_text(json.dumps(out,indent=2)+'\n')
     print(name,'portability',out['passed'],out.get('error',''),flush=True)
     if not out['passed']:raise RuntimeError(out['error'])
  finally:
   for s in servers:s.shutdown()
   (E/'independent-server-requests.json').write_text(json.dumps(requests,indent=2)+'\n')
asyncio.run(run())
