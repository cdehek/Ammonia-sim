import {pack,bits} from '../browser_eos_b5b_c1/adapter.mjs';
const ok=(v,m)=>{if(!v)throw Error(m);};
export function call(e,request,fresh=false){
 const before={stack:e.stackPointer(),memory:e.memory()},logIndex=e.init.logs.length;
 let out={};
 try{const s=fresh?e.evaluateFresh(request):{...e.evaluate(request),phase:e.state.keyed_output(e.module.parameters.iPhase)};out.state=pack(s);}
 catch(error){out.error={message:error.message,name:error.name,nativeException:error.nativeException??null};}
 out.after={stack:e.stackPointer(),memory:e.memory()};out.before=before;
 ok(before.stack===out.after.stack,'stack not restored');
 out.trace=e.init.logs.slice(logIndex).filter(s=>s.startsWith('{"event":')).map(s=>JSON.parse(s));
 ok(!out.error?.message.includes('Assertion failed'),'secondary exception assertion');
 return out;
}
export function checkInventory(record){
 const x=record.input.values;
 for(const [key,value]of Object.entries(x))ok(bits(value)===record.input.bits[key],'original '+key+' bits');
 ok(bits(x.M/x.V)===record.input.bits.rho,'original M/V arithmetic');
 ok(bits((x.U_kJ/x.M)*1000)===record.input.bits.u,'original U/M arithmetic');
 return x;
}
export function ledger(e,inputs){
 return inputs.map(record=>{
  const x=checkInventory(record),request={mode:'DU',args:[x.rho,x.u]};
  return {key:record.key,id:record.id,origin:record.origin,originalFullVLE:record.fullVLE,input:record.input,request,requestBits:request.args.map(bits),reused:call(e,request),fresh:call(e,request,true)};
 });
}
