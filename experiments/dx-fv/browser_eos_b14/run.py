"""Sequential bounded child processes. Never retry a failed scientific run."""
import argparse,gzip,json,os,resource,signal,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';T=B/'.runtime';T.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('variant',choices=['canonical','observed','capture','control']);p.add_argument('fixture',choices=['cold','warm']);p.add_argument('schedule',choices=['original','added','fine']);p.add_argument('name');p.add_argument('--out-dir',default='evidence');p.add_argument('--horizon',type=float,default=.01);p.add_argument('--seconds',type=int,default=40);a=p.parse_args()
E=(B/a.out_dir).resolve();assert E.is_relative_to(B);E.mkdir(parents=True,exist_ok=True)
assert 0<a.horizon<=.01 and 1<=a.seconds<=45 and '/' not in a.name
out=E/(a.name+'.jsonl.gz');assert not out.exists()
cmd=['node','--max-old-space-size=512',str(B/'probe.mjs'),a.variant,a.fixture,a.schedule,str(a.horizon)]
def limits():
 os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(a.seconds,a.seconds+1));resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,64*1024**2));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
start=time.monotonic();timeout=False;raw=T/(a.name+'.jsonl');err=T/(a.name+'.stderr')
with raw.open('wb')as f,err.open('wb')as e:
 child=subprocess.Popen(cmd,stdout=f,stderr=e,preexec_fn=limits)
 try:code=child.wait(timeout=a.seconds)
 except subprocess.TimeoutExpired:timeout=True;os.killpg(child.pid,signal.SIGKILL);code=child.wait()
rows=[]
for line in raw.read_text().splitlines():
 try:rows.append(json.loads(line))
 except json.JSONDecodeError:pass
with raw.open('rb')as f,gzip.open(out,'wb',compresslevel=9)as z:
 for block in iter(lambda:f.read(1024**2),b''):z.write(block)
checks=[r for r in rows if r['type']=='checkpoint'];complete=next((r for r in rows if r['type']=='complete'),None)
receipt=dict(command=cmd,wallLimitSeconds=a.seconds,cpuLimitSeconds=a.seconds,v8HeapLimitMiB=512,fileLimitMiB=64,processGroupTermination=True,returncode=code,timedOut=timeout,wallSeconds=time.monotonic()-start,complete=complete,lastCheckpointSeconds=checks[-1]['seconds']if checks else None,lastIndependentlyAcceptedSeconds=max([r['seconds']for r in rows if r['type']in ['checkpoint','partial-progress']],default=0),stderr=err.read_text(),uncompressedBytes=raw.stat().st_size,compressedBytes=out.stat().st_size,terminationKind='external-wall-budget'if timeout else 'external-cpu-budget'if code==-signal.SIGXCPU else 'completed'if code==0 and complete else 'process-failure')
(E/(a.name+'.exit.json')).write_text(json.dumps(receipt,indent=2)+'\n');raw.unlink()
print(json.dumps({k:v for k,v in receipt.items()if k not in ['command','complete']},indent=2))
if code!=0 or not complete:raise SystemExit('STOP: failed/refused run, inspect receipt before any further experiment')
