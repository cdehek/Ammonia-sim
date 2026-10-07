const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {chromium}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
(async()=>{
 const browser=await chromium.launch(launchOptions);
 try{
  const page=await browser.newPage({acceptDownloads:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.clock.install();await page.goto(process.env.TEST_URL);await page.locator('#tab-live').click();
  await page.locator('#temperature-unit').selectOption('C');await page.locator('#pressure-unit').selectOption('bara');
  async function profile(name,key,value){
   await page.locator('#profile-new').click();await page.locator('#profile-name').fill(name);
   await page.locator('#profile-'+key).fill(String(value));await page.locator('#profile-save').click();await page.locator('#profile-use').click();
  }
  await profile('Immediate pressure trip','highTrip',3);
  for(const speed of ['1','60','300']){
   await page.locator('#live-reset').click();await page.locator('#live-speed').selectOption(speed);
   await page.locator('#live-start').click();await page.clock.runFor(1500);
   assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');
   assert.match(await page.locator('#live-status').textContent(),/TRIPPED/);assert(await page.locator('#live-start').isEnabled());
   assert.match(await page.locator('#live-fault').textContent(),/Detected at 0.00 simulated seconds.*Suction.*Discharge.*Limits: high 3.00 bar\(a\)/);
   assert.match(await page.locator('#live-metrics .metric').nth(1).textContent(),/off/);
   await page.locator('#live-step').click();assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');
   await page.locator('#live-start').click();assert.match(await page.locator('#live-error').textContent(),/Reset the trip/);
  }
  await page.locator('#temperature-unit').selectOption('F');await page.locator('#pressure-unit').selectOption('psig');
  assert.match(await page.locator('#live-fault').textContent(),/psig/);assert.match(await page.locator('#live-fault').textContent(),/°F/);
  const pending=page.waitForEvent('download');await page.locator('#live-export').click();const download=await pending;
  const file=path.join(__dirname,'fault-results.csv');await download.saveAs(file);const csv=fs.readFileSync(file,'utf8');
  assert.match(csv,/Captured suction bar absolute/);assert.match(csv,/"equipment","High discharge pressure","0"/);
  await page.locator('#live-trip-reset').click();assert(await page.locator('#live-fault').isHidden());
  await page.locator('#temperature-unit').selectOption('C');await page.locator('#pressure-unit').selectOption('bara');
  await profile('No condenser equilibrium','condUA',.1);await page.locator('#live-step').click();
  assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');
  assert.match(await page.locator('#live-status').textContent(),/SOLVER LIMIT/);assert.doesNotMatch(await page.locator('#live-status').textContent(),/TRIPPED/);
  assert.match(await page.locator('#live-fault').textContent(),/no equipment trip is asserted/);
  assert.equal(await page.locator('#live-trip-reset').textContent(),'Clear model stop');assert(await page.locator('#live-error').isHidden());
  await page.locator('#live-start').click();assert.match(await page.locator('#live-error').textContent(),/Clear the model stop/);
  await page.locator('#live-trip-reset').click();await page.locator('#live-step').click();
  assert.equal(await page.locator('#live-clock').textContent(),'00:01:01 simulated'); // minimum-off timer, no stale batch
  await page.locator('#live-step').click();assert.match(await page.locator('#live-status').textContent(),/SOLVER LIMIT/);
  await page.locator('#profile-select').selectOption('default');await page.locator('#profile-use').click();
  await page.locator('#live-available').uncheck();await page.locator('#live-initial').fill('40');await page.locator('#live-thermalMass').fill('.1');await page.locator('#live-gain').fill('5000');await page.locator('#live-reset').click();await page.locator('#live-step').click();
  assert.match(await page.locator('#live-status').textContent(),/MODEL LIMIT/);assert.doesNotMatch(await page.locator('#live-status').textContent(),/TRIPPED/);
  assert.equal(await page.locator('#live-clock').textContent(),'00:00:01 simulated');assert.match(await page.locator('#live-fault').textContent(),/reset the plant/);
  await page.locator('#live-initial').fill('15');await page.locator('#live-gain').fill('2');await page.locator('#live-thermalMass').fill('30');await page.locator('#live-available').check();await page.locator('#live-reset').click();await page.locator('#live-step').click();
  assert(await page.locator('#live-fault').isHidden());assert(await page.locator('#live-error').isHidden());assert.deepEqual(errors,[]);
  console.log('PASS: fault pause at all playback speeds, trip evidence, unit conversion, CSV, distinct solver/domain labels and clear/reset recovery.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
