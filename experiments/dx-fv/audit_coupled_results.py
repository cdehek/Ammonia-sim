"""Independent stored-energy/face/link audit of the Stage 2A JS report.
Standard-library temperature-coordinate accounting; imports no JS or reference solver.
"""
import json
import math
import sys
from pathlib import Path

length = .003/(math.pi*.020**2/4)
tube_c = math.pi/4*(.024**2-.020**2)*length*7850*.470
fin_c = 1910*math.pi/4*(.080**2-.024**2)*.0002*2700*.900
capacities = [tube_c/5,fin_c/5]*5+[6*.718]
report=json.loads(Path(sys.argv[1]).read_text())
assert report['passed'] and report['sectionCount']==5
worst = dict(sectionMassKg=0.,sectionEnergyKJ=0.,thermalNodeKJ=0.,combinedEnergyKJ=0.,instantaneousTubeRefrigerantKW=0.)
rows=0
for case in report['cases']:
    for run in case['runs']:
        initial=run['initial']
        for sample in run['rows']:
            rows += 1
            assert sample['stop'] is None
            assert len(sample['sections'])==5 and len(sample['temperaturesK'])==11
            ledger=sample['ledger']
            faces=ledger['faces']
            heat=ledger['tubeRefrigerantKJ']
            expected_thermal=[0.]*10+[ledger['airLoadKJ']]
            combined=0.
            for i,(start,end) in enumerate(zip(initial['sections'],sample['sections'])):
                mass=end['massKg']-start['massKg']-faces[i]['massKg']+faces[i+1]['massKg']
                energy=end['internalEnergyKJ']-start['internalEnergyKJ']-faces[i]['energyKJ']+faces[i+1]['energyKJ']-heat[i]
                assert abs(mass)<1e-8 and abs(energy)<1e-6
                worst['sectionMassKg']=max(worst['sectionMassKg'],abs(mass))
                worst['sectionEnergyKJ']=max(worst['sectionEnergyKJ'],abs(energy))
                combined += end['internalEnergyKJ']-start['internalEnergyKJ']
                air_tube,air_fin,fin_tube=ledger['thermalLinksKJ'][3*i:3*i+3]
                expected_thermal[10] -= air_tube+air_fin
                expected_thermal[2*i] += air_tube+fin_tube-heat[i]
                expected_thermal[2*i+1] += air_fin-fin_tube
                calculated=.12*(sample['temperaturesK'][2*i]-(end['T']+273.15))
                difference=abs(calculated-sample['fluxes']['tubeRefrigerant'][i])
                assert difference<1e-6
                worst['instantaneousTubeRefrigerantKW']=max(worst['instantaneousTubeRefrigerantKW'],difference)
            for i,(a,b) in enumerate(zip(initial['temperaturesK'],sample['temperaturesK'])):
                change=capacities[i]*(b-a)
                residual=change-expected_thermal[i]
                assert abs(residual)<1e-6
                worst['thermalNodeKJ']=max(worst['thermalNodeKJ'],abs(residual))
                combined += change
            combined -= faces[0]['energyKJ']-faces[-1]['energyKJ']+ledger['airLoadKJ']
            assert abs(combined)<1e-6
            worst['combinedEnergyKJ']=max(worst['combinedEnergyKJ'],abs(combined))
result=dict(passed=True,source='Independent Python standard-library physical-capacity and signed face/link accounting; no JavaScript imports',rows=rows,worstResiduals=worst)
if len(sys.argv)>2:
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
