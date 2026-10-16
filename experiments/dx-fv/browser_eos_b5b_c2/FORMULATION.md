# The exact certificate target and thermodynamic equations

## Stored inventory and arithmetic

The proposed external target is the exact real/rational triple represented by
the original finite binary64 **M kg, U_kJ kJ, V m³** bits. They have no numerical
input uncertainty once stored. Measurement/model uncertainty is a different
quantity and is never an allowance to move those bits.

The accepted construction and recovery order is preserved, with rounding after
each original binary64 operation:

```
V = 0.003 / 5
M = rho * V
U_kJ = M * (h / 1000) - 100 * (P / 1e5) * V
rho_DU = M / V
u_DU = (U_kJ / M) * 1000
```

In particular, the `100 * (P / 1e5) * V` work term is evaluated left to right.
No multiplication/division is canceled and no FMA is introduced. V is
`3f43a92a30553262`, the exact rational **2767011611056433/4611686018427387904**,
not the decimal real 0.0006. `inventory-arithmetic.json` records every operand
bit pattern, result rational and rational rounding error for all nine originals.
The construction request P is separate from actual PH getter p.

For the external target, define exact real quantities:

```
d* = M / V                 (exact rational division)
u* = 1000 U_kJ / M         (exact rational division and unit conversion)
v* = V / M
```

These are not generally binary64 values. The actual historical adapter instead
sends `fl(M/V)` and `fl(fl(U_kJ/M)*1000)` to CoolProp. The prototype retains
both targets and does not silently substitute them. Its exact target is external
M/U/V even if a caller originated it from PH.

CoolProp's pinned `AbstractState.cpp:437` converts DmassUmass to DmolarUmolar
with `value1 /= mm; value2 *= mm`. Thus the third diagnostic target is:

```
n_in = fl(rho_DU / W)
e_in = fl(u_DU * W)
d_internal_equivalent = exact(n_in) * exact(W)
u_internal_equivalent = exact(e_in) / exact(W)
```

Here W is the original binary64 molar mass. Upstream source copies in evidence
bind this conversion. The third target isolates input conversion; later reduced
coordinate/EOS arithmetic and inverse errors remain in actual raw recovery.
No claim is made that the internal coordinate target equals the external target.
Control 76 proves that even its pressure side can differ. A future verifier
working in molar variables must use exact `M/(V W)` and `1000 U W/M`, or enclose
and rigorously transport the conversion discrepancy to the external target.
Reporting a narrow interval at the rounded internal inputs is insufficient.

## Mathematical EOS identity and reference

Use the preserved ammonia JSON, parsed to the **same binary64 constants** as
the historical implementation and promoted exactly. Do not interpret its decimal
tokens as exact decimal coefficients. Derived constants in the mathematical
model are computed as real expressions of those binary64 constants:

```
R = R_molar / W
d_c = n_c W
delta = d / d_c
tau = T_c / T
alpha(delta,tau) = alpha0(delta,tau) + alphar(delta,tau)
```

All eight power, ten Gaussian and two GaoB terms are retained. The ideal lead,
log-tau and three Planck-Einstein terms are unchanged. The original ideal lead
`a2` fixes caloric reference; `a1` fixes entropy reference. There is no external
reference-state setter or fitted offset in this evaluator. The default JSON
reference convention, including both constants, is part of the identity. No
IIR/ASHRAE/NBP conversion is made. The independent pressure/u evaluator does not
need the entropy constant a1; the coexistence g evaluator retains it. A future
certificate must invalidate on any reference convention change.

This mathematical definition does not say every intermediate expression in
CoolProp is evaluated exactly; its rounding is precisely one subject of research.
Compiled source/artifact identities and mathematical EOS identity are both
needed. In C2 the separate ball evaluator encloses the mathematical functions,
not the execution error of a complete CoolProp recovery.

## Stable homogeneous inversion

At d=d*, solve **F(T)=u(d*,T)−u*=0** without prescribing a preferred pressure.
Then compute p(d*,T). For either homogeneous liquid or vapor:

```
p = d R T (1 + delta alphar_delta)
u = R T tau (alpha0_tau + alphar_tau)
s = R [tau (alpha0_tau + alphar_tau) - alpha0 - alphar]
h = u + p/d
g = h - T s
cv = -R tau² (alpha0_tautau + alphar_tautau)
p_d|T = R T [1 + 2 delta alphar_delta + delta² alphar_deltadelta]
p_T|d = d R [1 + delta alphar_delta - delta tau alphar_deltatau]
u_d|T = R T_c alphar_taudelta / d_c
cp = cv + T (p_T|d)² / (d² p_d|T)
kappa_T = 1 / (d p_d|T)
```

