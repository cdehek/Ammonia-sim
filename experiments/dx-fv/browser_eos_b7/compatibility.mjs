import {createAdapter,errorJSON,pack,bits} from '../browser_eos_b5b_c1/adapter.mjs';
const read=async path=>await(await fetch(new URL(path,import.meta.url))).json();
const ok=(v,m)=>{if(!v)throw Error(m);};
export async function compatibility(load,artifacts,engine){
 const mod={exports:{}};new Function('module','exports',await(await fetch(new URL('../../../engine.js',import.meta.url))).text())(mod,mod.exports);
 const guard=mod.exports.createEngine(await read('../../../properties.json'));
 const failures=(await read('./evidence/original-failures.json')).rows.filter(r=>r.runtime===engine),inputs=await read('./evidence/fixed-inputs.json'),historical=await read(`../browser_eos_b6/evidence/c1-original-${engine}-subset.json`),rows=[];
 for(const id of ['rebuiltB4C','gateA'])for(const fullVLE of [false,true]){
  const e=await load(artifacts[id],{fullVLE}),adapter=createAdapter(e,guard),cases=[];
  try{
   for(const f of failures){
    const x=f.fixedInput.values,request={mode:'DU',args:[x.rho,x.u]};let raw,rawError,state,error;
    try{raw=pack(e.evaluate(request));}catch(z){rawError=errorJSON(z);}
    try{state=pack(adapter.stateMVU(x.M,x.V,x.U_kJ,35));}catch(z){error=errorJSON(z);}
    if(!fullVLE){ok(!state&&error&&error.faultKind==='solver','original seven default refusals');ok(JSON.stringify(error)===JSON.stringify(historical.rows.find(r=>r.key===f.fixedKey).error),'historical C1 classification/diagnostics');}
    if(error)ok(error.evidence.propertyFailure.physicalTrajectoryExit==='unproved','numerical refusal cannot prove physical exit');
    if(state)ok(state.values.p>=.3&&state.values.p<=35,'strict returned-state pressure guard');
    cases.push({key:f.fixedKey,input:f.fixedInput,raw,rawError,state,error,originalDefaultRefusalPreserved:!fullVLE&&!state,physicalQualification:'Unresolved original reference/phase contract; any full-VLE raw/adapter return is not a scientific success',exactVsRounded:'C2 distinguishes exact stored M/U/V mathematics from rounded DU mathematics; neither is inferred from raw pressure'});
   }
   const hazards=[];
   for(const r of inputs.filter(r=>['webkit-ledger-69','webkit-ledger-76'].includes(r.key))){
    const x=r.input.values;let raw,error,state;try{raw=pack(e.evaluate({mode:'DU',args:[x.rho,x.u]}));}catch(z){error=errorJSON(z);}
    try{state=pack(adapter.stateMVU(x.M,x.V,x.U_kJ,35));}catch(z){error=errorJSON(z);}
    hazards.push({key:r.key,input:r.input,raw,state,error,certified:false,qualificationBlocker:true});
   }
   const explicit=[];
   for(const pBar of [.29999999999999993,35.00000000000001]){
    let state,error;try{state=adapter.ph(pBar,1000);}catch(z){error=errorJSON(z);}
    ok(!state&&error,'original explicit support refusal');explicit.push({pBar,inputBits:bits(pBar),error,inputScope:'Actual original bar-based adapter interface; no Pa-to-bar inward rounding'});
   }
   rows.push({id,fullVLE,cases,hazards,explicit,strictGuardUnchanged:true,scope:fullVLE?'Additional isolated full-VLE diagnostic; retained returns are unqualified':'Original browser default interface and seven refusals'});
  }finally{e.dispose();}
 }
 return {rows,passed:true,fullGateBPassed:false,C1SourceUnchanged:true,fullA2Run:false};
}
