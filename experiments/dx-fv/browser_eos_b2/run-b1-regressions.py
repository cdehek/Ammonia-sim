"""Re-execute the complete original property/precision matrix into B2 evidence."""
import os
from pathlib import Path
B=Path(__file__).resolve().parent;old=B.parent/'browser_eos_backend'
E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
script=old/'run_browser.py';text=script.read_text()
# Both writer and skip check must point to the new evidence directory.
text=text.replace("B / 'evidence'",f"Path({str(E)!r})").replace("B/'evidence'",f"Path({str(E)!r})")
exec(compile(text,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
