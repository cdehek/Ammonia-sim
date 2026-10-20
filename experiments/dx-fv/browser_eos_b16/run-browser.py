"""Bounded, local-only genuine browser Workers. No external service or deployment."""
from pathlib import Path
import argparse, http.server, threading, subprocess, sys, os, signal, resource, time, json, gzip, hashlib
B=Path(__file__).resolve().parent; E=B/'evidence'; T=B/'.runtime';T.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('suite',choices=['science','performance','micro','retention','smoke','owner-ui']);p.add_argument('--name');p.add_argument('--browser',choices=['chromium','webkit','edge'],default='chromium');p.add_argument('--child',action='store_true');a=p.parse_args()
name=a.name or a.browser+'-'+a.suite
assert '/' not in name and name not in ['.','..']
for filename,x in json.loads((E/'copied-assets.json').read_text()).items():assert hashlib.sha256((B/filename).read_bytes()).hexdigest()==x['sha256'],'frozen source mismatch: '+filename
out=E/(name+('.json.gz' if a.suite=='science' else '.json'))
if a.child:
 from playwright.sync_api import sync_playwright
 os.chdir(B);os.environ['TMPDIR']='.runtime'
 class Handler(http.server.SimpleHTTPRequestHandler):
  extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.js':'text/javascript'}
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(B),**kwargs)
  def log_message(self,*args):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 errors=[];samples=E/(name+'-samples.jsonl')
 with sync_playwright() as pw:
  target={'chromium':pw.chromium,'webkit':pw.webkit,'edge':pw.chromium}[a.browser]
  launch={'headless':True}
  if a.browser!='webkit':launch.update(executable_path='/usr/bin/chromium' if a.browser=='chromium' else '/usr/bin/microsoft-edge',args=['--no-sandbox','--disable-dev-shm-usage','--js-flags=--max-old-space-size=512'])
  browser=target.launch(**launch)
  try:
   page=browser.new_page();page.set_default_timeout(90000)
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda e: print(e.text,flush=True) if e.type=='log' else None)
   def capture(row):
    with samples.open('a') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')
   page.expose_function('capture',capture)
   base='http://127.0.0.1:'+str(server.server_port)
   page.goto(base+'/index.html')
   if a.suite=='owner-ui':
    import zipfile
    package=T/'owner-package';package.mkdir(exist_ok=True)
    with zipfile.ZipFile(B/'b16-owner-benchmark.zip') as z:z.extractall(package)
    page.goto(base+'/.runtime/owner-package/index.html')
    mime=page.request.get(base+'/.runtime/owner-package/worker.mjs').headers.get('content-type')
    assert mime.startswith('text/javascript'),mime
    page.fill('#machine','Linux cloud package verification ONLY; not an owner device')
    page.click('#run');page.wait_for_function("!document.getElementById('download').disabled",timeout=240000)
    with page.expect_download() as download:page.click('#download')
    downloaded=T/'owner-download.json';download.value.save_as(downloaded);result=json.loads(downloaded.read_text());assert len(result['rows'])==24
    for f in ['cold','warm']:
     for pair in range(1,7):
      rows=[r for r in result['rows']if r['fixture']==f and r['pair']==pair];assert rows[0]['checksum']==rows[1]['checksum']
    result.update(passed=True,packageMIME=mime,scope='Actual local packaged UI/download on Linux cloud ONLY; no owner-device test')
    (B/'figures').mkdir(exist_ok=True);page.screenshot(path=str(B/'figures/owner-handoff-linux-smoke.png'))
   elif a.suite=='smoke':
    result=page.evaluate("async()=>{const{sample}=await import('./suite.mjs');return {passed:true,row:await sample('control','cold')};}")
   else:
    suite={'science':'scientificSuite','performance':'performanceSuite','micro':'microSuite','retention':'retentionSuite'}[a.suite]
    result=page.evaluate("async name=>{const m=await import('./suite.mjs');return m[name](x=>console.log(x),x=>window.capture(x));}",suite)
   result.update(browserVersion=browser.version,browser=a.browser,errors=errors)
   assert not errors,errors
   raw=(json.dumps(result,indent=2)+'\n').encode()
   if out.suffix=='.gz':out.write_bytes(gzip.compress(raw,mtime=0))
   else:out.write_bytes(raw)
  finally:browser.close()
 server.shutdown();print(json.dumps({'passed':True,'file':out.name}),flush=True);sys.exit(0)
assert not out.exists() and not (E/(name+'-samples.jsonl')).exists(),'use a new name; never overwrite receipts'
if a.suite in ['performance','micro','retention','owner-ui']:
 science=E/'chromium-science.json'
 assert json.loads(science.read_text() if science.exists() else gzip.decompress((E/'chromium-science.json.gz').read_bytes()))['passed'],'science first'
def limits():
 os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(480,481));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
start=time.monotonic();timeout=False
with (T/(name+'.stdout')).open('w') as stdout,(T/(name+'.stderr')).open('w') as stderr:
 child=subprocess.Popen([sys.executable,__file__,a.suite,'--name',name,'--browser',a.browser,'--child'],stdout=stdout,stderr=stderr,preexec_fn=limits)
 try:code=child.wait(timeout=600)
 except subprocess.TimeoutExpired:timeout=True;os.killpg(child.pid,signal.SIGKILL);code=child.wait()
 # Explicitly reap remaining children even after an abnormal browser failure.
 try:os.killpg(child.pid,signal.SIGTERM)
 except ProcessLookupError:pass
receipt={'returncode':code,'externalWallTermination':timeout,'wallSeconds':time.monotonic()-start,'wallBudgetSeconds':600,'cpuLimitPerProcessSeconds':480,'heapMiB':512,'stdout':(T/(name+'.stdout')).read_text(),'stderr':(T/(name+'.stderr')).read_text()}
(E/(name+'-exit.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['stdout','stderr']},indent=2))
assert code==0 and not timeout,receipt
