"""Logging-only instrumentation of the verified B4C native source.

No extra EOS evaluation, changed arithmetic, tolerance, dispatch or returned
coordinate. Stores a unified diff and exact originals for independent review.
Run only after preserving the rebuilt uninstrumented library.
"""
import difflib,sys,hashlib,json
from pathlib import Path
import os
B=Path(__file__).resolve().parent;S=Path(sys.argv[1]);O=Path(os.environ.get('B5_EVIDENCE',B/'evidence'))/'instrumentation';O.mkdir(exist_ok=True)
prefix='''#include <cstdio>
#include <cstdlib>
namespace {
inline void b5log(const char* event, double a=0, double b=0, double c=0, double d=0) {
 if (std::getenv("B5_TRACE")) std::fprintf(stderr,"{\\"event\\":\\"%s\\",\\"a\\":%.17g,\\"b\\":%.17g,\\"c\\":%.17g,\\"d\\":%.17g}\\n",event,a,b,c,d);
}
}
'''
diff=[];hashes={}
for filename in ['FlashRoutines.cpp','VLERoutines.cpp','Solvers.cpp']:
 relative='src/'+filename if filename=='Solvers.cpp'else'src/Backends/Helmholtz/'+filename
 p=S/relative;original=p.read_text();(O/filename).write_text(original);text=original
 def replace(a,b):
  global text
  assert text.count(a)==1,(filename,a,text.count(a));text=text.replace(a,b)
 if filename=='FlashRoutines.cpp':
  replace('void FlashRoutines::HSU_D_flash(HelmholtzEOSMixtureBackend& HEOS, parameters other) {','void FlashRoutines::HSU_D_flash(HelmholtzEOSMixtureBackend& HEOS, parameters other) {\n    b5log("DU_entry_rhomolar_umolar_config",HEOS._rhomolar,HEOS._umolar,get_config_bool(ENABLE_SUPERANCILLARIES),other);')
  # Work only within HSU_D_flash_twophase; no other residual is touched.
  a=text.index('void FlashRoutines::HSU_D_flash_twophase');b=text.index('// D given and one of P,H,S,U',a)
  section=text[a:b];section=section.replace('return Qo - Qd;','b5log("legacy_two_phase_residual_T_Qo_Qd_diff",T,Qo,Qd,Qo-Qd);\n            return Qo - Qd;')
  section=section.replace('Brent(resid, Tmin_sat, Tmax_sat - 0.01, DBL_EPSILON, 1e-12, 20);','b5log("legacy_two_phase_bracket",Tmin_sat,Tmax_sat-0.01,1e-12,20);\n    const double b5_Treturn=Brent(resid, Tmin_sat, Tmax_sat - 0.01, DBL_EPSILON, 1e-12, 20);\n    b5log("legacy_two_phase_return_Treturn_Tstate_Qd",b5_Treturn,HEOS._T,resid.Qd);')
  text=text[:a]+section+text[b:]
  replace('// ===================== legacy ancillary "sad path" =====================','// ===================== legacy ancillary "sad path" =====================\n        b5log("legacy_enter_rhomolar_umolar",HEOS._rhomolar,HEOS._umolar);')
  replace('for (int i_try = 0; i_try < 7; i_try++) {','for (int i_try = 0; i_try < 7; i_try++) {\n                b5log("satD_attempt_i_omega_maxiter_rho",i_try,optionsD.omega,optionsD.max_iterations,HEOS._rhomolar);')
  replace('if (value > Sat->keyed_output(other)) {','const CoolPropDbl b5_satvalue=Sat->keyed_output(other);\n            b5log("legacy_phase_value_satValue_satT_satRho",value,b5_satvalue,Sat->_T,Sat->_rhomolar);\n            if (value > b5_satvalue) {')
  replace('T_converged = Halley(resid, 0.5 * (Sat->keyed_output(iT) + HEOS.Tmax() * 1.5), 1e-10, 100);','b5log("legacy_homogeneous_seed_Tmin_Tmax",0.5*(Sat->keyed_output(iT)+HEOS.Tmax()*1.5),Sat->keyed_output(iT),HEOS.Tmax()*1.5);\n                    T_converged = Halley(resid, 0.5 * (Sat->keyed_output(iT) + HEOS.Tmax() * 1.5), 1e-10, 100);')
  # These temperature/limit getters read fixed coordinates, not additional EOS calls.
  replace('HSU_D_flash_twophase(HEOS, HEOS._rhomolar, other, value);','b5log("legacy_dispatch_two_phase",HEOS._rhomolar,value);\n                    HSU_D_flash_twophase(HEOS, HEOS._rhomolar, other, value);')
  replace('const double resid = Qo - Qd;','const double resid = Qo - Qd;\n            b5log("SA_two_phase_residual_T_Qo_Qd_diff",T,Qo,Qd,resid);')
  replace('const double eos = HEOS->keyed_output(other);','const double eos = HEOS->keyed_output(other);') if False else None
  a=text.index('void FlashRoutines::HSU_D_flash(');b=text.index('// ===================== legacy ancillary',a)
  section=text[a:b];assert section.count('double eos = HEOS->keyed_output(other);')==1
  section=section.replace('double eos = HEOS->keyed_output(other);','double eos = HEOS->keyed_output(other);\n            b5log("DU_homogeneous_residual_T_rho_eos_target",T,rhomolar,eos,value);')
  section=section.replace('const double a = edges[i], b = edges[i + 1];','const double a = edges[i], b = edges[i + 1];\n                        b5log("SA_interval",i,a,b,HEOS._rhomolar);')
  section=section.replace('HEOS.update(QT_INPUTS, std::clamp(Qd_final, 0.0, 1.0), Tsol);','b5log("SA_commit_T_Q",Tsol,Qd_final);\n                            HEOS.update(QT_INPUTS, std::clamp(Qd_final, 0.0, 1.0), Tsol);')
  text=text[:a]+section+text[b:]
 elif filename=='VLERoutines.cpp':
  a=text.index('void SaturationSolvers::saturation_D_pure(');b=text.index('void SaturationSolvers::saturation_T_pure(',a)
  section=text[a:b]
  section=section.replace('do {','b5log("satD_seed_T_rhoL_rhoV_omega",T,rhoL,rhoV,options.omega);\n    do {\n        b5log("satD_eval_T_rhoL_rhoV_iter",T,rhoL,rhoV,iter);',1)
  section=section.replace('v = linsolve(J, r);','b5log("satD_residual_r0_r1_pL_pV",r[0],r[1],pL,pV);\n        v = linsolve(J, r);\n        b5log("satD_step_dtau_ddelta_omega",v[0],v[1],options.omega);')
  section=section.replace('iter++;','b5log("satD_advanced_T_error_pError",T,error,p_error);\n        iter++;')
  section=section.replace('CoolPropDbl p_error_limit = 1e-3;','b5log("satD_exit_Tadvanced_TL_TV_error",T,SatL->T(),SatV->T(),error);\n    CoolPropDbl p_error_limit = 1e-3;')
  text=text[:a]+section+text[b:]
 else:
  a=text.index('double Brent(FuncWrapper1D*');b=text.index('}; /* namespace CoolProp */',a)
  section=text[a:b]
  section=section.replace('fa = f->call(a);','b5log("Brent_entry_a_b_t_maxiter",a,b,t,maxiter);\n    fa = f->call(a);',1)
  section=section.replace('return b;','b5log("Brent_return_b_fb_iter_threshold",b,fb,iter,2*macheps*std::abs(b));\n            return b;')
  section=section.replace('return a;','b5log("Brent_return_a_fa_iter_t",a,fa,iter,t);\n        return a;')
  # Give each return an unambiguous source label, without altering conditions.
  section=section.replace('if (std::abs(fb) < t) {','if (std::abs(fb) < t) {\n        b5log("Brent_stop_boundary_b",b,fb,t);')
  section=section.replace('if (std::abs(fa) < t) {','if (std::abs(fa) < t) {\n        b5log("Brent_stop_boundary_a",a,fa,t);')
  section=section.replace('if (std::abs(fb) < macheps) {','if (std::abs(fb) < macheps) {\n            b5log("Brent_stop_machine_residual",b,fb,macheps);')
  section=section.replace('if (std::abs(fb) < 2 * macheps * std::abs(b)) {','if (std::abs(fb) < 2 * macheps * std::abs(b)) {\n            b5log("Brent_stop_scaled_residual",b,fb,2*macheps*std::abs(b));')
  # Final return follows loop termination; earlier returns have their tags.
  pos=section.rfind('b5log("Brent_return_b_fb_iter_threshold"');section=section[:pos]+'b5log("Brent_stop_loop_m_tol_fb",m,tol,fb);\n    '+section[pos:]
  text=text[:a]+section+text[b:]
 text=prefix+text
 p.write_text(text);hashes[filename]=dict(before=hashlib.sha256(original.encode()).hexdigest(),after=hashlib.sha256(text.encode()).hexdigest())
 diff.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='a/'+relative,tofile='b/'+relative))
(O/'logging-only.patch').write_text(''.join(diff));(O/'hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
