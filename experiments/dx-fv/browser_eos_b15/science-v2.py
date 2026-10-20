"""Fresh corrected-candidate replay against byte-unchanged original controls."""
from pathlib import Path
import subprocess,sys
B=Path(__file__).resolve().parent
for f in ['cold','warm']:
 for s in ['original','added','fine']:
  suffix='-'+f+(''if s=='original'else'-'+s)
  for v in ['candidate','observe-candidate']:subprocess.run([sys.executable,str(B/'run.py'),v,f,s,v+suffix],check=True)
  for a,b in [('control','candidate'),('control','observe-control'),('candidate','observe-candidate'),('observe-control','observe-candidate')]:subprocess.run(['node','--max-old-space-size=512',str(B/'verify.mjs'),a+suffix,b+suffix],check=True)
for name,script in [('regressions','regressions.mjs'),('isolation','isolation.mjs'),('edge-ownership','edge-node.mjs')]:subprocess.run([sys.executable,str(B/'supervise.py'),name,script],check=True)
