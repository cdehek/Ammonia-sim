'use strict';
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),{chromium,webkit}=require('playwright');const B=__dirname,R=path.resolve(B,'../../..');
const server=http.createServer((req,res)=>{try{let f=path.resolve(R,'.'+new URL(req.url,'http://localhost').pathname);if(!f.startsWith(R+'/'))throw Error('Path');if(fs.statSync(f).isDirectory())f=path.join(f,'index.html');res.writeHead(200,{'Content-Type':({'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.wasm':'application/wasm'}[path.extname(f)]||'text/plain')});res.end(fs.readFileSync(f));}catch(e){res.writeHead(404);res.end();}});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));try{for(const [name,type]of [['chromium',chromium],['webkit',webkit]]){
 const bs=await type.launchServer({headless:true,...(name==='webkit'?{executablePath:process.env.EOS_WEBKIT_EXECUTABLE}:{})}),browser=await type.connect(bs.wsEndpoint());
 try{for(const version of ['8.0.0','7.2.0']){
  const file=path.join(B,'evidence',`${name}-synthetic-${version}.json`);if(fs.existsSync(file)){console.log('Retain',file);continue;}
  const context=await browser.newContext(),page=await context.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/experiments/dx-fv/browser_eos_precision/`);await page.waitForFunction(()=>window.precision);
  const targets=JSON.parse(fs.readFileSync(path.join(B,'evidence/native-contract.json'))).targets;
  const sources={linear:fs.readFileSync(path.join(R,'experiments/dx-fv/implicit.cjs'),'utf8'),newton:fs.readFileSync(path.join(R,'experiments/dx-fv/coupled-implicit.cjs'),'utf8')};
  const result=await page.evaluate(async({version,targets,sources})=>{
   const l={exports:{}};new Function('module','exports',sources.linear)(l,l.exports);const n={exports:{}};
   new Function('module','exports','require',sources.newton)(n,n.exports,key=>{if(key!=='./implicit.cjs')throw Error('Unexpected synthetic import');return l.exports;});
   const {synthetic}=await import('./synthetic.mjs'),e=await precision.loadEOS(version);try{return {version,init:e.init,...synthetic(e,targets,n.exports.coupledNewton),linearMemory:e.memory()};}finally{e.dispose();}
  },{version,targets,sources});Object.assign(result,{browser:name,browserVersion:browser.version(),physicalIPad:false});fs.writeFileSync(file,JSON.stringify(result,null,2)+'\n');console.log(name,version,result.rows.map(r=>`${r.target}/${r.n}/${r.accounting}:${r.converged}`).join(' '));await context.close();
 }}finally{await browser.close();await bs.close();}
}}finally{server.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
