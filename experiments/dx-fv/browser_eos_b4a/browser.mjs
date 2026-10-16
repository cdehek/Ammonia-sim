import {investigate} from '../browser_eos_b2/phase.mjs';
import {createAdapter} from '../browser_eos_backend/adapter.mjs';
export function run(eos,requests,references,historical,guard){
 const result=investigate(eos,requests),adapter=createAdapter(eos,guard),m=eos.module;
 const audit=m.factory('HEOS','Ammonia');
 const bits=x=>{const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);return d.getBigUint64(0).toString(16).padStart(16,'0');};
 const pack=s=>({values:s,bits:Object.fromEntries(Object.entries(s).map(([k,v])=>[k,bits(v)]))});
 function direct(rho,T){audit.update(m.input_pairs.DmassT_INPUTS,rho,T);return {p:audit.p(),h:audit.hmass(),u:audit.umass(),T:audit.T(),rho:audit.rhomass()};}
 try{
  for(const row of result.rows){
   if(!row.base)continue;
   const [p,h]=row.args,V=.003/5,ref=references.find(r=>r.request.id===row.id),old=historical.find(r=>r.id===row.id);
   row.inventories={};
   for(const [kind,state]of [['A',ref?.base?.reference?.converged?ref.base.reference.state:null],['B',old?.base?.state],['C',row.base.state]]){
    if(!state)continue;
    const M=state.rho*V,U=M*(h/1000)-100*(p/1e5)*V,rho=M/V,u=U/M*1000;
    const inv={input:pack({M,U_kJ:U,V,rho,u}),source:{A:'independent physical reference',B:'fixed historical B3 browser44 PH',C:'current tested PH'}[kind]};
    try{const du=eos.evaluate({mode:'DU',args:[rho,u]});inv.DU=pack(du);inv.independentDT=pack(direct(du.rho,du.T));
     inv.differences={p:du.p-p,h:du.h-h,T:du.T-state.T};inv.budgets={p:.1,h:.1,T:1e-4};
     inv.budgetPass=Object.fromEntries(Object.keys(inv.differences).map(k=>[k,Math.abs(inv.differences[k])<=inv.budgets[k]]));inv.canonicalPass=Object.values(inv.budgetPass).every(Boolean);
     inv.inventoryResiduals={rho:du.rho-rho,u:du.u-u};
    }catch(e){inv.error=String(e);inv.canonicalPass=false;}
    try{inv.acceptedAdapterRecovery=adapter.stateMVU(M,V,U,p/1e5);}catch(e){inv.acceptedAdapterError=String(e);}
    row.inventories[kind]=inv;
   }
   row.repeat=[];
   if(row.id==='approach-30298.937123458254-liquid-0.001'||row.id==='B1-liquid-precision'||row.id==='B1-vapor-regression'){
    for(let i=0;i<3;i++)row.repeat.push(pack(eos.evaluate({mode:'PH',args:[p,h]})));
   }
   if(row.id==='B1-vapor-regression'&&row.PTatReturnedT){const s=row.PTatReturnedT;row.PTindependentDT=direct(s.rho,s.T);row.PTcacheDifference=Object.fromEntries(['p','h','u'].map(k=>[k,s[k]-row.PTindependentDT[k]]));}
  }
  return result;
 }finally{audit.delete();}
}
export function performanceWork(eos,requests){
 const groups=[['primary',requests.filter(q=>q.id==='approach-30298.937123458254-liquid-0.001')],['boundary',requests.slice(0,57)],['B1',requests.filter(q=>q.id==='B1-liquid-precision')]];
 const rows=[];
 for(let round=0;round<3;round++)for(const [group,inputs]of groups){
  const start=performance.now();let calls=0,errors=[],checksum=0;
  do{for(const q of inputs){try{checksum+=eos.evaluate(q).rho;}catch(e){errors.push(String(e));}calls++;}}while(performance.now()-start<100);
  rows.push({round,group,calls,elapsedMS:performance.now()-start,errors,checksum,memoryBytes:eos.memory()});
 }
 return {init:eos.init,rows,memoryBytes:eos.memory(),jsHeap:performance.memory?{usedJSHeapSize:performance.memory.usedJSHeapSize,totalJSHeapSize:performance.memory.totalJSHeapSize}:null};
}
