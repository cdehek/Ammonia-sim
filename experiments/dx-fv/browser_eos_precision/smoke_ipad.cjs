'use strict';
// Desktop package readiness only. Never labels the emulated browser as a physical iPad.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),{chromium,webkit}=require('playwright');
const B=__dirname,root=path.resolve(process.argv[2]),output=process.argv[3],offlineOnly=process.argv.includes('--offline-only');
if(!root.startsWith('/workspace/')&&!root.startsWith('/tmp/'))throw Error('Isolated package path required');if(fs.existsSync(path.join(B,'evidence',output)))throw Error('Retain completed evidence');
let unavailable=false,blocked=0;const server=http.createServer((req,res)=>{if(unavailable){blocked++;res.writeHead(503);res.end('Origin disabled');return;}try{const u=new URL(req.url,'http://localhost');if(!u.pathname.startsWith('/precision/'))throw Error('Scope');let f=path.resolve(root,u.pathname.slice('/precision/'.length));if(!f.startsWith(root+'/')&&f!==root)throw Error('Path');if(fs.statSync(f).isDirectory())f=path.join(f,'index.html');res.writeHead(200,{'Content-Type':({'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.wasm':'application/wasm'}[path.extname(f)]||'text/plain')});res.end(fs.readFileSync(f));}catch(e){res.writeHead(404);res.end();}});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));const results=[];try{for(const [name,type]of [['chromium',chromium],['webkit',webkit]]){
 unavailable=false;const bs=await type.launchServer({headless:true,...(name==='webkit'?{executablePath:process.env.EOS_WEBKIT_EXECUTABLE}:{})}),browser=await type.connect(bs.wsEndpoint());
 try{const context=await browser.newContext(),page=await context.newPage(),url=`http://127.0.0.1:${server.address().port}/precision/`,row={browser:name,version:browser.version(),physicalIPad:false,online:[],errors:[]};page.on('pageerror',e=>row.errors.push(e.message));
 await page.goto(url);await page.waitForFunction(()=>window.ipadResearch);await page.evaluate(()=>ipadResearch.prepareOffline());await page.waitForFunction(()=>ipadResearch.getRecord().offlinePreparation||ipadResearch.getRecord().errors.length,{},{timeout:60000});
 row.preparation=await page.evaluate(()=>ipadResearch.getRecord());
 if(!offlineOnly)for(const version of ['8.0.0','7.2.0']){
  await page.selectOption('#version',version);await page.evaluate(()=>ipadResearch.run());await page.waitForFunction(()=>!ipadResearch.isRunning(),{},{timeout:120000});row.online.push(await page.evaluate(()=>ipadResearch.getRecord()));
 }
 unavailable=true;const before=blocked;await page.close();const fresh=await context.newPage();
 try{await fresh.goto(url);await fresh.waitForFunction(()=>window.ipadResearch,{},{timeout:10000});row.offlineRestart={loaded:true,fromFreshPage:true,originDisabled:true};
  if(!offlineOnly){await fresh.evaluate(()=>ipadResearch.run());await fresh.waitForFunction(()=>!ipadResearch.isRunning(),{},{timeout:120000});row.offlineRestart.record=await fresh.evaluate(()=>ipadResearch.getRecord());}
 }catch(e){row.offlineRestart={loaded:false,error:e.message,fromFreshPage:true,originDisabled:true};}
 row.offlineRestart.blockedOriginRequests=blocked-before;results.push(row);await context.close();console.log(name,'offlineLoaded',row.offlineRestart.loaded);
 }finally{await browser.close();await bs.close();}
 }}finally{server.close();}fs.writeFileSync(path.join(B,'evidence',output),JSON.stringify({packageManifest:JSON.parse(fs.readFileSync(path.join(root,'manifest.json'))),noPublishing:true,physicalIPad:false,results},null,2)+'\n');})().catch(e=>{console.error(e);process.exitCode=1;});
