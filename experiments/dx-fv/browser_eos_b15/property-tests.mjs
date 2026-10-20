// Browser-compatible deterministic property, support and ownership comparisons.
import {loader as original} from './control-bundle.mjs';
import {loader as optimized} from './candidate-bundle.mjs';
import {exact,same,assert} from '../browser_eos_b9/values.mjs';
export const encode=exact;
function failure(e){return {constructor:e?.constructor?.name,type:typeof e,fields:e&&typeof e==='object'?Object.fromEntries(Object.getOwnPropertyNames(e).filter(k=>k!=='stack').map(k=>[k,e[k]])):e};}
export function outcome(fn){try{return {ok:true,value:fn()};}catch(e){return {ok:false,error:failure(e)};}}
export function adjacent(x,up=true){if(Number.isNaN(x)||x===(up?Infinity:-Infinity))return x;if(x===0)return up?Number.MIN_VALUE:-Number.MIN_VALUE;const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);let b=d.getBigUint64(0);d.setBigUint64(0,b+((x>0)===up?1n:-1n));return d.getFloat64(0);}
export function run(extra=[]){
 const loads=[original(),optimized()],engines=loads.map(l=>l('table-only.cjs').createTableEngine()),wrappers=loads.map((l,i)=>l('thermodynamics.cjs').createThermodynamics(engines[i])),table=loads[0]('properties.json'),rows=[];
 const compare=(label,method,args,targets=engines)=>{const pair=targets.map(e=>outcome(()=>e[method](...args)));assert(same(...pair),'property mismatch '+label);rows.push({label,method,args:args.map(x=>typeof x==='object'||typeof x==='symbol'||typeof x==='bigint'||typeof x==='function'?String(x):x),result:pair[0]});return pair[0];};
 const pressures=[...table.p.flatMap(p=>[adjacent(p,false),p,adjacent(p)]),...table.p.slice(1).map((p,i)=>Math.sqrt(p*table.p[i]))];
 for(const p of pressures){const a=engines[0].sat(p),max=engines[0].statePT(p,a.T+250).h;
  const hs=[a.hf-1e-7,a.hf-1e-8,adjacent(a.hf-1e-8,false),a.hf,a.hf+1e-8,(a.hf+a.hg)/2,a.hg-1e-8,a.hg,adjacent(a.hg),a.hg+1e-8,adjacent(a.hg+1e-8,false),adjacent(a.hg+1e-8),a.hg+1e-7,a.hg+1e-5,a.hg+1,a.hg+100,max,adjacent(max),max+1e-7];
  for(const sh of [0,1e-12,1e-9,1e-8,1e-7,.01,1,5,25,100,249.999999,250])hs.push(engines[0].statePT(p,a.T+sh).h);
  for(const h of hs){compare('grid PH','ph',[p,h]);compare('wrapper grid PH','ph',[p,h],wrappers);}
 }
 for(const v of extra){compare('historical '+v.label,'ph',[v.p,v.h]);compare('historical wrapper '+v.label,'ph',[v.p,v.h],wrappers);}
 const invalid=[undefined,null,false,true,'bad','4',NaN,Infinity,-Infinity,-0,0,-1,1e-300,.3-1e-7,.3,35,35+1e-6,1e300,Symbol('invalid'),1n,{},[],[4],()=>4];
 for(const p of invalid){compare('invalid pressure','ph',[p,1700]);compare('invalid pressure wrapper','ph',[p,1700],wrappers);}
 for(const h of invalid){compare('invalid enthalpy','ph',[4,h]);compare('invalid enthalpy wrapper','ph',[4,h],wrappers);}
 for(const h of [-1e9,1e9,engines[0].statePT(4,engines[0].sat(4).T-30,'liquid').h])compare('enthalpy extremes','ph',[4,h]);
 for(const method of ['ps','statePT','statePX'])for(const p of [.3,4,35])for(const value of method==='ps'?[0,6,7,NaN]:method==='statePX'?[-1,0,.4,1,2,NaN]:[-100,0,50,1000,NaN])compare('other phase path',method,[p,value]);
 // Coercion objects are regenerated independently; compare actual event order.
 for(const which of ['p','h'])for(const failAt of [0,1,3,7,50]){
  const pair=engines.map(e=>{const events=[];let n=0;const value={valueOf(){events.push(++n);if(n===failAt)throw Object.assign(Error('coercion sentinel'),{faultKind:'sentinel',evidence:{n}});return which==='p'?4:1700;}};return {result:outcome(()=>e.ph(which==='p'?value:4,which==='h'?value:1700)),events};});assert(same(...pair),'coercion order');rows.push({label:'coercion '+which+' '+failAt,result:pair[0]});
 }
 const ownership=[];
 for(let i=0;i<2;i++){
  const e=engines[i],expected=e.ph(4,1700),mutated=e.ph(4,1700);mutated.rho=-1;mutated.phase='caller mutation';mutated.extra={bad:true};delete mutated.h;
  assert(same(e.ph(4,1700),expected),'caller mutation leaked');
  for(const p of [4,3.5,35,.3,4,3.5,4]){const a=e.ph(p,1700),b=engines[0].ph(p,1700);assert(same(a,b),'alternating pressure stale');assert(a!==e.ph(p,1700),'result alias');}
  const fail=outcome(()=>e.ph(4,1e9));assert(!fail.ok,'expected failed inversion');assert(same(e.ph(4,1700),expected),'failed call stale');
  const other=loads[i]('table-only.cjs').createTableEngine();assert(same(other.ph(4,1700),expected),'instance isolation');
  ownership.push({callerMutationIndependent:true,freshSuccessiveResults:true,alternatingPressuresIndependent:true,failedThenValidIndependent:true,separateEngineIndependent:true});
 }
 // Separate altered tables and malformed table rows; never mutate the pinned table.
 const freeze=x=>{if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;};
 for(const malformed of [false,true]){
  const pair=loads.map(l=>{const t=structuredClone(table);if(malformed)t.vapor[0][t.sh.length-1]=null;else for(const row of t.vapor)for(const v of row)if(v)v[1]+=.125;
   const e=l('engine.js').createEngine(freeze(t),true);return outcome(()=>e.ph(.3,1700));});assert(same(...pair),'separate/malformed table parity');rows.push({label:'separate frozen table '+malformed,result:pair[0]});
 }
 // Factory defaults preserve mutable custom-table behavior, including access order.
 const pair=loads.map(l=>{const t=structuredClone(table),e=l('engine.js').createEngine(t);const before=e.ph(4,1700);t.vapor[0][0][0]+=1;return {before,after:outcome(()=>e.ph(.3,1700))};});assert(same(...pair),'mutable table default fallback');
 return {passed:true,cases:rows.length,gridPressures:pressures.length,extraHistoricalStates:extra.length,ownership,fields:'all own enumerable result fields and own error fields except runtime stack; binary64, undefined/null, signed zero, property order and constructor',rows:encode(rows)};
}
