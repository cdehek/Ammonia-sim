import {loadEOS} from './loader.mjs';
import {performanceWork} from './workloads.mjs';
import {diagnose} from '../browser_eos_precision/diagnostic.mjs';
self.onmessage=async({data})=>{
 let eos;
 try{eos=await loadEOS(data.build);self.postMessage({ok:true,build:data.build,performance:await performanceWork(eos,data.requests),precision:data.inputs?await diagnose(eos,data.inputs):null});}
 catch(err){self.postMessage({ok:false,build:data.build,error:String(err)});}
 finally{eos?.dispose();}
};
