import {diagnostic} from './values.mjs';
self.onmessage=async ({data:q})=>{
 if(q.type==='crash'){setTimeout(()=>{throw Error('B9 deliberate disposable worker crash');},0);return;}
 const base={protocol:1,workerId:q.workerId,backendId:q.backendId,sessionId:q.sessionId,requestId:q.requestId,sequence:q.sequence,type:q.type,clock:null,acceptedVersion:null};
 try{let result;
 if(q.type==='c1')result=await (await import('./c1-tests.mjs')).local();
 else if(q.type==='echo')result=q.args;
 else if(q.type==='jsError')throw Error('B9 JS-origin error');
 else if(q.type==='b7')result=await (await import('./b7-subset.mjs')).local();
 else throw Error('Unsupported research probe');
 self.postMessage({...base,success:true,result,error:null});
 }catch(e){self.postMessage({...base,success:false,result:null,error:diagnostic(e)});}
};
