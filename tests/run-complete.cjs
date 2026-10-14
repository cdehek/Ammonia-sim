// Runs every requested suite, retaining failures instead of stopping at the first.
const http=require('http'),fs=require('fs'),path=require('path'),{spawn}=require('child_process');
const root=path.resolve(process.argv[2]||path.join(__dirname,'..')),output=path.resolve(process.argv[3]||'test-results');
const suites=['focus-mode-ui','default-units','tab-errors','browser','live-ui','profiles-ui','fault-ui','initialization-ui','storage-ui','valves-ui','release-ui','schematic-ui','history-ui','training-ui','dashboard-ui','visual-pass2-ui','industrial-styling-ui','hmi-uplift-ui','operator-assist-ui'];
const webkit=['focus-mode-ui','release-ui','schematic-ui','history-ui','training-ui','visual-pass2-ui','industrial-styling-ui','hmi-uplift-ui','operator-assist-ui'];
(async()=>{
 fs.mkdirSync(output,{recursive:true});const results=[];
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(root,'index.html')));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{for(const name of process.env.TEST_BROWSER==='webkit'?webkit:suites){
  const result=await new Promise((resolve,reject)=>{
   const stream=fs.createWriteStream(path.join(output,name+'.log'));
   const child=spawn(process.execPath,[path.join(root,'tests',name+'.cjs')],{env:{...process.env,TEST_URL:'http://127.0.0.1:'+server.address().port+(['tab-errors','browser','live-ui','release-ui'].includes(name)?'?workspace=all':'')}});
   child.stdout.pipe(stream);child.stderr.pipe(stream);child.on('error',reject);child.on('exit',(code,signal)=>{stream.end();resolve({suite:name,code,signal});});
  });results.push(result);fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(result));
 }}finally{await new Promise(r=>server.close(r));}
 if(results.some(r=>r.code!==0))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
