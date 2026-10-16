"""Logging-only native build: decision/dispatch and homogeneous evaluation count."""
import os
import hashlib,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;S=Path(sys.argv[1]);E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'))
header=r'''
// B4A diagnostics only. No additional thermodynamic evaluation.
#include <cstdio>
#include <cstdlib>
#include <cstdarg>
static void b4atrace(const char* event, const char* fmt, ...) {
    if (!std::getenv("B4A_TRACE")) return;
    std::fprintf(stderr, "{\"event\":\"%s\",", event);
    va_list args; va_start(args, fmt); std::vfprintf(stderr, fmt, args); va_end(args);
    std::fprintf(stderr, "}\n");
}
'''
paths=['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp','src/Backends/Helmholtz/FlashRoutines.cpp']
texts={p:(S/p).read_text()for p in paths};original=dict(texts)
h,f=paths
anchor='                // Start off by setting variables based on assumption that the state is two-phase'
assert texts[h].count(anchor)==1
texts[h]=texts[h].replace(anchor,anchor+r'''
                b4atrace("superanc_quality", "\"other\":%d,\"p\":%.17g,\"value\":%.17g,\"Q\":%.17g,\"liquid_dispatch\":%d", other, double(_p), double(value), double(Q), Q < -1e-9 || (Q < 0 && (other == iHmolar || other == iSmolar || other == iUmolar)));
''')
anchor='            // TODO: Check the speed penalty of these calls';assert texts[h].count(anchor)==1
texts[h]=texts[h].replace(anchor,anchor+r'''
            b4atrace("vle_quality", "\"other\":%d,\"p\":%.17g,\"value\":%.17g,\"Q\":%.17g,\"liquid_dispatch\":%d", other, double(_p), double(value), double(Q), Q < -1e-9 || (Q < 0 && (other == iHmolar || other == iSmolar || other == iUmolar)));
''')
anchor='        HEOS.p_phase_determination_pure_or_pseudopure(other, value, saturation_called);';assert texts[f].count(anchor)==1
texts[f]=texts[f].replace(anchor,anchor+r'''
        b4atrace("HSU_dispatch", "\"other\":%d,\"p\":%.17g,\"value\":%.17g,\"phase\":%d,\"homogeneous\":%d", int(other), double(HEOS._p), double(value), int(HEOS._phase), HEOS.isHomogeneousPhase());
''')
start=texts[f].index('void FlashRoutines::HSU_P_flash_singlephase_Brent(')
end=texts[f].index('// P given and one of H, S, or U',start)
region=texts[f][start:end];anchor='        double call(double T) override {';assert region.count(anchor)==1
region=region.replace(anchor,anchor+r'''
            b4atrace("homogeneous_eval", "\"other\":%d,\"T\":%.17g", int(other), T);
''');texts[f]=texts[f][:start]+region+texts[f][end:]
for p,t in texts.items():(S/p).write_text(header+t)
diff=subprocess.check_output(['git','-C',str(S),'diff','--',*paths]);target=E/'combined-instrumented.patch';assert not target.exists();target.write_bytes(diff)
# Standalone logging diff applies on top of the uninstrumented repaired stage.
import difflib
logging=''.join(''.join(difflib.unified_diff(original[p].splitlines(True),(header+texts[p]).splitlines(True),fromfile='a/'+p,tofile='b/'+p))for p in paths)
(E/'logging-only.patch').write_text(logging)
print('Instrumented source written',hashlib.sha256(diff).hexdigest())
