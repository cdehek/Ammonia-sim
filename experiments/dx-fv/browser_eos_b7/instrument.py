"""Two-unit logging only; no generic solvers or additional EOS evaluations."""
import argparse,difflib,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';W=Path('/workspace/b7-work');S=W/'upstream'
p=argparse.ArgumentParser();p.add_argument('label',choices=['control','candidate']);p.add_argument('--restore',action='store_true');a=p.parse_args();O=W/f'diagnostic-{a.label}';O.mkdir(exist_ok=True)
prefix='''#include <cstdio>
#include <cstdlib>
namespace {
inline void b7log(const char* event, double a=0, double b=0, double c=0, double d=0) {
 if(std::getenv("B7_TRACE")) std::fprintf(stderr,"{\\"event\\":\\"%s\\",\\"a\\":%.17g,\\"b\\":%.17g,\\"c\\":%.17g,\\"d\\":%.17g}\\n",event,a,b,c,d);
}
}
'''
diff=[];hashes={}
expected=json.loads((E/f'source-{a.label}.json').read_text())['trackedSourceSHA256']
for name in ['FlashRoutines.cpp','VLERoutines.cpp']:
 relative='src/Backends/Helmholtz/'+name;path=S/relative
 if a.restore:
  path.write_bytes((O/name).read_bytes());assert hashlib.sha256(path.read_bytes()).hexdigest()==expected[relative];continue
 original=path.read_text();assert hashlib.sha256(path.read_bytes()).hexdigest()==expected[relative]
 (O/name).write_text(original);text=original
 def replace(left,right):
  global text
  assert text.count(left)==1,(name,left,text.count(left));text=text.replace(left,right)
 if name=='FlashRoutines.cpp':
  replace('void FlashRoutines::HSU_D_flash(HelmholtzEOSMixtureBackend& HEOS, parameters other) {','void FlashRoutines::HSU_D_flash(HelmholtzEOSMixtureBackend& HEOS, parameters other) {\n    b7log("HSU_D_entry_rho_u_config_other",HEOS._rhomolar,HEOS._umolar,get_config_bool(ENABLE_SUPERANCILLARIES),other);')
  replace('// ===================== legacy ancillary "sad path" =====================','// ===================== legacy ancillary "sad path" =====================\n        b7log("legacy_DU_entry",HEOS._rhomolar,HEOS._umolar);')
  replace('optionsD.max_iterations = 200;','optionsD.max_iterations = 200;\n            b7log("DU_saturation_options_polish_other",'+('optionsD.polish_du' if a.label=='candidate' else '0')+',other,HEOS._rhomolar,optionsD.max_iterations);')
  replace('if (value > Sat->keyed_output(other)) {','const CoolPropDbl b7_satvalue=Sat->keyed_output(other);\n            b7log("DU_caloric_value_satvalue_T_rho",value,b7_satvalue,Sat->_T,Sat->_rhomolar);\n            if (value > b7_satvalue) {')
  replace('HSU_D_flash_twophase(HEOS, HEOS._rhomolar, other, value);','b7log("legacy_dispatch_twophase",HEOS._rhomolar,value);\n                    HSU_D_flash_twophase(HEOS, HEOS._rhomolar, other, value);')
 else:
  left=text.index('void SaturationSolvers::saturation_D_pure(');right=text.index('void SaturationSolvers::saturation_T_pure(',left);section=text[left:right]
  section=section.replace('    std::vector<CoolPropDbl> r(2, _HUGE), v;','    b7log("saturation_D_entry_rho_polish_imposed_iterations",rhomolar,'+('options.polish_du' if a.label=='candidate' else '0')+',options.imposed_rho,options.max_iterations);\n    std::vector<CoolPropDbl> r(2, _HUGE), v;')
  section=section.replace('SatV->update(DmolarT_INPUTS, rhoV, T);','SatV->update(DmolarT_INPUTS, rhoV, T);\n        b7log("saturation_D_evaluated_T_rhoL_rhoV_iteration",T,rhoL,rhoV,iter);')
  section=section.replace('v = linsolve(J, r);','b7log("saturation_D_residual_r0_r1_pL_pV",r[0],r[1],pL,pV);\n        v = linsolve(J, r);\n        b7log("saturation_D_correction_tau_delta_tau",v[0],v[1],tau);')
  section=section.replace('CoolPropDbl p_error_limit = 1e-3;','b7log("saturation_D_final_T_rhoL_rhoV_error",T,rhoL,rhoV,error);\n    b7log("saturation_D_cached_TL_rhoL_TV_rhoV",SatL->T(),SatL->rhomolar(),SatV->T(),SatV->rhomolar());\n    CoolPropDbl p_error_limit = 1e-3;')
  text=text[:left]+section+text[right:]
 text=prefix+text;path.write_text(text)
 hashes[relative]=dict(original=hashlib.sha256(original.encode()).hexdigest(),diagnostic=hashlib.sha256(text.encode()).hexdigest())
 diff.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='a/'+relative,tofile='b/'+relative))
if a.restore:
 assert all(hashlib.sha256((S/n).read_bytes()).hexdigest()==h for n,h in expected.items())
 print(a.label,'complete uninstrumented manifest restored')
else:
 (E/f'diagnostic-{a.label}.patch').write_text(''.join(diff))
 (E/f'diagnostic-{a.label}-source.json').write_text(json.dumps(dict(files=hashes,genericSolversUnchanged=hashlib.sha256((S/'src/Solvers.cpp').read_bytes()).hexdigest()==expected['src/Solvers.cpp'],onlyLogging=True),indent=2)+'\n')
 print(a.label,'two-unit logging applied')
