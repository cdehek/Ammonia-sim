const fs=require('fs');
module.exports.launchOptions={headless:true,args:['--no-sandbox'],...(fs.existsSync('/usr/bin/chromium')?{executablePath:'/usr/bin/chromium'}:{})};

module.exports.enterLive=async page=>{const tab=page.locator('#tab-live');if(await tab.isVisible())await tab.click();require('node:assert/strict')(await page.locator('#view-live').isVisible(),'Live Plant opens directly in focus mode');};

// Legacy workflows now navigate to the real console tool before acting.
// No clocks, playback state, assertions or simulated observations are changed.
module.exports.reveal=async(page,selector)=>{
 const target=page.locator(selector).first();
 if(!await target.count())return;
 const info=await target.evaluate(el=>({tool:el.closest('[data-console-tool]')?.dataset.consoleTool,library:!!el.closest('.training-library'),closed:!!el.closest('.training-library:not([open])')}));
 if(info.tool&&await target.isHidden()){
  if(info.tool==='operator-assist')await page.locator('#operator-assist-toggle').click();
  else await page.locator('.plant-nav a[href="#'+info.tool+'"]').click();
 }
 if(info.library&&info.closed)await page.locator('.training-library summary').click();
};
