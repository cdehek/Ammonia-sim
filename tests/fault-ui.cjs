const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {chromium}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
(async()=>{
 const browser=await chromium.launch(launchOptions);
 try{
  const page=await browser.newPage({acceptDownloads:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.clock.install();await page.goto(process.env.TEST_URL);await require('./browser-helpers.cjs').enterLive(page);
  await (await require('./browser-helpers.cjs').reveal(page,'#temperature-unit'),page.locator('#temperature-unit')).selectOption('C');await (await require('./browser-helpers.cjs').reveal(page,'#pressure-unit'),page.locator('#pressure-unit')).selectOption('bara');
  async function profile(name,key,value){
   await (await require('./browser-helpers.cjs').reveal(page,'#profile-new'),page.locator('#profile-new')).click();await (await require('./browser-helpers.cjs').reveal(page,'#profile-name'),page.locator('#profile-name')).fill(name);
   await (await require('./browser-helpers.cjs').reveal(page,'#profile-'+key),page.locator('#profile-'+key)).fill(String(value));await (await require('./browser-helpers.cjs').reveal(page,'#profile-save'),page.locator('#profile-save')).click();await (await require('./browser-helpers.cjs').reveal(page,'#profile-use'),page.locator('#profile-use')).click();
  }
  await profile('Immediate pressure trip','highTrip',3);
  for(const speed of ['1','60','300']){
   await (await require('./browser-helpers.cjs').reveal(page,'#live-reset'),page.locator('#live-reset')).click();await (await require('./browser-helpers.cjs').reveal(page,'#live-speed'),page.locator('#live-speed')).selectOption(speed);
   await (await require('./browser-helpers.cjs').reveal(page,'#live-start'),page.locator('#live-start')).click();await page.clock.runFor(1500);
   assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');
   assert.match(await page.locator('#live-status').textContent(),/TRIPPED/);assert(await page.locator('#live-start').isEnabled());
   assert.match(await page.locator('#live-fault').textContent(),/Detected at 0.00 simulated seconds.*Suction.*Discharge.*Limits: high 3.00 bar\(a\)/);
   assert.match(await page.locator('#live-metrics .metric').nth(1).textContent(),/off/);
   await (await require('./browser-helpers.cjs').reveal(page,'#live-step'),page.locator('#live-step')).click();assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');
   await (await require('./browser-helpers.cjs').reveal(page,'#live-start'),page.locator('#live-start')).click();assert.match(await page.locator('#live-error').textContent(),/Reset the trip/);
  }
  await (await require('./browser-helpers.cjs').reveal(page,'#temperature-unit'),page.locator('#temperature-unit')).selectOption('F');await (await require('./browser-helpers.cjs').reveal(page,'#pressure-unit'),page.locator('#pressure-unit')).selectOption('psig');
  assert.match(await page.locator('#live-fault').textContent(),/psig/);assert.match(await page.locator('#live-fault').textContent(),/°F/);
  const pending=page.waitForEvent('download');await (await require('./browser-helpers.cjs').reveal(page,'#live-export'),page.locator('#live-export')).click();const download=await pending;
  const file=path.join(__dirname,'fault-results.csv');await download.saveAs(file);const csv=fs.readFileSync(file,'utf8');
  assert.match(csv,/Captured suction bar absolute/);assert.match(csv,/"equipment","High discharge pressure","0"/);
  await (await require('./browser-helpers.cjs').reveal(page,'#live-trip-reset'),page.locator('#live-trip-reset')).click();assert(await page.locator('#live-fault').isHidden());
  await (await require('./browser-helpers.cjs').reveal(page,'#temperature-unit'),page.locator('#temperature-unit')).selectOption('C');await (await require('./browser-helpers.cjs').reveal(page,'#pressure-unit'),page.locator('#pressure-unit')).selectOption('bara');
  await profile('No condenser equilibrium','condUA',.1);await (await require('./browser-helpers.cjs').reveal(page,'#live-step'),page.locator('#live-step')).click();
  assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');
  assert.match(await page.locator('#live-status').textContent(),/SOLVER LIMIT/);assert.doesNotMatch(await page.locator('#live-status').textContent(),/TRIPPED/);
  assert.match(await page.locator('#live-fault').textContent(),/no equipment trip is asserted/);
  assert.equal(await page.locator('#live-trip-reset').textContent(),'Clear model stop');assert(await page.locator('#live-error').isHidden());
  await (await require('./browser-helpers.cjs').reveal(page,'#live-start'),page.locator('#live-start')).click();assert.match(await page.locator('#live-error').textContent(),/Clear the model stop/);
  await (await require('./browser-helpers.cjs').reveal(page,'#live-trip-reset'),page.locator('#live-trip-reset')).click();await (await require('./browser-helpers.cjs').reveal(page,'#live-step'),page.locator('#live-step')).click();
  assert.equal(await page.locator('#live-clock').textContent(),'00:01:01 simulated'); // minimum-off timer, no stale batch
  await (await require('./browser-helpers.cjs').reveal(page,'#live-step'),page.locator('#live-step')).click();assert.match(await page.locator('#live-status').textContent(),/SOLVER LIMIT/);
  await (await require('./browser-helpers.cjs').reveal(page,'#profile-select'),page.locator('#profile-select')).selectOption('default');await (await require('./browser-helpers.cjs').reveal(page,'#profile-use'),page.locator('#profile-use')).click();
  await (await require('./browser-helpers.cjs').reveal(page,'#live-available'),page.locator('#live-available')).uncheck();await (await require('./browser-helpers.cjs').reveal(page,'#live-initial'),page.locator('#live-initial')).fill('40');await (await require('./browser-helpers.cjs').reveal(page,'#live-thermalMass'),page.locator('#live-thermalMass')).fill('.1');await (await require('./browser-helpers.cjs').reveal(page,'#live-gain'),page.locator('#live-gain')).fill('5000');await (await require('./browser-helpers.cjs').reveal(page,'#live-reset'),page.locator('#live-reset')).click();await (await require('./browser-helpers.cjs').reveal(page,'#live-step'),page.locator('#live-step')).click();
  assert.match(await page.locator('#live-status').textContent(),/MODEL LIMIT/);assert.doesNotMatch(await page.locator('#live-status').textContent(),/TRIPPED/);
  assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');assert.match(await page.locator('#live-fault').textContent(),/reset the plant/);
  await (await require('./browser-helpers.cjs').reveal(page,'#live-initial'),page.locator('#live-initial')).fill('15');await (await require('./browser-helpers.cjs').reveal(page,'#live-gain'),page.locator('#live-gain')).fill('2');await (await require('./browser-helpers.cjs').reveal(page,'#live-thermalMass'),page.locator('#live-thermalMass')).fill('30');await (await require('./browser-helpers.cjs').reveal(page,'#live-available'),page.locator('#live-available')).check();await (await require('./browser-helpers.cjs').reveal(page,'#live-reset'),page.locator('#live-reset')).click();await (await require('./browser-helpers.cjs').reveal(page,'#live-step'),page.locator('#live-step')).click();
  assert(await page.locator('#live-fault').isHidden());assert(await page.locator('#live-error').isHidden());assert.deepEqual(errors,[]);
  console.log('PASS: fault pause at all playback speeds, trip evidence, unit conversion, CSV, distinct solver/domain labels and clear/reset recovery.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
