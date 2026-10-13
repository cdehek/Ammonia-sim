// Static block inventory closure. Runs the unchanged generic Newton routine;
// does not import the coupled model, transport, evaporator or time integrator.
export function synthetic(eos,targets,coupledNewton){
 const rows=[];
 for(const n of [5,9])for(const target of targets)for(const accounting of ['input-h','returned-h']){
  const V=.003/n,s=target.reference,M=s.rho*V,U=M*s.h-s.p*V,scales=[Math.max(.01,M),Math.max(1,Math.abs(U/1000))];
  const initial=Array.from({length:n},()=>[target.args[0]/1e5+.000001,target.args[1]/1000+.00001]).flat().concat(Array(2*n+1).fill(.000001));
  const variables=Array.from({length:n},(_,section)=>[{kind:'pressure',section},{kind:'enthalpy',section}]).flat().concat(Array.from({length:2*n+1},()=>({kind:'thermal-energy',capacityKJK:1})));
  const work={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]},t=performance.now();
  function evaluate(x){const states=[],residual=[];
   for(let i=0;i<n;i++){
    const p=x[2*i]*1e5,h=x[2*i+1]*1000,a=eos.evaluate({mode:'PH',args:[p,h]});
    const mass=a.rho*V,energy=mass*(accounting==='input-h'?h:a.h)-p*V;
    residual.push((mass-M)/scales[0],(energy/1000-U/1000)/scales[1]);states.push({...a,p:x[2*i],h:x[2*i+1],phase:'liquid',x:null});
   }
   return {states,residual:residual.concat(x.slice(2*n).map(e=>e/.1))};
  }
  const row={n,dimension:4*n+1,target:target.id,accounting,V,M,U,scales,settings:{nonlinearTolerance:1e-11,maxIterations:30},initial,finitePressureStepPa:1e-7*Math.max(1,initial[0])*1e5,finiteEnthalpyStepJkg:1e-8*Math.max(1,initial[1])*1000};
  try{const q=coupledNewton(evaluate,initial,variables,row.settings,work);Object.assign(row,{converged:true,error:q.error,result:q.x,pressureErrorPa:q.x[0]*1e5-target.args[0],enthalpyErrorJkg:q.x[1]*1000-target.args[1]});}
  catch(e){Object.assign(row,{converged:false,error:e.message,nonlinearResidual:e.nonlinearResidual??null});}
  work.diagnosticCounts=Object.fromEntries([...new Set(work.diagnostics.map(d=>d.type))].map(type=>[type,work.diagnostics.filter(d=>d.type===type).length]));
  work.lineSearch={rejected:work.diagnostics.filter(d=>d.type==='line-search'&&d.outcome!=='accepted').length,minFactor:Math.min(1,...work.diagnostics.filter(d=>d.type==='line-search').map(d=>d.factor))};
  work.diagnostics=work.diagnostics.filter(d=>['iteration','solve-failed'].includes(d.type)||(d.type==='derivative'&&d.iteration===0&&d.column<2));
  Object.assign(row,{elapsedMS:performance.now()-t,work});rows.push(row);
 }
 return {rows,warning:'Static zero-flow inventory closure and identity thermal rows. No TR-BDF2 stages, physical thermal dynamics, coupled trajectory or qualification is run.'};
}
