"""Research-boundary and completed-evidence audit; never qualifies a backend."""
import ast,hashlib,json,re,struct,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence';checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True).strip()
def read(p):return json.loads(p.read_text())
base='f17623f61592bd897200206692ec002088f0a605';branch='research/browser-eos-flash-precision-20261013';prefix=str(B.relative_to(R))+'/'
checkpoint=read(E/'checkpoint.json')
check('Repository identity',bool(re.search(r'github\.com[:/]cdehek/Ammonia-sim(?:\.git)?$',git('remote','get-url','origin'))))
check('Isolated research branch',git('branch','--show-current')==branch)
check('Exact starting commit is an ancestor',subprocess.run(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=R).returncode==0)
check('Accepted A2 is a starting-commit ancestor',subprocess.run(['git','merge-base','--is-ancestor',checkpoint['acceptedA2'],base],cwd=R).returncode==0)
check('All 341 starting files preserved',len(checkpoint['originalFiles'])==341 and all(hashlib.sha256((R/p).read_bytes()).hexdigest()==sha for p,sha in checkpoint['originalFiles'].items()))
changes=set(git('diff','--name-only',base).splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());changes.discard('')
check('Only isolated new research paths',all(p.startswith(prefix)for p in changes))
check('No deleted or overwritten starting paths',not(set(changes)&set(checkpoint['originalFiles'])))
inputs=read(B/'inputs.json');primary=inputs['cases'][0]
check('Exact binary64 inputs and unchanged pressure step',primary['inputBits']==['40dd96bbf9d4ab61','40f713b589b87e86']and primary['dp']==.01 and len(inputs['cases'])==63)
versions={'8.0.0':'ae81610e7d23efc57f9d051c8e70a4d66e87537f','7.2.0':'98b3523d5daa98454618d381d2ae53f7471d216b'}
for name in ['native','chromium','webkit']:
 for v,sha in versions.items():
  x=read(E/f'{name}-{v}.json');check(f'{name} {v} exact source provenance and complete rows',x['version']==v and x['git']==sha and len(x['rows'])==(274 if name!='native'and v=='7.2.0'else 365)and all('error'not in r for r in x['rows']))
  rr=[r for r in x['rows']if r['id']=='exact-saved'];check(f'{name} {v} original bit patterns retained',all(r['inputBits']==primary['inputBits']for r in rr))
  if name!='native':
   check(f'{name} {v} transport and repeats',all(x['transport'][k]==primary['inputBits']for k in ['json','dataView','literal','original'])and len(set(tuple(r['rhoBits'])for r in x['repetition']))==1 and len(x['repetition'])==30)
for name in ['chromium','webkit']:
 for v in versions:
  x=read(E/f'{name}-synthetic-{v}.json');check(f'{name} {v} static closure scope and complete evidence',len(x['rows'])==16 and x['physicalIPad']is False and 'No TR-BDF2' in x['warning']and all(r['settings']=={'nonlinearTolerance':1e-11,'maxIterations':30}and r['dimension']==4*r['n']+1 for r in x['rows']))
  check(f'{name} {v} reproduced expected diagnostic outcomes',sum(r['converged']for r in x['rows'])==(14 if v=='8.0.0'else 16))
for p in B.glob('*.py'):ast.parse(p.read_text());checks.append('Python syntax: '+p.name)
for p in list(B.glob('*.cjs'))+list(B.glob('*.mjs'))+list((B/'ipad').glob('*.mjs'))+list((B/'ipad').glob('*.js')):
 subprocess.run(['node','--check',str(p)],check=True,capture_output=True);checks.append('JavaScript syntax: '+str(p.relative_to(B)))
for entry in read(B/'upstream/PROVENANCE.json'):check('Pinned source digest: '+entry['file'],hashlib.sha256((B/'upstream'/entry['file']).read_bytes()).hexdigest()==entry['sha256'])
v1=read(E/'ipad-smoke-v1.json');v2=read(E/'ipad-smoke-v2.json');package=read(E/'ipad-package-v2.json')
check('Package V1 failure retained',all(not r['offlineRestart']['loaded']for r in v1['results']))
check('Package V2 manifest is the tested package',v2['packageManifest']==package['manifest'])
for name,meta in package['manifest']['assets'].items():
 if name in ['index.html','app.mjs','worker.mjs','sw.js']:source=B/'ipad'/name
 elif name=='eos.mjs' or name.startswith('vendor/'):source=B.parent/'browser_eos'/name
 else:source=B/name
 check('Tested package asset still matches source: '+name,source.stat().st_size==meta['bytes']and hashlib.sha256(source.read_bytes()).hexdigest()==meta['sha256'])
for r in v2['results']:
 check(r['browser']+' package readiness and offline restart',r['physicalIPad']is False and not r['errors'] and r['preparation']['offlinePreparation']['controller']and r['offlineRestart']['loaded']and r['offlineRestart']['fromFreshPage']and r['offlineRestart']['originDisabled'])
 for rec in r['online']+[r['offlineRestart']['record']]:
  x=rec['result'];stress=x['stress'];check(r['browser']+' '+rec['requestedVersion']+' worker evidence and error recovery',not rec['errors']and all(z['failures']==0 for z in x['throughput']+x['sustained'])and stress['validAfterError']==5 and len(stress['errors'])==5 and all(z!='Unexpected success'for z in stress['errors'])and stress['stackBefore']==stress['stackAfter']and stress['memoryBefore']==stress['memoryAfter']and x['physicalIPadQualification']is False)
for name in ['ENGINEERING_REPORT.md','MECHANICS_REPORT.md','README.md','IPAD_TEST_INSTRUCTIONS.md']:
 p=B/name;check('Completed deliverable: '+name,p.exists()and p.stat().st_size>500)
 for href in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://'not in href:check('Report local link: '+href,(B/href).exists())
root=read(E/'root-cause.json');check('Residual attribution and blocker accurately retained',root['ratio']>20 and abs(root['attributionRelativeResidual'])<1e-5)
summary=read(E/'summary.json');check('Unqualified conclusion and no physical-device claim','remains incompatible'in summary['classification']and all(not x['actualPhysicalIPad']for x in summary['ipad']))
out={'status':'PASS — complete isolated diagnostic/preparation evidence, NOT backend qualification','startingCommit':base,'branch':branch,'originalFilesPreserved':341,'researchPaths':sorted(changes),'checks':checks,'protectedLocalRefs':git('for-each-ref','--format=%(refname) %(objectname)','refs/heads/main','refs/heads/research/browser-eos-feasibility-20261012','refs/heads/research/gibbs-two-patch-feasibility-20261012','refs/heads/wip/dx-fv-stage2b-property-research-20261012').splitlines(),'noProductionChanges':True,'noCoupledTrajectories':True,'noPublishing':True,'physicalIPadTested':False}
f=E/'audit.json';text=json.dumps(out,indent=2)+'\n'
if f.exists():
 old=read(f);check('Prior completed audit conditions still hold',old['status']==out['status']and old['originalFilesPreserved']==341 and old['protectedLocalRefs']==out['protectedLocalRefs']);print('Verified without overwriting existing audit')
else:f.write_text(text)
print(out['status'],len(checks),'checks')
