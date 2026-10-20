"""Supplemental process-wide V8 GC observations, excluded from timing statistics."""
from pathlib import Path
import subprocess,resource,signal,os,json,re,gzip,time
B=Path(__file__).resolve().parent;E=B/'evidence';rows=[]
for f in ['cold','warm']:
 for v in ['control','candidate']:
  def limits():
   os.setsid();resource.setrlimit(resource.RLIMIT_CPU,(40,41));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
  p=subprocess.Popen(['node','--max-old-space-size=512','--trace-gc-nvp',str(B/'benchmark.mjs'),v,f],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,preexec_fn=limits)
  try:out,err=p.communicate(timeout=40)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();raise
  assert p.returncode==0,err
  name='gc-'+v+'-'+f;assert not(E/(name+'.log.gz')).exists();(E/(name+'.log.gz')).write_bytes(gzip.compress(out.encode()));pauses=[float(m)for m in re.findall(r'\bpause=([0-9.]+)',out)];rows.append({'variant':v,'fixture':f,'gcEvents':len(pauses),'processWidePauseMS':sum(pauses),'maxPauseMS':max(pauses,default=0),'stderr':err,'scope':'Entire fresh process, including initialization and record, trace instrumentation perturbs runtime; not timed advance attribution or primary sample'})
(E/'gc-observations.json').write_text(json.dumps(rows,indent=2)+'\n');print('Retained four supplemental V8 GC traces')
