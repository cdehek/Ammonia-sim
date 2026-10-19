// External runtime selection only. Does not change original tests or assertions.
const path=require('path');
const pw=require(path.join(__dirname,'.runtime/pinned/node_modules/playwright'));
for(const name of ['chromium','webkit']){
 const launch=pw[name].launch.bind(pw[name]);
 pw[name].launch=(options={})=>launch({...options,executablePath:name==='webkit'?path.join(__dirname,'.runtime/webkit.sh'):path.join(__dirname,'.runtime/browsers/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell')});
}
