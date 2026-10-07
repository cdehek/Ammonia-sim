const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {chromium}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
(async()=>{
 const browser=await chromium.launch(launchOptions);
 try{
  const page=await browser.newPage({acceptDownloads:true,viewport:{width:1280,height:950}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{Array.prototype.at=undefined;});
  await page.goto(process.env.TEST_URL);
  await page.locator('#tab-live').click();assert(await page.locator('section.metrics').isHidden());
  assert.equal(await page.locator('#live-initial').inputValue(),'59');assert.equal(await page.locator('#live-target').inputValue(),'32');
  await page.locator('#live-step').click();assert.equal(await page.locator('#live-clock').textContent(),'00:01:00 simulated');
  assert.match(await page.locator('#live-status').textContent(),/Paused/);assert(await page.locator('#live-error').isHidden());
  assert.equal(await page.locator('#live-metrics .metric').count(),9);assert(await page.locator('#live-trends svg').isVisible());
  await page.locator('#live-mode').selectOption('manual');await page.locator('#live-manualSpeed').fill('60');await page.locator('#live-form button[type="submit"]').click();
  for(let i=0;i<10;i++)await page.locator('#live-step').click();assert.match(await page.locator('#live-metrics').textContent(),/60 \/ 60%/);
  const powerBefore=await page.locator('#live-metrics .metric').nth(5).textContent();
  await page.locator('[data-disturbance="ambient"]').click();assert.equal(await page.locator('#live-ambient').inputValue(),'86');
  await page.locator('[data-disturbance="condenser"]').click();assert.equal(await page.locator('#live-condUA').inputValue(),'18.75');
  await page.locator('[data-disturbance="gain"]').click();assert.equal(await page.locator('#live-gain').inputValue(),'12');await page.locator('#live-step').click();
  assert.notEqual(await page.locator('#live-metrics .metric').nth(5).textContent(),powerBefore);assert(await page.locator('#live-error').isHidden());
  const downloadPromise=page.waitForEvent('download');await page.locator('#live-export').click();const download=await downloadPromise;const filename=path.join(__dirname,'live-results.csv');await download.saveAs(filename);assert.match(fs.readFileSync(filename,'utf8'),/Suction bar absolute/);
  await page.locator('#temperature-unit').selectOption('C');await page.locator('#pressure-unit').selectOption('bara');assert.equal(await page.locator('#live-initial').inputValue(),'15');assert.equal(await page.locator('#live-ambient').inputValue(),'30');assert.match(await page.locator('#live-trends').textContent(),/°C/);
  await page.locator('[data-disturbance="availability"]').click();await page.locator('#live-step').click();assert.match(await page.locator('#live-status').textContent(),/unavailable/);assert.match(await page.locator('#live-metrics .metric').nth(5).textContent(),/0.0 kW/);assert.match(await page.locator('#live-metrics .metric').nth(1).textContent(),/off/);
  await page.locator('#live-initial').fill('20');await page.locator('#live-form button[type="submit"]').click();assert(await page.locator('#live-error').isVisible());await page.locator('#live-reset').click();assert(await page.locator('#live-error').isHidden());assert.match(await page.locator('#live-metrics .metric').first().textContent(),/20.0 °C/);
  await page.locator('[data-disturbance="availability"]').click();await page.locator('.live-tuning summary').click();await page.locator('#live-highTrip').fill('3');await page.locator('#live-form button[type="submit"]').click();await page.locator('#live-step').click();assert.match(await page.locator('#live-status').textContent(),/TRIPPED/);
  await page.locator('#live-highTrip').fill('24');await page.locator('#live-form button[type="submit"]').click();await page.locator('#live-trip-reset').click();await page.locator('#live-step').click();assert.doesNotMatch(await page.locator('#live-status').textContent(),/TRIPPED/);
  const beforePlayback=await page.locator('#live-clock').textContent();await page.locator('#live-start').click();await page.waitForFunction(previous=>document.querySelector('#live-clock').textContent!==previous,beforePlayback);await page.locator('#live-pause').click();assert(await page.locator('#live-start').isEnabled());
  await page.evaluate(()=>window.dispatchEvent(new ErrorEvent('error',{message:'Script error.'})));assert(await page.locator('#startup-notice').isHidden());assert(await page.locator('#runtime-notice').isHidden());
  await page.evaluate(()=>window.dispatchEvent(new ErrorEvent('error',{message:'Test recoverable application error',filename:location.href})));assert(await page.locator('#runtime-notice').isVisible());await page.locator('#runtime-dismiss').click();
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(__dirname,'live-mobile.png'),fullPage:true});
  await page.setViewportSize({width:1280,height:950});await page.screenshot({path:path.join(__dirname,'live-desktop.png'),fullPage:true});
  await page.locator('#tab-cycle').click();assert(await page.locator('section.metrics').isVisible());assert.equal(await page.locator('#metric-Q').textContent(),'112.6 kW');assert.deepEqual(errors,[]);
  console.log('PASS: Live plant controls, disturbances, equipment response, trips/reset, playback, units, CSV, runtime errors, mobile layout, and reference-mode isolation.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
