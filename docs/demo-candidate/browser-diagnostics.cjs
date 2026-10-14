// Test-only, read-only close observer. Does not change browser clocks/assertions.
const fs=require('fs'),pw=require('playwright');
for(const type of ['chromium','webkit']){
 const original=pw[type].launch.bind(pw[type]);pw[type].launch=async(...args)=>{
  const browser=await original(...args),close=browser.close.bind(browser);
  browser.close=async(...args)=>{const pages=[];for(const context of browser.contexts())for(const page of context.pages()){
   try{pages.push(await page.evaluate(()=>({url:location.href,hidden:document.hidden,clock:document.querySelector('#storage-clock')?.textContent,status:document.querySelector('#storage-status')?.textContent,playback:document.querySelector('#storage-playback')?.dataset.state,error:document.querySelector('#storage-error')?.textContent,plot:document.querySelector('.history-plot')?.clientWidth,svg:document.querySelector('.history-plot svg')?.viewBox.baseVal.width})));}catch(e){pages.push({error:e.message});}
  }fs.writeFileSync(process.env.TEST_DIAGNOSTIC_OUTPUT,JSON.stringify({browser:type,pages},null,2)+'\n');return close(...args);};return browser;
 };
}
