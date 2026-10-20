"""Six paired comparisons per workload; clean sequential, bounded child processes."""
from pathlib import Path
import subprocess,resource,signal,os,time,json,sys
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--out-file',default='evidence/timing-samples.json');args=parser.parse_args()
B=Path(__file__).resolve().parent;E=B/'evidence';dest=(B/args.out_file).resolve();assert dest.is_relative_to(B) and not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
# Fail closed: performance is forbidden until every required science/contract gate passes.
assert json.loads((E/'property-summary.json').read_text())['passed']
import gzip
assert json.loads(gzip.decompress((E/'regressions.json.gz').read_bytes()))['passed']
for f in ['cold','warm']:
 for s in ['', '-added','-fine']:
  for left,right in [('control','candidate'),('control','observe-control'),('candidate','observe-candidate'),('observe-control','observe-candidate')]:
   x=json.loads((E/('equivalence-'+left+'-'+f+s+'--'+right+'-'+f+s+'.json')).read_text());assert x['passed']
   assert x['sources']['right']['sha256']==json.loads((E/'build-manifest.json').read_text())['builds'][right]['sha256']
   if left=='observe-control':assert x['conservation']['passed'] and x['actualMatricesAndCorrectionsCompared']>0
assert json.loads((E/'external-termination-validation.json').read_text())['passed']
assert json.loads(gzip.decompress((E/'isolation.json.gz').read_bytes()))['passed']
for f in ['cold','warm']:
 for s in ['original','added','fine']:
  browser=json.loads((E/('browser-'+f+'-'+s+'.json')).read_text());assert browser['passed'] and browser['sourceBuilds']['observe-candidate']==json.loads((E/'build-manifest.json').read_text())['builds']['observe-candidate']['sha256']
assert json.loads(gzip.decompress((E/'interface-regression.json.gz').read_bytes()))['passed']
rows=[]
def run(v,k,pair,order):
 def limits():
  os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(40,41));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(4*1024**2,4*1024**2))
 start=time.monotonic();p=subprocess.Popen(['node','--max-old-space-size=512',str(B/'benchmark.mjs'),v,k],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,preexec_fn=limits)
 try:out,err=p.communicate(timeout=40)
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate();rows.append({'variant':v,'kind':k,'pair':pair,'order':order,'externalWallTermination':True,'returncode':p.returncode});dest.write_text(json.dumps(rows,indent=2)+'\n');raise
 assert p.returncode==0,(out,err)
 x=json.loads(out);x.update(pair=pair,order=order,processWallMS=(time.monotonic()-start)*1000,limits={'wallSeconds':40,'cpuSeconds':40,'heapMiB':512},stderr=err);rows.append(x);dest.write_text(json.dumps(rows,indent=2)+'\n')
for k in ['ph','cold','warm']:
 for pair,order in enumerate(['AB','BA','BA','AB','AB','BA'],1):
  for v in order:run('control'if v=='A'else'candidate',k,pair,order)
# Separate count-only and no inner timing observations, outside primary sample statistics.
for f in ['cold','warm']:
 for v in ['control','candidate']:run('count-'+v,f,0,'count-only')
 for v in ['control','candidate']:run(v,'notimer-'+f,0,'no-inner-timer')
print('Retained',len(rows),'bounded samples; six pairs per primary workload')
