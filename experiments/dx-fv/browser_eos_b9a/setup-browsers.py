"""Reuse preserved B9 pinned setup; writes only /workspace/b9-runtime. Outer 420s."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parent.parent/'browser_eos_b9/setup-browsers.py'),run_name='__main__')
