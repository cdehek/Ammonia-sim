import {loadEOS as candidate} from './candidate-diagnostic.mjs';
import {loadEOS as control} from './control-diagnostic.mjs';
import {step} from './lifecycle.mjs';
export async function run(){const fixtures=await(await fetch(new URL('./evidence/historical-rejected-pt.json',import.meta.url))).json(),rows=[];
 for(const [name,load]of [['control',control],['candidate',candidate]]){const opts={events:[]},e=await load('candidateB',opts),operations=[];const before=opts.runtimeStatus();try{
  for(let i=0;i<16;i++){const rejection=step(e,fixtures[i%2?3:0].request,{candidate:name==='candidate',expectReject:true,events:opts.events}),status=opts.runtimeStatus(),supported=step(e,{mode:'PT',args:[350000,300]},{candidate:name==='candidate',events:opts.events});operations.push({i,rejection,status,supported});}
  const high=step(e,fixtures[0].request,{candidate:name==='candidate',expectReject:true,highLevel:true,events:opts.events});rows.push({name,before,after:opts.runtimeStatus(),operations,high,events:opts.events});
 }finally{e.dispose();}}
 return {rows};
}
