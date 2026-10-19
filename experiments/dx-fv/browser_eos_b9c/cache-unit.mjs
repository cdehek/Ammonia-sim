// Mechanical tests of the exact source closure, NOT an injected model backend.
import {assert,same} from '../browser_eos_b9/values.mjs';
export async function run(){
 const source=await(await fetch('./isolated/coupled-model.cjs')).text();
 const start=source.indexOf('const boundaries=[undefined,undefined];'),end=source.indexOf('    const exactColumns=',start);
 assert(start>0&&end>start,'closure source');const closure=source.slice(start,end);
 const catcher='boundaries[0]=boundaries[1]=undefined;throw cause;';assert(source.includes('catch(cause) { '+catcher+' }'),'actual catch source');
 let calls=0,fail=false;const error=Object.assign(Error('synthetic unit refusal'),{faultKind:'domain'});
 const c=new Function('thermo',closure+'return (i,p,h)=>{try{return boundaryPH(i,p,h);}catch(cause){'+catcher+'}};')({ph(p,h){calls++;if(fail)throw error;if(!Number.isFinite(p)||!Number.isFinite(h))throw error;return {p,h,serial:calls};}});
 const a=c(0,4,500),b=c(1,3.5,1700);assert(c(0,4,500)===a&&c(1,3.5,1700)===b&&calls===2,'exact success reuse');
 assert(c(0,4,500+Number.EPSILON*512)!==a&&calls===3,'binary64 changed h misses');
 const zero=c(0,4,0);assert(c(0,4,-0)!==zero&&calls===5,'signed-zero distinct');
 fail=true;for(let i=0;i<2;i++){let caught;try{c(0,4,600);}catch(e){caught=e;}assert(caught===error,'original error identity');}assert(calls===7,'failure never cached');
 fail=false;assert(c(1,3.5,1700)!==b&&calls===8,'failure clears both slots');
 for(let i=0;i<2;i++){try{c(0,4,NaN);}catch(e){assert(e===error);}}assert(calls===10,'NaN not installed');
 return {passed:true,sourceExtracted:true,mechanicalOnly:true,calls,exactIdentity:true,signedZero:true,NaNRefuses:true,failuresNeverCached:true,bothClearedOnFailure:true,errorIdentity:true};
}
