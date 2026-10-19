import {workload,regressions,c1} from './harness.mjs';
self.onmessage=async e=>{try{const a=e.data;const result=a.task==='regressions'?await regressions(a.mode):a.task==='c1'?await c1():await workload(a.mode,a.fixture,a.observed);self.postMessage({success:true,result});}catch(e){self.postMessage({success:false,error:{message:e.message,stack:e.stack}});}};
