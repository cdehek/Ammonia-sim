import {loadEOS,loadQualifiedEOS} from './loader.mjs';
import {step,originalSequences,lifecycle,javascriptPaths} from '../browser_eos_b6/lifecycle.mjs';
import {pack,bits} from '../browser_eos_b5b_c1/adapter.mjs';
import {call,ledger} from './matrix.mjs';
import {run as focused} from '../browser_eos_b4a/browser.mjs';
import {compatibility} from './compatibility.mjs';
import {workers} from './workers.mjs';
import {c1 as originalC1A2} from '../browser_eos_b6/science.mjs';
import {performanceSamples} from './performance.mjs';
const read=async path=>await(await fetch(new URL(path,import.meta.url))).json();
const ok=(v,m)=>{if(!v)throw Error(m);};
export async function run({engine,stage}){
 const artifacts=await read('./evidence/artifacts-with-diagnostics.json');
 const fixtures=(await read('../browser_eos_b6/evidence/historical-rejected-pt.json')).filter(r=>r.engine===engine);
 const choose=(id,extra={})=>(_legacy,options={})=>loadQualifiedEOS(artifacts[id],{...extra,...options});
 if(stage==='abi'){
  const rows=[];
  for(const id of ['rebuiltB4C','gateA','diagnosticB4C','diagnosticGateA']){
   const options={events:[]},e=await loadQualifiedEOS(artifacts[id],options),operations=[],baseline=options.runtimeStatus();
   try{
    for(let i=0;i<16;i++){
     const rejection=step(e,fixtures[i%fixtures.length].request,{expectReject:true,candidate:true,events:options.events});
     const status=options.runtimeStatus();ok(status.uncaught===baseline.uncaught&&status.observedCatchDepth===baseline.observedCatchDepth,'native bookkeeping baseline');
     const supported=step(e,{mode:'PT',args:[350000,300]},{candidate:true,events:options.events});operations.push({i,rejection,status,supported});
    }
    const high=step(e,fixtures[0].request,{candidate:true,expectReject:true,highLevel:true,events:options.events});
    rows.push({id,identity:artifacts[id],baseline,after:options.runtimeStatus(),operations,high,events:options.events,init:e.init,capabilities:e.capabilities});
   }finally{e.dispose();}
  }
  return {rows,passed:true};
 }
 if(stage==='activation'){
  const inputs=await read('./evidence/fixed-inputs.json'),keys=[146,148,151,152,162,164,165].map(n=>'native-ledger-'+n),rows=[];
  const seven=keys.map(key=>inputs.find(r=>r.key===key));ok(seven.every(Boolean),'seven fixed identities');
  for(const [base,diagnostic]of [['rebuiltB4C','diagnosticB4C'],['gateA','diagnosticGateA']])for(const fullVLE of [false,true]){
   const normal=await loadQualifiedEOS(artifacts[base],{fullVLE}),traced=await loadQualifiedEOS(artifacts[diagnostic],{fullVLE,trace:true}),off=await loadQualifiedEOS(artifacts[diagnostic],{fullVLE});
   try{
    rows.push({base,diagnostic,fullVLE,normal:ledger(normal,seven),loggingOn:ledger(traced,seven),loggingOff:ledger(off,seven),environment:traced.environmentObservations,normalEnvironment:normal.environmentObservations});
   }finally{normal.dispose();traced.dispose();off.dispose();}
  }
  return {rows,qualificationDecision:'Requires independent activation/cache/parity audit before main matrix'};
 }
 if(stage==='ledger'){
  const inputs=await read('./evidence/fixed-inputs.json'),additional=(await read('./evidence/additional-inputs.json')).rows,rows=[];
  ok(inputs.length===250,'250 original records');ok(new Set(inputs.map(r=>r.input.bits.rho+':'+r.input.bits.u)).size===73,'73 original pairs');
  for(const id of ['rebuiltB4C','gateA'])for(const fullVLE of [false,true]){
   const e=await loadQualifiedEOS(artifacts[id],{fullVLE});
   try{
    const saved=additional.map(r=>({key:r.failureKey,id:r.failureKey,origin:r.origin,input:{values:r.input,bits:r.bits}}));
    rows.push({id,identity:artifacts[id],fullVLE,init:e.init,environment:e.environmentObservations,records:ledger(e,inputs),additional:ledger(e,saved),memory:e.memory()});
   }finally{e.dispose();}
  }
  return {rows,originalRecords:250,originalPairs:73,additionalIndependentInventories:21,scope:'Actual results; physical qualification is decided by independent audit'};
 }
 if(stage==='regressions'){
  const references=(await read('../browser_eos_b4c/evidence/native-candidateB.json')).rows,requests=references.map(r=>r.request),historical=(await read('../browser_eos_b3/evidence/chromium-build44.json')).rows;
  const text=await(await fetch(new URL('../../../engine.js',import.meta.url))).text(),mod={exports:{}};new Function('module','exports',text)(mod,mod.exports);
  const guard=mod.exports.createEngine(await read('../../../properties.json')),rows=[];
  for(const id of ['rebuiltB4C','gateA'])for(const fullVLE of [false,true]){
   const e=await loadQualifiedEOS(artifacts[id],{fullVLE});
   try{rows.push({id,fullVLE,init:e.init,result:focused(e,requests,references,historical,guard)});}finally{e.dispose();}
  }
  return {rows,originalBaseFixtures:86,originalSignedProbes:344,noSignedStepChange:true,scope:'Original B4A/B4C focused harness, preserved phase/endpoint exclusions'};
 }
 if(stage==='shared'){
  const rows=[];
  for(const id of ['rebuiltB4C','gateA'])for(const fullVLE of [false,true]){
   const e=await loadQualifiedEOS(artifacts[id],{fullVLE}),cases=await read(`../browser_eos_b5a/evidence/shared-A1-${fullVLE?'full-vle':'default'}.json`),density=await read('../browser_eos_b5a/evidence/shared-density.json');
   try{
    const pressure=cases.rows.map(r=>({id:r.id,mode:r.mode,input:r.input,inputBits:r.inputBits})),dens=density.rows.filter(r=>r.fullVLE===fullVLE).map(r=>({id:r.fixture.id,mode:r.mode,input:r.input,inputBits:r.inputBits}));
    const results=[];
    for(const request of [...pressure,...dens]){
     ok(request.input.every((v,i)=>bits(v)===request.inputBits[i]),'shared exact input bits');
     results.push({...request,reused:call(e,{mode:request.mode,args:request.input}),fresh:call(e,{mode:request.mode,args:request.input},true)});
    }
    rows.push({id,fullVLE,pressureCases:pressure.length,densityCases:dens.length,results});
   }finally{e.dispose();}
  }
  return {rows,scope:'Original saved PH/PS/PU and DH/DS/DP inputs; exceptions remain explicit'};
 }
 if(stage==='c1')return compatibility(loadQualifiedEOS,artifacts,engine);
 if(stage==='workers')return workers(artifacts,engine);
 if(stage==='a2')return originalC1A2(choose('rebuiltB4C'),choose('gateA'),engine,fixtures[0]);
 if(stage==='performance')return performanceSamples(artifacts,engine);
 if(stage==='selection'){
  const {loadEOS:historical}=await import('../browser_eos_b6/loader.mjs');const a=await loadEOS(),b=await historical();
  const rows=[];
  try{for(const request of [{mode:'PT',args:[350000,300]},{mode:'PH',args:[799999.9981754856,1624022.744737779]},{mode:'PQ',args:[350000,.4]}]){
   const before=a.evaluate(request),after=b.evaluate(request);ok(JSON.stringify(before)===JSON.stringify(after),'historical controlA selection');rows.push({request,state:pack(before)});
  }}finally{a.dispose();b.dispose();}
  const errors=[];
  for(const identity of [undefined,{...artifacts.gateA,id:'unknown'},{...artifacts.gateA,jsSHA256:'0'.repeat(64)}]){
   let rejected=false;try{await loadQualifiedEOS(identity);}catch(error){rejected=true;errors.push(error.message);}ok(rejected,'qualification identity required');
  }
  return {passed:true,historicalDefaultControlAExact:true,qualificationRequiresExplicitVerifiedIdentity:true,rows,errors};
 }
 if(stage==='lifecycle'){
  const archive=await read(`../browser_eos_b4c/evidence/${engine}-candidateB-lifecycle.json`),rows=[];
  for(const id of ['rebuiltB4C','gateA']){
   const load=choose(id);rows.push({id,original:await originalSequences(load,archive,true),lifecycle:await lifecycle(load,fixtures,true),javascript:await javascriptPaths(load,fixtures[0])});
  }
  return {rows,passed:true};
 }
 throw Error('Unknown B7 stage '+stage);
}
