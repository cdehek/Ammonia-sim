// Separate startup probe: install receiver before asynchronous module loading.
const scriptStartedAt=performance.timeOrigin+performance.now(),t=performance.now();
const ready=import('./service.mjs').then(m=>({service:m.service,serviceModuleImportAndEvaluationMS:performance.now()-t}));
const mode=new URL(import.meta.url).searchParams.get('mode');let owner,chain=Promise.resolve();
self.onmessage=({data:q})=>{chain=chain.then(async()=>{const {service,serviceModuleImportAndEvaluationMS}=await ready;if(!owner)owner=service(q.workerId,q.sessionId,{mode});const r=await owner(q);r.startupProbe={scriptStartedAt,serviceModuleImportAndEvaluationMS,scope:'Combined dependency import/fetch/evaluation in separate probe; normal static worker timing is creation-to-receipt'};self.postMessage(r);});};
