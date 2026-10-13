'use strict';
// Static browser research. Does not import or advance any coupled simulator.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),os=require('node:os');
const {execFileSync}=require('node:child_process');const {chromium,webkit}=require('playwright');
const B=__dirname,R=path.resolve(B,'../../..'),E=path.join(B,'evidence');
const inputs=JSON.parse(fs.readFileSync(path.join(B,'inputs.json'))),steps=process.argv.slice(2);
const wanted=steps.length?steps:['accuracy','initialization','performance','worker','deployment'];
const prefix='/Ammonia-sim/',urlPath=prefix+'experiments/dx-fv/browser_eos/';
function save(name,data){fs.writeFileSync(path.join(E,name),JSON.stringify(data,null,2)+'\n');}
function rssTree(root){
  const a=execFileSync('ps',['-eo','pid=,ppid=,rss='],{encoding:'utf8'}).trim().split('\n').map(v=>v.trim().split(/\s+/).map(Number));
  const ids=new Set([root]);let old=0;while(old!==ids.size){old=ids.size;for(const [pid,ppid]of a)if(ids.has(ppid))ids.add(pid);}
  return {processes:a.filter(([pid])=>ids.has(pid)).map(([pid,ppid,rssKiB])=>({pid,ppid,rssKiB})),summedRSSKiB:a.filter(([pid])=>ids.has(pid)).reduce((v,r)=>v+r[2],0),caution:'Summed process RSS double-counts shared pages; not exclusive memory or iPad usage.'};
}
let serverUnavailable=false,blockedRequests=0;
const server=http.createServer((req,res)=>{
  if(serverUnavailable){blockedRequests++;req.socket.destroy();return;}
  try{
    const u=new URL(req.url,'http://localhost');if(!u.pathname.startsWith(prefix)){res.writeHead(404);res.end();return;}
    let name=path.resolve(R,decodeURIComponent(u.pathname.slice(prefix.length)));if(!name.startsWith(R+path.sep)&&name!==R){res.writeHead(403);res.end();return;}
    if(fs.statSync(name).isDirectory())name=path.join(name,'index.html');
    const ext=path.extname(name),mime=u.searchParams.get('mime')==='bad'?'application/octet-stream':({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.wasm':'application/wasm'}[ext]||'text/plain');
    const body=fs.readFileSync(name);res.writeHead(200,{'Content-Type':mime,'Content-Length':body.length,'Cache-Control':'no-store'});res.end(body);
  }catch(e){res.writeHead(404);res.end('Asset unavailable');}
});
async function pageReady(browser,base,options={}){const context=await browser.newContext(options),page=await context.newPage();await page.goto(base);await page.waitForFunction(()=>!!window.lab);return {context,page};}
async function main(){
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${server.address().port}${urlPath}`;
  const environment={node:process.version,playwright:require('playwright/package.json').version,platform:os.platform(),arch:os.arch(),cpu:os.cpus()[0]?.model,logicalCPUs:os.cpus().length,totalRAMBytes:os.totalmem(),testedOnPhysicalIPad:false,noCoupledRuns:true};
  save('benchmark-environment.json',environment);
  try{for(const [name,type]of [['chromium',chromium],['webkit',webkit]]){
    const launch={headless:true};if(name==='webkit'&&process.env.EOS_WEBKIT_EXECUTABLE)launch.executablePath=process.env.EOS_WEBKIT_EXECUTABLE;
    let bs,browser;
    try{bs=await type.launchServer(launch);browser=await type.connect(bs.wsEndpoint());}catch(e){save(name+'-unavailable.json',{error:e.message});continue;}
    try{for(const step of wanted){
      const file=`${name}-${step}.json`;if(fs.existsSync(path.join(E,file))){console.log('Retain completed',file);continue;}
      console.log('Start',name,step);const report={browser:name,version:browser.version(),environment};
      if(step==='accuracy'){
        report.builds=[];
        for(const version of ['7.2.0','8.0.0']){
          const partial=`${name}-accuracy-${version}.json`;
          if(fs.existsSync(path.join(E,partial))){report.builds.push(JSON.parse(fs.readFileSync(path.join(E,partial))));continue;}
          const {context,page}=await pageReady(browser,base);report.beforeMemory=rssTree(bs.process().pid);
          const refs=JSON.parse(fs.readFileSync(path.join(E,`python-${version}.json`)));
          const data=await page.evaluate(async({version,inputs,refs})=>{
            const eos=await lab.loadEOS(version),rows=[];let maxWork=0,maxMaxwell=0;
            for(let i=0;i<inputs.requests.length;i++){
              const q=inputs.requests[i],r=refs.rows[i],row={id:q.id,mode:q.mode};
              try{row.state=eos.evaluate(q,{extras:true});row.errors=r.state?Object.fromEntries(Object.keys(r.state).filter(k=>k in row.state).map(k=>[k,row.state[k]-r.state[k]])):null;
                const s=row.state;row.workIdentityJkg=s.h-s.u-s.p/s.rho;maxWork=Math.max(maxWork,Math.abs(row.workIdentityJkg));
                if('hp'in s){row.maxwellResidual=s.hp-(1/s.rho+s.T*s.rhoT/s.rho**2);maxMaxwell=Math.max(maxMaxwell,Math.abs(row.maxwellResidual));}
              }catch(e){row.error=e.message;}
              row.referenceError=r.error||null;rows.push(row);
            }
            // Persistent-state reuse after errors and order changes.
            const before=eos.stackPointer(),heap=eos.memory();let errorCount=0,recoveryCount=0;
            const good=inputs.requests.find(q=>q.mode==='PH'&&q.region==='liquid'&&q.id.startsWith('p3.5-'));
            for(let i=0;i<100;i++){try{eos.evaluate({mode:'PQ',args:[350000,1.1]});}catch(e){errorCount++;}const q=eos.evaluate(good);if(Number.isFinite(q.rho))recoveryCount++;}
            const stress={nativeErrors:errorCount,subsequentValidUpdates:recoveryCount,stackBefore:before,stackAfter:eos.stackPointer(),linearMemoryBefore:heap,linearMemoryAfter:eos.memory()};
            const reordered=inputs.requests.filter(q=>q.historical).reverse().map(q=>{try{return {id:q.id,state:eos.evaluate(q)};}catch(e){return {id:q.id,error:e.message};}});
            const out={init:eos.init,capabilities:eos.capabilities,rows,maxWorkIdentityJkg:maxWork,maxMaxwell,stress,reordered,linearMemoryFinal:eos.memory()};eos.dispose();return out;
          },{version,inputs,refs});
          const completed={requestedVersion:version,...data,processMemory:rssTree(bs.process().pid)};save(partial,completed);report.builds.push(completed);await context.close();
        }
      }else if(step==='initialization'){
        report.rounds=[];
        for(let i=0;i<3;i++){
          const {context,page}=await pageReady(browser,base);const out=await page.evaluate(async()=>{const e=await lab.loadEOS('8.0.0');const r={init:e.init,linearMemory:e.memory(),userAgent:navigator.userAgent,crossOriginIsolated};e.dispose();return r;});report.rounds.push({...out,processMemory:rssTree(bs.process().pid)});await context.close();
        }
        report.transfer='Loopback uncompressed assets; fresh contexts, shared browser compiler/OS caches possible. No WAN latency claim.';
      }else if(step==='performance'){
        const {context,page}=await pageReady(browser,base);report.baselineProcessMemory=rssTree(bs.process().pid);
        const engine=fs.readFileSync(path.join(R,'engine.js'),'utf8'),table=JSON.parse(fs.readFileSync(path.join(R,'properties.json')));
        Object.assign(report,await page.evaluate(async({inputs,engine,table})=>{
          const m={exports:{}};new Function('module','exports',engine)(m,m.exports);const original=m.exports.createEngine(table);
          const tableEval=q=>{
            const [a,b]=q.args;let r;
            if(q.mode==='PH')r=original.ph(a/1e5,b/1000);
            else if(q.mode==='DU')r=original.stateDU(a,b/1000);
            else if(q.mode==='PQ')r=original.statePX(a/1e5,b);
            else if(q.mode==='PT')r=original.statePT(a/1e5,b-273.15);
            else if(q.mode==='SAT'){r=original.sat(a/1e5);return {p:a,T:r.T+273.15,hf:r.hf*1000,hg:r.hg*1000,sf:r.sf*1000,sg:r.sg*1000,rhof:r.rhof,rhog:r.rhog};}
            return {p:r.p*1e5,T:r.T+273.15,h:r.h*1000,s:r.s*1000,rho:r.rho,u:r.u===undefined?r.h*1000-a/r.rho:r.u*1000,Q:r.x===null?-1:r.x};
          };
          const eos=await lab.loadEOS('8.0.0'),cached=lab.exactCache(eos);const timings=[];
          // Small diverse physical workloads, equal seven outputs per state.
          const groups=[];
          for(const region of ['liquid','vapor','two-phase'])for(const mode of ['PH','DU','PT']){
            if(region==='two-phase'&&mode==='PT')continue;
            groups.push({name:mode+'-'+region,requests:inputs.requests.filter(q=>q.mode===mode&&q.region===region&&['p3.5-','p8.0-','p32.65314902038559-'].some(s=>q.id.startsWith(s))).slice(0,12)});
          }
          groups.push({name:'SAT',requests:[3.5e5,8e5,32.65314902038559e5].map(p=>({mode:'SAT',args:[p,0]}))});
          for(const g of groups){
            for(let round=0;round<3;round++)for(const method of round%2?['table','high-level8','state8']:['state8','high-level8','table']){
              const fn=method==='table'?tableEval:method==='high-level8'?q=>eos.evaluate(q,{highLevel:true}):q=>eos.evaluate(q);let calls=0,failures=0,checksum=0;
              for(const q of g.requests){try{fn(q);}catch(e){}}
              const start=performance.now();do{for(const q of g.requests){try{const a=fn(q);checksum+=a.rho||a.rhof;}catch(e){failures++;}calls++;}}while(performance.now()-start<120);
              timings.push({group:g.name,method,round,calls,failures,elapsedMS:performance.now()-start,checksum});
            }
          }
          // Newton call graph, not a trajectory or new Newton implementation.
          function iteration(n,region,method){
            const seed=inputs.states.find(r=>r.region===region&&r.id.startsWith(region==='liquid'?'p32.65314902038559-':'p3.5-'));
            const s=seed.state,v=Array.from({length:n},(_,i)=>({mode:'PH',args:[s.p+i*10,s.h+i]}));
            const vectors=[v];for(let i=0;i<n;i++)for(let k=0;k<2;k++)vectors.push(v.map((q,j)=>j===i?{mode:'PH',args:q.args.map((a,b)=>b===k?a+(k===0?1e-7*Math.max(1,a/1e5)*1e5:1e-8*Math.max(1,a/1000)*1000):a)}:q));
            for(let i=0;i<2*n+1;i++)vectors.push(v);vectors.push(v.map(q=>({mode:'PH',args:[q.args[0]+.1,q.args[1]+.01]})));
            const fn=method==='table'?tableEval:method==='cached-state8'?q=>cached.evaluate(q):q=>eos.evaluate(q),stage=new Map();let calls=0,hits=0,checksum=0;
            cached.clear();
            for(const vector of vectors){
              for(const q of vector){const key=q.args.join(':');let state=stage.get(key);if(!state){state=fn(q);calls++;stage.set(key,state);fn({mode:'SAT',args:[q.args[0],0]});calls++;}else hits++;checksum+=state.rho;}
              for(let i=0;i<2;i++){fn(v[i%n]);fn({mode:'SAT',args:[v[i%n].args[0],0]});calls+=2;}
            }
            for(const q of v){const a=fn(q);fn({mode:'DU',args:[a.rho,a.u]});fn({mode:'SAT',args:[a.p,0]});calls+=3;}
            return {calls,stageHits:hits,cache:cached.stats(),checksum,residualEvaluations:vectors.length};
          }
          const patterns=[];
          for(const n of [5,9])for(const region of ['liquid','vapor','two-phase'])for(let round=0;round<3;round++)for(const method of ['table','state8','cached-state8']){
            const start=performance.now();const data=iteration(n,region,method);patterns.push({n,region,round,method,elapsedMS:performance.now()-start,...data});
          }
          // Exact cache equivalence against the same call order, no rounded keys.
          const qs=inputs.requests.filter(q=>q.mode==='PH'&&q.region==='liquid').slice(0,20),equivalence=[];cached.clear();
          for(const q of qs.concat(qs)){const a=eos.evaluate(q),b=cached.evaluate(q);equivalence.push({id:q.id,maxDifference:Math.max(...Object.keys(a).map(k=>Math.abs(a[k]-b[k])))});}
          const cacheProof={rows:equivalence,stats:cached.stats()};
          const sustained=[],work=groups.filter(g=>g.name.startsWith('PH-')||g.name.startsWith('DU-')).flatMap(g=>g.requests);
          for(let epoch=0;epoch<3;epoch++){
            const start=performance.now();let calls=0,checksum=0;do{for(const q of work){const a=eos.evaluate(q);checksum+=a.rho;calls++;}}while(performance.now()-start<1500);
            sustained.push({epoch,calls,elapsedMS:performance.now()-start,linearMemoryBytes:eos.memory(),checksum});
          }
          const out={init:eos.init,timings,patterns,cacheProof,sustained,linearMemoryFinal:eos.memory(),tableInputsHashMeaning:'Unchanged frozen table; identical SI request coordinates and result fields; failures counted, not made successful.'};eos.dispose();return out;
        },{inputs,engine,table}));report.finalProcessMemory=rssTree(bs.process().pid);
        if(name==='chromium'){const cdp=await context.newCDPSession(page);const m=await cdp.send('Runtime.getHeapUsage');report.chromiumHeapUsage=m;}
        await context.close();
      }else if(step==='scientific-supplement'){
        const {context,page}=await pageReady(browser,base);Object.assign(report,await page.evaluate(async(inputs)=>{
          const e=await lab.loadEOS('8.0.0'),canonical=[],derivatives=[];
          for(const q of inputs.requests.filter(q=>q.mode==='PH'&&['liquid','vapor','two-phase','saturation'].includes(q.region))){
            try{
              const a=e.evaluate(q),V=.003/5,M=a.rho*V,U=M*a.h-a.p*V,u=U/M;
              const b=e.evaluate({mode:'DU',args:[M/V,u]});
              canonical.push({id:q.id,region:q.region,inventory:{Mkg:M,Vm3:V,UJ:U},nativeUminusAccountingUJkg:a.u-u,
                recoveryErrors:{p:b.p-a.p,T:b.T-a.T,h:b.h-a.h,rho:b.rho-a.rho,u:b.u-u},PH:a,recovered:b});
            }catch(err){canonical.push({id:q.id,error:err.message});}
          }
          const chosen=inputs.requests.filter(q=>q.mode==='PH'&&['liquid','vapor'].includes(q.region)&&['p0.3029893712344606-liquid-z1.0','p32.65314902038559-liquid-z0.1','p3.5-vapor-z25.0'].some(p=>q.id.startsWith(p)));
          for(const q of chosen){
            const a=e.evaluate(q,{extras:true}),[p,h]=q.args;
            const analytical={rhoPAtH:a.rhoP-a.rhoT*a.hp/a.cp,rhoHAtP:a.rhoT/a.cp};
            const dp=1e-7*Math.max(1,p/1e5)*1e5,dh=1e-8*Math.max(1,h/1000)*1000;
            const pp=e.evaluate({mode:'PH',args:[p+dp,h]}),hp=e.evaluate({mode:'PH',args:[p,h+dh]});
            const finite={rhoPAtH:(pp.rho-a.rho)/dp,rhoHAtP:(hp.rho-a.rho)/dh};
            derivatives.push({id:q.id,pressureProbePa:dp,enthalpyProbeJkg:dh,analytical,finite,relativeErrors:Object.fromEntries(Object.keys(finite).map(k=>[k,(finite[k]-analytical[k])/analytical[k]]))});
          }
          const s=e.evaluate({mode:'SAT',args:[3.5e5,0]}),f=e.evaluate({mode:'PQ',args:[3.5e5,0]}),g=e.evaluate({mode:'PQ',args:[3.5e5,1]});
          const saturation={liquidGMinusVaporGJkg:(f.h-f.T*f.s)-(g.h-g.T*g.s),latentHMinusTDeltaSJkg:(g.h-f.h)-f.T*(g.s-f.s),saturationState:s};
          const out={canonical,derivatives,saturation,accountingEquation:'M=rho*V; U=M*h-P*V in SI; unchanged from accepted experimental physical definition',noSolverIntegration:true};e.dispose();return out;
        },inputs));await context.close();
      }else if(step==='probe-sweep'){
        const {context,page}=await pageReady(browser,base);Object.assign(report,await page.evaluate(async(inputs)=>{
          const saved=inputs.requests.find(q=>q.id==='p0.3029893712344606-liquid-z1.0-PH');const targets=[{name:'exact-saved-input',args:saved.args},{name:'declared-historical-input',args:[.3029893712344606*1e5,94.52334612321303*1000]}],builds=[];
          for(const version of ['7.2.0','8.0.0']){
            const e=await lab.loadEOS(version),rows=[];
            for(const target of targets){
              const a=e.evaluate({mode:'PH',args:target.args},{extras:true}),[p,h]=target.args,analytic=a.rhoP-a.rhoT*a.hp/a.cp;
              for(const dp of [.003,.01,.03,.1,.3,1.,3.]){
                const b=e.evaluate({mode:'PH',args:[p+dp,h]});
                const ha=e.module.PropsSI('Hmass','Dmass',a.rho,'T',a.T,'HEOS::Ammonia'),hb=e.module.PropsSI('Hmass','Dmass',b.rho,'T',b.T,'HEOS::Ammonia');
                rows.push({target:target.name,args:target.args,pressureStepPa:dp,analyticRhoPAtH:analytic,finiteRhoPAtH:(b.rho-a.rho)/dp,base:a,perturbed:b,baseUnderlyingHResidualJkg:ha-h,perturbedUnderlyingHResidualJkg:hb-h});
              }
            }
            builds.push({version,rows});e.dispose();
          }
          return {builds,noSolverPerturbationChanged:true,reason:'Investigate observed native flash convergence sensitivity at the existing low-pressure finite-difference step; larger steps are diagnostics, not adopted solver settings.'};
        },inputs));await context.close();
      }else if(step==='interior-patterns'){
        const {context,page}=await pageReady(browser,base);const engine=fs.readFileSync(path.join(R,'engine.js'),'utf8'),table=JSON.parse(fs.readFileSync(path.join(R,'properties.json')));
        Object.assign(report,await page.evaluate(async({inputs,engine,table})=>{
          const m={exports:{}};new Function('module','exports',engine)(m,m.exports);const old=m.exports.createEngine(table),e=await lab.loadEOS('8.0.0'),cache=lab.exactCache(e);
          const tableEval=q=>{const [a,b]=q.args;let s;if(q.mode==='SAT'){const r=old.sat(a/1e5);return {p:a,T:r.T+273.15,hf:r.hf*1000,hg:r.hg*1000,sf:r.sf*1000,sg:r.sg*1000,rhof:r.rhof,rhog:r.rhog};}
            if(q.mode==='PH')s=old.ph(a/1e5,b/1000);else s=old.stateDU(a,b/1000);return {p:s.p*1e5,T:s.T+273.15,h:s.h*1000,rho:s.rho,u:s.h*1000-s.p*1e5/s.rho,Q:s.x};};
          const rounds=[];
          function iteration(n,region,method){
            const id={liquid:'p32.65314902038559-liquid-z0.1',vapor:'p3.5-vapor-z25.0','two-phase':'p3.5-Q0.2'}[region],seed=inputs.states.find(r=>r.id===id).state;
            const fn=method==='table'?tableEval:method==='cached-state8'?q=>cache.evaluate(q):q=>e.evaluate(q),stage=new Map();cache.clear();let calls=0,checksum=0;
            const v=Array.from({length:n},(_,i)=>({mode:'PH',args:[seed.p+i*10,seed.h+i]})),vectors=[v];
            for(let i=0;i<n;i++)for(let k=0;k<2;k++)vectors.push(v.map((q,j)=>j===i?{mode:'PH',args:q.args.map((x,b)=>b===k?x+(k===0?1e-7*Math.max(1,x/1e5)*1e5:1e-8*Math.max(1,x/1000)*1000):x)}:q));
            for(let i=0;i<2*n+1;i++)vectors.push(v);vectors.push(v.map(q=>({mode:'PH',args:[q.args[0]+.1,q.args[1]+.01]})));
            const boundaries=[{mode:'PH',args:[seed.p-1000,seed.h-100]},{mode:'PH',args:[seed.p+1000,seed.h+100]}];
            for(const vector of vectors){for(const q of vector){const key=q.args.join(':');let a=stage.get(key);if(!a){a=fn(q);stage.set(key,a);fn({mode:'SAT',args:[q.args[0],0]});calls+=2;}checksum+=a.rho;}
              for(const q of boundaries){fn(q);fn({mode:'SAT',args:[q.args[0],0]});calls+=2;}}
            for(const q of v){const a=fn(q);fn({mode:'DU',args:[a.rho,a.u]});fn({mode:'SAT',args:[a.p,0]});calls+=3;}
            return {calls,cache:cache.stats(),residualEvaluations:vectors.length,checksum,seedID:id};
          }
          for(const n of [5,9])for(const region of ['liquid','vapor','two-phase'])for(let round=0;round<3;round++)for(const method of round%2?['table','cached-state8','state8']:['state8','cached-state8','table']){
            const start=performance.now();let last;for(let j=0;j<10;j++)last=iteration(n,region,method);rounds.push({n,region,round,method,repeats:10,elapsedMS:performance.now()-start,...last});
          }
          e.dispose();return {rounds,meaning:'Interior liquid 0.1 K subcooling, vapor 25 K superheat, Q=0.2; independent boundary PH pairs; original stage cache represented; 10 iteration patterns per timing round. No coupled run.'};
        },{inputs,engine,table}));await context.close();
      }else if(step==='legacy-high-level'){
        const {context,page}=await pageReady(browser,base);Object.assign(report,await page.evaluate(async(inputs)=>{
          const e=await lab.loadEOS('7.2.0'),timings=[],groups=[{name:'PH-liquid',q:inputs.requests.find(q=>q.id==='p3.5-liquid-z1.0-PH')},{name:'DU-liquid',q:inputs.requests.find(q=>q.id==='historical-low-original-inventory')},{name:'SAT',q:{mode:'SAT',args:[350000,0]}}];
          for(const {name,q}of groups)for(let round=0;round<3;round++){e.evaluate(q);const t=performance.now();let calls=0,checksum=0;do{const a=e.evaluate(q);checksum+=a.rho||a.rhof;calls++;}while(performance.now()-t<150);timings.push({group:name,round,calls,elapsedMS:performance.now()-t,checksum});}
          const out={init:e.init,timings,linearMemoryFinal:e.memory(),scope:'Official 7.2.0 scalar PropsSI fallback, seven result fields; selected historical/representative inputs. No AbstractState binding enhancement built.'};e.dispose();return out;
        },inputs));await context.close();
      }else if(step==='worker'){
        const {context,page}=await pageReady(browser,base);Object.assign(report,await page.evaluate(async(inputs)=>{
          const w=new Worker('./worker.mjs',{type:'module'});let id=0;const pending=new Map();w.onmessage=({data})=>{const p=pending.get(data.id);pending.delete(data.id);data.error?p.reject(Error(data.error)):p.resolve(data.result);};
          const call=d=>new Promise((resolve,reject)=>{const i=++id;pending.set(i,{resolve,reject});w.postMessage({id:i,...d});});
          const start=performance.now(),init=await call({command:'init',version:'8.0.0'});const startupRoundtripMS=performance.now()-start;
          const requests=inputs.requests.filter(q=>['PH','DU'].includes(q.mode)&&q.region==='liquid').slice(0,12);let ticks=0;const timer=setInterval(()=>ticks++,20);
          const t=performance.now(),work=await call({command:'sustain',requests,durationMS:1800});const elapsed=performance.now()-t;clearInterval(timer);
          const probe=await call({command:'batch',requests:[{mode:'DU',args:[708.6710262223568,94480.59153610271]}]});
          await call({command:'dispose'});w.terminate();return {init,startupRoundtripMS,work,mainThreadTicks:ticks,mainThreadElapsedMS:elapsed,historicalProbe:probe,userAgent:navigator.userAgent};
        },inputs));report.processMemory=rssTree(bs.process().pid);await context.close();
      }else if(step==='deployment'||step==='offline-server-disabled'){
        const {context,page}=await pageReady(browser,base);Object.assign(report,await page.evaluate(async()=>{
          const bad=await lab.loadEOS('8.0.0',{badMime:true});const mimeFallback={init:bad.init,state:bad.evaluate({mode:'DU',args:[708.6710262223568,94480.59153610271]})};bad.dispose();let missing;
          try{await lab.loadEOS('8.0.0',{wasmURL:'./missing.wasm'});}catch(e){missing=e.message;}
          const registration=await navigator.serviceWorker.register('./sw.js',{scope:'./'});await navigator.serviceWorker.ready;
          if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));
          const cache=await caches.open('ammonia-eos-research-8.0.0-v1');const names=(await cache.keys()).map(r=>new URL(r.url).pathname);return {mimeFallback,missingAssetError:missing,serviceWorkerScope:registration.scope,cachedURLs:names};
        }));
        serverUnavailable=true;blockedRequests=0;
        try{await page.reload();await page.waitForFunction(()=>!!window.lab);}catch(e){report.offlineReloadError=e.message;save(file,report);throw e;}
        report.offline=await page.evaluate(async()=>{const e=await lab.loadEOS('8.0.0');const q=e.evaluate({mode:'DU',args:[708.6710262223568,94480.59153610271]});const r={init:e.init,state:q,online:navigator.onLine};e.dispose();return r;});
        report.offlineVerification={serverUnavailableDuringReloadAndEOSLoad:true,HTTPRequestsRejectedByServer:blockedRequests,networkEmulationUsed:false,navigatorOnLineIsNotAnOfflineProof:true};serverUnavailable=false;
        await page.evaluate(async()=>{for(const r of await navigator.serviceWorker.getRegistrations())await r.unregister();await caches.delete('ammonia-eos-research-8.0.0-v1');});await context.close();
      }
      save(file,report);console.log('Saved',file);
    }}catch(e){save(name+'-unfinished-failure.json',{message:e.message,stack:e.stack});throw e;}finally{await browser?.close();await bs?.close();}
  }}finally{await new Promise(resolve=>server.close(resolve));}
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
