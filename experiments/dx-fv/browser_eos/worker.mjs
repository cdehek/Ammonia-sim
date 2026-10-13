import {loadEOS,exactCache} from './eos.mjs';
let eos,cached;
self.onmessage=async({data})=>{
  const {id,command}=data;
  try{
    if(command==='init'){eos=await loadEOS(data.version);cached=exactCache(eos);postMessage({id,result:{init:eos.init,capabilities:eos.capabilities}});}
    else if(command==='batch'||command==='sustain'){
      const start=performance.now();let last,checksum=0;
      let calls=0;do{for(let i=0;i<(data.repeats||1);i++)for(const q of data.requests){last=(data.cache?cached:eos).evaluate(q);checksum+=last.rho||last.rhof;calls++;}}while(command==='sustain'&&performance.now()-start<(data.durationMS||1500));
      postMessage({id,result:{last,checksum,elapsedMS:performance.now()-start,calls,linearMemoryBytes:eos.memory(),cache:cached.stats()}});
    }else if(command==='dispose'){eos.dispose();postMessage({id,result:true});close();}
    else throw Error('Unknown worker command');
  }catch(e){postMessage({id,error:e.message||String(e)});}
};
