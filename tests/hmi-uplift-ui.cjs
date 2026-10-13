const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {chromium,webkit}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
function parseCSV(text){
 const rows=[];let row=[],field='',quoted=false;
 for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}else if(!quoted&&(c===','||c==='\n')){row.push(field);field='';if(c==='\n'){rows.push(row);row=[];}}else if(c!=='\r'||quoted)field+=c;}
 if(field||row.length){row.push(field);rows.push(row);}return rows;
}
(async()=>{
 const which=process.env.TEST_BROWSER==='webkit'?'webkit':'chromium',browser=await (which==='webkit'?webkit:chromium).launch(which==='webkit'?{headless:true}:launchOptions),directory=path.resolve(__dirname,'../docs/ui-hmi-uplift');fs.mkdirSync(directory,{recursive:true});
 try{
  const page=await browser.newPage({viewport:{width:1024,height:768}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.clock.install();await page.goto(process.env.TEST_URL);await page.locator('#tab-live').click();assert.equal(await page.locator('[data-microtrend]').count(),0);assert.equal(await page.locator('#storage-form').getAttribute('data-applied'),'false');
  await page.locator('#storage-example').click();assert.equal(await page.locator('#storage-form').getAttribute('data-applied'),'true');for(let i=0;i<8;i++)await page.locator('#storage-step').click();
  assert.equal(await page.locator('[data-illustration]').count(),6);assert.equal(await page.locator('.machine-surface').count(),5);assert.equal(await page.locator('.model-partition-surface').count(),1);assert(await page.locator('#schematic-depth').count());
  const download=page.waitForEvent('download');await page.locator('#storage-history-export').click();const file=path.join(directory,'checked-history-'+which+'.csv');await (await download).saveAs(file);const rows=parseCSV(fs.readFileSync(file,'utf8')),header=rows.find(r=>r[0]==='Record type'),details=header.indexOf('Details JSON SI'),samples=rows.filter(r=>r[0]==='sample').map(r=>JSON.parse(r[details])),end=samples.at(-1).seconds,recent=samples.filter(s=>s.seconds>=end-60);
  assert(end>=79.9,'A real run supplies more than one minute of history');
  const reads={suction:s=>s.pressures.outlet,discharge:s=>s.pressures.condenser,room:s=>s.temperatures.room,superheat:s=>s.actualSuperheat,feed:s=>s.opening};
  for(const [pressure,T]of [['psig','F'],['bara','C']]){
   await page.locator('#pressure-unit').selectOption(pressure);await page.locator('#temperature-unit').selectOption(T);
   for(const [key,read]of Object.entries(reads)){
    const convert=v=>['suction','discharge'].includes(key)?pressure==='psig'?(v-1.01325)*14.503773773:v:key==='feed'?v*100:key==='room'&&T==='F'?v*1.8+32:key==='superheat'&&T==='F'?v*1.8:v;
    const values=recent.map(read).filter(Number.isFinite).map(convert),trace=page.locator('[data-microtrend="'+key+'"]');
    assert(Math.abs(Number(await trace.getAttribute('data-min'))-Math.min(...values))<1e-9);assert(Math.abs(Number(await trace.getAttribute('data-max'))-Math.max(...values))<1e-9);
    assert.equal(Number(await trace.getAttribute('data-from')),recent[0].seconds);assert.equal(Number(await trace.getAttribute('data-to')),end);
    const ids=(await trace.getAttribute('data-sample-ids')).split(',').map(Number);assert(ids.every(id=>recent.some(s=>s.id===id)),'Microtrend points are retained observations');assert.match(await trace.getAttribute('aria-label'),/Independently scaled; gaps are unavailable/);
   }
  }
  await page.locator('#pressure-unit').selectOption('psig');await page.locator('#temperature-unit').selectOption('F');
  for(const viewport of [{width:1440,height:1000},{width:1024,height:768},{width:768,height:1024},{width:390,height:844}]){
   await page.setViewportSize(viewport);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const overlap=await page.locator('.instrument-band').evaluateAll(bands=>bands.map(b=>{const strong=b.querySelector('strong').getBoundingClientRect(),trace=b.querySelector('.instrument-trace,.instrument-state-mark,.instrument-no-trace').getBoundingClientRect();return strong.right>trace.left+1||b.querySelector('strong').scrollWidth>b.querySelector('strong').clientWidth+1;}));assert(overlap.every(value=>!value),'Instrument values and traces do not overlap at '+viewport.width);
   assert(await page.locator('#storage-start').evaluate(el=>el.getBoundingClientRect().height>=44));
  }
  await page.setViewportSize({width:1024,height:768});await page.locator('#storage-example').click();await page.locator('#storage-start').click();await page.clock.runFor(250);await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(directory,'after-'+which+'-running-ipad-landscape.png')});assert.match(await page.locator('#tab-live').getAttribute('title'),/Connected playback: Running/);await page.locator('#storage-pause').click();
  await page.locator('#storage-compressorOn').uncheck();await page.locator('#storage-form button[type="submit"]').click();await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(directory,'after-'+which+'-off-ipad-landscape.png')});
  await page.locator('#storage-valveMode').selectOption('manual');await page.locator('#storage-manualOpening').fill('45');await page.locator('.plant-nav a[href="#storage-form"]').click();await page.screenshot({path:path.join(directory,'after-'+which+'-draft-controls-ipad-landscape.png')});
  await page.locator('#pressure-unit').selectOption('bara');await page.locator('#profile-new').click();await page.locator('#profile-name').fill('HMI actual trip');await page.locator('#profile-highTrip').fill('3');await page.locator('#profile-save').click();await page.locator('#profile-use').click();await page.locator('#storage-example').click();await page.locator('#storage-step').click();assert.equal(await page.locator('#storage-alarm').getAttribute('data-severity'),'equipment');await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(directory,'after-'+which+'-equipment-trip-ipad-landscape.png')});
  await page.locator('#profile-new').click();await page.locator('#profile-name').fill('HMI actual domain stop');await page.locator('#profile-inventory summary').click();await page.locator('#profile-fill-receiver').fill('100');await page.locator('#profile-save').click();await page.locator('#profile-use').click();await page.locator('#storage-circuit').selectOption('closed');await page.locator('#storage-compressorOn').uncheck();await page.locator('#storage-receiverHeat').fill('100');await page.locator('#storage-initialize').click();await page.locator('#storage-step').click();assert.equal(await page.locator('#storage-alarm').getAttribute('data-severity'),'model');assert.match(await page.locator('#tab-live').getAttribute('title'),/MODEL-DOMAIN STOP/);assert.equal(await page.locator('[data-microtrend="superheat"],[data-microtrend="feed"]').count(),0,'Unavailable values have no invented trace');await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(directory,'after-'+which+'-model-stop-ipad-landscape.png')});
  assert.deepEqual(errors,[]);console.log('PASS: '+which+' five microtrends agree with exported retained SI samples and unit conversion; one-minute scope, exact sample IDs, unavailable gaps, six existing symbols, five material treatments, value/trace separation, touch targets and real state screenshots.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
