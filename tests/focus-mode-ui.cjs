const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {chromium,webkit}=require('playwright'),{launchOptions}=require('./browser-helpers.cjs');
(async()=>{
 const which=process.env.TEST_BROWSER==='webkit'?'webkit':'chromium';
 const browser=await (which==='webkit'?webkit:chromium).launch(which==='webkit'?{headless:true}:launchOptions);
 const directory=path.resolve(__dirname,'../docs/live-plant-focus/screenshots');fs.mkdirSync(directory,{recursive:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));await page.clock.install();await page.goto(process.env.TEST_URL.split('?')[0]);
  const hidden=['cycle','thermo','room','scenarios','validation'];
  assert(await page.locator('#view-live').isVisible());assert(await page.locator('.top .tabs').isHidden());
  assert.equal(await page.getByRole('tab').count(),0);assert(await page.locator('.sidebar').isHidden());
  assert.match(await page.locator('.brand').textContent(),/Ammonia Lab.*Live Plant/);
  for(const key of hidden){assert.equal(await page.locator('#tab-'+key).count(),1);assert(await page.locator('#tab-'+key).isHidden());assert(await page.locator('#view-'+key).isHidden());}
  const summary=page.locator('#model-information summary');assert(await summary.isVisible());await summary.focus();await page.keyboard.press('Enter');
  assert.match(await page.locator('#model-information').textContent(),/illustrative refrigeration simulator.*not manufacturer-calibrated.*does not establish real-plant accuracy.*actual plant safety decisions/s);
  const validation=await page.locator('#validation-table').innerHTML(),integration=await page.locator('#integration-table').innerHTML();
  await (await require('./browser-helpers.cjs').reveal(page,'#show-validation'),page.locator('#show-validation')).click();assert(await page.locator('#view-validation').isVisible());assert.equal(await page.locator('#integration-table tr').count(),24);
  assert.equal(await page.locator('#validation-return').evaluate(el=>el===document.activeElement),true);
  await (await require('./browser-helpers.cjs').reveal(page,'#validation-return'),page.locator('#validation-return')).click();assert(await page.locator('#view-live').isVisible());assert.equal(await summary.evaluate(el=>el===document.activeElement),true);
  await summary.click();
  async function capture(state){for(const [name,width,height] of [['desktop',1440,1000],['ipad-landscape',1024,768],['ipad-portrait',768,1024]]){
   await page.setViewportSize({width,height});await page.evaluate(()=>scrollTo(0,0));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   for(const id of ['storage-start','operator-assist-toggle'])assert(await page.locator('#'+id).evaluate(el=>{const r=el.getBoundingClientRect();return r.width>=44&&r.height>=44;}));
   if(state==='startup')assert(await page.locator('#schematic-graphic').evaluate(el=>el.getBoundingClientRect().top<innerHeight));
   await page.screenshot({path:path.join(directory,which+'-'+state+'-'+name+'.png'),animations:'disabled'});
  }}
  await capture('startup');await (await require('./browser-helpers.cjs').reveal(page,'#storage-example'),page.locator('#storage-example')).click();await (await require('./browser-helpers.cjs').reveal(page,'#storage-step'),page.locator('#storage-step')).click();assert.match(await page.locator('#storage-clock').textContent(),/10.0 s/);assert.equal(await page.locator('[data-illustration]').count(),6);await capture('plant');
  const retainedClock=await page.locator('#storage-clock').textContent(),retainedSummary=await page.locator('#storage-overview').textContent();await summary.click();await (await require('./browser-helpers.cjs').reveal(page,'#show-validation'),page.locator('#show-validation')).click();await (await require('./browser-helpers.cjs').reveal(page,'#validation-return'),page.locator('#validation-return')).click();await summary.click();assert.equal(await page.locator('#storage-clock').textContent(),retainedClock);assert.equal(await page.locator('#storage-overview').textContent(),retainedSummary);
  for(const target of ['storage-lab','storage-form','storage-trends','storage-training','plant-diagnostics','equipment-profiles','independent-room']){
   await (await require('./browser-helpers.cjs').reveal(page,'.plant-nav a[href="#'+target+'"]'),page.locator('.plant-nav a[href="#'+target+'"]')).click();assert.equal(await page.evaluate(()=>document.activeElement.id),target);
  }
  await (await require('./browser-helpers.cjs').reveal(page,'#storage-compressorSpeed'),page.locator('#storage-compressorSpeed')).fill('80');await (await require('./browser-helpers.cjs').reveal(page,'#storage-form button[type="submit"]'),page.locator('#storage-form button[type="submit"]')).click();assert.equal(await page.locator('#storage-form').getAttribute('data-dirty'),'false');
  await (await require('./browser-helpers.cjs').reveal(page,'[data-component="compressor"]'),page.locator('[data-component="compressor"]')).click();assert.match(await page.locator('#schematic-detail').textContent(),/Compressor/i);
  await (await require('./browser-helpers.cjs').reveal(page,'#storage-trend-group'),page.locator('#storage-trend-group')).selectOption('pressure');assert(await page.locator('.history-plot svg').count());
  for(const id of ['storage-export','storage-history-export']){const pending=page.waitForEvent('download');await (await require('./browser-helpers.cjs').reveal(page,'#'+id),page.locator('#'+id)).click();const stream=await (await pending).createReadStream(),chunks=[];for await(const chunk of stream)chunks.push(chunk);assert(Buffer.concat(chunks).length>100);}
  await (await require('./browser-helpers.cjs').reveal(page,'#profile-new'),page.locator('#profile-new')).click();await (await require('./browser-helpers.cjs').reveal(page,'#profile-name'),page.locator('#profile-name')).fill('Focus preservation');await (await require('./browser-helpers.cjs').reveal(page,'#profile-save'),page.locator('#profile-save')).click();assert.match(await page.locator('#profile-select').textContent(),/Focus preservation/);
  await (await require('./browser-helpers.cjs').reveal(page,'#training-load'),page.locator('#training-load')).click();await (await require('./browser-helpers.cjs').reveal(page,'#training-advance'),page.locator('#training-advance')).click();assert.match(await page.locator('#training-status').textContent(),/In progress/);
  await (await require('./browser-helpers.cjs').reveal(page,'#storage-example'),page.locator('#storage-example')).click();await (await require('./browser-helpers.cjs').reveal(page,'#operator-assist-toggle'),page.locator('#operator-assist-toggle')).click();assert.match(await page.locator('#operator-assist').textContent(),/PLAYBACK PAUSED/);await capture('assist');await (await require('./browser-helpers.cjs').reveal(page,'#operator-assist-close'),page.locator('#operator-assist-close')).click();
  // Restore every retained workspace with the documented URL option.
  const full=await browser.newPage();await full.goto(process.env.TEST_URL.split('?')[0]+'?workspace=all');assert.equal(await full.getByRole('tab').count(),6);assert(await full.locator('#view-cycle').isVisible());
  for(const key of ['cycle','thermo','room','scenarios','validation','live']){await (await require('./browser-helpers.cjs').reveal(full,'#tab-'+key),full.locator('#tab-'+key)).click();assert(await full.locator('#view-'+key).isVisible());}
  assert.equal(await full.locator('#validation-table').innerHTML(),validation);assert.equal(await full.locator('#integration-table').innerHTML(),integration);
  // Persistent build configuration uses the same mechanism, without network/storage.
  const configured=await browser.newPage();await configured.setContent(fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8').replace("const DEFAULT_WORKSPACE = 'live';","const DEFAULT_WORKSPACE = 'all';"));assert.equal(await configured.getByRole('tab').count(),6);assert(await configured.locator('#view-cycle').isVisible());
  // Load the standalone bytes with network disabled (also works without browser storage).
  const offline=await browser.newPage({viewport:{width:768,height:1024}}),requests=[];offline.on('pageerror',e=>errors.push(e.message));offline.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});await offline.context().setOffline(true);
  await offline.setContent(fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8'));assert(await offline.locator('#view-live').isVisible());assert(await offline.locator('#startup-notice').isHidden());await (await require('./browser-helpers.cjs').reveal(offline,'#storage-example'),offline.locator('#storage-example')).click();await (await require('./browser-helpers.cjs').reveal(offline,'#storage-step'),offline.locator('#storage-step')).click();assert.match(await offline.locator('#storage-clock').textContent(),/10.0 s/);await (await require('./browser-helpers.cjs').reveal(offline,'#model-information summary'),offline.locator('#model-information summary')).click();assert(await offline.locator('#show-validation').isVisible());assert.deepEqual(requests,[]);assert.deepEqual(errors,[]);
  console.log('PASS: '+which+' focus startup, hidden retained workspaces, URL/build restoration, existing validation route and keyboard return, all seven Live Plant sections, controls/schematic/trends/exercises/profiles/CSV exports, desktop/iPad layouts and standalone offline startup.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
