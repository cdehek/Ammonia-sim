import {investigate} from '../browser_eos_b2/phase.mjs';
import {createAdapter} from '../browser_eos_backend/adapter.mjs';
export function run(eos, requests, references, guard) {
 const bits=x=>{const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);return d.getBigUint64(0).toString(16).padStart(16,'0');};
 const pack=x=>({values:x,bits:Object.fromEntries(Object.entries(x).map(([k,v])=>[k,bits(v)]))});
 const result=investigate(eos,requests),adapter=createAdapter(eos,guard);
 for(const row of result.rows){
  if(!row.base)continue;
  const [p,h]=row.args,V=.003/5,ref=references.find(q=>q.request.id===row.id);
  row.inventories={};
  for(const [kind,state]of [['B',row.base.state],['A',ref?.reference?.converged?ref.reference.state:null]]){
   if(!state)continue;
   const M=state.rho*V,U=M*(h/1000)-100*(p/1e5)*V,rho=M/V,u=U/M*1000;
   const inv={input:pack({M,U_kJ:U,V,rho,u}),source:kind==='A'?'independent diagnostic DT root':'unchanged returned PH density'};
   try{const du=eos.evaluate({mode:'DU',args:[rho,u]});inv.DU=pack(du);
    inv.differences={p:du.p-p,h:du.h-h,T:du.T-state.T};
    inv.canonicalPass=Math.abs(inv.differences.p)<=.1&&Math.abs(inv.differences.h)<=.1&&Math.abs(inv.differences.T)<=1e-4;
   }catch(e){inv.error=String(e);inv.canonicalPass=false;}
   try{inv.acceptedAdapterRecovery=adapter.stateMVU(M,V,U,p/1e5);}catch(e){inv.acceptedAdapterError=String(e);}
   row.inventories[kind]=inv;
  }
  row.repeat=[];
  if(row.id==='approach-30298.937123458254-liquid-0.001'||row.id==='B1-vapor-regression'){
   for(let i=0;i<3;i++)row.repeat.push(pack(eos.evaluate({mode:'PH',args:[p,h]})));
  }
 }
 return result;
}
