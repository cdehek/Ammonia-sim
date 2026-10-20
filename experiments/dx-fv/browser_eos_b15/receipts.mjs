import fs from'node:fs';import zlib from'node:zlib';
const E=new URL('./evidence/',import.meta.url),cache=new Map();
export function readReceipt(name,ancestors=[]){
 if(!/^[a-z0-9-]+$/.test(name)||ancestors.includes(name))throw Error('invalid/cyclic receipt ref');if(cache.has(name))return cache.get(name);
 const rows=zlib.gunzipSync(fs.readFileSync(new URL(name+'.jsonl.gz',E))).toString().trim().split('\n').map(JSON.parse);
 function resolve(x){if(!x||typeof x!=='object')return x;if(x.$b15ref){const r=x.$b15ref,source=readReceipt(r.receipt,[...ancestors,name]).find(x=>x.type===r.type&&(r.seconds===undefined||x.seconds===r.seconds));if(!source)throw Error('missing exact reference');return source[r.field];}if(Array.isArray(x))return x.map(resolve);return Object.fromEntries(Object.entries(x).map(([k,v])=>[k,resolve(v)]));}
 const result=rows.map(resolve);cache.set(name,result);return result;
}
