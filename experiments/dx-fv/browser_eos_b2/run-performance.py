"""Replay the unchanged B1 matched workload into new B2 evidence only.

Run after every other numerical worker exits. The sole harness substitutions
select build30/build44 and redirect output; original workload text is unchanged.
"""
import hashlib,os
from pathlib import Path
B=Path(__file__).resolve().parent
script=B.parent/'browser_eos_backend/run_performance.py'
text=script.read_text()
old="(['official8','build30','build44','official72'] if name=='chromium' else ['official72','build44','build30','official8'])"
assert text.count(old)==1
text=text.replace(old,"(['build30','build44'] if name=='chromium' else ['build44','build30'])")
assert text.count("f=B/'evidence'/")==1
text=text.replace("f=B/'evidence'/",f"f=Path({os.environ.get('B2_EVIDENCE',str(B/'evidence'))!r})/")
exec(compile(text,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
