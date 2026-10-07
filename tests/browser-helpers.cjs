const fs=require('fs');
module.exports.launchOptions={headless:true,args:['--no-sandbox'],...(fs.existsSync('/usr/bin/chromium')?{executablePath:'/usr/bin/chromium'}:{})};
