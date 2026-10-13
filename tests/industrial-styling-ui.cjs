const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {chromium,webkit}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
(async()=>{
 const which=process.env.TEST_BROWSER==='webkit'?'webkit':'chromium',browser=await (which==='webkit'?webkit:chromium).launch(which==='webkit'?{headless:true}:launchOptions);
 const directory=path.resolve(__dirname,'../docs/ui-styling');fs.mkdirSync(directory,{recursive:true});
 try{
  const page=await browser.newPage({viewport:{width:1024,height:768}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.clock.install();await page.goto(process.env.TEST_URL);await page.locator('#tab-live').click();
  const playback=page.locator('#storage-playback'),compressor=page.locator('[data-summary="compressor"]');
  const state=async(p,c)=>{assert.equal(await playback.getAttribute('data-state'),p);assert.equal(await compressor.getAttribute('data-state'),c);};
  const color=()=>playback.evaluate(el=>getComputedStyle(el).color);
  const capture=async(name)=>{await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(directory,'after-'+which+'-'+name+'-ipad-landscape.png')});};
  await state('ready','—');await page.locator('#storage-example').click();await state('paused','paused');const pausedColor=await color();
  await page.locator('#storage-start').click();await page.clock.runFor(250);await state('running','running');assert.notEqual(await color(),pausedColor);await capture('running');
  await page.locator('#storage-pause').click();await state('paused','paused');
  await page.locator('#storage-compressorOn').uncheck();await page.locator('#storage-form button[type="submit"]').click();await state('paused','off');await capture('off');
  await page.locator('#storage-valveMode').selectOption('manual');await page.locator('#storage-manualOpening').fill('45');assert.equal(await page.locator('#storage-form').getAttribute('data-dirty'),'true');
  await page.locator('.plant-nav a[href="#storage-form"]').click();await page.screenshot({path:path.join(directory,'after-'+which+'-draft-controls-ipad-landscape.png')});
  await page.locator('#storage-form button[type="submit"]').click();assert.equal(await page.locator('#storage-form').getAttribute('data-dirty'),'false');
  await page.locator('#pressure-unit').selectOption('bara');await page.locator('#profile-new').click();await page.locator('#profile-name').fill('Styling trip case');await page.locator('#profile-highTrip').fill('3');await page.locator('#profile-save').click();await page.locator('#profile-use').click();await page.locator('#storage-example').click();await page.locator('#storage-step').click();
  await state('stopped','stopped');assert.equal(await page.locator('#storage-alarm').getAttribute('data-severity'),'equipment');assert.match(await page.locator('#storage-alarm-summary').textContent(),/EQUIPMENT TRIP/);const tripColor=await color(),body=page.locator('[data-inspect="compressor"] .machine-body').first(),tripFill=await body.evaluate(el=>getComputedStyle(el).fill);await capture('equipment-trip');
  await page.locator('#profile-new').click();await page.locator('#profile-name').fill('Styling domain case');await page.locator('#profile-inventory summary').click();await page.locator('#profile-fill-receiver').fill('100');await page.locator('#profile-save').click();await page.locator('#profile-use').click();await page.locator('#storage-circuit').selectOption('closed');await page.locator('#storage-compressorOn').uncheck();await page.locator('#storage-receiverHeat').fill('100');await page.locator('#storage-initialize').click();await page.locator('#storage-step').click();
  await state('stopped','stopped');assert.equal(await page.locator('#storage-alarm').getAttribute('data-severity'),'model');assert.match(await page.locator('#storage-alarm-summary').textContent(),/MODEL-DOMAIN STOP.*no equipment trip asserted/);assert.notEqual(await color(),tripColor,'Equipment trips and model stops use distinct badge colors');assert.notEqual(await body.evaluate(el=>getComputedStyle(el).fill),tripFill,'Model stop does not paint compressor as an equipment trip');assert.match(await body.evaluate(el=>getComputedStyle(el).fill),/schematic-machine/);await capture('model-stop');
  assert.deepEqual(errors,[]);console.log('PASS: '+which+' display-only status hooks follow ready, paused, running, compressor-off, real equipment trip and model-domain stop; badge severity and draft/applied styling remain distinct.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
