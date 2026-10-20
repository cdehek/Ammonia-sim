// Separate frozen observer source; no timers inside scientific hooks.
import {open,setup,schedules} from './science.mjs';
import {same,assert} from './assets/values.mjs';
import {hash} from './hash.mjs';
const rows=[];
for(const fixture of ['cold','warm'])for(const variant of ['control','candidate']){
 const counts={},ph={},stack=[];let column=null;
 const inc=k=>counts[k]=(counts[k]||0)+1,enter=k=>{stack.push(k);return()=>assert(stack.pop()===k,'stack');};
 globalThis.__b15count=inc;
 globalThis.__b9c={enter,count:k=>inc('b9c.'+k),section:hit=>inc('section.'+(hit?'hit':'miss')),boundary(side,p,h,fn){const before=counts['public.ph']||0;try{return fn();}finally{inc('boundary.'+((counts['public.ph']||0)>before?'miss':'hit'));}},property(method,fn,args){inc('public.'+method);const stage=stack.includes('stage')?'implicit-stage':'outside-implicit-stage',ctx=column!==null?'column-'+column:stack.includes('record')?'record':stack.includes('residual')?'residual-other':stack.includes('trial')?'trial-other':'other';try{const v=fn(...args);if(method==='ph'){const k=stage+'|'+ctx+'|'+v.phase;ph[k]=(ph[k]||0)+1;}return v;}catch(e){inc('failed.'+method);throw e;}}};
 globalThis.__b14={enter,column(k){column=k;return()=>column=null;},probe(){},matrix(){},temporal(){},controller(){},committed(){}};
 const {load,engine}=await open('observe-'+variant),s=setup(load,engine,fixture),initialCounts={...counts},initialPH={...ph};let record;
 for(const target of schedules.original){record=s.model.advance(s.state,target-s.state.seconds);assert(!s.state.stop,'unexpected stop');}
 const delta=(all,before)=>Object.fromEntries(Object.entries(all).map(([k,v])=>[k,v-(before[k]||0)]).filter(([,v])=>v));
 rows.push({fixture,variant,initialCounts,advanceCounts:delta(counts,initialCounts),initialPH,advancePH:delta(ph,initialPH),scientificSHA256:hash({state:s.state,record,attempts:s.attempts})});
}
for(const fixture of ['cold','warm']){const [a,b]=rows.filter(r=>r.fixture===fixture);assert(a.scientificSHA256===b.scientificSHA256&&same(a.advancePH,b.advancePH),'observer parity');assert(a.advanceCounts.pressureBrackets-b.advanceCounts.pressureBrackets===39*b.advanceCounts.ownedHolders,'pressure work');}
console.log(JSON.stringify({passed:true,scope:'Advance only, original schedule; initialization excluded; no additional checkpoint record calls',rows}));
