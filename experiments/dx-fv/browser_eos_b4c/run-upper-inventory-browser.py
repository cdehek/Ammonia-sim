import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'))
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   old=json.loads((E/f'{name}-controlA-focused.json').read_text())['rows'];samples={}
   for r in old:
    for x in [r['base']]+[q['output'] for q in r['probes'] if 'output'in q]:
     if 1<x['state']['Q']<=1+1e-9:samples[tuple(x['inputBits'])]=dict(p=x['p'],h=x['h'],inputBits=x['inputBits'])
   browser=getattr(pw,name).launch(timeout=30000,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' else {}));page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/')
   try:
    result=page.evaluate('''async requests=>{const {loadEOS}=await import('/experiments/dx-fv/browser_eos_b4c/loader.mjs');const rows=[];for(const build of ['controlA','candidateB']){const e=await loadEOS(build);try{for(const q of requests){const s=e.evaluate({mode:'PH',args:[q.p,q.h]}),V=.003/5,M=s.rho*V,U=M*(q.h/1000)-100*(q.p/1e5)*V,rho=M/V,u=U/M*1000,row={build,...q,state:s,inventory:{M,U_kJ:U,V,rho,u}};try{const du=e.evaluate({mode:'DU',args:[rho,u]});row.DU=du;row.canonicalDifferences={p:du.p-q.p,h:du.h-q.h,T:du.T-s.T};row.canonicalPass=Math.abs(row.canonicalDifferences.p)<=.1&&Math.abs(row.canonicalDifferences.h)<=.1&&Math.abs(row.canonicalDifferences.T)<=1e-4;row.strictRecoveredPressureSupport=du.p>=3e4&&du.p<=35e5;}catch(x){row.error=String(x);row.canonicalPass=false;}rows.push(row);}}finally{e.dispose();}}return {rows};}''',list(samples.values()))
    result.update(browser=name,browserVersion=browser.version,allCandidateCanonicalPass=all(r['canonicalPass'] for r in result['rows'] if r['build']=='candidateB'))
    target=E/f'{name}-upper-quality-inventories.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n');assert result['allCandidateCanonicalPass'];print(name,len(samples),'unique invalid inventories pass',flush=True)
   finally:page.close();browser.close()
finally:server.shutdown()