Positive cv, cp, compressibility and p_d|T are necessary local stability evidence.
They are insufficient to exclude a metastable or dome-interior homogeneous root.
The relevant stable saturation branch and competing phases must be established
independently at this T. Under a proven single-coexistence topology, liquid lies
at/above dL(T) and vapor at/below dV(T); a root between endpoints cannot be used
as the homogeneous reference. No global topology theorem is assumed proved by
these sampled diagnostics.

For a same-branch local perturbation:

```
dT = (du - u_d|T dd) / cv
dp = (p_T|d / cv) du + [p_d|T - (p_T|d / cv) u_d|T] dd
dd = dM/V - M dV/V²
du = 1000 (dU_kJ/M - U_kJ dM/M²)
```

The recorded sensitivities are about 366 Pa/(J/kg) for these liquids and 8
Pa/(J/kg) for vapors; exact per-case values are in references.json. Linear
sensitivity explains why tiny caloric errors matter but is not itself an error
bound. An error bound needs derivative enclosures over the entire connecting
region, with phase validity established there. Do not use a homogeneous Jacobian
across boiling. Conserved inventory itself is not an interval to be adjusted;
only its representation in the verifier is enclosed.

If an existing local bracket and continuity are proved, and inf(cv)>0 throughout,
the mean-value theorem can bound temperature error from a rigorously enclosed
residual at T0. A pressure bound can use sup(|p_T|) times that temperature error,
plus rigorous pressure-evaluation error and exact input-conversion effects.
Without an existence bracket, an applicable derivative bound and root/phase
selection, `residual / point-Jacobian` is only a conditioning estimate. C2 uses
the direct bracket/interval-pressure method instead of claiming such a point
estimate is a certificate.

## Equilibrium mixture and endpoints

For pure-fluid equilibrium solve the simultaneous equations at original d*,u*:

```
p(dL,T) - p(dV,T) = 0
g(dL,T) - g(dV,T) = 0
(1-q)/dL + q/dV - V/M = 0
(1-q)u(dL,T) + q u(dV,T) - 1000 U_kJ/M = 0
```

Pressure is the common endpoint pressure, never a homogeneous EOS evaluation at
the mean mixture density. Require dL>dV>0, physical T, 0<=q<=1, stable endpoints,
the relevant stable coexistence branch, and exclusion of the trivial dL=dV root
and competing branches. This pure-fluid q is mass fraction (also mole fraction).

Volume elimination gives q=(v*−1/dL)/(1/dV−1/dL). For endpoint diagnostics use
centered fractions to avoid subtracting nearly equal quantities:

```
q = (dL-d*) dV / [d* (dL-dV)]          near liquid
w = (d*-dV) dL / [d* (dL-dV)]          near vapor, q=1-w
Fu = (uL-u*) + q (uV-uL)              near liquid
Fu = (uV-u*) - w (uV-uL)              near vapor
```

Endpoint signs must be enclosed; small negative q or w is not clamped. Exact
q=0 or 1 is admissible only if equality is established for the exact input.
Intervals containing both signs leave the branch unresolved. Interval Newton or
Krawczyk can establish a coupled local root/uniqueness with a nonsingular
interval Jacobian and verified containment, but that root still needs stable
phase/topology evidence. Extrapolated q<0 or q>1 roots are retained as excluded
diagnostics. The trivial equal-density solution and near-critical degeneracy
need explicit safeguards. No scalar homogeneous proof is substituted here.

The Gate B endpoint diagnostics show why this matters: homogeneous roots with
positive local derivatives can be algebraically valid while the actual selected
mathematical branch is coexistence. C2's adversarial local enclosure reproduces
that insufficiency without returning an accepted property state.

## Proof scope of the bounded prototype

Arb balls contain exact d*,u*, constants and every arithmetic/transcendental
result. At fixed d*, opposing energy signs prove a root by continuity. The
positive whole-interval cv proves only local uniqueness. Pressure over the box
contains that root's pressure. All three steps account for arithmetic/EOS
evaluation errors; seed agreement is not used as proof. Exact dyadic endpoints
are serialized as rationals. The proof depends on the stated formula mapping,
Arb correctness and platform/library integrity. Finite cross-checks do not prove
the whole software stack. Physical branch, global uniqueness and full support
conditions remain outside this local proof. Complete status is UNRESOLVED.
