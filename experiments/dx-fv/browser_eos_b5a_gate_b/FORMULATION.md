# Fixed-density/internal-energy equilibrium formulation

Let the exact requested mass density and internal energy be d and u*, with
v*=1/d. They are lifted directly from the saved binary64 bit patterns. For pure
ammonia the mass and molar vapor fractions coincide. The four unknowns are
(rhoL,rhoV,T,Q). At a two-phase equilibrium:

```
Fp = p(rhoL,T) - p(rhoV,T) = 0
Fg = g(rhoL,T) - g(rhoV,T) = 0
Fv = (1-Q)/rhoL + Q/rhoV - 1/d = 0
Fu = (1-Q)*u(rhoL,T) + Q*u(rhoV,T) - u* = 0
```

The same temperature is used in both phases. Pure-fluid chemical potential per
unit mass is g. Require rhoL>rhoV>0, physical temperature, 0<=Q<=1, positive cv
and dp/drho|T (and checked positive cp/compressibility) at both endpoints, and
the stable liquid/vapor coexistence branch. Local derivative positivity alone
does not exclude a metastable homogeneous root. Homogeneous roots must also lie
on the stable side of independently evaluated saturation at their own T.
This is a local investigation near the known 35-bar branch, not a global proof
excluding every possible remote EOS root or critical-region topology.

All properties use B5's independently implemented original ammonia Helmholtz EOS,
including power, Gaussian and GaoB terms. No fit, interpolation, or changed
reference convention enters the equations. With delta=rho/rho_c, tau=Tc/T,
alpha=alpha0+alphar, and mass-specific R:

```
p = rho*R*T*(1 + delta*alphar_delta)
u = R*T*tau*(alpha0_tau + alphar_tau)
s = R*(tau*(alpha0_tau + alphar_tau) - alpha0 - alphar)
g = u + p/rho - T*s
```

Coefficients, R, molar mass, reducing coordinates and original inventory inputs
are exact binary64 values promoted into 65- or 90-digit arithmetic. Derived
constants are recomputed at each precision. This determines a mathematical EOS
root; it does not confer physical accuracy at those digits.

## Endpoint-centered elimination

Eliminate Fv analytically with Dv=1/rhoV-1/rhoL. Near the liquid endpoint:

```
Q = (rhoL-d)*rhoV / (d*(rhoL-rhoV))
Fu = (uL-u*) + Q*(uV-uL)
```

Near the vapor endpoint compute the small liquid fraction w directly:

```
w = (d-rhoV)*rhoL / (d*(rhoL-rhoV))
Q = 1-w
Fu = (uV-u*) - w*(uV-uL)
```

This avoids subtracting nearly equal reciprocal volumes and avoids computing
the small fraction as 1-Q. The binary64 prototype retains w even when Q rounds
to 1; admissibility checks both fractions. `math.fsum` improves the last energy
sum but cannot repair rounding already present in EOS endpoint energies.
Signed extrapolated fractions are retained as failed mixture candidates.

Solve Fp,Fg,Fu for rhoL,rhoV,T. Both diagnostic implementations scale residual
rows by 1e6. Binary64 scales unknowns by reducing density and temperature and
uses a dense 3x3 solve. Scaling changes no equation, requested inventory, or
acceptance criterion. Measured condition numbers do not show that this scaling
uniformly improves the matrix: scaled values are about 804–1755, versus
unscaled mixed-unit values about 520–1148. Those numbers depend on units; the
physical inequality near Q=0/1 is the dominant unresolved issue.

The analytic Jacobian uses p_r, p_T, u_r and cv from separate unmodified DT
states. At fixed T, g_r=p_r/rho; at fixed rho, g_T=-s+p_T/rho. Also:

```
dQ/drhoL = (1-Q)/(rhoL^2*Dv)
dQ/drhoV = Q/(rhoV^2*Dv)
dFu/drhoL = (1-Q)*uL_r + (uV-uL)*dQ/drhoL
dFu/drhoV = Q*uV_r + (uV-uL)*dQ/drhoV
dFu/dT = (1-Q)*cvL + Q*cvV
```

The high-precision prototype uses independently differentiated EOS residuals.
Its bounded Newton iteration stops at an arithmetic diagnostic residual of
10^(-dps+15). This is a convergence check at the selected arithmetic precision,
not a substitute for any accepted scientific budget.

## Branch selection and inventory invariance

The high-precision diagnostic solves coexistence first, retaining even its
nonphysical algebraic extension. If 0<=Q<=1, the stable coexistence solution is
selected. Otherwise it solves u(d,T)=u* at the original d, checks positive
stability derivatives, independently solves coexistence at this homogeneous T,
and selects the root only on the stable side of saturation. All original states
meet one of these mathematical tests. The three resolved liquid controls are
not forced into a mixture. Rows 148/164 have homogeneous algebraic roots with
positive local derivatives but lie inside the coexistence dome; they are excluded.

No preferred pressure is imposed anywhere in this DU formulation. Fixed-density
saturation references solve Fp=Fg=0 with the relevant endpoint density held at d;
fixed-temperature saturation references solve the same equalities with T fixed.
Neither supplies replacement DU inputs. Native internal-coordinate references
separately use the traced binary64 rhomolar/umolar values and exact molar mass.
The small conversion differences are reported, never erased.

An endpoint design must satisfy all four constraints with Q exactly 0 or 1 when
that is the actual root. A sign smaller than the available evaluation error
cannot justify snapping to that endpoint. The present prototype has no endpoint
substitution or uncertainty-to-success rule. Binary64 coexistence iterations
remain algebraic diagnostic candidates until branch admissibility is established;
the diagnostic wrapper does not claim to certify their phase.

## Bracket interpretation

At these fixed densities, local physical coexistence temperatures approach the
fixed-density saturation boundary from below. A scalar saturation-temperature
method would need a sign bracket wholly within its physical quality interval.
`temperature-brackets.json` samples nine adjacent temperatures per original
unresolved inventory with the unchanged native QT endpoint evaluator. For 148
and 164 the observed energy sign changes occur across the physical-quality
boundary, with no pair of adjacent physically admissible samples bracketing
zero. The true mathematical temperature gaps are only 0.086 and 0.281 T ULP.
For 165 the extrapolated equilibrium root is outside the physical interval;
for 162 it is outside on the liquid side. No physical mixture bracket is
established for any of these four. This bounded test does not prove that every
binary64 formulation is impossible. Interval bounds or a more accurate EOS
evaluation could change what can be certified, and would require new research.
