"""Local read-only HTTP plus installed desktop Chromium. No deployments/UI changes."""
from pathlib import Path
import http.server,threading,json,subprocess,sys,signal,os,time,resource
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
# Relative temp path keeps Unix-domain socket names below Linux's 108-byte limit.
os.chdir(B);os.environ['TMPDIR']='.runtime'
if len(sys.argv)==3 and sys.argv[1]=='--child':
 from playwright.sync_api import sync_playwright
 case=sys.argv[2]
 class Handler(http.server.SimpleHTTPRequestHandler):
  def __init__(self,*a,**k):super().__init__(*a,directory=str(R),**k)
  def log_message(self,*a):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--js-flags=--max-old-space-size=512']);page=browser.new_page();page.goto(base+'/experiments/dx-fv/browser_eos_b15/');page.set_default_timeout(35000)
  if case=='interface':result=page.evaluate("async()=>{const{run}=await import('./interface-regression.mjs');const x=run();delete x.rows;return {...x,runtime:navigator.userAgent};}")
  elif case=='edges':result=page.evaluate("async()=>{const{run}=await import('./edge-ownership.mjs');const x=run();delete x.rows;delete x.tableWitnesses;return {...x,runtime:navigator.userAgent};}")
  elif case=='properties':result=page.evaluate("async()=>{const{run}=await import('./property-tests.mjs');const x=run();delete x.rows;return {...x,runtime:navigator.userAgent};}")
  else:
   fixture,schedule=case.split('-');result=page.evaluate("async arg=>{const{run}=await import('./browser-science.mjs');return run(...arg);}",[fixture,schedule])
  result['browserVersion']=browser.version;browser.close()
 server.shutdown();print(json.dumps(result));sys.exit(0)
case=sys.argv[1];assert case in ['properties','edges','interface']or case in [f+'-'+s for f in ['cold','warm']for s in ['original','added','fine']]
name=sys.argv[2]if len(sys.argv)==3 else'browser-'+case;assert '/'not in name and name not in ['.','..'];out=E/(name+'.json');assert not out.exists();T=B/'.runtime';start=time.monotonic();timeout=False
with (T/(name+'.stdout')).open('w')as f,(T/(name+'.stderr')).open('w')as e:
 def limits():
  os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(40,41));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 p=subprocess.Popen([sys.executable,__file__,'--child',case],stdout=f,stderr=e,preexec_fn=limits)
 try:code=p.wait(timeout=40)
 except subprocess.TimeoutExpired:timeout=True;os.killpg(p.pid,signal.SIGKILL);code=p.wait()
receipt={'wallSeconds':time.monotonic()-start,'wallBudgetSeconds':40,'cpuLimitInheritedPerProcessSeconds':40,'heapMiB':512,'returncode':code,'externalTermination':timeout,'stderr':(T/(name+'.stderr')).read_text()};(E/(name+'.exit.json')).write_text(json.dumps(receipt,indent=2)+'\n');assert code==0 and not timeout,receipt
result=json.loads((T/(name+'.stdout')).read_text());manifest=json.loads((E/'build-manifest.json').read_text());result['sourceBuilds']={k:manifest['builds'][k]['sha256']for k in ['control','candidate','observe-control','observe-candidate']};assert result['passed'];out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'case':case,'passed':True,'browserVersion':result['browserVersion'],'wallSeconds':receipt['wallSeconds']}))
