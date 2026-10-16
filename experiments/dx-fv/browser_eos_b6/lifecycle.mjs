import {raw} from './observe.mjs';
import {pack,bits} from '../browser_eos_b5b_c1/adapter.mjs';
const ok=(v,m)=>{if(!v)throw Error(m);};
const equal=(a,b,m)=>ok(JSON.stringify(a)===JSON.stringify(b),m);
const q=(mode,...args)=>({mode,args});
function error(e){return {...raw(e),nativeException:e.nativeException??null};}
function freshSupported(eos,request){
 const m=eos.module,s=m.factory('HEOS','Ammonia');
 try{const [a,b]=request.args;const pairs={PT:['PT_INPUTS',a,b],PH:['HmassP_INPUTS',b,a],DU:['DmassUmass_INPUTS',a,b],PQ:['PQ_INPUTS',a,b]};const [key,x,y]=pairs[request.mode];s.update(m.input_pairs[key],x,y);return {p:s.p(),T:s.T(),h:s.hmass(),s:s.smass(),rho:s.rhomass(),u:s.umass(),Q:s.Q()};}
 finally{s.delete();ok(s.isDeleted(),'fresh state deletion');}
}
export function step(eos,request,{expectReject=false,candidate=false,events=null,highLevel=false,synthetic=false}={}){
 const index=events?.length??0,out={request:{mode:request.mode,args:request.args,inputBits:request.args.map(bits)},expectReject,highLevel,synthetic,phaseImposition:false,before:{stack:eos.stackPointer(),memory:eos.memory()}};
 try{out.value=pack(eos.evaluate(request,{highLevel}));}
 catch(e){out.error=error(e);}
 if(out.value){
  ok(!expectReject,'invalid request accepted');
  if(!synthetic&&!highLevel&&['PT','PH','DU','PQ'].includes(request.mode)){out.fresh=pack(freshSupported(eos,request));equal(out.value,out.fresh,'fresh/reused supported property bits');}
 }else if(candidate){ok(expectReject,'unexpected candidate failure: '+out.error?.string);ok(!out.error?.string.includes('Assertion failed'),'candidate cleanup assertion');}
 out.after={stack:eos.stackPointer(),memory:eos.memory()};out.events=[index,events?.length??0];
 if(candidate)equal(out.before.stack,out.after.stack,'candidate stack restored');
 return out;
}
export async function lifecycle(load,fixtures,candidate){
 const e=await load('candidateB'),rows=[];const basePT=q('PT',350000,300),liquid=q('PT',350000,250),vapor=q('PT',350000,300),pq=q('PQ',350000,.4);
 const ph=q('PH',799999.9981754856,1624022.744737779),s=e.evaluate(ph),du=q('DU',s.rho,s.u),reject=fixtures[0].request;
 const bad=q('PT',-100000,300),nf=q('PT',Infinity,300);
 const seqs=[
 ['valid-valid',[basePT,vapor]],['valid-rejected-valid',[basePT,reject,basePT]],['rejected-valid',[reject,basePT]],
 ['rejected-rejected-valid',[reject,reject,basePT]],['alternating',[reject,basePT,reject,basePT,reject,basePT]],
 ['PH-rejected-PH',[ph,reject,ph]],['PT-DU-rejected-PT',[basePT,du,reject,basePT]],['PQ-rejected-PQ',[pq,reject,pq]],
 ['liquid-rejected-vapor',[liquid,reject,vapor]],['vapor-rejected-liquid',[vapor,reject,liquid]],
 ['nonfinite-input',[basePT,nf,basePT]],['unsupported-pressure',[basePT,bad,basePT]],
 ['low-high-supported',[basePT,basePT]],['factory-disposal',[basePT]],['worker-rejection-recovery',[reject,basePT]],
 ['bounded-alternation',Array.from({length:128},()=>[reject,basePT]).flat()]
 ];
 try{
  const warmup=step(e,basePT,{candidate});
  for(const [name,requests]of seqs){
   for(const fresh of [false,true]){
    const a=fresh?await load('candidateB'):e,operations=[];const before=a.memory();
    try{for(let i=0;i<requests.length;i++){
     const r=requests[i];operations.push(step(a,r,{candidate,expectReject:r===reject||r===bad||r===nf,highLevel:name==='low-high-supported'&&i===1}));
    }}finally{if(fresh)a.dispose();}
    rows.push({name,fresh,prior:fresh?[]:['initial PH seed',warmup,...rows.filter(x=>!x.fresh).map(x=>x.name)],operations,deleted:fresh?a.state.isDeleted():null,memoryBefore:before,memoryAfter:a.memory()});
   }
  }
  const stateBeforeDispose=e.state.isDeleted();const before=e.memory();e.dispose();const deleted=e.state.isDeleted();let secondDelete,invalidReuse;
  try{e.dispose();}catch(x){secondDelete=error(x);}try{e.evaluate(basePT);}catch(x){invalidReuse=error(x);}
  ok(deleted&&secondDelete&&invalidReuse,'terminal delete contract');
  return {candidate,warmup,rows,stateBeforeDispose,deleted,secondDelete,invalidReuse,memoryBeforeDispose:before,memoryAfterDispose:e.memory()};
 }finally{if(!e.state.isDeleted())e.dispose();}
}
export async function originalSequences(load,archive,candidate,events=[]){
 const e=await load('candidateB',{events}),rows=[];
 try{for(const r of archive.rows){const operations=[];operations.push(step(e,{mode:'PH',args:r.request.args},{candidate}));
  for(const z of r.sequences)operations.push(step(e,{mode:z.mode,args:z.args},{candidate,expectReject:!!z.error,events}));
  rows.push({fixture:r.request,operations});}
  return {rows,events,memory:e.memory(),stack:e.stackPointer()};
 }finally{e.dispose();}
}
export async function javascriptPaths(load,fixture){
 const events=[],e=await load('candidateB',{events}),rows=[];
 try{
  rows.push(step(e,{mode:'PT',args:[NaN,300]},{candidate:true,expectReject:true,events}));
  rows.push(step(e,{mode:'PT',args:[-100000,300]},{candidate:true,expectReject:true,events}));
  rows.push(step(e,fixture.request,{candidate:true,expectReject:true,events,highLevel:true}));
  rows.push(step(e,{mode:'unknown',args:[350000,300]},{candidate:true,expectReject:true,events}));
  const saved=e.state.update;
  for(const injected of [new Error('Synthetic JS diagnostic'),123456,{excPtr:123456,message:'Synthetic excPtr lookalike'},Object.assign(new Error('Synthetic forged CppException'),{name:'CppException',excPtr:123456})]){
   e.state.update=()=>{throw injected;};rows.push(step(e,{mode:'PT',args:[350000,300]},{candidate:true,expectReject:true,events,synthetic:true}));e.state.update=saved;
   rows.push(step(e,{mode:'PT',args:[350000,300]},{candidate:true,events}));
  }
  // Explicit JS nonfinite-property rejection after a completed native update.
  const old=e.state.p;e.state.p=()=>Infinity;
  rows.push(step(e,{mode:'PT',args:[350000,300]},{candidate:true,expectReject:true,events,synthetic:true}));e.state.p=old;
  rows.push(step(e,{mode:'PT',args:[350000,300]},{candidate:true,events}));
  return {rows,events,syntheticErrorsAreNotCoolPropRefusals:true};
 }finally{e.dispose();}
}
