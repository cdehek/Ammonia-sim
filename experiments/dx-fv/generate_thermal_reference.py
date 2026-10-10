"""Independent constant-C/G references: SciPy expm, no JS solver/geometry imports.

Inputs reproduce the approved contract. Temperatures and affine boundaries are
assembled independently; augmented exponential also integrates every link/load.
"""
import json
import sys
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.optimize import brentq

L = .003 / (np.pi * .020**2 / 4)
CT = 7850 * np.pi/4 * (.024**2-.020**2) * L * .470
CF = 2700 * 1910 * np.pi/4 * (.080**2-.024**2) * .0002 * .900
CA = 6 * .718
GAT = np.pi*.024*(L-1910*.0002)*50/1000
GAF = 1910*(2*np.pi/4*(.080**2-.024**2)+np.pi*.080*.0002)*50/1000


def projected(bins, left, right):
    return sum(max(0, min(right, b)-max(left, a))*t for a, b, t in bins)/(right-left)


def fixture(n=1, nonuniform=False, reservoir=False):
    capacities, initial, links = [], [], []
    for i in range(n):
        a, b = i/n, (i+1)/n
        capacities += [CT*(b-a), CF*(b-a)]
        initial += ([projected([(0,.3,260),(.3,1,320)],a,b),
                     projected([(0,.6,290),(.6,1,270)],a,b)] if nonuniform else [273.15,283.15])
        links += [(2*n,2*i,GAT*(b-a)), (2*n,2*i+1,GAF*(b-a)), (2*i+1,2*i,2*(b-a))]
    if not reservoir:
        capacities += [CA]
        initial += [293.15]
    return capacities, initial, links


def propagate(capacities, temperatures, links, seconds, load=0, reservoir=None):
    n = len(capacities)
    # [T_0..T_n, affine 1, integrated signed links, integrated external load]
    size = n+1+len(links)+1
    a = np.zeros((size,size))
    for j,(src,dst,g) in enumerate(links):
        q = np.zeros(size)
        q[src if src<n else n] += g if src<n else g*reservoir
        q[dst if dst<n else n] -= g if dst<n else g*reservoir
        if src<n:
            a[src] -= q/capacities[src]
        if dst<n:
            a[dst] += q/capacities[dst]
        a[n+1+j] = q
    if reservoir is None:
        a[n-1,n] += load/capacities[-1]
    a[-1,n] = load
    y = np.zeros(size)
    y[:n],y[n] = temperatures,1
    out = expm(a*seconds) @ y
    return out[:n].tolist(),out[n+1:-1].tolist(),float(out[-1])


cases = {}
for name,n,nonuniform,reservoir,end,events in [
    ('closed',1,False,False,300,[]),
    ('loaded',1,False,False,120,[(0,1)]),
    ('stepped',1,False,False,60,[(0,1),(15,2),(30,1)]),
    ('reservoir',1,False,True,60,[(0,293.15),(15,303.15),(30,283.15)]),
    ('nonuniform5',5,True,False,60,[]),
    ('nonuniform9',9,True,False,60,[])]:
    c,t,links=fixture(n,nonuniform,reservoir)
    initial=t[:]
    times=sorted(set([0,.1,1,10,15,30,60,end]))
    times=[v for v in times if v<=end]
    outputs=[]
    for target in times:
        current=0.;state=initial[:];ledger=np.zeros(len(links));load_integral=0.
        for boundary in sorted(set([v for v,_ in events if 0<v<target]+[target])):
            setting=next((q for when,q in reversed(events) if when<=current),0)
            state,qs,ql=propagate(c,state,links,boundary-current,load=0 if reservoir else setting,reservoir=setting if reservoir else None)
            ledger+=qs;load_integral+=ql;current=boundary
        outputs.append(dict(seconds=target,temperaturesK=state,linksKJ=ledger.tolist(),loadKJ=load_integral))
    cases[name]=dict(capacitiesKJK=c,initialK=initial,samples=outputs)

c,t,links=fixture()
def maximum_at(seconds):
    return max(propagate(c,t,links,seconds,load=1)[0])-400
domain_time=brentq(maximum_at,120,1800,xtol=1e-10)
result=dict(source='Independent temperature-coordinate SciPy matrix exponential with augmented link/load integrals',numpy=np.__version__,scipy=scipy.__version__,cases=cases,connectedDomainSeconds=domain_time,isolatedAirDomainSeconds=(400-293.15)*CA)
with open(sys.argv[1], 'w') as f:
    json.dump(result,f,indent=2,allow_nan=False)
    f.write('\n')
print(json.dumps(dict(cases=len(cases),connectedDomainSeconds=domain_time)))
