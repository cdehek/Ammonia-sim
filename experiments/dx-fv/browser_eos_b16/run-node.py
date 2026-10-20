"""Sequential fresh-process paired campaign; interrupted evidence never counted valid."""
from pathlib import Path
import subprocess,resource,signal,os,time,json,argparse,gzip,hashlib
B=Path(__file__).resolve().parent;E=B/'evidence'
p=argparse.ArgumentParser();p.add_argument('campaign',choices=['primary','counters','jitless','trace']);p.add_argument('--name');a=p.parse_args()
dest=E/((a.name or 'node-'+a.campaign)+'.json');assert not dest.exists()
science=E/'chromium-science.json'
assert json.loads(science.read_text() if science.exists() else gzip.decompress((E/'chromium-science.json.gz').read_bytes()))['passed'],'browser science must pass first'
for name,x in json.loads((E/'copied-assets.json').read_text()).items():assert hashlib.sha256((B/name).read_bytes()).hexdigest()==x['sha256'],'frozen source mismatch: '+name
orders=['AB','BA','BA','AB','AB','BA'];rows=[]
def run(variant,kind,warmups,pair,order,flags):
 def limits():
  os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(60,61));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024**2,16*1024**2))
 cmd=['node','--max-old-space-size=512',*flags,str(B/'benchmark-node.mjs'),variant,kind,str(warmups)]
 start=time.monotonic();child=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,preexec_fn=limits);timeout=False
 try:out,err=child.communicate(timeout=65)
 except subprocess.TimeoutExpired:timeout=True;os.killpg(child.pid,signal.SIGKILL);out,err=child.communicate()
 lines=out.splitlines();receipts=[x[len('B16_RESULT '):]for x in lines if x.startswith('B16_RESULT ')]
 row={'variant':variant,'kind':kind,'warmups':warmups,'pair':pair,'order':order,'flags':flags,'externalWallTermination':timeout,'returncode':child.returncode,'processWallMS':(time.monotonic()-start)*1000,'limits':{'wallSeconds':65,'cpuSeconds':60,'heapMiB':512},'stderr':err}
 if len(receipts)==1:row.update(json.loads(receipts[0]))
 if a.campaign=='trace':
  trace='\n'.join(x for x in lines if not x.startswith('B16_RESULT '))+'\n'+err
  path=E/f'trace-{variant}-{kind}.txt.gz';assert not path.exists();path.write_bytes(gzip.compress(trace.encode(),mtime=0));row['traceFile']=path.name;row['traceLines']=len(trace.splitlines())
 rows.append(row);dest.write_text(json.dumps(rows,indent=2)+'\n')
 print(f'{a.campaign}: {kind} warmups={warmups} pair={pair} {variant} rc={child.returncode}',flush=True)
 assert child.returncode==0 and not timeout and len(receipts)==1,row
if a.campaign=='primary':
 for warmups in [0,2]:
  for kind in ['cold','warm']:
   for pair,order in enumerate(orders,1):
    for v in order:run('control' if v=='A' else 'candidate',kind,warmups,pair,order,[])
 for pair,order in enumerate(orders,1):
  for v in order:run('control' if v=='A' else 'candidate','ph',0,pair,order,[])
elif a.campaign=='counters':
 for kind in ['cold','warm']:
  for pair,order in enumerate(orders,1):
   for v in order:run('count-control' if v=='A' else 'count-candidate',kind,0,pair,order,[])
elif a.campaign=='jitless':
 for kind in ['cold','warm']:
  for pair,order in enumerate(orders[:3],1):
   for v in order:run('control' if v=='A' else 'candidate',kind,0,pair,order,['--jitless'])
else:
 for kind in ['cold','warm']:
  for variant in ['control','candidate']:run(variant,kind,0,0,'observed',['--trace-opt','--trace-deopt','--trace-turbo-inlining','--trace-file-names','--trace-gc-nvp'])
