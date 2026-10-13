const {chromium}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
const path=require('path'),fs=require('fs'),http=require('http'),{execFileSync}=require('child_process');
(async()=>{
 const stage=process.argv[2]||'after',browser=await chromium.launch(launchOptions);
 const baseline=stage==='before'?execFileSync('git',['show','0473d32f62db992fde0f581d116e1bd0c8e7d8ed:index.html'],{cwd:path.resolve(__dirname,'..'),maxBuffer:4*1024*1024}):null;
 const observations=[];fs.mkdirSync(path.resolve(__dirname,'../docs/ui-evidence'),{recursive:true});
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html');res.end(baseline||fs.readFileSync(path.resolve(__dirname,'../index.html')));});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{
  for(const [name,width,height] of [['desktop-landscape',1440,1000],['desktop-portrait',900,1400],['ipad-landscape',1024,768],['ipad-portrait',768,1024]]){
   const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
   await page.clock.install();await page.goto('http://127.0.0.1:'+server.address().port);await page.locator('#tab-live').click();await page.locator('#storage-example').click();await page.locator('#storage-step').click();await page.evaluate(()=>scrollTo(0,0));
   observations.push({name,width,height,...await page.evaluate(()=>({schematicTop:document.getElementById('storage-schematic').getBoundingClientRect().top,documentWidth:document.documentElement.scrollWidth}))});
   await page.screenshot({path:path.resolve(__dirname,'../docs/ui-evidence/'+stage+'-'+name+'.png')});
   if(name==='ipad-landscape')await page.locator('#storage-schematic').screenshot({path:path.resolve(__dirname,'../docs/ui-evidence/'+stage+'-schematic.png')});
   await page.close();
  }
 fs.writeFileSync(path.resolve(__dirname,'../docs/ui-evidence/'+stage+'-viewports.json'),JSON.stringify(observations,null,2)+'\n');
 }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
