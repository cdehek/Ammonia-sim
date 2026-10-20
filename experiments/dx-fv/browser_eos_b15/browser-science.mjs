import{same,exact,assert,auditRecord}from'../browser_eos_b9/values.mjs';
const schedules={original:[.0001,.0005,.001,.002,.005,.01],added:[.0001,.0005,.001,.002,.005,.00525,.0055,.01],fine:[.0001,.0005,.001,.002,.005,.0051,.0052,.0053,.0054,.0055,.0056,.01]};
async function digest(x){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(exact(x))));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('');}
export async function run(fixture,schedule){
 let reference;const results=[];
 for(const variant of ['control','candidate']){
  const originals=variant==='control',captured={},index={};
  const capture=(key,value)=>{index[key]=(index[key]||0)+1;if(originals)(captured[key]??=[]).push(structuredClone(value));else assert(same(value,reference[key][index[key]-1]),'browser '+key+' '+index[key]);};
  globalThis.__b15count=()=>{};const noop=()=>()=>{};
  globalThis.__b9c={enter:noop,count(){},section(){},boundary(s,p,h,fn){return fn();},property(m,fn,args){return fn(...args);}};
  globalThis.__b14={enter:noop,column:noop,probe(step,shrink){capture('probes',{step,shrink});},matrix(j){capture('matrices',j);},temporal(s,coarse,fine,error){capture('temporals',{seconds:s.seconds,cells:s.cells,energies:s.energies,coarse,fine,error});},controller(seconds,proposal,next){capture('controllers',{seconds,proposal,next});},committed(s,piece,dt,start){capture('commits',{cells:s.cells,energies:s.energies,ledger:s.ledger,piece,dt,start});}};
  const{loader}=await import('./observe-'+variant+'-bundle.mjs'),load=loader(),e=load('table-only.cjs').createTableEngine();
  const lin=load('implicit.cjs'),L=lin.solveLinear;lin.solveLinear=(a,b)=>{const delta=L(a,b);capture('linear',{a,b,delta});return delta;};
  const imp=load('coupled-implicit.cjs'),N=imp.coupledNewton;imp.coupledNewton=(evaluate,...args)=>N(x=>{const value=evaluate(x);capture('residuals',{x,residual:value.residual});return value;},...args);
  const attempts=[],model=load('coupled-model.cjs').createCoupledModel(e,{trace:true,timestepGrowth:'failure-aware'},a=>{assert(attempts.length<250,'attempt cap');attempts.push(a);}),state=model.create(load('coupled-fixtures.cjs').fixture(fixture)),checkpoints=[];
  const checkpoint=()=>{const r=model.record(state);auditRecord(r);capture('checkpoints',{state,record:r});checkpoints.push({seconds:state.seconds,state:structuredClone(state),record:r});};checkpoint();
  for(const t of schedules[schedule]){model.advance(state,t-state.seconds);assert(!state.stop,'browser unexpected stop');checkpoint();}
  capture('attempts',attempts);if(originals)reference=captured;else for(const [k,v]of Object.entries(reference))assert(index[k]===v.length,'browser count '+k);
  results.push({variant,checkpoints:await Promise.all(checkpoints.map(async x=>({seconds:x.seconds,hash:await digest(x)}))),attemptsHash:await digest(attempts),counts:index,events:state.events,accepted:state.acceptedSteps,rejected:state.rejectedSteps});
 }
 return {passed:true,fixture,schedule,runtime:navigator.userAgent,sameBrowserBinary64ScienceAttemptsResidualsJacobiansCorrectionsHalfStepsAndDecisions:true,results,exampleMatrixBinary64:exact(reference.matrices[0]),qualification:'UNQUALIFIED RESEARCH beyond 0.001 s; no Node/browser bit equality claimed'};
}
