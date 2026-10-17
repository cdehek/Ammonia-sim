"""Actual browsers; process deadline supplied by timeout. Sequential scientific work."""
import argparse,asyncio,functools,gzip,http.server,json,os,threading,time,traceback
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--engines',default='chromium,webkit');p.add_argument('--tag',default='');a=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
async def main():
 async with async_playwright() as pw:
  for name in a.engines.split(','):
   target=E/f'{a.stage}-{name}{a.tag}.json.gz';assert not target.exists(),target
   opts=dict(timeout=30000,headless=True)
   if name=='webkit':opts['executable_path']='/workspace/b9-runtime/webkit.sh'
   browser=None;out={};logs=[]
   try:
    browser=await getattr(pw,name).launch(**opts)
    async def page_new():
     ctx=await browser.new_context();page=await ctx.new_page();page.set_default_timeout(30000)
     page.on('pageerror',lambda e:logs.append(str(e)))
     await page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9/index.html',timeout=30000)
     return ctx,page
    if a.stage in ['benchmark','errorsbench']:
     out['blocks']=[]
     for round in range(3):
      for mode in (['worker','main'] if round%2 else ['main','worker']):
       ctx,page=await page_new();block={'round':round,'mode':mode,'runs':[]};acks=[];running=True
       async def clicks():
        while running:
         t=time.monotonic()
         try:await page.mouse.click(70,30)
         except TypeError:await page.mouse.click(70,30)
         acks.append((time.monotonic()-t)*1000);await asyncio.sleep(.05)
       task=asyncio.create_task(clicks())
       for fixture in (['cold','warm'] if a.stage=='benchmark' else ['C1-supported-error']):
        for temperature in (['cold-session','warm-restart'] if a.stage=='benchmark' else ['fresh-sequence']):
         value=await asyncio.wait_for(page.evaluate("async a=>{const m=await import('./experiment.mjs');const v=await m.run(a.fixture==='C1-supported-error'?'c1timed':'workload',a);delete v.science;delete v.records;if(v.diagnostics)delete v.diagnostics.attempts;return JSON.stringify(v)}",dict(mode=mode,fixture=fixture,engine=name)),60)
         value=json.loads(value)
         # Binary64 science was compared in browser before this timing campaign.
         for k in ['science','records']:value.pop(k,None)
         value.update(temperature=temperature);block['runs'].append(value)
       running=False;await task;block['automationInputRoundtripMS']=acks;block['browserInputAcks']=await page.evaluate('window.inputAcks');out['blocks'].append(block);await ctx.close()
       print(name,'round',round,mode,'complete',flush=True)
    else:
     ctx,page=await page_new()
     out['result']=await asyncio.wait_for(page.evaluate("async a=>{const m=await import('./experiment.mjs');const v=await m.run(a.stage,a);if(a.stage==='parity'){const {exact}=await import('./values.mjs');for(const r of v.results)for(const mode of ['main','worker']){r[mode].science=exact(r[mode].science);r[mode].diagnostics.attempts=exact(r[mode].diagnostics.attempts);}}return JSON.stringify(v);}",dict(stage=a.stage,mode='both')),240)
     out['result']=json.loads(out['result'])
     await ctx.close()
    out.update(engine=name,browserVersion=browser.version,physicalSafariOrIPad=False,passed=True)
   except Exception as ex:out.update(passed=False,harnessError=str(ex),traceback=traceback.format_exc())
   finally:
    if browser:await browser.close()
    out['console']=logs;target.write_bytes(gzip.compress((json.dumps(out,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0));print(target.name,out['passed'],flush=True)
   if not out['passed']:raise RuntimeError(out.get('harnessError'))
try:asyncio.run(main())
finally:server.shutdown()
