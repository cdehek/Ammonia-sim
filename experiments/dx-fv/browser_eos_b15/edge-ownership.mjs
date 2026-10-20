// Additional public phase combinations and pressure-axis/table ownership checks.
import{loader as control}from'./control-bundle.mjs';import{loader as candidate}from'./candidate-bundle.mjs';import{same,exact,assert}from'../browser_eos_b9/values.mjs';import{outcome}from'./property-tests.mjs';
export function run(){
 const l=[control(),candidate()],e=l.map(x=>x('table-only.cjs').createTableEngine()),rows=[];
 for(const p of [.3,4,35])for(const offset of [-30,-1e-8,0,1e-8,1,250,251])for(const kind of ['liquid','vapor','solid','',null,undefined]){
  const T=e[0].sat(p).T+offset,pair=e.map(e=>outcome(()=>e.statePT(p,T,kind)));assert(same(...pair),'phase combination');rows.push({p,T,kind,result:pair[0]});
 }
 const freeze=x=>{if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;};
 const tables=l.map(x=>{const t=structuredClone(x('properties.json'));t.p=t.p.map(p=>p*1.01);for(const row of t.vapor)for(const v of row)if(v)v[1]+=.125;return x('engine.js').createEngine(freeze(t),true);});
 const alternate=[];for(let i=0;i<4;i++)for(const p of [4,3.5,12]){
  const expected=tables[0].ph(p,1700),other=tables[1].ph(p,1700),original=e[0].ph(p,1700);assert(same(expected,other),'different pressure-axis table parity');assert(!same(expected,original),'custom table witness ineffective');assert(same(e[0].ph(p,1700),e[1].ph(p,1700)),'cross-table contamination');alternate.push({p,control:expected,candidate:other,original});
 }
 return {passed:true,phaseCombinationComparisons:rows.length,differentPressureAxisAlternations:alternate.length,immutableDistinctTableOwnership:true,rows:exact(rows),tableWitnesses:exact(alternate)};
}
