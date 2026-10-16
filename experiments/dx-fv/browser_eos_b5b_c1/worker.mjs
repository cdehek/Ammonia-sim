import {createAdapter,errorJSON,pack} from './adapter.mjs';
import {loadEOS} from '../browser_eos_b4c/loader.mjs';
postMessage({ping:true});
onmessage=async({data:a})=>{
 let eos;try{
  const em={exports:{}};new Function('module','exports',a.engine)(em,em.exports);eos=await loadEOS('candidateB');
  const adapter=createAdapter(eos,em.exports.createEngine(a.table)),f=a.fixtures[0],decode=b=>{const d=new DataView(new ArrayBuffer(8));d.setBigUint64(0,BigInt('0x'+b));return d.getFloat64(0);},x=Object.fromEntries(Object.entries(f.fixedInput.bits).map(([k,b])=>[k,decode(b)]));
  let error;try{adapter.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){error=errorJSON(e);}
  const s=a.supported,state=pack(adapter.stateMVU(s.M,s.V,s.U_kJ,35));
  postMessage({passed:!!error&&error.faultKind==='solver',error,state,memoryBytes:eos.memory()});
 }catch(e){postMessage({passed:false,error:errorJSON(e)});}finally{eos?.dispose();}
};
