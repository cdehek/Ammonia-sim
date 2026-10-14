// Read-only geometry probe, native clocks, separate from unchanged browser assertions.
const fs=require('fs'),http=require('http'),{webkit}=require('playwright');
(async()=>{const results=[];
 for(const [index,file] of process.argv.slice(2).entries()){
  const html=fs.readFileSync(file),server=http.createServer((q,r)=>{r.setHeader('Content-Type','text/html; charset=utf-8');r.end(html);});await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const browser=await webkit.launch({headless:true});try{
   for(const motion of ['no-preference','reduce']){
    const page=await browser.newPage({viewport:{width:1024,height:768},reducedMotion:motion});await page.goto('http://127.0.0.1:'+server.address().port);await page.locator('#storage-example').click();await page.locator('#storage-step').click();await page.locator('#storage-trend-group').selectOption('pressure');await page.locator('.plant-nav a[href="#storage-trends"]').click();
    const read=()=>page.evaluate(()=>({viewport:innerWidth,plot:document.querySelector('.history-plot').clientWidth,svg:document.querySelector('.history-plot svg').viewBox.baseVal.width,clock:document.querySelector('#storage-clock').textContent}));
    const geometry=[{phase:'initial',...await read()}];
    for(const size of [{width:768,height:1024},{width:1024,height:768},{width:1440,height:1000}]){await page.setViewportSize(size);await page.waitForTimeout(350);geometry.push({phase:'350ms',...await read()});await page.waitForTimeout(1000);geometry.push({phase:'1350ms',...await read()});}
    await page.locator('#storage-trend-group').selectOption('temperature');await page.locator('#storage-trend-group').selectOption('pressure');await page.waitForTimeout(350);geometry.push({phase:'after-existing-group-selection',...await read()});results.push({artifact:index===0?'exact-approved-baseline':'candidate',motion,sha256:require('crypto').createHash('sha256').update(html).digest('hex'),geometry});await page.close();
   }
  }finally{await browser.close();await new Promise(r=>server.close(r));}
 }
 fs.writeFileSync('docs/demo-candidate/verification/native-webkit-resize.json',JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
