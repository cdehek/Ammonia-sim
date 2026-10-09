'use strict';
function solveLinear(matrix,rhs){
 const a=matrix.map((row,i)=>[...row,rhs[i]]),n=rhs.length;
 for(let k=0;k<n;k++){
  let pivot=k;for(let j=k+1;j<n;j++)if(Math.abs(a[j][k])>Math.abs(a[pivot][k]))pivot=j;
  if(Math.abs(a[pivot][k])<1e-15)throw Error('Singular implicit Jacobian.');
  [a[k],a[pivot]]=[a[pivot],a[k]];
  for(let j=k+1;j<n;j++){const f=a[j][k]/a[k][k];for(let t=k;t<=n;t++)a[j][t]-=f*a[k][t];}
 }
 const x=Array(n);for(let k=n-1;k>=0;k--){let r=a[k][n];for(let t=k+1;t<n;t++)r-=a[k][t]*x[t];x[k]=r/a[k][k];}return x;
}
const norm=r=>Math.max(...r.map(Math.abs));
function newton(evaluate,initial,{tolerance=1e-11,maxIterations=24,onEvaluation=()=>{},onIteration=()=>{},pressureDifference=1e-5,enthalpyDifference=1e-4,sameRegion=null,lineSearchMinimum=1/4096}={}){
 let calls=0;const counted=values=>{calls++;onEvaluation();return evaluate(values);};
 let x=[...initial],value=counted(x);
 for(let iteration=0;iteration<=maxIterations;iteration++){
  const error=norm(value.residual);if(error<=tolerance)return {x,value,iterations:iteration,calls,error};
  if(iteration===maxIterations)break;onIteration();
  const n=x.length,jac=Array.from({length:n},()=>Array(n));
  for(let k=0;k<n;k++){
   const epsilon=(k%2===0?pressureDifference:enthalpyDifference)*Math.max(1,Math.abs(x[k]));
   let v,step=epsilon,lastCause=null;
   // Prefer a derivative within the current constitutive branch. Across saturation
   // liquid and mixture compressibility differ enormously; a crossing secant can
   // prevent convergence even though a valid conservative root exists.
   for(let shrink=0;shrink<12&&!v;shrink++){
    for(const sign of [1,-1]){
     const trial=[...x];step=sign*epsilon*2**(-shrink);trial[k]+=step;
     try{const candidate=counted(trial);if(!sameRegion||sameRegion(value,candidate,k)){v=candidate;break;}}catch(cause){lastCause=cause;}
    }
   }
   if(!v){if(lastCause)throw lastCause;throw Error('Could not form an implicit derivative within the property branch.');}
   for(let i=0;i<n;i++)jac[i][k]=(v.residual[i]-value.residual[i])/step;
  }
  const delta=solveLinear(jac,value.residual.map(r=>-r));let accepted=false,validTrials=0,lastDomain=null;
  for(let factor=1;factor>=lineSearchMinimum;factor/=2){
   const trial=x.map((v,k)=>v+factor*delta[k]);
   try{const next=counted(trial);validTrials++;if(norm(next.residual)<error){x=trial;value=next;accepted=true;break;}}catch(cause){if(cause.faultKind==='domain')lastDomain=cause;}
  }
  if(!accepted){if(validTrials===0&&lastDomain)throw lastDomain;throw Object.assign(Error('Implicit line search could not reduce the conservative residual.'),{nonlinearResidual:error,domainCause:lastDomain?.message});}
 }
 throw Error('Implicit nonlinear iteration did not converge.');
}
module.exports={newton,solveLinear};
