"""Optional logging only in classifier and homogeneous pressure-flash evaluator.

No generic solver edit, no extra EOS evaluation, no changed decision or return.
"""
import difflib,sys
from pathlib import Path
S=Path(sys.argv[1]);E=Path(sys.argv[2]);E.mkdir(exist_ok=False)
paths=['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp','src/Backends/Helmholtz/FlashRoutines.cpp']
header=r'''
// B4C diagnostic logging only. Set B4C_TRACE to enable.
#include <cstdio>
#include <cstdlib>
#include <cstdarg>
static void b4ctrace(const char* event,const char* fmt,...) {
 if (!std::getenv("B4C_TRACE")) return;
 std::fprintf(stderr,"{\"event\":\"%s\",",event);
 va_list args;va_start(args,fmt);std::vfprintf(stderr,fmt,args);va_end(args);
 std::fprintf(stderr,"}\n");
}
'''
before={p:(S/p).read_text() for p in paths};texts=before.copy();h,f=paths
anchor='                // Start off by setting variables based on assumption that the state is two-phase'
assert texts[h].count(anchor)==1
texts[h]=texts[h].replace(anchor,r'''
                b4ctrace("superanc_quality", "\"other\":%d,\"p\":%.17g,\"value_molar\":%.17g,\"Tsat\":%.17g,\"Q\":%.17g,\"hf_molar\":%.17g,\"hg_molar\":%.17g,\"rhoL_molar\":%.17g,\"rhoV_molar\":%.17g", int(other),double(_p),double(value),double(Tsat),double(Q),double(SatL->hmolar()),double(SatV->hmolar()),double(SatL->rhomolar()),double(SatV->rhomolar()));
'''+anchor)
anchor='            // TODO: Check the speed penalty of these calls'
assert texts[h].count(anchor)==1
texts[h]=texts[h].replace(anchor,r'''
            b4ctrace("vle_quality", "\"other\":%d,\"p\":%.17g,\"value_molar\":%.17g,\"Tsat\":%.17g,\"Q\":%.17g,\"hf_molar\":%.17g,\"hg_molar\":%.17g,\"rhoL_molar\":%.17g,\"rhoV_molar\":%.17g", int(other),double(_p),double(value),double(HEOS.SatV->T()),double(Q),double(HEOS.SatL->hmolar()),double(HEOS.SatV->hmolar()),double(HEOS.SatL->rhomolar()),double(HEOS.SatV->rhomolar()));
'''+anchor)
anchor='        HEOS.p_phase_determination_pure_or_pseudopure(other, value, saturation_called);'
assert texts[f].count(anchor)==1
texts[f]=texts[f].replace(anchor,anchor+r'''
        b4ctrace("caloric_dispatch", "\"other\":%d,\"p\":%.17g,\"value_molar\":%.17g,\"phase\":%d,\"homogeneous\":%d,\"saturation_called\":%d", int(other),double(HEOS._p),double(value),int(HEOS._phase),HEOS.isHomogeneousPhase(),saturation_called);
''')
start=texts[f].index('void FlashRoutines::HSU_P_flash_singlephase_Brent(');end=texts[f].index('// P given and one of H, S, or U',start);part=texts[f][start:end];anchor='        double call(double T) override {';assert part.count(anchor)==1
part=part.replace(anchor,anchor+r'''
            b4ctrace("homogeneous_eval", "\"other\":%d,\"T\":%.17g",int(other),T);
''');texts[f]=texts[f][:start]+part+texts[f][end:]
for p in paths:
 (E/Path(p).name).write_text(before[p]);(S/p).write_text(header+texts[p])
(E/'logging-only.patch').write_text(''.join(''.join(difflib.unified_diff(before[p].splitlines(True),(header+texts[p]).splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p in paths))
