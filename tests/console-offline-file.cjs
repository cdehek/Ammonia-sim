const {chromium,webkit}=require('playwright'),fs=require('fs'),path=require('path'),os=require('os');
const which=process.env.TEST_BROWSER==='webkit'?'webkit':'chromium';
(async()=>{const browser=await(which==='webkit'?webkit:chromium).launch({headless:true}),results=[];const dir=fs.mkdtempSync(path.join(os.tmpdir(),'ammonia-console-offline-'));
try{for(const [label,bytes] of [['baseline',require('child_process').execFileSync('git',['show','aa5612eb1caaeac38831fc0ae97cb94fe8048735:index.html'],{maxBuffer:4*1024*1024})],['candidate',fs.readFileSync(path.resolve(__dirname,'../index.html'))]]){
 const file=path.join(dir,label+'.html');fs.writeFileSync(file,bytes);const context=await browser.newContext({offline:true}),page=await context.newPage(),requests=[];page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
 try{await page.goto('file://'+file);await page.locator('#storage-example').click();await page.locator('#storage-step').click();require('node:assert/strict').match(await page.locator('#storage-clock').textContent(),/10.0 s/);require('node:assert/strict').deepEqual(requests,[]);results.push({label,pass:true,requests});}catch(e){results.push({label,pass:false,error:e.message,requests});}finally{await context.close();}
}}finally{await browser.close();fs.rmSync(dir,{recursive:true,force:true});}
fs.writeFileSync(path.resolve(__dirname,'../docs/operator-workstation/verification/'+which+'-offline-file.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));if(results.some(r=>!r.pass))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
