'use strict';
// Diagnostic envelope only. No property result and no physical proof factory.
const propertyFailure=e=>e?.evidence?.propertyFailure||e?.propertyCause?.evidence?.propertyFailure||e?.domainCause?.evidence?.propertyFailure;
const describe=e=>({message:e.message||String(e),faultKind:e.faultKind||'solver',evidence:e.evidence||null,
  propertyCause:e.propertyCause||null,domainCause:e.domainCause||null});
const bits=x=>{const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);return d.getBigUint64(0).toString(16).padStart(16,'0');};
const pack=x=>({values:x,bits:Object.fromEntries(Object.entries(x).filter(([,v])=>typeof v==='number').map(([k,v])=>[k,bits(v)]))});
function classify(e,operation,inputScope='requested-coordinate',explicit=false,input=null){
 if(!propertyFailure(e))e.evidence={...e.evidence,propertyFailure:{schemaVersion:'C1/1',operation,inputScope,
  input:input?pack(input):null,
  reason:explicit?'explicit-unsupported-input':'inverse-recovery-failure',physicalTrajectoryExit:'unproved',
  rawRecovery:'unknown',originalError:{message:e.message,faultKind:e.faultKind||null},numericalPressureEnclosure:false}};
 if(inputScope==='fixed-inventory')e.evidence={...e.evidence,recoveryContext:{operation,input:input?pack(input):null}};
 e.faultKind=explicit?'domain':'solver';
 return e;
}
module.exports={propertyFailure,describe,classify};
