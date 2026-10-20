from pathlib import Path
import subprocess,sys
B=Path(__file__).resolve().parent;E=B/'evidence'
for f in ['cold','warm']:
 for suffix in ['.jsonl.gz','.exit.json']:(E/('init-candidate-'+f+suffix)).rename(E/('prototype-v1-init-candidate-'+f+suffix))
 subprocess.run([sys.executable,str(B/'run.py'),'observe-candidate',f,'original','init-candidate-'+f,'--horizon','0.0000001'],check=True)
for suffix in ['.jsonl.gz','.exit.json']:(E/('external-budget'+suffix)).rename(E/('prototype-v1-external-budget'+suffix))
(E/'external-termination-validation.json').rename(E/'prototype-v1-external-termination-validation.json')
r=subprocess.run([sys.executable,str(B/'run.py'),'candidate','warm','original','external-budget','--seconds','1']);assert r.returncode!=0
subprocess.run(['node',str(B/'verify-termination.mjs')],check=True)
subprocess.run(['node','--max-old-space-size=512',str(B/'compact.mjs')],check=True)
subprocess.run(['node','--max-old-space-size=512',str(B/'verify-compaction.mjs')],check=True)
subprocess.run(['node','--max-old-space-size=512',str(B/'analyze.mjs')],check=True)
