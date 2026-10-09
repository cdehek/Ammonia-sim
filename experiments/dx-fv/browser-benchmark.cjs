'use strict';
// Synthetic browser execution of the isolated modules, with no app/UI imports.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium,webkit}=require('playwright');
const root=path.resolve(__dirname,'../..'),sources={};
for(const file of ['engine.js','experiments/dx-fv/conservation.cjs','experiments/dx-fv/thermodynamics.cjs','experiments/dx-fv/hydraulics.cjs','experiments/dx-fv/implicit.cjs','experiments/dx-fv/time-control.cjs','experiments/dx-fv/evaporator.cjs'])sources[file.replace(/\.(?:cjs|js)$/,'')]=fs.readFileSync(path.join(root,file),'utf8');
sources['properties.json']='module.exports='+fs.readFileSync(path.join(root,'properties.json'),'utf8');
const results={sectionCount:3,kind:'Synthetic desktop headless browser; not physical iPad',browsers:[]};
(async()=>{
 for(const [name,type]of [['chromium',chromium],['webkit',webkit]].filter(([name])=>!process.env.DX_FV_BROWSERS||process.env.DX_FV_BROWSERS.split(',').includes(name))){
  const browser=await type.launch({headless:true});try{
   const page=await browser.newPage();
   await page.evaluate(sources=>{
    const cache={};function load(id){if(cache[id])return cache[id].exports;const module={exports:{}};cache[id]=module;
     const require=ref=>{const parts=(ref.startsWith('.')?id.split('/').slice(0,-1).join('/')+'/'+ref:ref).split('/'),clean=[];for(const part of parts){if(part==='..')clean.pop();else if(part&&part!=='.')clean.push(part);}return load(clean.join('/').replace(/\.(?:cjs|js)$/,''));};
     if(!sources[id])throw Error('Unknown benchmark module '+id);new Function('module','exports','require',sources[id])(module,module.exports,require);return module.exports;
    }window.dxBenchmark={engine:load('engine').createEngine(load('properties.json')),create:load('experiments/dx-fv/evaporator').createEvaporator};
   },sources);
   const rows=await page.evaluate(()=>{
    const {engine,create}=window.dxBenchmark,rows=[];
    const config=q=>({sectionCount:3,inletMinorK:1000,inlet:{p:4,h:500},outlet:{p:3.5,h:1700},initial:[{p:3.9,h:1000},{p:3.8,h:1400},{p:3.65,h:1650}],heatKW:q});
    const options={method:'tr-bdf2',adaptive:true,relativeTolerance:1e-6,massAbsoluteKg:1e-11,energyAbsoluteKJ:1e-8,pressureAbsoluteBar:1e-6,enthalpyAbsoluteKJkg:1e-4,minStep:1e-9};
    // Warm the same module path before timing. No CPU throttling extrapolation.
    const warm=create(engine,options);warm.advance(warm.create(config([4,4,4])),1);
    for(const [name,seconds,q]of [['startup',1,[4,4,4]],['one-hour dry',3600,[6,6,6]],['one-hour wet',3600,[4,4,4]]]){
     const model=create(engine,options),state=model.create(config(q)),start=performance.now(),r=model.advance(state,seconds);
     rows.push({name,seconds,elapsedMS:performance.now()-start,terminal:r.terminal,massResidualKg:r.massResidualKg,energyResidualKJ:r.energyResidualKJ,calls:r.attemptedResidualEvaluations,steps:r.acceptedSteps,rejected:r.rejectedSteps,stop:r.stop});
    }
    // Largest synchronous chunk while advancing a cold transient in 0.1 s calls.
    const model=create(engine,options),cold=config([6,6,6]);cold.initial=[{p:3.55,h:500},{p:3.53,h:500},{p:3.51,h:500}];const state=model.create(cold);let longest=0,total=0;
    for(let i=0;i<50;i++){const start=performance.now();model.advance(state,.1);const elapsed=performance.now()-start;longest=Math.max(longest,elapsed);total+=elapsed;}
    rows.push({name:'cold startup in 0.1 s batches',seconds:state.seconds,elapsedMS:total,longestSynchronousCallMS:longest,stop:state.stop});return rows;
   });
   rows.forEach(r=>{assert(!r.stop,JSON.stringify(r.stop));if(r.massResidualKg!==undefined){assert(Math.abs(r.massResidualKg)<1e-8);assert(Math.abs(r.energyResidualKJ)<1e-6);}});
   results.browsers.push({name,version:browser.version(),rows});
  }finally{await browser.close();}
 }
 results.passed=true;if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results,null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
