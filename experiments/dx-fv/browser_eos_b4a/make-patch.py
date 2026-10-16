"""Apply the reviewed liquid-dispatch change to pinned B1 source44 only."""
import hashlib, subprocess, sys
from pathlib import Path
S=Path(sys.argv[1]); B=Path(__file__).resolve().parent
assert subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD']).decode().strip()=='ae81610e7d23efc57f9d051c8e70a4d66e87537f'
f=S/'src/Backends/Helmholtz/FlashRoutines.cpp'
assert hashlib.sha256(f.read_bytes()).hexdigest()=='9e6d3be44cc61c3ca5b539fa10f4587cfeef3e286dec2d267fe90933df67c0e3'
p=S/'src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp'
original=subprocess.check_output(['git','-C',str(S),'show','HEAD:src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp'])
assert p.read_bytes()==original
t=original.decode(); start=t.index('void HelmholtzEOSMixtureBackend::p_phase_determination_pure_or_pseudopure(');end=t.index('void HelmholtzEOSMixtureBackend::calc_ssat_max()',start)
region=t[start:end];assert region.count('if (Q < -1e-9) {')==2
replacement='''// Resolve negative caloric quality by the existing bounded liquid flash.
{indent}// Saturation uncertainty does not permit extrapolating mixture volume.
{indent}if (Q < -1e-9 || (Q < 0 && (other == iHmolar || other == iSmolar || other == iUmolar))) {'''
for indent in ['                ','            ']:
 anchor=indent+'if (Q < -1e-9) {'
 assert region.count(anchor+'\n'+indent+'    this->_phase')==1
 region=region.replace(anchor+'\n'+indent+'    this->_phase',indent+replacement.replace('{indent}',indent)+'\n'+indent+'    this->_phase',1)
p.write_text(t[:start]+region+t[end:])
diff=subprocess.check_output(['git','-C',str(S),'diff','--','src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp'])
target=B/'liquid-classification.patch'
if target.exists():assert target.read_bytes()==diff
else:target.write_bytes(diff)
print('liquid patch SHA256',hashlib.sha256(diff).hexdigest())
