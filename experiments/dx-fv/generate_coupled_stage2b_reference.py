"""Stage 2B five/nine-cell direct-EOS conserved-state reference; no JavaScript imports.
Independent SciPy Radau, same declared closures/EOS source, not plant validation.
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import CoolProp
from CoolProp import AbstractState, HmassP_INPUTS, DmassUmass_INPUTS, DmassT_INPUTS, PQ_INPUTS

assert CoolProp.__version__ == '7.2.0'
assert scipy.__version__ == '1.16.2'
assert np.__version__ == '2.5.3'
eos = AbstractState('HEOS', 'Ammonia')
fallbacks = 0
N = int(sys.argv[2]) if len(sys.argv)>2 else 9
assert N in (5, 9), 'Only five and nine meshes are authorized'
VOLUME, DIAMETER = .003, .020
FLUID, THERMAL = 2*N, 2*N+1
JOINT = FLUID+THERMAL
# Record emitted Radau warnings without suppressing them or changing its RHS/Jacobian.
import inspect
import warnings
warning_records=[]
original_showwarning=warnings.showwarning
def record_warning(message,category,filename,lineno,file=None,line=None):
    item=dict(message=str(message),category=category.__name__,file=filename,line=lineno)
    frame=inspect.currentframe().f_back
    while frame is not None:
        if frame.f_code.co_filename==filename:
            factor=frame.f_locals.get('factor')
            if isinstance(factor,np.ndarray):
                large=np.flatnonzero((~np.isfinite(factor))|(np.abs(factor)>1e300)).tolist()
                item.update(largeFactorColumns=large,passiveLedgerColumns=[i for i in large if i>=JOINT],physicalColumns=[i for i in large if i<JOINT])
            break
        frame=frame.f_back
    warning_records.append(item)
    original_showwarning(message,category,filename,lineno,file,line)
warnings.showwarning=record_warning
FACE_END = JOINT+2*(N+1)
TR_END = FACE_END+N
LINK_END = TR_END+3*N
BUDGETS = 2*(N+1)+N+3*N+1
AREA = math.pi*DIAMETER**2/4
CELL_VOLUME = VOLUME/N
LENGTH = VOLUME/AREA
FACES = [(LENGTH/N/2, 1000)] + [(LENGTH/N, 0)]*(N-1) + [(LENGTH/N/2, 2)]
# Independently derive all capacities and exposed areas from the declared inputs.
TUBE_C = math.pi/4*(.024**2-.020**2)*LENGTH*7850*.470
FIN_PLAN = math.pi/4*(.080**2-.024**2)
FIN_C = 1910*FIN_PLAN*.0002*2700*.900
AIR_C = 6*.718
G_AT = math.pi*.024*(LENGTH-1910*.0002)*50/1000
G_AF = 1910*(2*FIN_PLAN+math.pi*.080*.0002)*50/1000
CAPACITIES = np.array([TUBE_C/N, FIN_C/N]*N+[AIR_C])
LINKS = [item for i in range(N) for item in [(2*N,2*i,G_AT/N),(2*N,2*i+1,G_AF/N),(2*i+1,2*i,2/N)]]

def snapshot():
    p, h, t, rho = eos.p()/1e5, eos.hmass()/1000, eos.T()-273.15, eos.rhomass()
    q = eos.Q()
    return dict(p=p, h=h, T=t, rho=rho, u=eos.umass()/1000, quality=q if 0 <= q <= 1 else None)

def ph(p, h):
    eos.update(HmassP_INPUTS, h*1000, p*1e5)
    return snapshot()

def mu(mass, energy):
    global fallbacks
    rho, u = mass/CELL_VOLUME, energy*1000/mass
    try:
        eos.update(DmassUmass_INPUTS, rho, u)
    except ValueError as error:
        if 'Input vapor quality' not in str(error):
            raise
        def residual(t):
            eos.update(DmassT_INPUTS, rho, t)
            return eos.umass()-u
        temperature = brentq(residual, 200, 600, xtol=1e-10)
        eos.update(DmassT_INPUTS, rho, temperature)
        if abs(eos.umass()-u) > 1e-4:
            raise RuntimeError('Independent D/T fallback failed energy recovery')
        fallbacks += 1
    return snapshot()

def saturation(p):
    eos.update(PQ_INPUTS, p*1e5, 0)
    hf, t = eos.hmass()/1000, eos.T()-273.15
    eos.update(PQ_INPUTS, p*1e5, 1)
    return dict(hf=hf, hg=eos.hmass()/1000, T=t)

def states(y):
    return [mu(*y[2*i:2*i+2]) for i in range(N)]

def initial(name):
    warm = name in ('warm', 'heat-reversal')
    s = ph(3.65 if warm else 3.5, 1650 if warm else 500)
    fluid = np.tile([s['rho']*CELL_VOLUME, s['rho']*CELL_VOLUME*s['u']], N)
    metal_warm = name == 'warm'
    temperatures = np.array([293.15 if metal_warm else 273.15]*FLUID+[293.15 if metal_warm else 278.15])
    if name == 'nonuniform':
        bins=[(0.,.27,3.5,500.),(.27,.64,3.5,600.),(.64,1.,3.5,700.)]
        fluid=np.zeros(FLUID)
        for i in range(N):
            left,right=i/N,(i+1)/N
            for a,b,p,h in bins:
                overlap=max(0.,min(right,b)-max(left,a));state=ph(p,h)
                fluid[2*i]+=VOLUME*overlap*state['rho']
                fluid[2*i+1]+=VOLUME*overlap*state['rho']*state['u']
            for k,profile in enumerate([[(0.,.43,273.15),(.43,1.,290.)],[(0.,.61,278.15),(.61,1.,288.)]]):
                temperatures[2*i+k]=N*sum(max(0.,min(right,b)-max(left,a))*t for a,b,t in profile)
        temperatures[-1]=293.15
    return np.r_[fluid, CAPACITIES*(temperatures-273.15), np.zeros(BUDGETS)]

def rates(y, inlet_p, load, sealed):
    refrigerant = states(y)
    nodes = [ph(inlet_p, 500)]+refrigerant+[ph(3.5, 1700)]
    fluxes = []
    for i, (length, minor) in enumerate(FACES):
        left, right = nodes[i:i+2]
        dp = (left['p']-right['p'])*1e5
        donor = left if dp >= 0 else right
        linear = 128*1e-5*length/(math.pi*DIAMETER**4*donor['rho'])
        quadratic = (.02*length/DIAMETER+minor)/(2*donor['rho']*AREA**2)
        flow = 0. if sealed else math.copysign(2*abs(dp)/(linear+math.sqrt(linear**2+4*quadratic*abs(dp))), dp)
        fluxes.append([flow, flow*donor['h']])
    temperatures = 273.15+y[FLUID:JOINT]/CAPACITIES
    thermal = np.zeros(THERMAL)
    thermal[2*N] = load
    links = []
    for source, destination, conductance in LINKS:
        q = conductance*(temperatures[source]-temperatures[destination])
        thermal[source] -= q
        thermal[destination] += q
        links.append(q)
    qtr = np.array([.60/N*(temperatures[2*i]-(refrigerant[i]['T']+273.15)) for i in range(N)])
    thermal[0:FLUID:2] -= qtr
    fluid = np.array(fluxes[:-1])-np.array(fluxes[1:])
    fluid[:,1] += qtr
    return np.r_[fluid.reshape(FLUID), thermal, np.array(fluxes).reshape(2*(N+1)), qtr, links, load]

def domain_event(t, y):
    values = states(y)
    margins = []
    for s in values:
        sat = saturation(s['p'])
        margins += [s['p']-.3, 35-s['p'], 250-(s['T']-sat['T']), 30-(sat['T']-s['T'])]
    temperatures = 273.15+y[FLUID:JOINT]/CAPACITIES
    return min(*margins, float(np.min(temperatures)-200), float(400-np.max(temperatures)))
domain_event.terminal = True
domain_event.direction = -1

def wet_event(t, y):
    s = mu(*y[FLUID-2:FLUID])
    return s['h']-saturation(s['p'])['hg']
wet_event.direction = 0

SAMPLES = {
    'cold':[.01,.05,.2,1,5,15,30,60,120],
    'warm':[.01,.05,.2,1,5,15,30,60,120],
    'load-step':[.01,.2,1,5,15,15.1,20,30,30.1,45,60],
    'feed-step':[.01,.2,1,5,15,15.01,15.1,20,30,30.01,30.1,45,60],
    'heat-reversal':[.01,.05,.2,1,5,15,30,60],
}
if len(sys.argv)>3:
    if sys.argv[3]=='nonuniform':
        SAMPLES={'nonuniform':[.01,.05,.2,1,5,15,30,60]}
    elif sys.argv[3]=='extended':
        SAMPLES={'extended':[.01,.2,1,5,15,30,60,120,120.1,150,180,180.1,210,240,240.1,270,300,360]}
    else:
        SAMPLES={sys.argv[3]:SAMPLES[sys.argv[3]]}

def sample(t, y, y0):
    fluid = states(y)
    faces = y[JOINT:FACE_END].reshape(N+1,2)
    qtr, links, load = y[FACE_END:TR_END], y[TR_END:LINK_END], y[LINK_END]
    node_integrals = np.zeros(THERMAL)
    node_integrals[2*N] = load
    for (source,destination,_), integral in zip(LINKS,links):
        node_integrals[source] -= integral
        node_integrals[destination] += integral
    node_integrals[0:FLUID:2] -= qtr
    initial_fluid = y0[:FLUID].reshape(N,2)
    current_fluid = y[:FLUID].reshape(N,2)
    budgets = current_fluid-initial_fluid-faces[:-1]+faces[1:]
    budgets[:,1] -= qtr
    thermal_residuals = y[FLUID:JOINT]-y0[FLUID:JOINT]-node_integrals
    combined = np.sum(current_fluid[:,1]-initial_fluid[:,1])+np.sum(y[FLUID:JOINT]-y0[FLUID:JOINT])-(faces[0,1]-faces[-1,1])-load
    return dict(seconds=t, sections=fluid, temperaturesK=(273.15+y[FLUID:JOINT]/CAPACITIES).tolist(),
                faces=faces.tolist(), tubeRefrigerantKJ=qtr.tolist(), linksKJ=links.tolist(), airLoadKJ=float(load),
                maximumMassResidualKg=float(np.max(np.abs(budgets[:,0]))), maximumFluidEnergyResidualKJ=float(np.max(np.abs(budgets[:,1]))),
                maximumThermalResidualKJ=float(np.max(np.abs(thermal_residuals))), combinedEnergyResidualKJ=float(combined))

def run(name, tolerance, max_step):
    y0 = initial(name)
    y = y0.copy()
    inlet, load = 4., 1.
    targets = SAMPLES[name]
    changes = {15:2.,30:1.} if name=='load-step' else {15:4.3,30:4.} if name=='feed-step' else {}
    if name=='extended': changes={120:(3.5,0.),180:(3.3,0.),240:(4.,1.)}
    boundaries = sorted(set([0,targets[-1],*changes]))
    samples, events, domains = [], [], []
    steps = evaluations = 0
    for a,b in zip(boundaries[:-1],boundaries[1:]):
        solution = solve_ivp(lambda t,y:rates(y,inlet,load,name=='heat-reversal'),(a,b),y,method='Radau',rtol=tolerance,
            atol=np.r_[np.tile([1e-13,1e-10],N),np.full(THERMAL,1e-10),np.full(BUDGETS,1e-10)],
            max_step=max_step,events=[wet_event,domain_event],dense_output=True)
        if not solution.success:
            raise RuntimeError(solution.message)
        steps += len(solution.t)-1
        evaluations += solution.nfev
        events += solution.t_events[0].tolist()
        domains += solution.t_events[1].tolist()
        samples += [sample(t,solution.sol(t),y0) for t in targets if a<t<=solution.t[-1]]
        y = solution.y[:,-1]
        if domains:
            break
        if b in changes:
            if name=='extended': inlet,load=changes[b]
            elif name=='load-step': load=changes[b]
            else: inlet=changes[b]
    return dict(relativeTolerance=tolerance, maxStepSeconds=max_step, steps=steps, evaluations=evaluations,
                samples=samples, terminalSaturationEventsSeconds=events, domainEventsSeconds=domains,
                supportedSeconds=float(solution.t[-1]))

output = dict(source='Independent CoolProp 7.2.0 D/U EOS and SciPy 1.16.2 Radau; conserved M/U plus tube/fin/finite-air energy and independently integrated link/face budgets',
              sectionCount=N, numpy=np.__version__, scipy=scipy.__version__, CoolProp=CoolProp.__version__,
              geometry=dict(totalVolumeM3=VOLUME,diameterM=DIAMETER,lengthM=LENGTH,tubeCapacityKJK=TUBE_C,finCapacityKJK=FIN_C,airCapacityKJK=AIR_C,
                            airTubeConductanceKWK=G_AT,airFinConductanceKWK=G_AF,finTubeConductanceKWK=2.,tubeRefrigerantConductanceKWK=.60),
              cases=[])
target=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/coupled-stage2b-reference.json')
assert not target.resolve().is_relative_to(Path(__file__).resolve().parents[2]), 'Generated references belong outside Git'
try:
    for name in SAMPLES:
        print('Independent coupled reference: '+name,flush=True)
        item=dict(name=name,runs=[])
        output['cases'].append(item)
        for tolerance,max_step in [(1e-8,.1),(1e-10,.025)]:
            item['runs'].append(run(name,tolerance,max_step))
            Path(str(target)+'.partial.json').write_text(json.dumps(output,indent=2)+'\n')
    output['boundaryFlashFallbacks'] = fallbacks
    output['emittedWarnings'] = warning_records
    target.write_text(json.dumps(output,indent=2)+'\n')
except BaseException as error:
    output['failure']=dict(kind=type(error).__name__,message=str(error))
    Path(str(target)+'.failure.json').write_text(json.dumps(output,indent=2)+'\n')
    raise
print(json.dumps(dict(path=str(target),cases=len(output['cases']),fallbacks=fallbacks)))
