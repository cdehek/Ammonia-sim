const {chromium}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
const path=require('path'),fs=require('fs'),http=require('http'),{execFileSync}=require('child_process');
(async()=>{
 const stage=process.argv[2]||'after',directory=path.resolve(__dirname,'../docs/ui-pass2');fs.mkdirSync(directory,{recursive:true});
 const html=stage==='before'?execFileSync('git',['show','22d2067dfb71e4055fd6488016adedabf42618c2:index.html'],{cwd:path.resolve(__dirname,'..'),maxBuffer:4*1024*1024}):fs.readFileSync(path.resolve(__dirname,'../index.html'));
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch(launchOptions),measurements=[];
 try{
  for(const [name,width,height] of [['desktop-landscape',1440,1000],['desktop-portrait',900,1400],['ipad-landscape',1024,768],['ipad-portrait',768,1024]]){
   const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});await page.clock.install();await page.goto('http://127.0.0.1:'+server.address().port);await page.locator('#tab-live').click();await page.locator('#storage-example').click();await page.locator('#storage-step').click();await page.evaluate(()=>scrollTo(0,0));
   measurements.push({name,width,height,...await page.evaluate(()=>{const svg=document.querySelector('#schematic-graphic svg'),rect=svg.getBoundingClientRect();return {diagramTop:rect.top,diagramBottom:rect.bottom,diagramWidth:rect.width,documentWidth:document.documentElement.scrollWidth};})});
   await page.screenshot({path:path.join(directory,stage+'-'+name+'.png')});
   if(name==='ipad-landscape'){
    await page.locator('#storage-schematic').screenshot({path:path.join(directory,stage+'-schematic.png'),style:'.plant-nav{visibility:hidden}'});
    await page.locator('.plant-nav a[href="#storage-trends"]').click();await page.locator('#storage-trend-group').selectOption('pressure');await page.screenshot({path:path.join(directory,stage+'-trends-ipad-landscape.png')});
   }
   if(stage==='after'&&name==='ipad-portrait'){await page.locator('#schematic-graphic').evaluate(el=>el.scrollLeft=el.scrollWidth);await page.screenshot({path:path.join(directory,'after-ipad-portrait-right.png')});}
   await page.close();
  }
  fs.writeFileSync(path.join(directory,stage+'-measurements.json'),JSON.stringify(measurements,null,2)+'\n');
 }finally{await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
