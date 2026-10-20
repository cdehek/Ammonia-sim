"""Remaining schedules, one bounded process at a time; no performance claims."""
from pathlib import Path
import subprocess,sys
B=Path(__file__).resolve().parent
for f in ['cold','warm']:
 for s in ['added','fine']:
  for v in ['control','candidate','observe-control','observe-candidate']:
   subprocess.run([sys.executable,str(B/'run.py'),v,f,s,v+'-'+f+'-'+s],check=True)
  for a,b in [('control','candidate'),('control','observe-control'),('candidate','observe-candidate'),('observe-control','observe-candidate')]:
   subprocess.run(['node','--max-old-space-size=512',str(B/'verify.mjs'),a+'-'+f+'-'+s,b+'-'+f+'-'+s],check=True)
for f in ['cold','warm']:
 for a,b in [('control','observe-control'),('candidate','observe-candidate')]:subprocess.run(['node',str(B/'verify.mjs'),a+'-'+f,b+'-'+f],check=True)
