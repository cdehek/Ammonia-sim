"""Adapt original B3 logging to either PT commit; never add an EOS evaluation."""
import os,sys,subprocess,difflib
from pathlib import Path
B=Path(__file__).resolve().parent;S=Path(sys.argv[1]);E=Path(sys.argv[2]);E.mkdir(exist_ok=True)
paths=['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp','src/Backends/Helmholtz/FlashRoutines.cpp','src/Solvers.cpp'];before={p:(S/p).read_text()for p in paths}
script=(B.parent/'browser_eos_b3/instrument.py').read_text()
if '        HEOS.update_DmolarT_direct(rhomolar, T);' in before[paths[1]][before[paths[1]].index('void FlashRoutines::PT_flash('):before[paths[1]].index('// Define the residual',before[paths[1]].index('void FlashRoutines::PT_flash('))]:
 script=script.replace("insert(f, '        HEOS._rhomolar = HEOS.solver_rho_Tp(HEOS._T, HEOS._p);',", "insert(f, '        HEOS.update_DmolarT_direct(rhomolar, T);',")
 # This exact line is unique in the selected source.
env=os.environ.copy();env['B3_EVIDENCE']=str(E)
script='__file__='+repr(str(B.parent/'browser_eos_b3/instrument.py'))+'\n'+script
subprocess.run([sys.executable,'-c',script,str(S)],env=env,check=True)
h=S/paths[0];t=h.read_text();start=t.index('void HelmholtzEOSMixtureBackend::update_DmolarT_direct(');end=t.index('\nvoid ',start+1);part=t[start:end]
anchor='    post_update(optional_checks);';assert part.count(anchor)==1
part=part.replace(anchor,anchor+r'''
    b3trace("DT_commit", "\"T\":%.17g,\"rho_molar\":%.17g,\"delta\":%.17g,\"tau\":%.17g,\"p\":%.17g", double(_T), double(_rhomolar), double(_delta), double(_tau), double(_p));
''');h.write_text(t[:start]+part+t[end:])
f=S/paths[1];t=f.read_text();start=t.index('void FlashRoutines::HSU_P_flash_singlephase_Brent(');end=t.index('// P given and one of H, S, or U',start);part=t[start:end];anchor='        double call(double T) override {';assert part.count(anchor)==1
part=part.replace(anchor,anchor+r'''
            b3trace("homogeneous_eval", "\"other\":%d,\"T\":%.17g", int(other), T);
''');f.write_text(t[:start]+part+t[end:])
logging=''.join(''.join(difflib.unified_diff(before[p].splitlines(True),(S/p).read_text().splitlines(True),fromfile='a/'+p,tofile='b/'+p))for p in paths)
(E/'logging-only.patch').write_text(logging)
for p,t in before.items():
 target=E/Path(p).name;target.write_text(t) # exact restoration after diagnostic build
