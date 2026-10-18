"""Sequential bounded workers. Outer timeout 300s. No historical evidence writes."""
import asyncio,functools,gzip,http.server,json,threading,argparse,time,traceback,os
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['baseline','passive','matrix','validation','failure'],required=True);p.add_argument('--engines',default='chromium,webkit');a=p.parse_args()
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
async def main():
 async with async_playwright() as pw:
  for name in a.engines.split(','):
   target=E/f'{a.stage}-{name}.json.gz';assert not target.exists(),target
   browser=None;out={'engine':name,'stage':a.stage,'runs':[],'passed':False};logs=[]
   try:
    opts={'headless':True,'timeout':30000}
    if name=='webkit':opts['executable_path']='/workspace/b9-runtime/webkit.sh'
    browser=await getattr(pw,name).launch(**opts);out['browserVersion']=browser.version
    out['executable']=opts.get('executable_path',getattr(pw,name).executable_path)
    ctx=await browser.new_context();page=await ctx.new_page();page.on('pageerror',lambda e:logs.append(str(e)))
    await page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9b/index.html');await page.wait_for_function('!!window.workerRun')
    async def run(mode,fixture,**kw):
     return await asyncio.wait_for(page.evaluate('a=>window.workerRun(a)',dict(mode=mode,fixture=fixture,**kw)),40)
    if a.stage=='baseline':
     # Reuse unchanged original B9 service workload in addition to direct workers.
     out['originalService']=await asyncio.wait_for(page.evaluate("async()=>{const m=await import('../browser_eos_b9/experiment.mjs');const results=[];for(const fixture of ['cold','warm']){const r=await m.workload('worker',fixture,{engine:'"+name+"'});delete r.science;delete r.records;delete r.diagnostics.attempts;results.push(r);}return results;}"),90)
     for f in ['cold','warm']:out['runs'].append(await run('original',f))
    elif a.stage=='matrix':
     for round in range(3):
      for f in ['cold','warm']:
       for mode in ['original','pass-through','instrumented','original']:
        r=await run(mode,f);r['round']=round;out['runs'].append(r)
       print(name,'round',round,f,'complete',flush=True)
    elif a.stage=='validation':
     for f in ['cold','warm']:
      for mode in ['original','instrumented']:out['runs'].append(await run(mode,f,sequence=True))
    elif a.stage=='failure':
     out['failure']=await run('original','cold',failures=True)
     out['acceptedCopyFailure']=await run('original','cold',failureCopy=True)
    elif a.stage=='passive':
     try:
      cdp=await ctx.new_cdp_session(page);out['samplingSupported']=True;out['protocolVersion']=await cdp.send('Browser.getVersion')
     except Exception as ex:
      out['samplingSupported']=False;out['limitation']=str(ex)
     if out['samplingSupported']:
      pending={};profiles=[];ids=iter(range(1,100000));tasks=[];sampling=False
      async def send(session,method,params={}):
       id=next(ids);future=asyncio.get_running_loop().create_future();pending[(session,id)]=future
       await cdp.send('Target.sendMessageToTarget',{'sessionId':session,'message':json.dumps(dict(id=id,method=method,params=params))})
       return await asyncio.wait_for(future,10)
      def received(event):
       msg=json.loads(event['message']);key=(event['sessionId'],msg.get('id'))
       if key in pending:
        future=pending.pop(key)
        if 'error' in msg:future.set_exception(RuntimeError(str(msg['error'])))
        else:future.set_result(msg.get('result',{}))
      cdp.on('Target.receivedMessageFromTarget',received)
      async def attached(event):
       if event['targetInfo']['type']!='worker':return
       session=event['sessionId']
       if sampling:
        profiles.append(session)
        await send(session,'Profiler.enable');await send(session,'Profiler.setSamplingInterval',{'interval':500});await send(session,'Profiler.start')
       await send(session,'Runtime.runIfWaitingForDebugger')
      cdp.on('Target.attachedToTarget',lambda event:tasks.append(asyncio.create_task(attached(event))))
      await cdp.send('Target.setAutoAttach',{'autoAttach':True,'waitForDebuggerOnStart':True,'flatten':False})
      # Dedicated persistent worker so profiling is stopped before termination.
      await page.evaluate("()=>{window.sampleRun=async function(args){window.sampleWorker=new Worker('./worker.mjs',{type:'module'});return await new Promise((resolve,reject)=>{window.sampleWorker.onmessage=e=>e.data.success?resolve(e.data.result):reject(Error(JSON.stringify(e.data.error)));window.sampleWorker.onerror=e=>reject(Error(e.message));window.sampleWorker.postMessage(args);});};}")
      for f in ['cold','warm']:
       out['runs'].append(await run('original',f))
       sampling=True
       r=await asyncio.wait_for(page.evaluate("a=>window.sampleRun(a)",dict(mode='original',fixture=f)),40)
       await asyncio.gather(*tasks);session=profiles[-1];profile=await send(session,'Profiler.stop');(E/f'cpu-{name}-{f}.json').write_text(json.dumps(profile))
       r['passive']=True;out['runs'].append(r);await page.evaluate('window.sampleWorker.terminate()');sampling=False;out['runs'].append(await run('original',f))
      await cdp.send('Target.setAutoAttach',{'autoAttach':False,'waitForDebuggerOnStart':False,'flatten':False})
     else:
      for f in ['cold','warm']:out['runs'].append(await run('original',f))
    out['passed']=True
   except Exception as ex:out.update(error=str(ex),traceback=traceback.format_exc())
   finally:
    if browser:await browser.close()
    out['console']=logs;target.write_bytes(gzip.compress((json.dumps(out,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0));print(target.name,out['passed'],flush=True)
   if not out['passed']:raise RuntimeError(out.get('error'))
try:asyncio.run(main())
finally:server.shutdown()
