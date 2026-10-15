"""Generate a one-expression controlled patch, verifying the exact input hash."""
from pathlib import Path
import hashlib, difflib, sys

root = Path(sys.argv[1]).resolve()
rel = 'src/Backends/Helmholtz/FlashRoutines.cpp'
path = root / rel
original = path.read_bytes()
assert hashlib.sha256(original).hexdigest() == 'debf60f85d1d0955f08596e64d3a4958d7f369657cb3161a6b7625fa508cf3df'
old = 'auto [l, r] = toms748_solve(f, Tmin, Tmax, resid_Tmin, resid_Tmax, boost::math::tools::eps_tolerance<double>(30), max_iter);'
new = old.replace('(30)', '(44)')
text = original.decode()
assert text.count(old) == 1
changed = text.replace(old, new)
patch = ''.join(difflib.unified_diff(text.splitlines(True), changed.splitlines(True), fromfile='a/'+rel, tofile='b/'+rel))
out = Path(__file__).resolve().parent
(out / 'flash-44.patch').write_text(patch)
path.write_text(changed)
print(hashlib.sha256(original).hexdigest(), hashlib.sha256(path.read_bytes()).hexdigest())
