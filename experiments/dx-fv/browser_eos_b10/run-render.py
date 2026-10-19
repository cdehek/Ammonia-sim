"""Independent display formula assertions on actual accepted worker projections."""
import asyncio,functools,http.server,json,threading
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start()
async def main():
 async with async_playwright() as pw:
  out=[]
  for n in ['chromium','webkit']:
   path=B/'.runtime/webkit.sh' if n=='webkit' else next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))
   browser=await getattr(pw,n).launch(executable_path=str(path),headless=True)
   try:
    p=await browser.new_page();await p.goto(f'http://127.0.0.1:{s.server_port}/experiments/dx-fv/browser_eos_b10/');await p.locator('#b10-a2-link').click();await p.wait_for_function('!!window.b10')
    rows=await p.evaluate('''async()=>{const rows=[];for(const fixture of ['cold','warm']){await b10.initialize(fixture);for(let i=0;i<4;i++){if(i)await b10.action('advance');const snapshot=b10.client.view.snapshot,original=JSON.stringify(snapshot);for(const unit of ['SI','US']){const input=b10.root.querySelector('#units');input.value=unit;input.dispatchEvent(new Event('change',{bubbles:true}));const cells=[...b10.root.querySelectorAll('[data-reading]')];for(const cell of cells){const key=cell.dataset.conversion;let value=cell.dataset.reading.split('.').reduce((v,k)=>v?.[k],snapshot);if(!['identity','pressure','C','K','delta'].includes(key))throw Error('Unrecognized unit meaning');if(unit==='US'&&typeof value==='number'){if(key==='pressure')value=(value-1.01325)*14.503773773;else if(key==='C')value=1.8*value+32;else if(key==='K')value=1.8*(value-273.15)+32;else if(key==='delta')value=1.8*value;}const expected=value===null||value===undefined?'unavailable':typeof value==='number'&&Number.isFinite(value)?value.toPrecision(12):String(value);if(cell.textContent!==expected)throw Error('Independent source/unit mismatch '+cell.dataset.reading);}if(JSON.stringify(snapshot)!==original)throw Error('Formatting mutated accepted projection');rows.push({fixture,time:snapshot.clockSeconds,unit,cells:cells.length,sourceUnchanged:true});}}}await b10.action('dispose');return rows;}''');out.append({'browser':n,'passed':True,'independentFormulaChecks':True,'rows':rows});print(n,'render PASS',flush=True)
   finally:await browser.close()
  (E/'independent-render.json').write_text(json.dumps(out,indent=2)+'\n')
try:asyncio.run(main())
finally:s.shutdown()
