import {run,seal,failures} from './profile.mjs';
self.onmessage=async e=>{try{const r=e.data.failureCopy?(await import('./failure-copy.mjs')).run():e.data.failures?await failures():await seal(run(e.data.mode,e.data.fixture,e.data));self.postMessage({success:true,result:r});}catch(error){self.postMessage({success:false,error:{message:error.message,stack:error.stack}});}};
