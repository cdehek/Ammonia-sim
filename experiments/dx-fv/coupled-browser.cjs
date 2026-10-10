'use strict';
// Numerical portability only; blank pages, no application or integration claim.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium,webkit}=require('playwright');
const root=path.resolve(__dirname,'../..'),sources={};
for(const file of ['engine.js',...['conservation','thermodynamics','hydraulics','implicit','time-control','evaporator','spatial-fixtures','thermal-network','thermal-geometry','coupled-implicit','coupled-model','coupled-fixtures'].map(v=>'experiments/dx-fv/'+v+'.cjs')])sources[file.replace(/\.(cjs|js)$/,'')]=fs.readFileSync(path.join(root,file),'utf8');
sources['properties.json']='module.exports='+fs.readFileSync(path.join(root,'properties.json'),'utf8');
const reference=JSON.parse(fs.readFileSync(process.env.DX_COUPLED_REFERENCE_PATH||path.join(__dirname,'coupled-reference.json'),'utf8'));
const report={stage:'2A',sectionCount:5,kind:'Synthetic desktop headless numerical portability; no UI/device/performance-integration qualification',browsers:[]};
(async()=>{
  for(const [name,type]of [['chromium',chromium],['webkit',webkit]]){
    const browser=await type.launch({headless:true});
    try{
      const page=await browser.newPage();
      await page.evaluate(sources=>{
        const cache={};
        function load(id){
          if(cache[id])return cache[id].exports;
          if(!sources[id])throw Error('Unknown coupled module '+id);
          const module={exports:{}};cache[id]=module;
          function require(ref){
            const input=(ref.startsWith('.')?id.split('/').slice(0,-1).join('/')+'/'+ref:ref).split('/'),clean=[];
            for(const part of input){if(part==='..')clean.pop();else if(part&&part!=='.')clean.push(part);}
            return load(clean.join('/').replace(/\.(cjs|js)$/,''));
          }
          new Function('module','exports','require',sources[id])(module,module.exports,require);return module.exports;
        }
        window.coupled={engine:load('engine').createEngine(load('properties.json')),create:load('experiments/dx-fv/coupled-model').createCoupledModel,cases:load('experiments/dx-fv/coupled-fixtures').cases};
      },sources);
      const rows=await page.evaluate(()=>{
        const {engine,create,cases}=window.coupled;
        return cases().map(c=>{
          const m=create(engine),s=m.create(c.config),rows=[];
          for(const t of c.samples){const r=m.advance(s,t-s.seconds);rows.push({seconds:r.seconds,stop:r.stop,sections:r.sections.map(v=>({p:v.p,h:v.h,T:v.T})),temperaturesK:r.nodes.map(v=>v.temperatureK),massResidualKg:r.massResidualKg,sectionMassResidualKg:Math.max(...r.sectionResiduals.map(v=>Math.abs(v.massKg))),sectionEnergyResidualKJ:Math.max(...r.sectionResiduals.map(v=>Math.abs(v.energyKJ))),nodeEnergyResidualKJ:Math.max(...r.nodes.map(v=>Math.abs(v.residualKJ))),refrigerantEnergyResidualKJ:r.refrigerantEnergyResidualKJ,thermalEnergyResidualKJ:r.thermalEnergyResidualKJ,combinedEnergyResidualKJ:r.combinedEnergyResidualKJ,terminal:r.terminal,outlet:r.outlet});if(r.stop)break;}
          return {name:c.name,rows,events:m.record(s).events,boundaryEvents:s.boundaryEvents};
        });
      });
      const errors={pressureBar:0,enthalpyKJkg:0,refrigerantTemperatureK:0,thermalTemperatureK:0,terminalEventSeconds:0};
      for(const c of rows){
        const ref=reference.cases.find(v=>v.name===c.name).runs[1];assert.equal(c.rows.length,ref.samples.length);
        c.rows.forEach((r,j)=>{
          const sample=ref.samples[j];assert.equal(r.stop,null);assert.equal(r.seconds,sample.seconds);
          for(const key of ['massResidualKg','sectionMassResidualKg'])assert.ok(Math.abs(r[key])<1e-8);
          for(const key of ['sectionEnergyResidualKJ','nodeEnergyResidualKJ','refrigerantEnergyResidualKJ','thermalEnergyResidualKJ','combinedEnergyResidualKJ'])assert.ok(Math.abs(r[key])<1e-6);
          r.sections.forEach((v,i)=>{const w=sample.sections[i];errors.pressureBar=Math.max(errors.pressureBar,Math.abs(v.p-w.p));errors.enthalpyKJkg=Math.max(errors.enthalpyKJkg,Math.abs(v.h-w.h));errors.refrigerantTemperatureK=Math.max(errors.refrigerantTemperatureK,Math.abs(v.T-w.T));});
          errors.thermalTemperatureK=Math.max(errors.thermalTemperatureK,...r.temperaturesK.map((v,i)=>Math.abs(v-sample.temperaturesK[i])));
        });
        const events=c.events.filter(v=>v.section===4&&v.boundary==='vapor');assert.equal(events.length,ref.terminalSaturationEventsSeconds.length);
        events.forEach((v,i)=>{errors.terminalEventSeconds=Math.max(errors.terminalEventSeconds,Math.abs(v.seconds-ref.terminalSaturationEventsSeconds[i]));});
        if(c.name.endsWith('step'))assert.deepEqual(c.boundaryEvents.map(v=>v.seconds),[15,30]);
      }
      assert.ok(errors.pressureBar<1e-4&&errors.enthalpyKJkg<.05&&errors.refrigerantTemperatureK<.01&&errors.thermalTemperatureK<.01&&errors.terminalEventSeconds<.001,JSON.stringify(errors));
      report.browsers.push({name,version:browser.version(),errors,cases:rows});
    }finally{await browser.close();}
  }
  report.passed=true;if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,browsers:report.browsers.map(v=>({name:v.name,version:v.version,errors:v.errors}))}));
})().catch(error=>{
  report.passed=false;report.failure={message:error.message,stack:error.stack};
  if(process.argv[2])fs.writeFileSync(process.argv[2]+'.failure.json',JSON.stringify(report,null,2)+'\n');
  console.error(error);process.exitCode=1;
});
