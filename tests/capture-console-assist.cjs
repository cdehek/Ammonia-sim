const {chromium,webkit}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const which=process.env.TEST_BROWSER==='webkit'?'webkit':'chromium';
(async()=>{const browser=await(which==='webkit'?webkit:chromium).launch({headless:true});
try{const page=await browser.newPage({viewport:{width:1024,height:768},hasTouch:true});await page.clock.install();await page.setContent(fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8'));
await page.locator('.plant-nav a[href="#storage-training"]').click();await page.locator('#training-select').selectOption('hot');await page.locator('#training-load').click();await page.locator('#training-answer').selectOption('0');await page.locator('#training-check').click();await page.locator('#training-disturbance').click();
for(let i=0;i<12&&await page.locator('#training-advance').isEnabled();i++)await page.locator('#training-advance').click();assert.match(await page.locator('#storage-alarm-summary').textContent(),/EQUIPMENT TRIP.*High discharge temperature/);await page.locator('#operator-assist-toggle').click();assert.equal(await page.locator('#operator-assist-close').evaluate(el=>el===document.activeElement),true);
for(const [name,width,height]of [['desktop',1440,1000],['ipad-landscape',1024,768],['ipad-portrait',768,1024]]){
 await page.setViewportSize({width,height});await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.resolve(__dirname,'../docs/operator-workstation/screenshots/'+which+'-'+name+'-assist-partial.png')});
 if(await page.locator('#console-expand').isVisible())await page.locator('#console-expand').click();await page.screenshot({path:path.resolve(__dirname,'../docs/operator-workstation/screenshots/'+which+'-'+name+'-assist-expanded.png')});await page.locator('#console-collapse').click();
}console.log('PASS: '+which+' Assist opens with Close focused; desktop and iPad viewport captures use the actual recorded hot-air trip.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
