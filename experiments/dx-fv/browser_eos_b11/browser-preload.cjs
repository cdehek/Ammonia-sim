// External runtime selection only. Does not change original tests or assertions.
const path=require('path');
for(const root of ['pinned','candidate']){
 const modulePath=path.join(__dirname,'.runtime',root,'node_modules/playwright');if(!require('fs').existsSync(modulePath))continue;
 const pw=require(modulePath);
 for(const name of ['chromium','webkit']){
  const launch=pw[name].launch.bind(pw[name]);
  pw[name].launch=(options={})=>launch({...options,executablePath:name==='webkit'?path.join(__dirname,'.runtime/webkit.sh'):path.join(__dirname,'.runtime/browsers/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell')});
 }
}
