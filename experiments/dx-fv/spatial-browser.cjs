'use strict';
// Synthetic isolated numerical benchmark. No application or UI file is loaded.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium,webkit}=require('playwright');
const root=path.resolve(__dirname,'../..'),sources={};
for(const file of ['engine.js',...['conservation','thermodynamics','hydraulics','implicit','time-control','evaporator','spatial-fixtures','spatial-observables','spatial-runner'].map(v=>'experiments/dx-fv/'+v+'.cjs')])sources[file.replace(/\.(?:cjs|js)$/,'')]=fs.readFileSync(path.join(root,file),'utf8');
sources['properties.json']='module.exports='+fs.readFileSync(path.join(root,'properties.json'),'utf8');
const report={meshes:[3,5],method:'adaptive tr-bdf2 1e-6',kind:'Synthetic desktop browser; not physical iPad',browsers:[]};
(async()=>{
 for(const [name,type]of [['chromium',chromium],['webkit',webkit]].filter(([name])=>!process.env.DX_FV_BROWSERS||process.env.DX_FV_BROWSERS.split(',').includes(name))){
  const browser=await type.launch({headless:true});try{
   const page=await browser.newPage();await page.evaluate(sources=>{
    const cache={};function load(id){if(cache[id])return cache[id].exports;const module={exports:{}};cache[id]=module;
     const require=ref=>{const parts=(ref.startsWith('.')?id.split('/').slice(0,-1).join('/')+'/'+ref:ref).split('/'),clean=[];for(const part of parts){if(part==='..')clean.pop();else if(part&&part!=='.')clean.push(part);}return load(clean.join('/').replace(/\.(?:cjs|js)$/,''));};
     if(!sources[id])throw Error('Unknown benchmark module '+id);new Function('module','exports','require',sources[id])(module,module.exports,require);return module.exports;
    }window.dxSpatial={engine:load('engine').createEngine(load('properties.json')),create:load('experiments/dx-fv/evaporator').createEvaporator,fixtures:load('experiments/dx-fv/spatial-fixtures'),observables:load('experiments/dx-fv/spatial-observables')};
   },sources);
   const rows=await page.evaluate(()=>{
    const {engine,create,fixtures,observables}=window.dxSpatial,result={coldRepeats:[],hours:[],warm:[]};
    const observe=(model,state)=>observables.observe(model.record(state),state.spec,engine);
    for(const n of [3,5]){const model=create(engine,fixtures.numericalOptions(1e-6));model.advance(model.create(fixtures.fixture(n)),.1);}
    for(let repeat=0;repeat<3;repeat++)for(const n of repeat%2?[5,3]:[3,5]){
     const model=create(engine,fixtures.numericalOptions(1e-6)),state=model.create(fixtures.fixture(n));let total=0,longest=0;
     for(let i=0;i<50;i++){const start=performance.now();model.advance(state,.1);const ms=performance.now()-start;total+=ms;longest=Math.max(longest,ms);}
     const row=observe(model,state);result.coldRepeats.push({sectionCount:n,repeat,elapsedMS:total,longestCallMS:longest,steps:row.steps,rejected:row.rejected,calls:row.calls,iterations:row.iterations,terminal:row.terminal,terminalEvents:row.terminalEvents,stop:row.stop,massResidualKg:row.massResidualKg,energyResidualKJ:row.energyResidualKJ});
    }
    for(const totalHeatKW of [12,18])for(const n of [3,5]){
     const model=create(engine,fixtures.numericalOptions(1e-6)),state=model.create(fixtures.fixture(n,{totalHeatKW})),start=performance.now();model.advance(state,3600);const ms=performance.now()-start,row=observe(model,state);
     result.hours.push({sectionCount:n,totalHeatKW,elapsedMS:ms,steps:row.steps,rejected:row.rejected,calls:row.calls,iterations:row.iterations,terminal:row.terminal,totals:row.totals,stop:row.stop,massResidualKg:row.massResidualKg,energyResidualKJ:row.energyResidualKJ});
    }
    for(const n of [3,5]){
     const model=create(engine,fixtures.numericalOptions(1e-6)),state=model.create(fixtures.cases(n)[0].config),start=performance.now();model.advance(state,2);const ms=performance.now()-start,row=observe(model,state);
     result.warm.push({sectionCount:n,seconds:row.seconds,elapsedMS:ms,terminal:row.terminal,stop:row.stop,massResidualKg:row.massResidualKg,energyResidualKJ:row.energyResidualKJ});
    }
    return result;
   });
   for(const r of [...rows.coldRepeats,...rows.hours,...rows.warm]){if(rows.warm.includes(r)&&r.sectionCount===5){assert.equal(r.stop?.kind,'domain');assert(r.terminal.superheatK>249.99);}else assert(!r.stop,JSON.stringify(r.stop));assert(Math.abs(r.massResidualKg)<1e-8);assert(Math.abs(r.energyResidualKJ)<1e-6);}
   const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
   const summary=[3,5].map(n=>({sectionCount:n,medianColdElapsedMS:median(rows.coldRepeats.filter(v=>v.sectionCount===n).map(v=>v.elapsedMS)),medianLongestCallMS:median(rows.coldRepeats.filter(v=>v.sectionCount===n).map(v=>v.longestCallMS)),maximumCallMS:Math.max(...rows.coldRepeats.filter(v=>v.sectionCount===n).map(v=>v.longestCallMS))}));
   report.browsers.push({name,version:browser.version(),...rows,summary,coldFiveToThreeRatio:summary[1].medianColdElapsedMS/summary[0].medianColdElapsedMS});
  }finally{await browser.close();}
 }
 report.passed=true;report.verificationMeaning='Expected five-section warm EOS-domain limit is verified separately from successful cold/hour operation.';
 if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
