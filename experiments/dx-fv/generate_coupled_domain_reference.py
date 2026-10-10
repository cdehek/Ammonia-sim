"""Independent direct-EOS pressure-edge directional diagnostic, not an accepted step.
No JavaScript imports or property-grid extension. The beyond-35-bar result is
evidence of an unsupported conservative direction, never runtime state.
"""
import json
import sys
from pathlib import Path
import CoolProp
from CoolProp import AbstractState, PQ_INPUTS, DmassUmass_INPUTS
assert CoolProp.__version__ == '7.2.0'
eos=AbstractState('HEOS','Ammonia')
eos.update(PQ_INPUTS,35e5,1)
temperature=eos.T()
mass=eos.rhomass()*.003/5
energy=mass*eos.umass()/1000
qtr=.60/5*(400-temperature)
dt=1e-6
eos.update(DmassUmass_INPUTS,mass/(.003/5),(energy+dt*qtr)*1000/mass)
result=dict(source='Independent CoolProp 7.2.0 direct D/U directional pressure-edge diagnostic',
            diagnosticOnly=True,initialPressureBar=35.,initialTemperatureK=temperature,
            cellVolumeM3=.003/5,massKg=mass,initialInternalEnergyKJ=energy,
            tubeTemperatureK=400.,cellConductanceKWK=.60/5,heatKW=qtr,diagnosticSeconds=dt,
            diagnosticPressureBar=eos.p()/1e5,pairedTubeEnergyChangeKJ=-dt*qtr,refrigerantEnergyChangeKJ=dt*qtr,
            expectedDomainSource='refrigerant')
assert result['diagnosticPressureBar']>35 and qtr>0
target=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('coupled-domain-reference.json')
target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
