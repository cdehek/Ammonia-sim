import {workload,regressions,c1} from '../browser_eos_b9c/harness.mjs';
import {hardening} from './hardening.mjs';
import {additional} from './regressions.mjs';
self.onmessage=async({data:a})=>{try{const result=a.task==='hardening'?await hardening():a.task==='additional'?await additional(a.mode):a.task==='regressions'?await regressions(a.mode):a.task==='c1'?await c1():await workload(a.mode,a.fixture,true);postMessage({ok:true,result});}catch(e){postMessage({ok:false,error:e.message,stack:e.stack});}};
