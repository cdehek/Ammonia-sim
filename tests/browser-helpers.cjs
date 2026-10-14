const fs=require('fs');
module.exports.launchOptions={headless:true,args:['--no-sandbox'],...(fs.existsSync('/usr/bin/chromium')?{executablePath:'/usr/bin/chromium'}:{})};

module.exports.enterLive=async page=>{const tab=page.locator('#tab-live');if(await tab.isVisible())await tab.click();require('node:assert/strict')(await page.locator('#view-live').isVisible(),'Live Plant opens directly in focus mode');};
