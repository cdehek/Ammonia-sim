// Run literal pinned suites, with actual static module serving for the derivative.
const http=require('http'),fs=require('fs'),path=require('path'),{spawn}=require('child_process');
const B=__dirname,R=path.resolve(B,'../../..'),mode=process.argv[2]||'candidate';
const root=path.join(B,'.runtime',mode==='baseline'?'pinned':'candidate');
const output=path.join(B,'evidence',mode+'-'+(process.env.TEST_BROWSER||'chromium'));
const all=['focus-mode-ui','default-units','tab-errors','browser','live-ui','profiles-ui','fault-ui','initialization-ui','storage-ui','valves-ui','release-ui','schematic-ui','history-ui','training-ui','dashboard-ui','visual-pass2-ui','industrial-styling-ui','hmi-uplift-ui','operator-assist-ui'];
const wk=['focus-mode-ui','release-ui','schematic-ui','history-ui','training-ui','visual-pass2-ui','industrial-styling-ui','hmi-uplift-ui','operator-assist-ui'];
const mime={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json'};
(async()=>{
 fs.mkdirSync(output,{recursive:true});const results=[];
 const server=http.createServer((req,res)=>{
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  const file=pathname==='/'?path.join(root,'index.html'):path.resolve(mode==='baseline'?root:path.join(B,'preview'),'.'+pathname);
  if(!file.startsWith(B+path.sep)||!fs.existsSync(file)||fs.statSync(file).isDirectory()){res.writeHead(404);return res.end('Not found');}
  res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');res.end(fs.readFileSync(file));
 });await new Promise(r=>server.listen(0,'127.0.0.1',r));
 try{for(const name of process.env.TEST_BROWSER==='webkit'?wk:all){
  const code=await new Promise((resolve,reject)=>{
   const stream=fs.createWriteStream(path.join(output,name+'.log'));
   const child=spawn(process.execPath,[path.join(root,'tests',name+'.cjs')],{env:{...process.env,TEST_URL:'http://127.0.0.1:'+server.address().port+(['tab-errors','browser','live-ui','release-ui'].includes(name)?'?workspace=all':'')}});
   child.stdout.pipe(stream);child.stderr.pipe(stream);child.on('error',reject);child.on('exit',code=>{stream.end();resolve(code);});
  });results.push({suite:name,code});fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(results,null,2));console.log(name,code);
 }}finally{await new Promise(r=>server.close(r));}
 if(results.some(r=>r.code!==0))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
