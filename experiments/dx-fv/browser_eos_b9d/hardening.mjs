import {loader} from '../browser_eos_b9c/candidate-bundle.mjs';
import {assert,same} from '../browser_eos_b9/values.mjs';
export async function hardening(){
 const load=loader(),owner=load('table-only.cjs'),engine=owner.createTableEngine(),data=load('properties.json');
 let objects=0;function frozen(v){if(v&&typeof v==='object'){objects++;assert(Object.isFrozen(v),'recursive table freeze');Object.values(v).forEach(frozen);}}frozen(data);
 assert(Object.isFrozen(engine),'engine frozen');
 const factory=load('coupled-model.cjs').createCoupledModel;
 const other=loader();const refused=[];
 for(const [name,e] of [['unowned-table',load('engine.js').createEngine(data)],['injected',{ph(){throw Error('must not call');}}],['proxy',new Proxy(engine,{})],['other-registry',other('table-only.cjs').createTableEngine()],['null',null]]){
  let error;try{factory(e);}catch(e){error=e;}assert(error?.message==='B9C requires its owned original table engine.',name);refused.push(name);
 }
 const thermo=load('thermodynamics.cjs').createThermodynamics(engine),a=thermo.ph(4,500),b=thermo.ph(4,500);
 assert(a!==b&&same(a,b)&&Object.values(a).every(v=>v===null||typeof v!=='object'),'flat fresh deterministic PH');
 a.p=999;assert(thermo.ph(4,500).p===4,'result mutation cannot affect table');
 let blocked=0;for(const fn of [()=>data.sat[0][0]=0,()=>engine.ph=()=>null])try{fn();}catch{blocked++;}assert(blocked===2,'mutation refused');
 const source=await(await fetch('../browser_eos_b9c/isolated/coupled-model.cjs')).text();
 const i=source.indexOf('const boundaries=[undefined,undefined];'),j=source.indexOf('    const exactColumns=',i),body=source.slice(i,j);
 assert(i>0&&j>i,'actual closure');
 let calls=0,fail=false;const error=Object.assign(Error('mechanical-only PH refusal'),{faultKind:'domain'});
 const make=()=>new Function('thermo',body+'return (i,p,h)=>{try{return boundaryPH(i,p,h);}catch(cause){boundaries[0]=boundaries[1]=undefined;throw cause;}};')({ph(p,h){calls++;if(fail||!Number.isFinite(p)||!Number.isFinite(h))throw error;return {p,h};}});
 const cache=make(),x=cache(0,4,500),y=cache(1,3.5,1700);assert(cache(0,4,500)===x&&cache(1,3.5,1700)===y&&calls===2,'success hit');
 assert(cache(0,4+Number.EPSILON*4,500)!==x,'exact changed pressure');
 const plus=cache(0,4,0);assert(cache(0,4,-0)!==plus,'signed zero');
 for(const [p,h] of [[NaN,500],[Infinity,500],[4,NaN],[4,Infinity],[4,-Infinity]])for(let k=0;k<2;k++){const n=calls;let e;try{cache(0,p,h);}catch(c){e=c;}assert(e===error&&calls===n+1,'nonfinite refusal never installed');}
 fail=true;for(let k=0;k<2;k++){let e;try{cache(0,4,600);}catch(c){e=c;}assert(e===error,'failure identity');}fail=false;
 assert(cache(1,3.5,1700)!==y,'failure clears both slots');assert(make()(0,4,500)!==x,'new stage no sharing');
 return {passed:true,recursivelyFrozenObjects:objects,refused,mutationRefused:blocked,exactKeys:true,signedZero:true,nonfiniteRefusal:true,noFailedCaching:true,bothSlotsCleared:true,newClosureIndependent:true,mechanicalOnly:true,assumptions:['trusted unmodified registry/JS intrinsics','no third-party callbacks in synchronous stage','only this worker owns its loader; arbitrary hostile module mutation is outside eligibility contract']};
}
