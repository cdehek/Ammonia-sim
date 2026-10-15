"""New evidence only; serves the repository on loopback, never publishes it."""
import functools, http.server, json, os, platform, subprocess, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

B = Path(__file__).resolve().parent
R = B.parents[2]
class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.mjs': 'text/javascript', '.wasm': 'application/wasm'}
    def log_message(self, *args): pass

def save(name, data):
    path = B / 'evidence' / name
    assert not path.exists(), f'Retain evidence: {path}'
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(R)))
threading.Thread(target=server.serve_forever, daemon=True).start()
inputs = json.loads((B.parent/'browser_eos_precision/inputs.json').read_text())
requests = json.loads((B.parent/'browser_eos/inputs.json').read_text())['requests']
targets = json.loads((B.parent/'browser_eos_precision/evidence/native-contract.json').read_text())['targets']
sources = {n: (B/'accepted'/n).read_text() for n in ['implicit.cjs','coupled-implicit.cjs']}
environment = {'python': platform.python_version(), 'platform': platform.platform(), 'physicalIPad': False,
               'playwright': subprocess.check_output(['python3','-m','pip','show','playwright'],text=True).split('Version: ')[1].splitlines()[0]}
try:
    with sync_playwright() as p:
        for name in ['chromium', 'webkit']:
            opts = {'headless': True}
            if name == 'webkit' and os.environ.get('EOS_WEBKIT_EXECUTABLE'): opts['executable_path'] = os.environ['EOS_WEBKIT_EXECUTABLE']
            try: browser = getattr(p, name).launch(**opts)
            except Exception as exc:
                save(name+'-unavailable.json', {'error': str(exc), 'environment':environment})
                continue
            try:
                for build in ['official8', 'build30', 'build44', 'official72']:
                    filename = f'{name}-{build}.json'
                    if (B/'evidence'/filename).exists(): continue
                    if build.startswith('build') and not (B/'vendor'/build/'coolprop.wasm').exists(): continue
                    context = browser.new_context()
                    page = context.new_page()
                    page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/')
                    page.wait_for_function('!!window.b1')
                    print('Running', name, build, flush=True)
                    data = page.evaluate('''async ({build,inputs,requests,targets,sources})=>{
                      const e=await b1.loadEOS(build);
                      try {
                        const precision=await b1.diagnose(e,inputs);
                        const accuracy=[];
                        for(const q of requests){
                          try {accuracy.push({id:q.id,mode:q.mode,region:q.region,state:e.evaluate(q,{extras:true})});}
                          catch(err){accuracy.push({id:q.id,mode:q.mode,region:q.region,error:String(err)});}
                        }
                        let synthetic=null;
                        // Screening is assessed offline before enabling solver execution.
                        if(build==='build44' && location.search.includes('solver'))throw Error('Use gated solver runner');
                        return {build,precision,accuracy,linearMemory:e.memory(),userAgent:navigator.userAgent};
                      }finally{e.dispose();}
                    }''', {'build':build,'inputs':inputs,'requests':requests,'targets':targets,'sources':sources})
                    data.update(browser=name,browserVersion=browser.version,environment=environment)
                    save(filename, data)
                    print(name,build,len(data['precision']['rows']),'precision rows',len(data['accuracy']),'accuracy rows',flush=True)
                    context.close()
            finally: browser.close()
finally: server.shutdown()
