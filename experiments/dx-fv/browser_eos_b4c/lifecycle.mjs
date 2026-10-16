// Additional labeled lifecycle diagnostics. No accepted fixtures are regenerated.
export function lifecycle(eos,cases){
 const m=eos.module,k=m.parameters,dt=m.factory('HEOS','Ammonia'),rows=[];
 const props=s=>({p:s.p(),T:s.T(),rho:s.rhomass(),h:s.hmass(),u:s.umass(),Q:s.Q()});
 const derivatives=s=>({arT:s.keyed_output(k.idalphar_dtau_constdelta),arD:s.keyed_output(k.idalphar_ddelta_consttau),pRho:s.first_partial_deriv(k.iP,k.iDmass,k.iT),hT:s.first_partial_deriv(k.iHmass,k.iT,k.iDmass),uT:s.first_partial_deriv(k.iUmass,k.iT,k.iDmass)});
 function snap(mode,args){
  const s=eos.evaluate({mode,args});dt.update(m.input_pairs.DmassT_INPUTS,s.rho,s.T);const independent=props(dt),out={mode,args,state:s,independentDT:independent};
  if(s.Q<0){const a=derivatives(eos.state),b=derivatives(dt);out.derivatives=a;out.independentDerivatives=b;out.derivativeDifferences=Object.fromEntries(Object.keys(a).map(k=>[k,a[k]-b[k]]));out.getterDifferences=Object.fromEntries(['p','h','u'].map(k=>[k,s[k]-independent[k]]));const V=.003/5,M=s.rho*V,U=M*s.h/1000-100*(s.p/1e5)*V;out.normalizedEnergyInconsistency=Math.abs(M*(s.u-independent.u)/1000)/Math.max(1,Math.abs(U));}
  else out.equilibriumQualityValid=s.Q>=0&&s.Q<=1;
  return out;
 }
 try{for(const request of cases){const [p,h]=request.args,row={request,sequences:[]};try{
  const base=snap('PH',[p,h]),s=base.state;row.base=base;
  const actions=s.Q<0?[['PT',[p,s.T]],['PT',[p,s.T]],['PH',[p,h]],['PH',[p,h]],['DU',[s.rho,s.u]],['PT',[p,s.T]],['PH',[p,h]]]:[['PH',[p,h]],['PH',[p,h]]];
  for(const [mode,args]of actions){try{row.sequences.push(snap(mode,args));}catch(e){row.sequences.push({mode,args,error:String(e)});}}
  if(s.Q<0){const f=m.factory('HEOS','Ammonia');try{f.update(m.input_pairs.PT_INPUTS,p,s.T);row.freshPT=props(f);}catch(e){row.freshPTError=String(e);}finally{f.delete();}}
 }catch(e){row.error=String(e);}rows.push(row);}return {rows,memoryBytes:eos.memory()};}finally{dt.delete();}
}
export function performanceWork(eos,cases){
 const saved=cases.find(q=>q.id==='B1-vapor-regression'),liquid=cases.find(q=>q.id==='approach-30298.937123458254-liquid-0.001'),b1=cases.find(q=>q.id==='B1-liquid-precision');
 const vapor=eos.evaluate({mode:'PH',args:saved.args});
 const groups=[['upper-vapor-PH',{mode:'PH',args:[799999.9981754856,1624019.7431341156]}],['B4B-vapor-PH',{mode:'PH',args:saved.args}],['vapor-PT',{mode:'PT',args:[saved.args[0],vapor.T]}],['liquid-PH',{mode:'PH',args:liquid.args}],['two-phase-PQ',{mode:'PQ',args:[350000,.4]}],['B1-PH',{mode:'PH',args:b1.args}]],rows=[];
 for(let round=0;round<5;round++)for(const [group,q]of groups){const start=performance.now();let calls=0,checksum=0,errors=[];do{try{checksum+=eos.evaluate(q).rho;}catch(e){errors.push(String(e));}calls++;}while(performance.now()-start<150);rows.push({round,group,calls,elapsedMS:performance.now()-start,checksum,errors,memoryBytes:eos.memory()});}
 return {rows,init:eos.init,memoryBytes:eos.memory(),jsHeap:performance.memory?{usedJSHeapSize:performance.memory.usedJSHeapSize,totalJSHeapSize:performance.memory.totalJSHeapSize}:null};
}
