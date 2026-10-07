const assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),P=require('../equipment-profiles');
const {chromium}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
(async()=>{
 const browser=await chromium.launch(launchOptions);
 try{
  const legacy={...P.copy(P.DEFAULT),schemaVersion:1,id:'legacy-plant',name:'Legacy plant',futureVolumes:{receiver:.5,evaporator:null,condenser:.12}};delete legacy.inventory;
  const page=await browser.newPage({acceptDownloads:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(old=>{if(!localStorage.getItem('ammonia-lab-equipment-v1'))localStorage.setItem('ammonia-lab-equipment-v1',JSON.stringify({schemaVersion:1,activeId:old.id,profiles:[old]}));},legacy);
  await page.goto(process.env.TEST_URL);await page.locator('#tab-live').click();
  assert.equal(await page.locator('#profile-select').inputValue(),legacy.id);assert.match(await page.locator('#profile-status').textContent(),/upgraded in memory/);
  assert.match(await page.locator('#profile-summary').textContent(),/not configured/);
  await page.locator('#profile-edit').click();await page.locator('#profile-inventory summary').click();
  assert.equal(await page.locator('#profile-volume-receiver').inputValue(),'0.5');assert.equal(await page.locator('#profile-volume-evaporator').inputValue(),'');assert.equal(await page.locator('#profile-init-mode').inputValue(),'none');
  await page.locator('#profile-init-mode').selectOption('levels');await page.locator('#profile-save').click();assert.match(await page.locator('#profile-error').textContent(),/all three/);
  await page.locator('#profile-volume-evaporator').fill('.08');await page.locator('#temperature-unit').selectOption('C');await page.locator('#pressure-unit').selectOption('bara');
  assert.equal(await page.locator('#profile-init-suctionPressure').inputValue(),'2.5');assert.equal(await page.locator('#profile-init-dischargePressure').inputValue(),'12');
  assert.match(await page.locator('#profile-inventory-preview').textContent(),/Calculated charge.*kg.*stage|Calculated charge.*kg.*Preview only/);
  await page.locator('#profile-save').click();assert(await page.locator('#profile-form').isHidden());
  assert.match(await page.locator('#profile-active-label').textContent(),/revision 1/);await page.locator('#live-step').click();const liveBefore=await page.locator('#live-metrics').textContent();
  await page.locator('#profile-edit').click();await page.locator('#profile-init-mode').selectOption('charge');assert(await page.locator('#profile-fill-receiver-control').isHidden());assert(await page.locator('#profile-charge-control').isVisible());
  await page.locator('#profile-charge').fill('10000000');await page.locator('#profile-save').click();assert.match(await page.locator('#profile-error').textContent(),/Feasible charge/);
  await page.locator('#profile-charge').fill('60.123456789');
  await page.locator('#profile-init-mode').selectOption('levels');assert(await page.locator('#profile-fill-receiver-control').isVisible());
  await page.locator('#profile-init-mode').selectOption('charge');assert(Math.abs(Number(await page.locator('#profile-charge').inputValue())-60.123456789)<1e-10);
  await page.locator('#profile-charge').fill('60.123456789');await page.locator('#profile-save').click();assert(await page.locator('#profile-form').isHidden());assert.equal(await page.locator('#live-metrics').textContent(),liveBefore);
  await page.locator('#profile-use').click();assert.equal(await page.locator('#live-clock').textContent(),'00:00:00 simulated');assert.match(await page.locator('#profile-summary').textContent(),/60.123 kg/);
  await page.locator('#profile-edit').click();await page.locator('#pressure-unit').selectOption('psig');await page.locator('#temperature-unit').selectOption('F');assert.match(await page.locator('#profile-inventory-preview').textContent(),/°F/);
  await page.locator('#profile-save').click();let pending=page.waitForEvent('download');await page.locator('#profile-export').click();let download=await pending;const filename=path.join(__dirname,'initialization-profile.json');await download.saveAs(filename);const exported=JSON.parse(fs.readFileSync(filename));
  assert.equal(exported.schemaVersion,2);assert.equal(exported.inventory.initialization.suctionPressure,2.5);assert.equal(exported.inventory.initialization.dischargePressure,12);assert.equal(exported.inventory.initialization.chargeKg,60.123456789);assert.equal(exported.inventory.initialization.liquidFractions.receiver,null);
  await page.reload();await page.locator('#tab-live').click();assert.match(await page.locator('#profile-summary').textContent(),/60.123 kg/);assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('ammonia-lab-equipment-v1')).schemaVersion),2);
  const oldPayload={name:'legacy.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(legacy))};await page.locator('#profile-import-file').setInputFiles(oldPayload);await page.waitForFunction(()=>document.querySelectorAll('#profile-select option').length===3);assert.match(await page.locator('#profile-summary').textContent(),/not configured/);
  const invalid=P.copy(exported);invalid.inventory.initialization.chargeKg=10000000;await page.locator('#profile-import-file').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(invalid))});await page.waitForFunction(()=>document.querySelector('#profile-status').textContent.includes('Import rejected'));assert.match(await page.locator('#profile-status').textContent(),/Feasible charge/);
  await page.locator('#profile-select').selectOption('default');await page.locator('#profile-new').click();await page.locator('#profile-inventory summary').click();await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#profile-init-mode').selectOption('none');await page.locator('#profile-volume-receiver').fill('');await page.locator('#profile-name').fill('Optional initialization');await page.locator('#profile-save').click();assert(await page.locator('#profile-form').isHidden());assert.match(await page.locator('#profile-summary').textContent(),/not configured/);assert.deepEqual(errors,[]);
  console.log('PASS: legacy browser migration, fill/charge editor, feasibility rejection, precise units, non-disruptive saves, exports/reload/import, optional initialization and mobile layout.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
