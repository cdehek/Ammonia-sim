"""Standalone Arb extension of C2's unchanged mathematical EOS, not a backend.

Analytic first/second Helmholtz derivatives are interval expressions on the full
input box. Coefficients are the original parsed binary64 rationals.
"""
import importlib.util
from pathlib import Path
from flint import arb

C2 = Path(__file__).resolve().parent.parent / 'browser_eos_b5b_c2'
spec = importlib.util.spec_from_file_location('c2local', C2/'local_enclosure.py')
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)
ball, serialize = local.ball, local.serialize

def eos(d, T):
    d, T = ball(d), ball(T)
    if not (d > 0 and T > 0 and d.is_finite() and T.is_finite()):
        raise ArithmeticError('nonpositive or nonfinite density/temperature box')
    D = local.lift(local.DATA)
    R = D['gas_constant']/D['molar_mass']
    Tc = D['STATES']['reducing']['T']
    dc = D['STATES']['reducing']['rhomolar']*D['molar_mass']
    delta, tau = d/dc, Tc/T
    ar, art, artt, ard, ardd, ardt = [arb(0) for _ in range(6)]
    for group in D['alphar']:
        for i, n in enumerate(group['n']):
            di, ti = group['d'][i], group['t'][i]
            v = n*delta**di*tau**ti
            lt, ltt = ti/tau, -ti/tau**2
            ld, ldd = di/delta, -di/delta**2
            if group['type'] == 'ResidualHelmholtzPower':
                le = group['l'][i]
                if not le.is_zero():
                    v *= (-delta**le).exp()
                    ld -= le*delta**(le-1)
                    ldd -= le*(le-1)*delta**(le-2)
            elif group['type'] == 'ResidualHelmholtzGaussian':
                eta, beta, eps, gamma = [group[k][i] for k in ['eta','beta','epsilon','gamma']]
                v *= (-eta*(delta-eps)**2-beta*(tau-gamma)**2).exp()
                ld -= 2*eta*(delta-eps)
                ldd -= 2*eta
                lt -= 2*beta*(tau-gamma)
                ltt -= 2*beta
            elif group['type'] == 'ResidualHelmholtzGaoB':
                eta, beta, eps, gamma, b = [group[k][i] for k in ['eta','beta','epsilon','gamma','b']]
                z = b+beta*(tau-gamma)**2
                if z.contains(0):
                    raise ArithmeticError('GaoB denominator interval includes zero')
                v *= (eta*(delta-eps)**2+1/z).exp()
                ld += 2*eta*(delta-eps)
                ldd += 2*eta
                lt -= 2*beta*(tau-gamma)/z**2
                ltt += -2*beta/z**2+8*beta**2*(tau-gamma)**2/z**3
            else:
                raise ValueError(group['type'])
            ar += v
            art += v*lt
            artt += v*(lt**2+ltt)
            ard += v*ld
            ardd += v*(ld**2+ldd)
            ardt += v*ld*lt  # exponent is separable in delta and tau
    lead, log, planck = D['alpha0']
    a0 = delta.log()+lead['a1']+lead['a2']*tau+log['a']*tau.log()
    a0t = lead['a2']+log['a']/tau
    a0tt = -log['a']/tau**2
    for n, t in zip(planck['n'],planck['t']):
        em = (t*tau).expm1()
        if em.contains(0):
            raise ArithmeticError('singular Planck denominator')
        a0 += n*(-(-t*tau).expm1()).log()
        a0t += n*t/em
        a0tt -= n*t**2*(t*tau).exp()/em**2
    p = d*R*T*(1+delta*ard)
    u = R*Tc*(a0t+art)
    s = R*(tau*(a0t+art)-a0-ar)
    # g=RT(alpha+1+delta ar_delta), independent of h-Ts cancellation.
    g = R*T*(a0+ar+1+delta*ard)
    cv = -R*tau**2*(a0tt+artt)
    pr = R*T*(1+2*delta*ard+delta**2*ardd)
    pt = d*R*(1+delta*ard-delta*tau*ardt)
    ur = R*Tc*ardt/dc
    result = dict(p=p,u=u,s=s,g=g,f=R*T*(a0+ar),cv=cv,pr=pr,pt=pt,ur=ur,
                  gr=pr/d,gt=-s+pt/d)
    if not all(v.is_finite() for v in result.values()):
        raise ArithmeticError('nonfinite EOS enclosure')
    return result

def stability(z, d, T):
    if not (z['cv'] > 0 and z['pr'] > 0):
        raise ArithmeticError('positive endpoint cv/pr not established')
    cp=z['cv']+T*z['pt']**2/(d**2*z['pr'])
    kappa=1/(d*z['pr'])
    if not (cp.is_finite() and kappa.is_finite() and cp>0 and kappa>0):
        raise ArithmeticError('positive finite endpoint cp/compressibility not established')
    return dict(cv=serialize(z['cv']),dp_drho_T=serialize(z['pr']),
                cp=serialize(cp),compressibility=serialize(kappa))
