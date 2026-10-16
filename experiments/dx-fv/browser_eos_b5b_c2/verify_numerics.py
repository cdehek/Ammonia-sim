"""Independent evaluator comparisons and false-certification adversaries."""
import json,os,time,statistics
from fractions import Fraction as F
from pathlib import Path
import reference as r
import local_enclosure as v
B=Path(__file__).resolve().parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'));r.precision(100)
refs=r.read(E/'references.json');checks=[]
def inside(z,interval):return F(interval['lower'])<=F(str(z))<=F(interval['upper'])
enclosures=r.read(E/'local-enclosures.json')
lookup={x['case']['key']:x for x in refs['rows']}
for row in enclosures['rows']:
 for name,target in row['targets'].items():
  if 'trials'not in target:continue
  root=lookup[row['key']]['targets'][name]['levels'][-1]
  for t in target['trials']:
   assert t['status']=='UNRESOLVED' and t['localRootExistence'] and t['localRootUnique'] and not t['physicalBranchCertified']
   assert inside(root['homogeneous']['p'],t['pressurePa']) and inside(root['stability']['cv'],t['cv'])
   assert F(t['lowerEnergyResidual']['upper'])<0 and F(t['upperEnergyResidual']['lower'])>0 and F(t['cv']['lower'])>0
checks.append(dict(check='Independent 90-digit EOS pressure and numerical derivative cv inside every 192/256-bit local enclosure',passed=True,comparisons=162))
points=[]
for d,T in [(521.53,345.56),(26.,345.57),(500.,350.),(20.,350.),(28.05137744719758,345.5636735993518)]:
 a=v.eos(v.ball(d),v.ball(T));b=r.hp.eos(r.mp.mpf(d),r.mp.mpf(T));b['cv']=r.mp.diff(lambda t:r.hp.eos(r.mp.mpf(d),t)['u'],r.mp.mpf(T))
 for k in ['p','u','cv']:assert inside(r.mp.nstr(b[k],90),v.serialize(a[k]))
 points.append(dict(rhoBits=r.bits(d),Tbits=r.bits(T),balls={k:v.serialize(a[k]) for k in ['p','u','cv']}))
checks.append(dict(check='Separate analytic ball evaluator versus inherited EOS and numerical cv differentiation',passed=True,points=points))
row=lookup['webkit-ledger-76'];t=row['targets']['exact_MUV'];d,u=[F(int(t[k]['numerator']),int(t[k]['denominator'])) for k in ['exactDensity','exactEnergyJkg']];seed=t['levels'][-1]['homogeneous']['T'];threats=[]
for label,dd,ss in [('bad seed',d,str(F(seed)+1)),('negative density',-d,seed)]:
 try:v.enclose(dd,u,ss);raise AssertionError('invalid proposal enclosed')
 except ArithmeticError as ex:threats.append(dict(hazard=label,result='NUMERICAL_FAILURE',reason=str(ex)))
wide=v.enclose(d,u,seed,radius='1e-12');assert wide['localPressureSide']=='STRADDLES' and wide['status']=='UNRESOLVED';threats.append(dict(hazard='boundary-straddling interval',result=wide))
# The Gate B homogeneous algebraic root can be locally enclosed despite being
# inside the dome. This is a deliberate demonstration of an INSUFFICIENT proof.
row=lookup['native-ledger-148'];t=row['targets']['exact_MUV'];d,u=[F(int(t[k]['numerator']),int(t[k]['denominator'])) for k in ['exactDensity','exactEnergyJkg']];z=t['levels'][-1]
assert z['branch']=='equilibrium' and not z['homogeneousStableSide']
metastable=v.enclose(d,u,z['homogeneous']['T']);assert metastable['status']=='UNRESOLVED';threats.append(dict(hazard='dome-interior homogeneous algebraic root with local cv proof',result=metastable,correctBranchDiagnostic=z['branch']))
checks.append(dict(check='False certification adversaries',passed=True,cases=threats))
p=E/'numerical-verification.json';assert not p.exists();p.write_text(json.dumps(dict(checks=checks,fullPhysicalBranchProof=False),indent=2)+'\n')
print('162 root/derivative enclosures checked; 5 independent EOS points; 4 adversaries; zero full certificates')
