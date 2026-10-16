import {loadEOS} from './loader.mjs';
import {performanceWork} from './lifecycle.mjs';
self.onmessage=async({data:{build,cases}})=>{try{const e=await loadEOS(build);try{self.postMessage({result:performanceWork(e,cases)});}finally{e.dispose();}}catch(e){self.postMessage({error:String(e)});}};
