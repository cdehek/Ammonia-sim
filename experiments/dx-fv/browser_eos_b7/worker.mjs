import {loadQualifiedEOS} from './loader.mjs';
import {originalSequences,javascriptPaths,step} from '../browser_eos_b6/lifecycle.mjs';
import {ledger} from './matrix.mjs';
const read=async p=>await(await fetch(new URL(p,import.meta.url))).json();
self.onmessage=async({data})=>{
 const started=performance.now();
 try{
  const {identity,engine}=data,archive=await read(`../browser_eos_b4c/evidence/${engine}-candidateB-lifecycle.json`),fixtures=(await read('../browser_eos_b6/evidence/historical-rejected-pt.json')).filter(r=>r.engine===engine);
  const load=(_ignored,options={})=>loadQualifiedEOS(identity,options);
  const original=await originalSequences(load,archive,true),javascript=await javascriptPaths(load,fixtures[0]);
  const e=await load(),alternation=[];
  let init,memoryBefore,memoryAfter;
  try{
   init=e.init;memoryBefore=e.memory();
   for(let i=0;i<64;i++){
    alternation.push({i,rejected:step(e,fixtures[i%fixtures.length].request,{candidate:true,expectReject:true}),supported:step(e,{mode:'PT',args:[350000,300]},{candidate:true})});
   }
   memoryAfter=e.memory();
  }finally{e.dispose();}
  const full=await loadQualifiedEOS(identity,{fullVLE:true}),inputs=(await read('./evidence/fixed-inputs.json')).filter(r=>[146,148,151,152,162,164,165].map(n=>'native-ledger-'+n).includes(r.key));
  let seven;
  try{seven=ledger(full,inputs);}finally{full.dispose();}
  self.postMessage({passed:true,id:identity.id,identity,original,javascript,alternation,seven,init,memoryBefore,memoryAfter,elapsedMS:performance.now()-started});
 }catch(error){self.postMessage({passed:false,message:error.message,stack:error.stack,elapsedMS:performance.now()-started});}
};
