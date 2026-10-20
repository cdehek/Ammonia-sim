"""One bounded process per invocation; never chooses a longer horizon automatically."""
import argparse,gzip,json,os,platform,resource,signal,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--variant',choices=['canonical','observed','control'],default='canonical');ap.add_argument('--fixture',choices=['cold','warm'],default='cold');ap.add_argument('--horizon',type=float,choices=[.001,.002,.005,.01],default=.001);ap.add_argument('--name',required=True);ap.add_argument('--seconds',type=int,default=30);a=ap.parse_args()
assert 1<=a.seconds<=60
out=B/'evidence'/a.name;assert out.parent==B/'evidence' and not out.exists()
assert a.name.endswith('.jsonl.gz')
targets=[t for t in [.0001,.0005,.001,.002,.005,.01] if t<=a.horizon]
cmd=['node','--max-old-space-size=512',str(B/'probe.mjs'),a.variant,a.fixture,','.join(map(str,targets))]
def limit():
 os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(a.seconds,a.seconds+1));resource.setrlimit(resource.RLIMIT_FSIZE,(128*1024**2,128*1024**2))
raw=B/'.runtime'/a.name.removesuffix('.gz');raw.parent.mkdir(exist_ok=True)
start=time.monotonic();timedout=False
with raw.open('wb') as f, (B/'.runtime'/(a.name+'.stderr')).open('wb') as err:
 p=subprocess.Popen(cmd,stdout=f,stderr=err,preexec_fn=limit)
 try:code=p.wait(timeout=a.seconds)
 except subprocess.TimeoutExpired:
  timedout=True;os.killpg(p.pid,signal.SIGKILL);code=p.wait()
with raw.open('rb') as f,gzip.open(out,'wb',compresslevel=9) as z:
 for block in iter(lambda:f.read(1024*1024),b''):z.write(block)
rows=[]
for line in raw.read_text().splitlines():
 try:rows.append(json.loads(line))
 except json.JSONDecodeError:pass
check=[r for r in rows if r['type']=='checkpoint'];progress=[r for r in rows if r['type']=='partial-progress']
last=check[-1] if check else None
receipt=dict(command=cmd,wallLimitSeconds=a.seconds,cpuLimitSeconds=a.seconds,v8HeapLimitMiB=512,fileLimitMiB=128,returncode=code,timedOut=timedout,processWallSeconds=time.monotonic()-start,complete=any(r['type']=='complete' for r in rows),lastCheckpointSeconds=last['seconds'] if last else None,lastObservedAcceptedSeconds=max([r['seconds'] for r in check+progress],default=0),stderr=(B/'.runtime'/(a.name+'.stderr')).read_text(),host=dict(platform=platform.platform(),cpu=platform.processor(),logicalCPUs=os.cpu_count()),output=a.name)
receipt['terminationKind']='parent-wall-budget-kill' if timedout else 'cpu-budget-signal' if code==-signal.SIGXCPU else 'completed' if code==0 and receipt['complete'] else 'process-failure'
(out.with_suffix('.exit.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2));raw.unlink()
