"""Logging-only insertion into the pinned B3 external source checkout.

No source equation, comparison, return, or tolerance is replaced. The optional
44-bit source variant must already be the exact historical B1 variant.
"""
import sys, hashlib, subprocess, os
from pathlib import Path
B = Path(__file__).resolve().parent
root = Path(sys.argv[1])
assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD']).decode().strip() == 'ae81610e7d23efc57f9d051c8e70a4d66e87537f'
header = r'''
// B3 diagnostic-only output; enabled at runtime, no additional EOS evaluation.
#include <cstdio>
#include <cstdlib>
#include <cstdarg>
static void b3trace(const char* event, const char* fmt, ...) {
    if (!std::getenv("B3_TRACE")) return;
    std::fprintf(stderr, "{\"event\":\"%s\",", event);
    va_list args; va_start(args, fmt); std::vfprintf(stderr, fmt, args); va_end(args);
    std::fprintf(stderr, "}\n");
}
'''
paths = ['src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp', 'src/Backends/Helmholtz/FlashRoutines.cpp','src/Solvers.cpp']
texts = {p:(root/p).read_text() for p in paths}
def insert(p, anchor, addition, count=1):
    assert texts[p].count(anchor) == count, (p,anchor,texts[p].count(anchor))
    texts[p] = texts[p].replace(anchor, anchor + addition)
h,f,s = paths
insert(h, '                // Start off by setting variables based on assumption that the state is two-phase', r'''
                if (other == iHmolar) b3trace("superanc_quality", "\"p\":%.17g,\"hmolar\":%.17g,\"Tsat\":%.17g,\"hf_molar\":%.17g,\"hg_molar\":%.17g,\"h_minus_hf_molar\":%.17g,\"h_minus_hg_molar\":%.17g,\"Q\":%.17g,\"below_lower\":%d,\"above_upper\":%d,\"rhoL_molar\":%.17g,\"rhoV_molar\":%.17g",
                    double(_p), double(value), double(Tsat), double(SatL->hmolar()), double(SatV->hmolar()), double(value-SatL->hmolar()), double(value-SatV->hmolar()), Q, Q < -1e-9, Q > 1+1e-9, double(SatL->rhomolar()), double(SatV->rhomolar()));
''')
# Insert before the return, after branch assignments; homogeneous branches have
# not solved density yet, so only phase and Q are emitted there.
anchor = '                }\n                return;\n            }\n        }\n\n        // Then fall back to normal ancillaries'
assert texts[h].count(anchor)==1
texts[h]=texts[h].replace(anchor, r'''                }
                if (other == iHmolar) b3trace("superanc_selected", "\"phase\":%d,\"Q\":%.17g", int(_phase), double(_Q));
                if (other == iHmolar && _phase == iphase_twophase) b3trace("superanc_lever", "\"T\":%.17g,\"rho_molar\":%.17g,\"v_molar\":%.17g", double(_T), double(_rhomolar), double(1/_rhomolar));
                return;
            }
        }

        // Then fall back to normal ancillaries''')
insert(h, '            // TODO: Check the speed penalty of these calls', r'''
            if (other == iHmolar) b3trace("vle_quality", "\"p\":%.17g,\"hmolar\":%.17g,\"Tsat\":%.17g,\"hf_molar\":%.17g,\"hg_molar\":%.17g,\"Q\":%.17g,\"below_lower\":%d,\"above_upper\":%d", double(_p), double(value), double(HEOS.SatL->T()), double(HEOS.SatL->hmolar()), double(HEOS.SatV->hmolar()), double(Q), Q < -1e-9, Q > 1+1e-9);
''')
insert(h, '        CoolPropDbl peos = HEOS->p();', r'''
        b3trace("density_residual_call", "\"T\":%.17g,\"rho_molar\":%.17g,\"p_target\":%.17g,\"p_eos\":%.17g,\"delta\":%.17g", double(T), rhomolar, double(p), double(peos), double(delta));
''')
insert(h, '    _d4alphar_dTau4 = derivs.d4alphar_dtau4;', r'''
    b3trace("alphar_cache_fill", "\"tau\":%.17g,\"delta\":%.17g,\"dar_dtau\":%.17g,\"dar_ddelta\":%.17g", double(tau), double(delta), double(derivs.dalphar_dtau), double(derivs.dalphar_ddelta));
''')
insert(h, '        _hmolar = R_u * _T * (1 + _tau.pt() * (da0_dTau + dar_dTau) + _delta.pt() * dar_dDelta);', r'''
        b3trace("homogeneous_hmolar", "\"T\":%.17g,\"rho_molar\":%.17g,\"tau\":%.17g,\"explicit_delta\":%.17g,\"dar_dtau\":%.17g,\"dar_ddelta\":%.17g,\"hmolar\":%.17g", double(_T), double(_rhomolar), double(_tau), double(_delta), double(dar_dTau), double(dar_dDelta), double(_hmolar));
''')
insert(f, '        HEOS.p_phase_determination_pure_or_pseudopure(other, value, saturation_called);', r'''
        if (other == iHmolar) b3trace("PH_dispatch", "\"p\":%.17g,\"hmolar\":%.17g,\"phase\":%d,\"homogeneous\":%d", double(HEOS._p), double(value), int(HEOS._phase), HEOS.isHomogeneousPhase());
''')
insert(f, '        HEOS._rhomolar = HEOS.solver_rho_Tp(HEOS._T, HEOS._p);', r'''
        b3trace("PT_density_assigned", "\"T\":%.17g,\"rho_molar\":%.17g,\"delta_cached_coordinate\":%.17g,\"p\":%.17g", double(HEOS._T), double(HEOS._rhomolar), double(HEOS._delta), double(HEOS._p));
''')
# Only the Householder4 region, never another solver's identical expressions.
a=texts[s].index('double Householder4('); z=texts[s].index('\n/**',a)
part=texts[s][a:z]
assert part.count('        x += dx;')==1
part=part.replace('        x += dx;', r'''        b3trace("Householder4_step", "\"iter\":%d,\"x_evaluated\":%.17g,\"fval\":%.17g,\"dx\":%.17g,\"ftol\":%.17g,\"xtol_rel\":%.17g", f->iter, x, fval, dx, ftol, xtol_rel);
        x += dx;''')
part=part.replace('            return x;', '            b3trace("Householder4_return_xtol", "\\\"x_returned\\\":%.17g", x);\n            return x;')
part=part.replace('    return x;', '    b3trace("Householder4_return", "\\\"x_returned\\\":%.17g", x);\n    return x;')
texts[s]=texts[s][:a]+part+texts[s][z:]
for p,t in texts.items(): (root/p).write_text(header+t)
diff=subprocess.check_output(['git','-C',str(root),'diff','--',*paths])
historical44='toms748_solve(f, Tmin, Tmax, resid_Tmin, resid_Tmax, boost::math::tools::eps_tolerance<double>(44), max_iter)'
target=Path(os.environ.get('B3_EVIDENCE',B/'evidence'))/('instrumentation44.diff' if historical44 in texts[f] else 'instrumentation30.diff')
assert not target.exists(), target
target.write_bytes(diff)
print('Logging-only diff:', target, hashlib.sha256(diff).hexdigest())
