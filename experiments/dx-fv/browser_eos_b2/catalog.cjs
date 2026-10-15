// Extract unchanged accepted test statements; retain exact text and source lines.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const acorn=require('/workspace/b2-runtime/node_modules/acorn');
const [root,out]=process.argv.slice(2),dir=path.join(root,'experiments/dx-fv');
const source=fs.readFileSync(path.join(dir,'coupled-test.cjs'),'utf8');
const ast=acorn.parse(source,{ecmaVersion:'latest',locations:true}),fn=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name==='verification'),body=fn.body.body;
const start=body.findIndex(n=>n.type==='BlockStatement'),prefix=source.slice(0,fn.start),setup=source.slice(body[0].start,body[start].start);
const blocks=body.slice(start).filter(n=>!source.slice(n.start,n.end).startsWith('report.passed=')).flatMap((n,i)=>{
 const text=source.slice(n.start,n.end),base={id:'block-'+i,line:n.loc.start.line,text,sha256:crypto.createHash('sha256').update(text).digest('hex')};
 return n.type==='ForOfStatement'&&source.slice(n.right.start,n.right.end)==='cases()'?['cold','warm','load-step','feed-step','heat-reversal'].map(caseName=>({...base,id:'operating-'+caseName,caseName})):[base];
});
const sources={};
for(const f of fs.readdirSync(dir).filter(f=>/\.(cjs|json)$/.test(f)))sources[f]=fs.readFileSync(path.join(dir,f),'utf8');
sources['../../engine']=fs.readFileSync(path.join(root,'engine.js'),'utf8');sources['../../properties.json']=fs.readFileSync(path.join(root,'properties.json'),'utf8');
const a1=sources['roadmap-a1.cjs'],a1ast=acorn.parse(a1,{ecmaVersion:'latest',locations:true});
let domain;
function walk(n){if(!n||typeof n!=='object')return;if(n.type==='IfStatement'&&n.test.type==='BinaryExpression'&&n.test.left.name==='mode'&&n.test.right.value==='domain')domain=n.consequent;for(const v of Object.values(n))if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}
walk(a1ast);if(!domain)throw Error('Missing accepted domain block');
const functions=['check','compiled'].map(name=>{const n=a1ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name);return a1.slice(n.start,n.end);}).join('\n');
fs.writeFileSync(out,JSON.stringify({prefix,setup,blocks,sources,domain:{text:a1.slice(domain.start,domain.end),line:domain.loc.start.line,functions}}));
