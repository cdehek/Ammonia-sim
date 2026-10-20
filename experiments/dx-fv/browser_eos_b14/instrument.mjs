// Observation-only source transformation. No solver/property settings are changed.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
export function instrument(){
 const url=new URL('../browser_eos_b9c/diagnostic-candidate-bundle.mjs',import.meta.url);
 let src=fs.readFileSync(url,'utf8');const changes=[];
 const change=(before,after)=>{if(src.split(before).length!==2)throw Error('Anchor drift: '+before);src=src.replace(before,after);changes.push({before,after});};
 change('for (let k = 0; k < x.length; k++) {',"const __jacDone=globalThis.__b14.enter('jacobian');\nfor (let k = 0; k < x.length; k++) {\nconst __columnDone=globalThis.__b14.column(k,variables[k],x[k]);try{");
 change('      }\n      work.linearSolves++;',"      }finally{__columnDone();}\n      }\n      globalThis.__b14.matrix(jacobian);__jacDone();\n      work.linearSolves++;");
 // The original loop closing brace now closes try; the inserted brace closes loop.
 change('  function errorEstimate(s, coarse, fine) {','  function errorEstimate(s, coarse, fine) {'); // manifest explicit anchor verification
 change('    return Math.max(fluid,thermal);','    const __result=Math.max(fluid,thermal);globalThis.__b14.temporal(s,coarse,fine,__result);return __result;');
 change('      s.nextStepSeconds=dt;','      s.nextStepSeconds=dt;globalThis.__b14.controller(s.seconds,proposal,dt);');
 change('s.maxAcceptedStepSeconds=Math.max(s.maxAcceptedStepSeconds,dt);\n  }\n  function applyBoundary', 's.maxAcceptedStepSeconds=Math.max(s.maxAcceptedStepSeconds,dt);globalThis.__b14.committed(s,piece,dt,start);\n  }\n  function applyBoundary');
 change('              const next = counted(probe);','              const next = counted(probe);globalThis.__b14.probe(step,shrink);');
 const hash=s=>createHash('sha256').update(s).digest('hex');
 return {src,manifest:{basePath:url.pathname,baseSHA256:hash(fs.readFileSync(url)),transformedSHA256:hash(src),changes}};
}
