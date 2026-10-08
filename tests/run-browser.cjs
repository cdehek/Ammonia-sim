const http=require('http'),fs=require('fs'),path=require('path'),{spawn}=require('child_process');
(async()=>{
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(__dirname,'../index.html')));});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 try{
  for(const test of (process.argv.length>2?process.argv.slice(2):['default-units.cjs','tab-errors.cjs','browser.cjs','live-ui.cjs','profiles-ui.cjs','fault-ui.cjs','initialization-ui.cjs','storage-ui.cjs','valves-ui.cjs','release-ui.cjs','schematic-ui.cjs','history-ui.cjs','training-ui.cjs','capacity-ui.cjs','capacity-controls-ui.cjs'])){
   const code=await new Promise((resolve,reject)=>{const child=spawn(process.execPath,[path.join(__dirname,test)],{stdio:'inherit',env:{...process.env,TEST_URL:'http://127.0.0.1:'+server.address().port}});child.on('error',reject);child.on('exit',resolve);});
   if(code!==0)throw Error(test+' failed');
  }
 }finally{await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;});
