"""Bounded diagnostic direct-EOS continuation; no frozen reference writes.

Equations are the preserved independently assembled Python Stage 2B balances,
not JavaScript solver code. New evidence is separate from accepted references.
"""
import ast
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[2]
scenario, destination, mesh, source_name, rtol, maxstep = sys.argv[1:]
N, RTOL, MAXSTEP = int(mesh), float(rtol), float(maxstep)
assert scenario in ('liquid', 'extended') and N in (5, 9)
target, seed_source = Path(destination).resolve(), Path(source_name).resolve()
assert not target.is_relative_to(ROOT)
for old in ('/tmp/ammonia-stage2b-evidence','/tmp/ammonia-phase-event-evidence','/tmp/ammonia-saturation-evidence'):
    assert not target.is_relative_to(Path(old))
source = ROOT/'experiments/dx-fv/generate_coupled_stage2b_reference.py'
tree = ast.parse(source.read_text()); prefix=[]
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id=='SAMPLES' for t in node.targets):break
    prefix.append(node)
else:raise AssertionError('Missing independent equation boundary')
argv=sys.argv;sys.argv=[str(source),str(target),str(N)]
ns={'__file__':str(source)}
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(source),'exec'),ns)
sys.argv=argv
F,J,CAP=ns['FLUID'],ns['JOINT'],ns['CAPACITIES']
saved=json.loads(seed_source.read_text())
if scenario=='liquid':
    run=saved['run'];assert run['sectionCount']==N and run['interpolation']=='linear'
    seed=run['seed'];fluid=np.array([v for c in seed['cells'] for v in (c['massKg'],c['internalEnergyKJ'])])
    y0=np.r_[fluid,seed['energies'],np.zeros(ns['BUDGETS'])]
    start,end,times=0.,.1,[0.,.001,.01,.05,.1]
    inlet,load,sealed=4.,0.,True
    initialization='Identical JS canonical M/U and thermal energies; no PH reinitialization.'
else:
    cold=next(c for c in saved['cases'] if c['name']=='cold')
    hi=cold['runs'][1];row=next(r for r in hi['samples'] if r['seconds']==120)
    fluid=np.array([v for c in row['sections'] for v in (c['rho']*.003/N,c['rho']*.003/N*c['u'])])
    budgets=np.r_[np.array(row['faces']).reshape(-1),row['tubeRefrigerantKJ'],row['linksKJ'],row['airLoadKJ']]
    y0=np.r_[fluid,CAP*(np.array(row['temperaturesK'])-273.15),budgets]
    start,end,times=120.,150.,[120.,120.1,150.]
    inlet,load,sealed=3.5,0.,False
    initialization='Continuation from preserved fine direct-EOS cold checkpoint at 120 s.'
assert len(y0)==J+ns['BUDGETS']
atol=np.r_[np.tile([1e-13,1e-10],N),np.full(ns['THERMAL'],1e-10),np.full(ns['BUDGETS'],1e-10)]
rhs=lambda t,y:ns['rates'](y,inlet,load,sealed)
solution=solve_ivp(rhs,(start,end),y0,method='Radau',rtol=RTOL,atol=atol,max_step=MAXSTEP,
                   events=[ns['wet_event'],ns['domain_event']],dense_output=True)
assert solution.success and not solution.t_events[1].size

def observation(t):
    y=solution.sol(t);values=ns['states'](y);thermal=273.15+y[F:J]/CAP
    faces=y[J:ns['FACE_END']].reshape(N+1,2);tr=y[ns['FACE_END']:ns['TR_END']];links=y[ns['TR_END']:ns['LINK_END']]
    sections=[];liquid=0.
    for i,v in enumerate(values):
        sat=ns['saturation'](v['p']);q=v['quality']
        fraction=(1-q) if q is not None else (1. if v['h']<=sat['hf'] else 0.)
        M,U=y[2*i:2*i+2];liquid+=M*fraction
        sections.append(dict(**v,massKg=float(M),internalEnergyKJ=float(U),volumeM3=ns['CELL_VOLUME'],liquidMassKg=float(M*fraction)))
    derivative=rhs(t,y);delta=y-y0;budget=y[J:]-y0[J:];df=budget[:2*(N+1)].reshape(N+1,2)
    dq=budget[2*(N+1):2*(N+1)+N];dl=budget[2*(N+1)+N:2*(N+1)+4*N];air=budget[-1]
    mass=delta[:F:2]-df[:-1,0]+df[1:,0]
    energy=delta[1:F:2]-df[:-1,1]+df[1:,1]-dq
    expected=np.zeros(ns['THERMAL']);expected[-1]=air
    for i in range(N):
        qa,qf,qc=dl[3*i:3*i+3];expected[-1]-=qa+qf;expected[2*i]+=qa+qc-dq[i];expected[2*i+1]+=qf-qc
    node=delta[F:J]-expected
    combined=sum(delta[1:F:2])+sum(delta[F:J])-(df[0,1]-df[-1,1])-air
    return dict(seconds=t,sections=sections,temperaturesK=thermal.tolist(),liquidMassKg=float(liquid),
        faces=faces.tolist(),tubeRefrigerantKJ=tr.tolist(),linksKJ=links.tolist(),airLoadKJ=float(y[-1]),
        tubeRefrigerantKW=derivative[ns['FACE_END']:ns['TR_END']].tolist(),
        maximumMassResidualKg=float(max(abs(mass))),maximumFluidEnergyResidualKJ=float(max(abs(energy))),
        maximumThermalResidualKJ=float(max(abs(node))),combinedEnergyResidualKJ=float(combined),
        totalMassKg=float(sum(y[:F:2])),totalInternalEnergyKJ=float(sum(y[1:F:2])))

samples=[observation(t) for t in times]
for r in samples:
    assert N*r['maximumMassResidualKg']<1e-8
    assert N*r['maximumFluidEnergyResidualKJ']<1e-6
    assert (2*N+1)*r['maximumThermalResidualKJ']<1e-6 and abs(r['combinedEnergyResidualKJ'])<1e-6
report=dict(diagnosticOnly=True,scenario=scenario,sectionCount=N,initialization=initialization,
    seedPhysical=y0[:J].tolist(),seedVector=y0.tolist(),sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
    seedSHA256=hashlib.sha256(seed_source.read_bytes()).hexdigest(),relativeTolerance=RTOL,maxStepSeconds=MAXSTEP,
    samples=samples,terminalSaturationEventsSeconds=solution.t_events[0].tolist(),domainEventsSeconds=solution.t_events[1].tolist(),
    steps=len(solution.t)-1,evaluations=solution.nfev,jacobians=solution.njev,linearFactorizations=solution.nlu,
    versions=dict(CoolProp=ns['CoolProp'].__version__,SciPy=ns['scipy'].__version__,NumPy=np.__version__,Python=sys.version.split()[0]),
    boundaryFlashFallbacks=ns['fallbacks'],emittedWarnings=ns['warning_records'],completed=True)
target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(output=str(target),completed=True,steps=report['steps'],events=report['terminalSaturationEventsSeconds'])))
