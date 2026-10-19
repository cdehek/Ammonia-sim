// Run original exhaustive harness; hash full evidence before releasing duplicate detail.
import {workload,regressions,c1,digest} from '../browser_eos_b9c/harness.mjs';
import {hardening} from '../browser_eos_b9d/hardening.mjs';
import {additional} from '../browser_eos_b9d/regressions.mjs';
self.onmessage=async({data:a})=>{try{
 let r=a.task==='hardening'?await hardening():a.task==='additional'?await additional(a.mode):a.task==='regressions'?await regressions(a.mode):a.task==='c1'?await c1():await workload(a.mode,a.fixture,true);
 if(!a.task){const {science,evidence,...compact}=r;r={...compact,fullScienceAndComponentHashesRetained:true};}
 if(a.task==='additional')r.rows=r.rows.map(({science,...row})=>row);
 if(a.task==='regressions')r.cases=await Promise.all(r.cases.map(async c=>({name:c.name,scientificHash:await digest({state:c.state,records:c.records,error:c.error,attempts:c.attempts}),componentHashes:c.componentHashes,audits:c.audits,logicalBoundaryHash:c.evidence.logicalBoundaryHash})));
 postMessage({ok:true,result:r});
}catch(e){postMessage({ok:false,error:e.message,stack:e.stack});}};
