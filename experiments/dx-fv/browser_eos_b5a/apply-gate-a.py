"""Apply A1 only to an exact inherited B4C source tree; write separate patch."""
import hashlib,json,sys,difflib
from pathlib import Path
B=Path(__file__).resolve().parent; S=Path(sys.argv[1]); H=B.parent/'browser_eos_b4c/evidence/source-stage-candidateB.json'
expected=json.loads(H.read_text())['trackedSourceSHA256']
assert all(hashlib.sha256((S/f).read_bytes()).hexdigest()==h for f,h in expected.items())
files=['src/Backends/Helmholtz/VLERoutines.h','src/Backends/Helmholtz/VLERoutines.cpp','src/Backends/Helmholtz/FlashRoutines.cpp']
old={f:(S/f).read_text() for f in files}; new=dict(old)
def replace(f,a,b):
 assert new[f].count(a)==1,(f,a)
 new[f]=new[f].replace(a,b)
h,v,f=files
replace(h,'    bool use_guesses,  ///< True to start off at the values specified by rhoL, rhoV, T\n', '    // Opt-in final-state consistency and roundoff-level polishing for legacy DU.\n    bool polish_du;\n    bool use_guesses,  ///< True to start off at the values specified by rhoL, rhoV, T\n')
replace(h,'    saturation_D_pure_options()\n      : use_guesses(false),','    saturation_D_pure_options()\n      : polish_du(false),\n        use_guesses(false),')
replace(f,'            optionsD.omega = 1;\n','            optionsD.polish_du = (other == iUmolar);\n            optionsD.omega = 1;\n')
start=new[v].index('void SaturationSolvers::saturation_D_pure('); end=new[v].index('void SaturationSolvers::saturation_T_pure(',start)
chunk=new[v][start:end]
a='''        double omega = options.omega;

        if (options.imposed_rho == saturation_D_pure_options::IMPOSED_RHOL) {'''
b='''        // For DU, a saturation convergence residual alone need not resolve
        // the caloric side of the boundary. Polish the undamped coordinate
        // correction to roundoff, and return the EVALUATED coordinates rather
        // than advancing once more while leaving SatL/SatV at the old iterate.
        if (options.polish_du) {
            error = sqrt(pow(r[0], 2) + pow(r[1], 2));
            p_error = (pL - pV) / pL;
            const CoolPropDbl free_delta = options.imposed_rho == saturation_D_pure_options::IMPOSED_RHOL ? deltaV : deltaL;
            if (error <= 1e-9 && std::abs(v[0]) <= 8 * DBL_EPSILON * std::abs(tau)
                && std::abs(v[1]) <= 8 * DBL_EPSILON * (options.use_logdelta ? 1 : std::abs(free_delta))) {
                break;
            }
        }

        double omega = options.omega;

        if (options.imposed_rho == saturation_D_pure_options::IMPOSED_RHOL) {'''
assert chunk.count(a)==1;chunk=chunk.replace(a,b)
a='''        rhoL = deltaL * reduce.rhomolar;
        rhoV = deltaV * reduce.rhomolar;'''
b='''        rhoL = options.polish_du && options.imposed_rho == saturation_D_pure_options::IMPOSED_RHOL ? rhomolar : deltaL * reduce.rhomolar;
        rhoV = options.polish_du && options.imposed_rho == saturation_D_pure_options::IMPOSED_RHOV ? rhomolar : deltaV * reduce.rhomolar;'''
assert chunk.count(a)==1;chunk=chunk.replace(a,b)
assert chunk.count('} while (error > 1e-9);')==1;chunk=chunk.replace('} while (error > 1e-9);','} while (options.polish_du || error > 1e-9);')
new[v]=new[v][:start]+chunk+new[v][end:]
patch=''.join(''.join(difflib.unified_diff(old[f].splitlines(True),new[f].splitlines(True),fromfile='a/'+f,tofile='b/'+f)) for f in files)
(B/'gate-a.patch').write_text(patch)
for f in files:(S/f).write_text(new[f])
(B/'evidence/source-stage-A1.json').write_text(json.dumps(dict(trackedSourceSHA256={f:hashlib.sha256((S/f).read_bytes()).hexdigest() for f in expected},patchSHA256=hashlib.sha256(patch.encode()).hexdigest()),indent=2)+'\n')
