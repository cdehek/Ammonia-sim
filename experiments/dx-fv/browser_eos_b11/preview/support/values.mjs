export function bits(x){const b=new DataView(new ArrayBuffer(8));b.setFloat64(0,x);return b.getBigUint64(0).toString(16).padStart(16,'0');}
// Evidence encoding only. Transport itself always uses structured clone.
export function exact(x){if(typeof x==='number')return {f64:bits(x)};if(x===undefined)return {undefined:true};if(x===null||typeof x!=='object')return x;if(ArrayBuffer.isView(x))return {typed:x.constructor.name,bytes:[...new Uint8Array(x.buffer,x.byteOffset,x.byteLength)]};if(x instanceof ArrayBuffer)return {buffer:[...new Uint8Array(x)]};if(Array.isArray(x))return x.map(exact);return Object.fromEntries(Object.entries(x).map(([k,v])=>[k,exact(v)]));}
export const same=(a,b)=>JSON.stringify(exact(a))===JSON.stringify(exact(b));
export function assert(v,message='B9 assertion failed'){if(!v)throw Error(message);}
export function diagnostic(e,depth=0){
 if(depth>20)return {diagnosticDepthExceeded:true};
 if(e===null||['string','number','boolean'].includes(typeof e))return e;
 if(e===undefined)return null;
 if(Array.isArray(e))return e.map(v=>diagnostic(v,depth+1));
 if(typeof e!=='object')return {thrownType:typeof e,text:String(e)};
 const blocked=new Set(['excPtr','ptr','pointer','handle','state','module','stack','cause']);
 const keys=e instanceof Error?['name','message','faultKind','evidence','propertyCause','domainCause','nonlinearResidual','recordFailure','nativeException','errors']:Object.keys(e);
 return Object.fromEntries(keys.filter(k=>!blocked.has(k)&&e[k]!==undefined).map(k=>[k,diagnostic(e[k],depth+1)]));
}
export function auditRecord(r){
 for(const key of ['massResidualKg','refrigerantEnergyResidualKJ','thermalEnergyResidualKJ','combinedEnergyResidualKJ'])assert(Math.abs(r[key])<(key==='massResidualKg'?1e-8:1e-6),key);
 r.sectionResiduals.forEach(v=>{assert(Math.abs(v.massKg)<1e-8,'section mass');assert(Math.abs(v.energyKJ)<1e-6,'section energy');});
 const independent=Array(11).fill(0);independent[10]=r.ledger.airLoadKJ;
 for(let i=0;i<5;i++){const [at,af,ft]=r.ledger.thermalLinksKJ.slice(3*i,3*i+3),q=r.ledger.tubeRefrigerantKJ[i];independent[10]-=at+af;independent[2*i]+=at+ft-q;independent[2*i+1]+=af-ft;}
 r.nodes.forEach((n,i)=>{assert(Math.abs(n.residualKJ)<1e-6,'node energy');assert(Math.abs(n.energyChangeKJ-independent[i])<=1e-6,'independent signed thermal closure');});
 assert(r.lastResidual===null||r.lastResidual<=1e-11,'Newton residual');assert(r.lastTimeError===null||r.lastTimeError<=1,'time residual');
 return {mass:r.massResidualKg,fluid:r.refrigerantEnergyResidualKJ,thermal:r.thermalEnergyResidualKJ,combined:r.combinedEnergyResidualKJ,sections:r.sectionResiduals,nodes:r.nodes.map((n,i)=>({id:n.id,residual:n.residualKJ,independent:n.energyChangeKJ-independent[i]}))};
}
