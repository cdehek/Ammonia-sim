import {local} from './attribution.mjs';import {diagnostic} from '../browser_eos_b9/values.mjs';
try{self.postMessage({success:true,result:await local()});}catch(e){self.postMessage({success:false,error:diagnostic(e)});}
