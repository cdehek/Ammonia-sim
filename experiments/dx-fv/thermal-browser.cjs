'use strict';
// Blank-page harness; standalone thermal modules only, no application imports.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium,webkit}=require('playwright');
const sources={};for(const file of ['implicit','time-control','thermal-network','thermal-geometry'])sources[file]=fs.readFileSync(path.join(__dirname,file+'.cjs'),'utf8');
const report={kind:'Synthetic desktop headless Chromium/WebKit; no device/main-thread integration claim',browsers:[]};
(async()=>{
 for(const [name,type]of [['chromium',chromium],['webkit',webkit]]){
  const browser=await type.launch({headless:true});
  try{
   const page=await browser.newPage();await page.evaluate(sources=>{
    const cache={};function load(id){id=id.replace(/^\.\//,'').replace(/\.cjs$/,'');if(cache[id])return cache[id].exports;if(!sources[id])throw Error('Unknown thermal module '+id);const module={exports:{}};cache[id]=module;new Function('module','exports','require',sources[id])(module,module.exports,load);return module.exports;}
    window.thermal={create:load('thermal-network').createIntegrator,config:load('thermal-geometry').createThermalConfig};
   },sources);
   const data=await page.evaluate(()=>{
    const {create,config}=window.thermal,rows=[],verification=[];
    for(const n of [5,9]){
     const warm=create();warm.advance(warm.create(config({sectionCount:n})),5);
     for(let repeat=0;repeat<3;repeat++){
      const I=create(),s=I.create(config({sectionCount:n}));let longest=0;const start=performance.now();
      for(let i=0;i<50;i++){const t=performance.now();I.advance(s,.1);longest=Math.max(longest,performance.now()-t);}
      const elapsedMS=performance.now()-start,r=I.record(s);
      rows.push({sections:n,repeat,elapsedMS,longestAdvanceMS:longest,linearSolves:r.attemptedLinearSolves,fluxEvaluations:r.attemptedFluxEvaluations,energyResidualKJ:r.energyResidualKJ,maxNodeResidualKJ:Math.max(...r.nodes.map(v=>Math.abs(v.residualKJ))),stop:r.stop});
     }
     const traces=[273.15,1e6].map(ref=>{const I=create({trace:true}),s=I.create(config({sectionCount:n,energyReferenceK:ref,airLoadKW:1,schedule:[{seconds:15,patch:{loadsKW:{air:2}}},{seconds:30,patch:{loadsKW:{air:1}}}]}));return I.advance(s,60);});
     const closed=create(),s=closed.create(config({sectionCount:n})),r=closed.advance(s,300);
     verification.push({sections:n,referenceTraceIdentical:JSON.stringify(traces[0].trace)===JSON.stringify(traces[1].trace)&&JSON.stringify(traces[0].rejectionTrace)===JSON.stringify(traces[1].rejectionTrace),referenceTemperaturesIdentical:JSON.stringify(traces[0].nodes.map(v=>v.temperatureK))===JSON.stringify(traces[1].nodes.map(v=>v.temperatureK)),exactLoadKJ:traces[0].ledger.externalKJ,scheduledTimes:traces[0].boundaryEvents.map(v=>v.seconds),equilibriumK:r.nodes.map(v=>v.temperatureK),closedResidualKJ:r.energyResidualKJ});
    }
    const I=create(),air=I.create({nodes:[{id:'air',capacityKJK:4.308,initialK:293.15}],loadsKW:{air:1}}),domain=I.advance(air,500);
    return {rows,verification,domain:{kind:domain.stop?.kind,seconds:domain.seconds,energyResidualKJ:domain.energyResidualKJ},sampledChromiumHeapBytes:performance.memory?.usedJSHeapSize??null};
   });
   for(const r of data.rows){assert.equal(r.stop,null);assert.ok(Math.abs(r.energyResidualKJ)<1e-6&&r.maxNodeResidualKJ<1e-6);}
   for(const v of data.verification){assert.ok(v.referenceTraceIdentical&&v.referenceTemperaturesIdentical);assert.ok(Math.abs(v.exactLoadKJ-75)<1e-8);assert.deepEqual(v.scheduledTimes,[15,30]);assert.ok(v.equilibriumK.every(t=>Math.abs(t-282.7312471906226)<.001));assert.ok(Math.abs(v.closedResidualKJ)<1e-6);}
   assert.equal(data.domain.kind,'domain');assert.ok(Math.abs(data.domain.seconds-460.3098)<1e-7);assert.ok(Math.abs(data.domain.energyResidualKJ)<1e-6);
   report.browsers.push({name,version:browser.version(),...data});
  }finally{await browser.close();}
 }
 report.passed=true;if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report.browsers.map(v=>({name:v.name,rows:v.rows}))));
})().catch(e=>{console.error(e);process.exitCode=1;});
