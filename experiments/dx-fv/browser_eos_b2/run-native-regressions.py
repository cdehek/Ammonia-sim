"""Unchanged complete native reference program; fresh B2 output directory."""
import os
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
script=B.parent/'browser_eos/reference.py';text=script.read_text()
original="E=B/'evidence'";assert text.count(original)==1
text=text.replace(original,f"E=Path({str(E)!r})")
exec(compile(text,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
