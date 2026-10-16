# Proof obligations — written before P1 numerical prototypes

This is standalone mathematical certification feasibility. No diagnostic output
is an accepted simulator property state. Level 1 is independently checked high
precision; Level 2 is a theorem with validated arithmetic and explicit scope;
Level 3 is the original simulator scientific qualification. These levels do not
imply one another beyond the particular demonstrated obligations.

## Exact input identity

Decode the saved hexadecimal binary64 M, U_kJ, V as exact rationals. Establish
positive finite M,V and bind every result to those bits, the unchanged EOS JSON,
binary64-promoted coefficients, reference convention and source identities.
The mathematical target is d*=M/V, u*=1000 U_kJ/M, v*=V/M by rational division.
Rounded DU and internal molar coordinates are different targets.

Preserve the accepted binary64 construction and operation order exactly:

```
V = 0.003 / 5
M = rho * V
U_kJ = M * (h / 1000) - 100 * (P / 1e5) * V
rho_DU = M / V
u_DU = (U_kJ / M) * 1000
```

Do not cancel operations, rewrite work terms, use display decimals, change
inventory, snap density or quality, or introduce a support epsilon.

## Homogeneous state

At exact d*, prove u(d*,T)=u* has a root in a positive-temperature interval,
uniqueness within that interval, continuity and valid nonsingular EOS coordinates.
Enclose pressure at that root. Enclose cv and dp/drho|T (and resulting cp and
compressibility) over the full box. These local conditions alone do not establish
the stable liquid/vapor branch. Validate saturation at every possible root
temperature and the strict appropriate endpoint-density inequality. Exclude
relevant competing equilibrium states by a proved bounded thermodynamic
potential/entropy comparison or a separately justified topology dependency.
Do not call pressure support a physical branch certificate.

## Coexistence and mixtures

For endpoints require a common T, equal p and equal mass-specific chemical
potential g; rhoL>rhoV>0; valid coordinates; endpoint stability; exclusion of the
trivial equal-density root. Enclose full residuals and the Jacobian over the
entire candidate box. State the actual existence and uniqueness theorem, prove
its hypotheses, and specify its local uniqueness scope. A point Jacobian or
small residual cannot replace this proof.

For fixed exact inventory also require

```
(1-Q)/rhoL + Q/rhoV = V/M
(1-Q)uL + Q uV = 1000 U_kJ/M
0 <= Q <= 1
```

Eliminating volume is allowed only with rigorously nonzero density separation
and algebraic equivalence. Retain signed endpoint fractions. Q<0 or Q>1 is an
inadmissible algebraic continuation. If an interval overlaps 0 or 1, withhold
admissibility unless exact endpoint equality is separately proved. Homogeneous
derivatives cannot cross a boiling boundary by assumption.

## Scope and topology

Distinguish a local numerical root, a locally stable branch, a bounded operating
region, and exclusion of all relevant competitors in that region. A local
coexistence root does not prove the equilibrium convex envelope. At fixed T,
one possible sufficient dependency is a global supporting tangent inequality
for Helmholtz free energy in specific volume over an explicit density domain,
with coverage of all relevant phases; at fixed U,V use the corresponding
entropy maximum argument and thermodynamic equivalence assumptions.

Topology A means rigorously established here. B means an explicit externally
justified mathematical assumption. C means diagnostics only. C cannot support
an unconditional physical branch claim. If the convex-envelope/topology theorem
cannot be proved within this bounded experiment, record it as unresolved and
stop expanding topology work. Do not assert global thermodynamic uniqueness.

## Verification, gates and stopping

Use unchanged C2 Arb infrastructure where useful; independently audit added
derivatives with mpmath differentiation. Repeat at 192 and 256 bits, preserve
exact rational outward endpoints, check finite/domain/denominator exclusions,
and reject incomplete proof conditions and deliberately wrong boxes. Precision
agreement is a cross-check, never the existence theorem. Trust python-flint,
FLINT/Arb and their build/runtime under documented assumptions; finite tests
cannot prove an entire arithmetic library or compiler.

Report separately inventory identity, homogeneous root and pressure, coexistence,
endpoint intervals, side inequality, mixture fraction, competing-phase exclusion,
complete branch certification, original scientific qualification and browser
portability. CONDITIONAL_PHASE_PROOF must name the missing dependency; otherwise
UNRESOLVED or NUMERICAL_FAILURE. Never coerce unknown to true.

Limit to two formulations: parameterized two-density coexistence and a
volume-eliminated three-variable mixture. Use short per-attempt timeouts, retain
failures, no source download/build, no critical-region program and a planning
ceiling of about 90 minutes active execution. Stop when remaining proof needs
unproved topology beyond scope; failure here does not prove impossibility.

## Protected scientific and operational meaning

Preserve canonical <=0.1 Pa, <=0.1 J/kg, <=1e-4 K; fluid residual <=1e-11;
standalone strictly <10 Pa, <50 J/kg, <0.01 K; independent resolution 1e-5 Pa,
1e-8 J/kg; hard maximum exactly 3,500,000 Pa absolute, all lower/temperature,
phase/conservation/thermal/signed derivative/Newton/TR-BDF2/domain-stop/rollback
contracts. Mathematical EOS consistency at sub-micropascal scales supplies no
experimental ammonia or plant measurement accuracy at those scales.

C1 refusal stays refusal; numerical failure is not physical-domain exit; genuine
independently proved exits stay protective; rollback stays exact. No raw
diagnostic becomes accepted state or a manufactured refrigeration trip.
