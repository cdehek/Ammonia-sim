"""Focused original numerical limits; explicitly not complete qualification."""
import json,os
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'))
def read(n):return json.loads((E/n).read_text())
rows=[]
for r in read('matrix.json')['rows']:
 raw=r['actual']['chromium']['raw']['values'];s=r['targets']['exact_MUV']['highPrecisionReference']['selected'];diff={k:float(F(raw[k])-F(s[k])) for k in ['p','h','T']}
 limits=dict(p=10,h=50,T=.01);assert all(abs(diff[k])<v for k,v in limits.items())
 rows.append(dict(key=r['key'],exactInventoryReferenceDifferences=diff,standaloneNumericalBudgetsPass=True,originalPhaseQualification=r['originalScientificQualification'],fullScientificQualificationClaimed=False))
ref=read('references.json');changes=[float(t['pressureRepeatDifferencePa']) for row in ref['rows'] for t in row['targets'].values() if 'pressureRepeatDifferencePa'in t]
assert max(changes)<1e-45
seven=[r for r in read('matrix.json')['rows'] if r['group']=='rows']
assert sum(float(r['targets']['rounded_DU']['pressureMinusLimitPaDiagnostic'])<0 for r in seven)==2
assert sum(float(r['targets']['exact_MUV']['pressureMinusLimitPaDiagnostic'])<0 for r in seven)==1
widths=[]
for r in read('local-enclosures.json')['rows']:
 for t in r['targets'].values():
  for z in t.get('trials',[]):
   if 'pressurePa'in z:widths.append(float(F(z['pressurePa']['upper'])-F(z['pressurePa']['lower'])))
out=dict(rows=rows,standaloneNumericalRows=len(rows),canonicalRows=33,maxStandaloneDifferences={k:max(abs(r['exactInventoryReferenceDifferences'][k]) for r in rows) for k in ['p','h','T']},max65vs90PressureDifferencePa=max(changes),localPressureWidthMaxPa=max(widths),historicalRoundedDUInsideCount=2,exactMUVInsideCount=1,
 originalBudgets=dict(canonical=dict(pPa=.1,hJkg=.1,TK=.0001),standaloneStrict=dict(pPa=10,hJkg=50,TK=.01),normalizedMassEnergy=1e-11,independentReferenceResolution=dict(pPa=1e-5,energyJkg=1e-8),maxPressurePa=3500000),fullBackendQualified=False,fullA2Run=False,physicalBranchCertified=False)
p=E/'scientific-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('37 independent standalone numerical comparisons; original phase/qualification limits retained')
