"""Local artifact and offline replay; no remote hosting or deployment."""
import os,sys
from pathlib import Path
B=Path(__file__).resolve().parent;old=B.parent/'browser_eos_backend'
E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
mode=sys.argv.pop(1)
script=old/('package_ipad.py' if mode=='package' else 'smoke_offline.py')
text=script.read_text()
if mode=='package':
 original="evidence_path=B/'evidence'/(sys.argv[2] if len(sys.argv)>2 else 'ipad-package.json')"
 assert text.count(original)==1
 text=text.replace(original,f"evidence_path=Path({str(E/'offline-package.json')!r})")
else:
 original="f=B/'evidence'/(sys.argv[2] if len(sys.argv)>2 else 'ipad-offline-smoke.json')"
 assert text.count(original)==1
 text=text.replace(original,f"f=Path({str(E/('offline-origin-only.json' if '--origin-only' in sys.argv else 'offline-context.json'))!r})")
exec(compile(text,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
