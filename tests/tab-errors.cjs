const path=require('path');const {launchOptions}=require('./browser-helpers.cjs');
const fs=require('fs'),http=require('http'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
  const source=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
  const server=http.createServer((req,res)=>{
    res.setHeader('Content-Type','text/html; charset=utf-8');
    res.end(req.url==='/broken' ? source.replace('<script id="property-data" type="application/json">','<script id="property-data" type="application/json">INVALID') : source);
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch(launchOptions);
  try {
    for(const mobile of [false,true]) {
      const page=await browser.newPage({viewport:mobile?{width:820,height:1180}:{width:1280,height:900}});
      const errors=[];
      page.on('pageerror',e=>errors.push(e.message));
      await page.addInitScript(()=>{Array.prototype.at=undefined;});
      await page.goto('http://127.0.0.1:'+server.address().port);
      for(let round=0;round<2;round++) for(const name of ['thermo','room','scenarios','validation','cycle']) {
        await page.locator('#tab-'+name).click();
        assert(await page.locator('#view-'+name).isVisible());
        assert.equal(await page.locator('#tab-'+name).getAttribute('aria-selected'),'true');
        assert(await page.locator('#startup-notice').isHidden());
      }
      assert.deepEqual(errors,[]);
      await page.evaluate(()=>{
        window.dispatchEvent(new ErrorEvent('error',{message:'Script error.'}));
        window.dispatchEvent(new Event('unhandledrejection'));
      });
      assert(await page.locator('#startup-notice').isHidden());
      await page.locator('#tab-thermo').focus();
      await page.keyboard.press('ArrowRight');
      assert(await page.locator('#view-room').isVisible());
      await page.locator('#run-room').click();
      assert.match(await page.locator('#room-status').textContent(),/First reached setpoint/);
      assert(await page.locator('#startup-notice').isHidden());
      await page.close();
    }
    const broken=await browser.newPage();
    await broken.goto('http://127.0.0.1:'+server.address().port+'/broken');
    assert(await broken.locator('#startup-notice').isVisible());
    assert.match(await broken.locator('#startup-notice').textContent(),/could not start/);
    console.log('PASS: first/repeated tab clicks, keyboard navigation, room simulation, older-browser compatibility, post-start error events, and genuine startup failure reporting.');
  } finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;});
