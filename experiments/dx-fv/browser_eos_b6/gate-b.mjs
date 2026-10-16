import {loadEOS as control} from '../browser_eos_b4c/loader.mjs';
import {loadEOS as candidate} from './loader.mjs';
import {loadEOS as diagnostic} from './candidate-diagnostic.mjs';
import {lifecycle,originalSequences,javascriptPaths} from './lifecycle.mjs';
import {science,c1} from './science.mjs';
import {performanceSamples,workers} from './performance.mjs';
const read=async p=>await(await fetch(new URL(p,import.meta.url))).json();
export async function run({engine,sections=null}){
 const all=await read('./evidence/historical-rejected-pt.json'),fixtures=all.filter(f=>f.engine===engine),archive=await read(`../browser_eos_b4c/evidence/${engine}-candidateB-lifecycle.json`),out={};
 async function attempt(label,fn){if(sections&&!sections.includes(label))return;try{out[label]=await fn();}catch(e){out[label]={passed:false,error:String(e),stack:e.stack,a2Partial:e.a2Partial??null};}console.log('B6 section',engine,label,out[label].passed===false?'FAILED':'complete');}
 await attempt('originalControl',()=>originalSequences(control,archive,false));
 await attempt('originalCandidate',()=>originalSequences(candidate,archive,true));
 await attempt('originalDiagnostic',()=>originalSequences(diagnostic,archive,true));
 await attempt('lifecycleControl',()=>lifecycle(control,fixtures,false));
 await attempt('lifecycleCandidate',()=>lifecycle(candidate,fixtures,true));
 await attempt('javascriptPaths',()=>javascriptPaths(diagnostic,fixtures[0]));
 await attempt('science',()=>science(control,candidate,engine));
 await attempt('c1',()=>c1(control,candidate,engine,fixtures[0]));
 await attempt('performance',()=>performanceSamples(control,candidate,fixtures[0]));
 await attempt('workers',()=>workers(fixtures[0]));
 await attempt('defaultSelection',async()=>{
  const a=await control(),b=await candidate();
  try{const request={mode:'PT',args:[350000,300]},x=a.evaluate(request),y=b.evaluate(request);if(JSON.stringify(x)!==JSON.stringify(y))throw Error('historical default selection changed');return {passed:true,request,control:x,candidate:y,scope:'Historical controlA default preserved. B6 scientific qualification explicitly selects candidateB.'};}
  finally{a.dispose();b.dispose();}
 });
 out.passed=Object.values(out).every(x=>x?.passed!==false);return out;
}
