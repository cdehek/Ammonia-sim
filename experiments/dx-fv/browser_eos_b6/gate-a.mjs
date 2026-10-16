import {raw} from './observe.mjs';
import {lifecycle} from '../browser_eos_b4c/lifecycle.mjs';
export async function run(kind,cases,fixtures){
 const events=[],operations=[],created=[];
 const path=kind==='historical'?'../browser_eos_b4c/loader.mjs':'./control-diagnostic.mjs';
 const {loadEOS}=await import(path);const eos=await loadEOS('candidateB',{events});
 const call=eos.evaluate;eos.evaluate=(q,o)=>{const first=events.length,sp=eos.stackPointer(),memory=eos.memory();let row={request:q,options:o||{},before:{stack:sp,memory}};
 try{const value=call(q,o);row.value=value;return value;}catch(e){row.error=raw(e);throw e;}finally{row.after={stack:eos.stackPointer(),memory:eos.memory()};row.events=[first,events.length];operations.push(row);}};
 const factory=eos.module.factory;eos.module.factory=(...a)=>{const s=factory(...a);created.push(s);return s;};
 const before={stack:eos.stackPointer(),memory:eos.memory()};const result=lifecycle(eos,cases);const after={stack:eos.stackPointer(),memory:eos.memory()};
 const deleted=created.map(s=>s.isDeleted());eos.dispose();
 // Separate interface comparison; never contaminate historical operation order.
 const interfaces=[];
 for(const f of fixtures.filter((v,i,a)=>a.findIndex(w=>w.row===v.row)===i)){
  for(const highLevel of [false,true]){
   const trace=[];const e=await loadEOS('candidateB',{events:trace});const pre={stack:e.stackPointer(),memory:e.memory()};let error,value,recovery;
   try{value=e.evaluate(f.request,{highLevel});}catch(x){error=raw(x);}
   const rejectedAfter={stack:e.stackPointer(),memory:e.memory()};
   try{recovery=e.evaluate({mode:'PH',args:f.fixture.args});}catch(x){recovery={error:raw(x)};}
   const recoveredAfter={stack:e.stackPointer(),memory:e.memory()};e.dispose();interfaces.push({fixture:f.fixture.id,request:f.request,inputBits:f.inputBits,highLevel,pre,error,value,rejectedAfter,recovery,recoveredAfter,trace,deleted:e.state.isDeleted()});
  }
 }
 return {kind,result,operations,events,before,after,created:created.length,temporaryDeleted:deleted,primaryDeleted:eos.state.isDeleted(),interfaces,capabilities:eos.capabilities};
}
