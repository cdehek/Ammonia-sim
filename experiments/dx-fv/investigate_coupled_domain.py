"""Direct-EOS versus actual JS table availability diagnostic; no frozen edits.
The JS probe is authoritative for runtime availability and separate from EOS
physical support. This script does not change reference trajectory integration.
"""
import json
import math
import subprocess
import sys
from pathlib import Path
import CoolProp
from CoolProp.CoolProp import PropsSI

assert CoolProp.__version__ == '7.2.0'
node = sys.argv[1]
root = Path(__file__).resolve().parents[2]
grid = json.loads((root/'properties.json').read_text())
cases = [(0.32,200.05),(0.3,200.05),(0.5,200.05),(3.5,240.),(3.5,267.),(3.5,278.15)]
points=[]
for p,t in cases:
    h=PropsSI('Hmass','P',p*1e5,'T',t,'Ammonia')/1000
    rho=PropsSI('Dmass','P',p*1e5,'T',t,'Ammonia')
    u=PropsSI('Umass','P',p*1e5,'T',t,'Ammonia')/1000
    sat=PropsSI('T','P',p*1e5,'Q',0,'Ammonia')
    nominal=min(p-.3,35-p,250-(t-sat),30-(sat-t))
    logs=[math.log(v) for v in grid['p']]
    i=next((i for i in range(len(logs)-1) if logs[i]<=math.log(p)<logs[i+1]),len(logs)-2)
    last=max(j for j in range(len(grid['sc'])) if grid['liquid'][i][j] and grid['liquid'][i+1][j])
    # Actual property mask is inspected diagnostically, not used to turn the
    # independent direct-EOS reference into an interpolation-table solver.
    max_subcool=grid['sc'][last] if last==len(grid['sc'])-1 else max(0,grid['sc'][last]-1e-7)
    points.append(dict(p=p,h=h,temperatureK=t,rho=rho,u=u,directEOSSaturationK=sat,nominalReferenceMargin=nominal,
        runtimePressureBracketBar=grid['p'][i:i+2],runtimeLiquidMaxSubcoolK=max_subcool))
probe=subprocess.run([node,str(root/'experiments/dx-fv/coupled-runtime-support.cjs')],input=json.dumps(points),text=True,capture_output=True,check=True)
runtime=json.loads(probe.stdout)
for point,result in zip(points,runtime['points']):point['runtime']=result
example=points[0]
assert example['nominalReferenceMargin']>0
assert example['runtime']['ph']['supported'] is False
assert example['runtime']['ph']['kind']=='domain'
result=dict(stage='2A-R',CoolProp=CoolProp.__version__,node=runtime['runtime'],points=points,passed=True,
    interpretation='Direct-EOS physical support, nominal reference envelope and actual table availability are distinct. PH availability, table-inventory recovery and EOS-inventory recovery are reported separately; a failed inversion does not alone establish a physical trajectory exit.',
    proposedFutureTest='Batch reference samples and safeguarded boundary brackets through the unchanged runtime PH and M/U/V probes in a separate qualification check. Keep independent EOS integration/refinement intact. To terminate references at matching interpolation limits, independently reproduce the table generation pressure brackets and missing-liquid mask, cross-check against this authoritative runtime probe, and bracket the continuous boundary; require separate approval before changing frozen references.')
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,example=example)))
