"""Apply only the reviewed PT state commit, requiring exact B4A sources."""
import hashlib,json,subprocess,sys,difflib,os
from pathlib import Path
B=Path(__file__).resolve().parent;S=Path(sys.argv[1]);E=Path(os.environ.get('B4B_EVIDENCE',B/'evidence'))
assert subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD']).decode().strip()=='ae81610e7d23efc57f9d051c8e70a4d66e87537f'
assert not (E/'source-stage-candidateB.json').exists(), 'Choose a fresh replay evidence directory'
before=json.loads((E/'source-stage-controlA.json').read_text())['trackedSourceSHA256']
for n,h in before.items():assert hashlib.sha256((S/n).read_bytes()).hexdigest()==h,n
p='src/Backends/Helmholtz/FlashRoutines.cpp';f=S/p;old=f.read_text();anchor='        HEOS._rhomolar = HEOS.solver_rho_Tp(HEOS._T, HEOS._p);'
assert old.count(anchor)==1
new=old.replace(anchor,'''        const CoolPropDbl T = HEOS._T;
        const CoolPropDbl rhomolar = HEOS.solver_rho_Tp(T, HEOS._p);
        // Commit the solved coordinates and invalidate residual-trial property caches.
        HEOS.update_DmolarT_direct(rhomolar, T);''')
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+p,tofile='b/'+p))
target=B/'pt-cache-consistency.patch'
if target.exists():assert target.read_text()==patch
else:target.write_text(patch)
f.write_text(new)
after={n:hashlib.sha256((S/n).read_bytes()).hexdigest()for n in before}
assert [n for n in before if before[n]!=after[n]]==[p]
(E/'source-stage-candidateB.json').write_text(json.dumps(dict(trackedSourceSHA256=after,patchSHA256=hashlib.sha256(patch.encode()).hexdigest(),algorithmSHA256=hashlib.sha256((B/'ALGORITHM.md').read_bytes()).hexdigest()),indent=2)+'\n')
print(patch)
