"""Independent whole-domain EOS/property audit; no accepted files are written."""
import json
import math
import sys
from pathlib import Path
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator
import CoolProp
from CoolProp.CoolProp import PropsSI

ROOT = Path(__file__).resolve().parents[2]
target = Path(sys.argv[2]).resolve()
assert not target.is_relative_to(ROOT)
rows = json.loads(Path(sys.argv[1]).read_text())
data = json.loads((ROOT / 'properties.json').read_text())
x, temperatures = np.log(data['p']), np.array(data['sat'])[:, 0]
curve = PchipInterpolator(x, temperatures, extrapolate=False)

def stats(values):
    a = np.array(values)
    return dict(maximumAbsolute=float(np.max(np.abs(a))), rms=float(np.sqrt(np.mean(a*a))),
                medianAbsolute=float(np.median(np.abs(a))), percentile95Absolute=float(np.percentile(np.abs(a), 95)))

sat, property_errors = [], {k: [] for k in ('hf', 'hg', 'sf', 'sg', 'rhof', 'rhog')}
for r in rows['saturation']:
    p, a, b = r['p'], r['baseline'], r['candidate']
    truth = PropsSI('T', 'P', p*1e5, 'Q', 0, 'Ammonia') - 273.15
    independent = float(curve(math.log(p)))
    assert abs(independent-b['T']) < 1e-11
    Tk = truth+273.15
    liquid, gas = {}, {}
    for name, prop in [('h', 'Hmass'), ('s', 'Smass'), ('rho', 'Dmass')]:
        scale = 1 if name == 'rho' else .001
        liquid[name] = scale*PropsSI(prop, 'P', p*1e5, 'Q', 0, 'Ammonia')
        gas[name] = scale*PropsSI(prop, 'P', p*1e5, 'Q', 1, 'Ammonia')
    for key in property_errors:
        kind = liquid if key.endswith('f') else gas
        field = key[:-1] if not key.startswith('rho') else 'rho'
        property_errors[key].append(a[key]-kind[field])
        assert a[key] == b[key]
    latent, entropy, dv = a['hg']-a['hf'], a['sg']-a['sf'], 1/a['rhog']-1/a['rhof']
    i = min(len(x)-2, max(0, int(np.searchsorted(x, math.log(p), side='right')-1)))
    slope = (temperatures[i+1]-temperatures[i])/(x[i+1]-x[i])
    # Clausius-Clapeyron: dT/dlog(p) = 100*p*T*(vg-vf)/(hg-hf),
    # using bar, kg, kJ. Existing h/s/rho interpolation is deliberately unchanged.
    sat.append(dict(p=p,truthC=truth,linearErrorK=a['T']-truth,candidateErrorK=b['T']-truth,
                    scipyAgreementK=b['T']-independent,
                    gibbsLinearKJkg=latent-(a['T']+273.15)*entropy,
                    gibbsCandidateKJkg=latent-(b['T']+273.15)*entropy,
                    clapeyronLinearRelative=slope/(100*p*(a['T']+273.15)*dv/latent)-1,
                    clapeyronCandidateRelative=r['derivativeLogPressure']/(100*p*(b['T']+273.15)*dv/latent)-1))

groups = {}
for r in rows['states']:
    trueT = PropsSI('T', 'P', r['p']*1e5, 'Hmass', r['h']*1e3, 'Ammonia')-273.15
    a, b = r['baseline'], r['candidate']
    groups.setdefault(r['kind'], []).append(dict(p=r['p'],h=r['h'],truthC=trueT,
        linearErrorK=a['T']-trueT,candidateErrorK=b['T']-trueT))

def comparison(r):
    return dict(linear=stats([v['linearErrorK'] for v in r]),candidate=stats([v['candidateErrorK'] for v in r]),
                points=len(r),pointwiseWorsened=sum(abs(v['candidateErrorK'])>abs(v['linearErrorK'])+1e-12 for v in r))

report = dict(diagnosticOnly=True, method=rows['method'], samplesImmutable=True, propertyTestsPassed=rows['passed'],
    versions=dict(python=sys.version.split()[0],CoolProp=CoolProp.__version__,SciPy=scipy.__version__,NumPy=np.__version__),
    saturationAccuracy=comparison(sat), regionAccuracy={key:comparison(values) for key,values in groups.items()},
    unchangedOtherSaturationErrors={key:stats(values) for key,values in property_errors.items()},
    consistency={key:stats([v[key] for v in sat]) for key in ['gibbsLinearKJkg','gibbsCandidateKJkg','clapeyronLinearRelative','clapeyronCandidateRelative']},
    saturationSamples=sat,regionSamples=groups,unsupportedNativeConditions=rows['unsupported'])
report['generalSaturationImprovement'] = all(report['saturationAccuracy']['candidate'][key] < report['saturationAccuracy']['linear'][key] for key in ['maximumAbsolute','rms'])
report['regionRegressions'] = [kind for kind, errors in report['regionAccuracy'].items()
    if any(errors['candidate'][key] > errors['linear'][key]+1e-10 for key in ['maximumAbsolute','rms'])]
report['passed'] = report['generalSaturationImprovement'] and not report['regionRegressions']
report['stopRequired'] = not report['passed']
report['interpretation'] = ('Property candidate rejected at focused gate; no event/integration qualification permitted.'
    if report['stopRequired'] else 'Focused property gate only; trajectory qualification remains required.')
target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({key:report[key] for key in ['passed','stopRequired','regionRegressions','saturationAccuracy','regionAccuracy','consistency']}))
assert report['passed']
