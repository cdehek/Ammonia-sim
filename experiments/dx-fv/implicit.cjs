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
function newton(evaluate,initial,{tolerance=1e-11,maxIterations=24}={}){
 let calls=0;const counted=values=>{calls++;return evaluate(values);};
 let x=[...initial],value=counted(x);
 for(let iteration=0;iteration<=maxIterations;iteration++){
  const error=norm(value.residual);if(error<=tolerance)return {x,value,iterations:iteration,calls,error};
  if(iteration===maxIterations)break;
  const n=x.length,jac=Array.from({length:n},()=>Array(n));
  for(let k=0;k<n;k++){
   const epsilon=(k%2===0?1e-5:1e-4)*Math.max(1,Math.abs(x[k])),trial=[...x];trial[k]+=epsilon;
   let v,step=epsilon;try{v=counted(trial);}catch{trial[k]=x[k]-epsilon;step=-epsilon;v=counted(trial);}
   for(let i=0;i<n;i++)jac[i][k]=(v.residual[i]-value.residual[i])/step;
  }
  const delta=solveLinear(jac,value.residual.map(r=>-r));let accepted=false,validTrials=0,lastDomain=null;
  for(let factor=1;factor>=1/4096;factor/=2){
   const trial=x.map((v,k)=>v+factor*delta[k]);
   try{const next=counted(trial);validTrials++;if(norm(next.residual)<error){x=trial;value=next;accepted=true;break;}}catch(cause){if(cause.faultKind==='domain')lastDomain=cause;}
  }
  if(!accepted){if(validTrials===0&&lastDomain)throw lastDomain;throw Error('Implicit line search could not reduce the conservative residual.');}
 }
 throw Error('Implicit nonlinear iteration did not converge.');
}
module.exports={newton,solveLinear};
