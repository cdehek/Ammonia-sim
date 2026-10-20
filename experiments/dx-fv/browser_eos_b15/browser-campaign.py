from pathlib import Path
import subprocess,sys
B=Path(__file__).resolve().parent
for case in ['properties','edges','interface',*[f+'-'+s for f in ['cold','warm']for s in ['original','added','fine']]]:subprocess.run([sys.executable,str(B/'browser.py'),case],check=True)
