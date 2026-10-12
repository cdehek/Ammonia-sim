"""Independent interpolation of the frozen table, for diagnostic comparators.

This is NOT a replacement property engine or an accepted EOS reference. Exact
piecewise interpolation/density inversion removes JS inversion quantization as a
confounder while retaining the table's constitutive values. Only the gas/two-phase
states encountered by this local investigation are supported; no extrapolation.
"""
import json
import math
import numpy as np
from scipy.optimize import brentq


class TableComparator:
    def __init__(self, filename):
        self.data = json.loads(filename.read_text())
        self.logs = np.log(self.data['p'])
        self.rows = np.array(self.data['sat'])
        self.sh = np.array(self.data['sh'])
        self.vapor = np.array(self.data['vapor'])

    def pressure(self, p):
        x = math.log(p)
        assert self.logs[0] <= x <= self.logs[-1]
        i = min(len(self.logs)-2, max(0, int(np.searchsorted(self.logs, x))-1))
        return i, (x-self.logs[i])/(self.logs[i+1]-self.logs[i])

    def saturation(self, p):
        i, w = self.pressure(p); a, b = self.rows[i:i+2]
        interp = lambda j: float(a[j]+(b[j]-a[j])*w)
        logarithmic = lambda j: math.exp(math.log(a[j])+(math.log(b[j])-math.log(a[j]))*w)
        return dict(p=p, T=interp(0), hf=interp(1), hg=interp(4),
                    rhof=logarithmic(3), rhog=logarithmic(6))

    def gas_curves(self, p):
        i, w = self.pressure(p); a, b = self.vapor[i:i+2]
        return a[:, 0]+(b[:, 0]-a[:, 0])*w, np.log(a[:, 2])+(np.log(b[:, 2])-np.log(a[:, 2]))*w

    def at_density(self, p, rho):
        sat = self.saturation(p)
        if sat['rhog'] <= rho <= sat['rhof']:
            q = (1/rho-1/sat['rhof'])/(1/sat['rhog']-1/sat['rhof'])
            h, t = sat['hf']+q*(sat['hg']-sat['hf']), sat['T']
        else:
            assert rho < sat['rhog'], 'Subcooled state is outside this comparator'
            hcurve, logrho = self.gas_curves(p); target = math.log(rho)
            assert logrho[-1] <= target <= logrho[0]+1e-12
            j = min(len(self.sh)-2, max(0, int(np.searchsorted(-logrho, -target))-1))
            w = (target-logrho[j])/(logrho[j+1]-logrho[j])
            h = float(hcurve[j]+(hcurve[j+1]-hcurve[j])*w)
            t = float(sat['T']+self.sh[j]+(self.sh[j+1]-self.sh[j])*w)
            q = None
        return dict(p=float(p), h=h, T=t, rho=float(rho), u=h-100*p/rho, quality=q)

    def mu(self, mass, energy, volume):
        rho, u = mass/volume, energy/mass
        # The saved interval stays near 3.5 bar. This diagnostic bracket is not
        # installed into any solver; an out-of-bracket state raises, never clamps.
        residual = lambda p: self.at_density(p, rho)['u']-u
        p = brentq(residual, 3.3, 3.7, xtol=1e-12, rtol=1e-14)
        return self.at_density(p, rho)

    def ph(self, p, h):
        sat = self.saturation(p)
        if sat['hf'] <= h <= sat['hg']:
            q = (h-sat['hf'])/(sat['hg']-sat['hf'])
            rho = 1/((1-q)/sat['rhof']+q/sat['rhog']); t = sat['T']
        else:
            assert h > sat['hg'], 'Subcooled state is outside this comparator'
            hc, lr = self.gas_curves(p); assert hc[0]-1e-8 <= h <= hc[-1]
            j = min(len(self.sh)-2, max(0, int(np.searchsorted(hc, h))-1))
            w = (h-hc[j])/(hc[j+1]-hc[j])
            rho = math.exp(float(lr[j]+(lr[j+1]-lr[j])*w))
            t = float(sat['T']+self.sh[j]+(self.sh[j+1]-self.sh[j])*w); q = None
        return dict(p=float(p), h=float(h), T=t, rho=rho, u=h-100*p/rho, quality=q)
