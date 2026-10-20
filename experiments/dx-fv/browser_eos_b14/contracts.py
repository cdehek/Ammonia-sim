import gzip,json,os,resource,signal,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent;out=B/'evidence/domain-and-rollback.json.gz';assert not out.exists()
def limits():
 os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(40,41));resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
t=time.monotonic();p=subprocess.Popen(['node','--max-old-space-size=512',str(B/'contracts.mjs')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits)
try:raw,err=p.communicate(timeout=40)
except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);raw,err=p.communicate();raise RuntimeError('External budget termination')
assert p.returncode==0,err.decode();assert json.loads(raw)['passed'];out.write_bytes(gzip.compress(raw,mtime=0))
(B/'evidence/contracts.exit.json').write_text(json.dumps(dict(returncode=p.returncode,wallSeconds=time.monotonic()-t,wallLimitSeconds=40,cpuLimitSeconds=40,heapMiB=512,processGroupTermination=True,passed=True),indent=2)+'\n')
print('PASS: domain/refusal/rollback exact A2/B9C/observed')
