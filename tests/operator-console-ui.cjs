const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {chromium,webkit}=require('playwright');
const which=process.env.TEST_BROWSER==='webkit'?'webkit':'chromium';
const output=path.resolve(__dirname,'../docs/operator-workstation');fs.mkdirSync(output+'/screenshots',{recursive:true});
const bytes=fs.readFileSync(path.resolve(__dirname,'../index.html'),'utf8');
const baseline=process.env.BASELINE_HTML?fs.readFileSync(process.env.BASELINE_HTML,'utf8'):require('child_process').execFileSync('git',['show','aa5612eb1caaeac38831fc0ae97cb94fe8048735:index.html'],{cwd:path.resolve(__dirname,'..'),encoding:'utf8',maxBuffer:4*1024*1024});
async function download(page,id){const pending=page.waitForEvent('download');await page.locator('#'+id).click();const stream=await(await pending).createReadStream(),chunks=[];for await(const c of stream)chunks.push(c);return Buffer.concat(chunks).toString();}
async function tool(page,id){if(id==='operator-assist'){if(await page.locator('#operator-assist').isHidden())await page.locator('#operator-assist-toggle').click();}else await page.locator('.plant-nav a[href="#'+id+'"]').click();}
async function manage(page){if(await page.locator('.training-library').count()&&!await page.locator('.training-library').evaluate(el=>el.open))await page.locator('.training-library summary').click();}
(async()=>{
 const browser=await(which==='webkit'?webkit:chromium).launch({headless:true});const errors=[];
 try{
  const page=await browser.newPage({viewport:{width:1024,height:768},hasTouch:true,acceptDownloads:true,reducedMotion:'reduce'});page.on('pageerror',e=>errors.push(e.message));await page.clock.install();await page.setContent(bytes);
  assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'collapsed');
  assert(await page.locator('#console-open').isVisible());assert(await page.locator('#console-body').isHidden());
  await page.locator('#storage-example').tap();await page.locator('#storage-step').tap();
  const summary=await page.locator('#storage-overview').textContent(),clock=await page.locator('#storage-clock').textContent();
  await page.locator('#console-open').tap();assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'partial');
  await page.locator('#console-expand').tap();assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'expanded');
  await page.keyboard.press('Escape');assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'partial');
  await page.locator('#console-collapse').tap();assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'collapsed');assert.equal(await page.locator('#console-open').evaluate(e=>e===document.activeElement),true);
  // Tool changes retain one set of controls, the same accepted state, and navigation.
  const before=await page.evaluate(()=>Array.from(document.querySelectorAll('[id]'),e=>e.id));assert.equal(new Set(before).size,before.length);
  for(const id of ['storage-form','storage-trends','plant-diagnostics','equipment-profiles','independent-room','operator-assist','storage-training']){
   await tool(page,id);assert(await page.locator('[data-console-tool="'+id+'"]').isVisible());
   assert.equal(await page.locator('#storage-clock').textContent(),clock);assert.equal(await page.locator('#storage-overview').textContent(),summary);
   assert(await page.locator('#storage-start').evaluate(el=>{const r=el.getBoundingClientRect(),c=document.querySelector('#operator-console').getBoundingClientRect();return r.top>=0&&r.bottom<c.top&&r.width>=44&&r.height>=44;}));
  }
  assert.equal(await page.locator('#storage-form').count(),1);assert.equal(await page.locator('#storage-compressorSpeed').count(),1);
  for(const [label,width,height] of [['desktop',1440,1000],['ipad-landscape',1024,768],['ipad-portrait',768,1024]]){
   await page.setViewportSize({width,height});await page.locator('#console-close').click();await page.evaluate(()=>scrollTo(0,0));
   assert(await page.locator('#schematic-graphic').evaluate(el=>{const r=el.getBoundingClientRect(),c=document.querySelector('#operator-console').getBoundingClientRect();return r.top<c.top&&r.width>600;}));
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.screenshot({path:output+'/screenshots/'+which+'-'+label+'-collapsed.png'});
   await tool(page,'storage-training');await manage(page);await page.locator('#training-select').selectOption('hot');await page.locator('#training-load').click();
   assert.match(await page.locator('#training-next-text').textContent(),/Answer the reflection/);
   assert.match(await page.locator('#training-observations').textContent(),/30.0 s.*bar\(a\).*K.*kg\/s/);
   assert.equal(await page.locator('#training-objectives .met').count(),0);
   assert(await page.locator('#training-next-text').evaluate(el=>{const r=el.getBoundingClientRect(),body=document.querySelector('#console-body').getBoundingClientRect();return r.top>=body.top&&r.top<body.bottom;}));
   await page.screenshot({path:output+'/screenshots/'+which+'-'+label+'-exercise-partial.png'});
   await page.locator('#console-expand').click();
   await page.waitForFunction(()=>document.querySelector('#storage-start').getBoundingClientRect().bottom<document.querySelector('#operator-console').getBoundingClientRect().top);
   await page.screenshot({path:output+'/screenshots/'+which+'-'+label+'-exercise-expanded.png'});
   await manage(page);await page.locator('#training-end').click();
  }
  // All five recipes: compare byte-for-byte exported evidence with the checkpoint.
  const old=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});old.on('pageerror',e=>errors.push(e.message));await old.clock.install();await old.setContent(baseline);
  const reports={};
  for(const id of ['startup','load','restriction','tuning','hot']){
   for(const p of [old,page]){
    if(p===page){await tool(p,'storage-training');await manage(p);}
    await p.locator('#training-select').selectOption(id);await p.locator('#training-load').click();
    if(p===page)assert.match(await p.locator('#training-next-text').textContent(),/Answer the reflection/);
    await p.locator('#training-answer').selectOption('0');await p.locator('#training-check').click();
    if(id!=='startup'){
     if(p===page)assert.match(await p.locator('#training-next-text').textContent(),/Automatic warmup is complete/);
     await p.locator('#training-disturbance').click();
    }
    for(let i=0;i<24&&await p.locator('#training-advance').isEnabled();i++)await p.locator('#training-advance').click();
    if(id==='hot'){
     assert.match(await p.locator('#storage-alarm-summary').textContent(),/EQUIPMENT TRIP.*High discharge temperature/);
     if(p===page){
      assert.match(await p.locator('#training-next-text').textContent(),/engine recorded/);
      await tool(p,'operator-assist');assert.match(await p.locator('#operator-assist').textContent(),/High discharge temperature/);
      const evidence=await p.locator('#operator-assist').textContent();await page.screenshot({path:output+'/screenshots/'+which+'-assist-trip.png'});
      await page.locator('#console-collapse').click();await tool(p,'storage-training');await tool(p,'operator-assist');assert.equal(await p.locator('#operator-assist').textContent(),evidence);
      await tool(p,'storage-training');
     }
     await p.locator('#training-restore').click();if(p===page)assert.match(await p.locator('#training-next-text').textContent(),/Clear the modeled stop/);
     await p.locator('#training-clear').click();await p.locator('#training-advance').click();
    }
    assert.match(await p.locator('#training-status').textContent(),/Objectives completed/,id);
   }
   await manage(page);const expected=await download(old,'training-export'),actual=await download(page,'training-export');assert.equal(actual,expected,id+' exported attempt and full SI history unchanged');
   reports[id]=JSON.parse(actual);fs.writeFileSync(output+'/verification/'+which+'-'+id+'-evidence.json',actual);
  }
  // Guidance is a suggestion: disturbance before reflection still grades normally.
  await manage(page);await page.locator('#training-select').selectOption('restriction');await page.locator('#training-load').click();await page.locator('#training-disturbance').click();await page.locator('#training-answer').selectOption('0');await page.locator('#training-check').click();await page.locator('#training-advance').click();assert.match(await page.locator('#training-status').textContent(),/Objectives completed/);
  // Read-only console inspection and rotation leave accepted SI CSV bytes unchanged.
  await tool(page,'storage-form');const csv=await download(page,'storage-export');
  for(const id of ['storage-training','storage-trends','operator-assist','plant-diagnostics'])await tool(page,id);
  await page.setViewportSize({width:768,height:1024});await page.locator('[data-component="condenser"]').focus();await page.keyboard.press('Enter');
  await tool(page,'storage-form');assert.equal(await download(page,'storage-export'),csv);
  await tool(page,'operator-assist');await page.locator('#operator-assist-close').focus();await page.keyboard.press('Escape');assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'collapsed');assert.equal(await page.locator('#operator-assist-toggle').evaluate(e=>e===document.activeElement),true);
  await page.locator('#console-open').focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'partial');await page.keyboard.press('Escape');assert.equal(await page.locator('#operator-console').getAttribute('data-size'),'collapsed');
  // Offline standalone startup, including touch and keyboard use, with no requests.
  const offline=await browser.newPage({viewport:{width:1024,height:768},hasTouch:true}),requests=[];offline.on('pageerror',e=>errors.push(e.message));offline.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});await offline.context().setOffline(true);await offline.setContent(bytes);
  await offline.locator('#storage-example').tap();await offline.locator('#storage-step').tap();await tool(offline,'operator-assist');assert.match(await offline.locator('#operator-assist').textContent(),/PLAYBACK PAUSED/);assert.deepEqual(requests,[]);assert.deepEqual(errors,[]);
  fs.writeFileSync(output+'/verification/'+which+'-console-summary.json',JSON.stringify({browser:which,workflows:Object.keys(reports),identicalEvidence:true,identicalSIExport:true,offlineRequests:requests,errors,physicalIPad:false},null,2));
  console.log('PASS: '+which+' console states, seven tools, one set of controls, schematic and playback visibility, touch/keyboard/Escape, desktop and iPad layouts, five actual workflows, real hot trip/recovery, retained Assist evidence, identical baseline SI trajectories and training exports, offline standalone bytes.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
