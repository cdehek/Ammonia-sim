'use strict';
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),os=require('node:os');
const {chromium,webkit}=require('playwright');const B=__dirname,R=path.resolve(B,'../../..');
const server=http.createServer((req,res)=>{try{let f=path.resolve(R,'.'+new URL(req.url,'http://localhost').pathname);if(!f.startsWith(R+'/'))throw Error('Path');if(fs.statSync(f).isDirectory())f=path.join(f,'index.html');const body=fs.readFileSync(f);res.writeHead(200,{'Content-Type':({'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.wasm':'application/wasm'}[path.extname(f)]||'text/plain')});res.end(body);}catch(e){res.writeHead(404);res.end();}});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));try{for(const [name,type]of [['chromium',chromium],['webkit',webkit]]){
 const launch={headless:true};if(name==='webkit')launch.executablePath=process.env.EOS_WEBKIT_EXECUTABLE;
 const bs=await type.launchServer(launch),browser=await type.connect(bs.wsEndpoint());
 try{for(const version of ['8.0.0','7.2.0']){
  const file=path.join(B,'evidence',`${name}-${version}.json`);if(fs.existsSync(file)){console.log('Retain',file);continue;}
  const context=await browser.newContext(),page=await context.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/experiments/dx-fv/browser_eos_precision/`);await page.waitForFunction(()=>!!window.precision);
  const inputs=JSON.parse(fs.readFileSync(path.join(B,'inputs.json')));
  const result=await page.evaluate(async({version,inputs})=>{const e=await precision.loadEOS(version);try{return await precision.diagnose(e,inputs);}finally{e.dispose();}},{version,inputs});
  Object.assign(result,{browser:name,browserVersion:browser.version(),environment:{node:process.version,playwright:require('playwright/package.json').version,cpu:os.cpus()[0].model,platform:os.platform()},userAgent:await page.evaluate(()=>navigator.userAgent)});
  fs.writeFileSync(file,JSON.stringify(result,null,2)+'\n');console.log(name,version,result.rows.length,'rows',result.elapsedMS,'ms');await context.close();
 }}finally{await browser.close();await bs.close();}
}}finally{server.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
