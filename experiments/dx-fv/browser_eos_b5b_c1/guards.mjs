import {createAdapter,errorJSON,pack} from './adapter.mjs';
import {createAdapter as historicalAdapter} from '../browser_eos_backend/adapter.mjs';
import {loadEOS} from '../browser_eos_b4c/loader.mjs';
export async function run({engine,table}){
 const m={exports:{}};new Function('module','exports',engine)(m,m.exports);const guard=m.exports.createEngine(table),eos=await loadEOS('candidateB'),rows=[];
 const capture=f=>{try{return {state:pack(f())};}catch(e){return {error:errorJSON(e)};}};
 try{
  for(const p of [.3,.29999999999999993,35,35.00000000000001]){
   const control=capture(()=>historicalAdapter(eos,guard).sat(p)),candidate=capture(()=>createAdapter(eos,guard).sat(p));
   if(!!control.state!==!!candidate.state)throw Error('guard outcome changed');
   if(candidate.error&&(candidate.error.faultKind!=='domain'||candidate.error.evidence.propertyFailure.reason!=='explicit-unsupported-input'))throw Error('input refusal semantics');
   rows.push({kind:'sat-input',p,control,candidate});
  }
  for(const T of [195.494,345.5636735993518-30-.001,345.5636735993518+250+.001]){
   const fake={evaluate:q=>q.mode==='DU'?{p:3500000,h:1100000,rho:100,u:1000000,T,s:3000,Q:-1}:eos.evaluate(q)};
   const control=capture(()=>historicalAdapter(fake,guard).stateMVU(1,.01,1000,35)),candidate=capture(()=>createAdapter(fake,guard).stateMVU(1,.01,1000,35));
   if(control.state||candidate.state||candidate.error.evidence.propertyFailure.reason!=='boundary-unresolved'||candidate.error.evidence.propertyFailure.physicalTrajectoryExit!=='unproved')throw Error('temperature refusal changed');
   rows.push({kind:'synthetic-temperature-guard-isolation',T,control,candidate});
  }
  // Actual browser loader finite-input refusal exercises numerical metadata
  // without entering the inherited rejected-PT C++ cleanup path.
  const control=capture(()=>historicalAdapter(eos,guard).stateMVU(Infinity,.01,1000,35)),candidate=capture(()=>createAdapter(eos,guard).stateMVU(Infinity,.01,1000,35));
  if(candidate.state||candidate.error.evidence.propertyFailure.reason!=='inverse-recovery-failure')throw Error('loader refusal lost');rows.push({kind:'loader-nonfinite-refusal',control,candidate});
  return {passed:true,rows};
 }finally{eos.dispose();}
}
