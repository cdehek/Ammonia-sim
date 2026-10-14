// Narrow preservation diagnostic. Runs the original assertions unchanged.
// Usage: node tests/verify-webkit-resize.cjs approved-checkpoint.html focus-mode.html
const fs=require('fs'),http=require('http'),path=require('path'),{spawn}=require('child_process');
const {webkit}=require('playwright');
(async()=>{
 const results=[];
 for(const [index,file] of process.argv.slice(2).entries()){
  const html=fs.readFileSync(file),server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html');res.end(html);});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const url='http://127.0.0.1:'+server.address().port;
  try{
   const original=await new Promise((resolve,reject)=>{const child=spawn(process.execPath,[path.join(__dirname,'visual-pass2-ui.cjs')],{env:{...process.env,TEST_BROWSER:'webkit',TEST_URL:url}});let output='';child.stdout.on('data',s=>output+=s);child.stderr.on('data',s=>output+=s);child.on('error',reject);child.on('exit',code=>resolve({code,output}));});
   const browser=await webkit.launch({headless:true});let geometry,nativeGeometry;
   try{
    const page=await browser.newPage({viewport:{width:1024,height:768}});await page.clock.install();await page.goto(url);await require('./browser-helpers.cjs').enterLive(page);await page.locator('#storage-example').click();await page.locator('#storage-step').click();
    for(const key of ['compressor','condenser','receiver','evaporator','outlet','feed']){await page.locator('[data-component="'+key+'"]').focus();await page.keyboard.press('Enter');}
    await page.locator('#storage-start').click();await page.clock.runFor(250);await page.locator('#storage-pause').click();await page.locator('.plant-nav a[href="#storage-trends"]').click();await page.locator('#storage-trend-group').selectOption('pressure');await page.clock.runFor(20);
    const plot=page.locator('.history-plot svg');await plot.evaluate(el=>{const box=el.getBoundingClientRect(),width=el.viewBox.baseVal.width;el.dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:box.left+60/width*box.width,clientY:box.top+80}));});
    const read=()=>page.evaluate(()=>({viewport:innerWidth,plotWidth:document.querySelector('.history-plot').clientWidth,viewBoxWidth:document.querySelector('.history-plot svg').viewBox.baseVal.width,pinned:document.querySelector('#storage-trend-time').textContent}));
    const before=await read();await page.setViewportSize({width:1440,height:1000});await page.clock.runFor(30);const immediate=await read();
    // Diagnostic only: allow native rendering to settle, then advance mock timers.
    await new Promise(resolve=>setTimeout(resolve,250));await page.clock.runFor(100);const settled=await read();
    geometry={before,immediate,settled};
    // Separate native-clock observation; never changes the failed assertion above.
    const native=await browser.newPage({viewport:{width:1024,height:768}});await native.goto(url);await require('./browser-helpers.cjs').enterLive(native);await native.locator('#storage-example').click();await native.locator('#storage-step').click();await native.locator('#storage-trend-group').selectOption('pressure');
    const nativeRead=()=>native.evaluate(()=>({viewport:innerWidth,plotWidth:document.querySelector('.history-plot').clientWidth,viewBoxWidth:document.querySelector('.history-plot svg').viewBox.baseVal.width}));
    const nativeBefore=await nativeRead();await native.setViewportSize({width:1440,height:1000});await native.waitForTimeout(350);nativeGeometry={before:nativeBefore,settled:await nativeRead()};await native.close();

   }finally{await browser.close();}
   const result={version:['approved-checkpoint','focus-mode'][index],sha256:require('crypto').createHash('sha256').update(html).digest('hex'),original,geometry,nativeGeometry};results.push(result);console.log(JSON.stringify(result));
  }finally{await new Promise(resolve=>server.close(resolve));}
 }
 fs.writeFileSync(path.join(__dirname,'../docs/live-plant-focus/verification/webkit-resize.json'),JSON.stringify({browser:'Playwright 1.62.1 WebKit',results},null,2)+'\n');
})().catch(e=>{console.error(e);process.exitCode=1;});
