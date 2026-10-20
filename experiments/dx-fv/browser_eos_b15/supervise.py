"""Sequential bounded scientific child. Output artifacts remain B15-owned."""
from pathlib import Path
import subprocess,resource,signal,time,json,gzip,sys,os
B=Path(__file__).resolve().parent;T=B/'.runtime';T.mkdir(exist_ok=True);E=B/'evidence'
name,script=sys.argv[1:3];seconds=float(sys.argv[3])if len(sys.argv)>3 else 40
assert '/'not in name and 0<seconds<=40
out=E/(name+'.json.gz');assert not out.exists()
def limits():
 os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(40,41));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,64*1024**2))
raw=T/(name+'.raw');err=T/(name+'.stderr');start=time.monotonic();killed=False
with raw.open('wb')as f,err.open('wb')as e:
 p=subprocess.Popen(['node','--max-old-space-size=512',str(B/script)],stdout=f,stderr=e,preexec_fn=limits)
 try:code=p.wait(timeout=seconds)
 except subprocess.TimeoutExpired:killed=True;os.killpg(p.pid,signal.SIGKILL);code=p.wait()
with raw.open('rb')as f,gzip.open(out,'wb')as z:
 for x in iter(lambda:f.read(1024**2),b''):z.write(x)
r={'wallSeconds':time.monotonic()-start,'wallBudgetSeconds':seconds,'cpuBudgetSeconds':40,'heapMiB':512,'returncode':code,'externalWallTermination':killed,'stderr':err.read_text(),'scientificCompletion':code==0 and not killed};(E/(name+'.exit.json')).write_text(json.dumps(r,indent=2)+'\n');raw.unlink();print(json.dumps(r));assert code==0 and not killed
