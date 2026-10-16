"""Limited original A2 dependency injection, after scientific gates only.

This is deliberately not a full A2 qualification matrix.
"""
import os
import argparse,functools,http.server,json,os,subprocess,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'))
ap=argparse.ArgumentParser();ap.add_argument('--tag',default='');ap.add_argument('--build',default='candidateB',choices=['controlA','rebuiltA','candidateB']);ap.add_argument('--zero-only',action='store_true');ap.add_argument('--cases',default='cold,warm,feed-step,heat-reversal');args=ap.parse_args()
gate=json.loads((E/'focused-gate.json').read_text());assert gate['eligibleForLimitedA2'],gate
boundary=json.loads((E/'boundary-gate.json').read_text());assert boundary['eligibleForLimitedA2'],boundary
sources={p.name:p.read_text()for p in (B.parent/'browser_eos_backend/accepted').glob('*.cjs')}
test=subprocess.check_output(['git','-C',str(R),'show','be9eb35a4ddf5098e685182f8104685127c6a6ee:experiments/dx-fv/coupled-test.cjs']).decode()
check=test[test.index('function check('):test.index('\nfunction compact(')]
requests=json.loads((B.parent/'browser_eos_b2/evidence/chromium-initialization-detail-build44.json').read_text())['rows']
requests=[q for q in requests if q['id']=='approach-30298.937123458254-liquid-0.001']
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  for name in ['chromium','webkit']:
   browser=getattr(pw,name).launch(timeout=30000,**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']}if name=='webkit'and os.environ.get('EOS_WEBKIT_EXECUTABLE')else{}))
   try:
    for case in (['zero','vapor-zero','upper-vapor-zero']if args.zero_only else args.cases.split(',')):
     f=E/f'{name}-A2-{case}{args.tag}.json';assert not f.exists();page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/');started=time.monotonic();result={}
     selectedRequests=requests if case=='zero' else [dict(id=case+'-exchange',exactSIInputs=[799999.9981754856,1624019.7431341156 if case=='upper-vapor-zero' else 1624022.744737779],adapterInputs=[799999.9981754856/1e5,(1624019.7431341156 if case=='upper-vapor-zero' else 1624022.744737779)/1000])]
     try:
      result=page.evaluate('''async({sources,engine,table,check,requests,caseName,build})=>{
       const {loadEOS}=await import('/experiments/dx-fv/browser_eos_b4c/loader.mjs');const {createAdapter}=await import('/experiments/dx-fv/browser_eos_backend/adapter.mjs');
       const em={exports:{}};new Function('module','exports',engine)(em,em.exports);const guard=em.exports.createEngine(table),eos=await loadEOS(build),adapter=createAdapter(eos,guard),cache={};
       function require(name){const key=name.startsWith('./')?name.slice(2):name;if(cache[key])return cache[key].exports;if(!sources[key])throw Error('Unexpected import '+name);const m={exports:{}};cache[key]=m;new Function('module','exports','require',sources[key])(m,m.exports,require);return m.exports;}
       const assert={ok:(v,m)=>{if(!v)throw Error(m||'assert.ok');},equal:(a,b,m)=>{if(a!==b)throw Error(m||`assert.equal ${a} ${b}`);}};
       const report={conservation:{massKg:0,sectionMassKg:0,refrigerantKJ:0,thermalKJ:0,combinedKJ:0,sectionEnergyKJ:0,nodeEnergyKJ:0}};
       const maximum=a=>Math.max(0,...a.map(Math.abs)),near=(a,b,t,label)=>assert.ok(Math.abs(a-b)<=t,`${label}: ${a} vs ${b}, limit ${t}`);
       const scientificCheck=new Function('assert','report','maximum','near','let lastRecord;'+check+';return check;')(assert,report,maximum,near);
       const {createCoupledModel}=require('./coupled-model.cjs'),F=require('./coupled-fixtures.cjs');
       try{
        if(['zero','vapor-zero','upper-vapor-zero'].includes(caseName)){
         const rows=[];for(const q of requests){const [p,h]=q.adapterInputs,row={id:q.id,exactSIInputs:q.exactSIInputs,adapterInputs:q.adapterInputs};
          try{const requested=adapter.ph(p,h),T=requested.T+273.15,model=createCoupledModel(adapter,{timestepGrowth:'failure-aware'}),s=model.create({sealed:true,refrigerantConductanceKWK:0,initial:Array.from({length:5},()=>({p,h})),thermal:{tubeProfileK:T,finProfileK:T,airInitialK:T,airLoadKW:0}});row.initial=scientificCheck(model.record(s));const before=JSON.stringify(s),work={evaluations:0,iterations:0,linearSolves:0,diagnostics:[]};
           try{const trial=model.trial(s,.001,work);row.trial={completed:true,cells:trial.cells,errorNorm:trial.error,scientificCheck:scientificCheck(model.record({...s,cells:trial.cells,energies:trial.energies,lastResidual:trial.error}))};}catch(e){row.trial={completed:false,error:String(e),faultKind:e.faultKind,evidence:e.evidence};}row.trial.work=work;row.exactTrialStatePreserved=JSON.stringify(s)===before;
          }catch(e){row.error=String(e);row.evidence=e.evidence;}rows.push(row);}
         return {case:caseName,rows,counts:adapter.counts,conservation:report.conservation,linearMemory:eos.memory(),secondsAdvanced:0};
        }
        const c=F.cases().find(c=>c.name===caseName),model=createCoupledModel(adapter,{...F.accuracyOptions(1e-6),trace:true,thermalJacobian:'finite-difference',timestepGrowth:'failure-aware'}),s=model.create(c.config);
        window.b4aCoupled={model,s,eos,adapter,scientificCheck,report};
        const samples=caseName==='feed-step'?c.samples.filter(t=>t<=15.01):c.samples.filter(t=>t<=.2);
        return {case:caseName,initial:scientificCheck(model.record(s)),samples,settings:model.record(s).settings,init:eos.init};
       }finally{if(['zero','vapor-zero','upper-vapor-zero'].includes(caseName))eos.dispose();}
      }''',dict(sources=sources,engine=(R/'engine.js').read_text(),table=json.loads((R/'properties.json').read_text()),check=check,requests=selectedRequests,caseName=case,build=args.build))
      result.update(build=args.build,sourceCommit='be9eb35a4ddf5098e685182f8104685127c6a6ee',browser=name,browserVersion=browser.version,fullQualification=False,physicalIPad=False)
      f.write_text(json.dumps(result,indent=2)+'\n')
      if case not in ['zero','vapor-zero','upper-vapor-zero']:
       result['rows']=[]
       for t in result['samples']:
        record=page.evaluate('''t=>{const {model,s,adapter,eos,scientificCheck,report}=b4aCoupled;const start=performance.now();const record=scientificCheck(model.advance(s,t-s.seconds));return {record,elapsedMS:performance.now()-start,counts:{...adapter.counts},linearMemory:eos.memory(),conservation:{...report.conservation}};}''',t)
        result['rows'].append(record);f.write_text(json.dumps(result,indent=2)+'\n');print(name,case,t,'reached',record['record']['seconds'],flush=True)
       result['completedAllSelectedSamples']=len(result['rows'])==len(result['samples']);page.evaluate('b4aCoupled.eos.dispose()')
     except Exception as exc:
      result['error']=str(exc)
     finally:
      result['elapsedSeconds']=time.monotonic()-started;f.write_text(json.dumps(result,indent=2)+'\n');page.close()
   finally:browser.close()
finally:server.shutdown()
