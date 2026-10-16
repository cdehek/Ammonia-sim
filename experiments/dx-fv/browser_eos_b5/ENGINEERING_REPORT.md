# B5 — 35-bar inverse recovery and property-domain forensics

**Final assessment: ROOT CAUSE CONFIRMED.**

There are multiple numerical mechanisms. The native full-VLE DU failures are
not evidence that the original ammonia states are physically impossible. The
browser failures return accurate raw DU states within the canonical budgets,
then encounter a strict pressure check. Some exact rounded inventories have a
mathematical EOS pressure slightly above the boundary; others have pressure
below it and are rejected because the numerical recovery overshoots. These
cases must not be combined into a single physical-domain diagnosis.

This milestone implements **no functional repair** and qualifies **no backend**.
Stop for engineering review and explicit approval. No corrective milestone,
complete A2 campaign, production integration, merge or deployment was started.

## Checkpoint, preservation and scope

Branch: `research/browser-eos-b5-35bar-inverse-forensics-20261016`.
Parent: exact `3622000309cacdd35aaaebbb805ae40d27c75603`, from B4C's requested
branch. The clone's HEAD and empty porcelain status were checked before creating
the new branch. The full delivery commit is the commit containing this report;
`git rev-parse HEAD` and the delivery response identify it without a self-referential
commit string inside its own tree.

All **1,557** starting tracked files retain SHA256. All changes are additions
under `experiments/dx-fv/browser_eos_b5/`. Before experiments, the B4C README,
engineering report, fixed inventories and saved results; B4A/B4B reports; B2/B3
inverse/boundary findings; and the accepted A2 property/solver contract were
reviewed. The starting remote head ledger is `evidence/refs-before.txt`.
PR #3 refs were also observed read-only; no PR action was taken.

The four inherited corrections remain exact: B1 44-bit PH precision; B4A liquid
classification; B4B final PT/cache commit; B4C upper-quality classification.
Reconstructing pinned CoolProp `ae81610e7d23efc57f9d051c8e70a4d66e87537f`
(tree `ca49b8c34df0dae93dcc7fe07e2815a10d967662`) with those four existing
patches matches every B4C source hash: **1,782 files**. All **nine** dependency
digests match. **137** historical native/browser artifact identities verify,
including decompressed native hashes. Both installed reference wheels match
all five historical binary hashes. The 12 accepted dependency snapshots match
Git objects at A2 `be9eb35a4ddf5098e685182f8104685127c6a6ee`.

Native diagnostic instrumentation was external to the repository's protected
sources. Its logging-only patch, original translation units and separate
binaries are retained here. The external source was restored to exact B4C
and reverified after tracing. No equations, tolerances, termination conditions,
selected roots, EOS/fluid data, accepted adapter or loader were changed.

## Exact inventory reproduction

The B4C native ledger contains **166** fixed records. Each is replayed without
regeneration through archived B4C and B4B, and the matching unmodified native
8.0 wheel. B4C raw outputs/errors reproduce the saved ledger exactly. Both
native experimental backends give identical results for identical fixed inputs.
The unmodified wheel returns identical successful scientific values; its Python
exception text omits the C API's `Error: ` prefix.

Each browser's saved ledger contributes 42 fixed inventories, including both
historical origins. Adding these to the native ledger gives **250 records**,
with **73 unique rho/u pairs**. The original seven full-VLE candidate-C
exceptions and seven candidate-C strict-adapter rejections per browser are
extracted from saved results, not encoded as expected totals.

[FAILURE_MATRIX.md](FAILURE_MATRIX.md) identifies every original failure and its
exact P/h/rho/u decimal and binary64 coordinates. `fixed-inputs.json` retains
all 250 records and their historical outputs; `fixed-inventory.csv` is the
flat inventory. Current PH-derived, historical fixed and newly constructed
reference inventories remain separate throughout.

Chromium **154.0.8037.57** and desktop WPE WebKit **26.5** each reproduce all
42 of their own saved fixed-inventory raw/adapter results and every saved
35-bar candidate PH result exactly. Each also executes all 167 default-path
records through B4B and B4C: 334 rows per browser. Browser scientific results
agree between engines. This is Linux desktop WebKit, not physical iPadOS Safari.

Identical native/browser inputs are compared explicitly. Across their shared
fields, 155/167 default records are bit-identical. Maximum differences are
1.35042e-8 Pa, 4.19095e-9 J/kg in h, 3.49246e-9 J/kg in u and 1.70530e-13 K.
Three retained native-origin records change strict guard side between native
and WASM. These last-bit runtime differences are preserved, not inferred away.

Fresh versus reused native state results agree for all 250 records, with
logging on, logging off and the uninstrumented rebuild. Both browsers agree
fresh/reused at all 73 unique inventories. Equivalent scalar PropsSI outputs
match state-object p/h/T/Q. Scalar rho/u can differ because `_PropsSI_outputs`
returns an input directly when that is the sole requested output; it can skip
the flash. The maximum differences are 6.48e-12 kg/m³ and 7.68e-9 J/kg. An input
echo is not an independent inversion check. No scalar/state pressure guard
side changes occur in this comparison.

## Independent thermodynamic references

Separate unmodified 8.0 DT states solve fixed rho/u without invoking DU. A
fixed-density homogeneous temperature Newton solve uses cv. A coexistence
Newton solve independently enforces pL=pV, gL=gV and mixture internal energy,
with Q determined by specific volume. Its seed is deliberately displaced.
It never forces a homogeneous mean-density root onto a coexistence state.

Every unique inventory has both algebraic calculations recorded. Physical
selection requires positive density, the stable side of saturation for a
homogeneous root, or 0<=Q<=1 for equilibrium. Selected homogeneous states and
equilibrium endpoints have positive cp, cv, compressibility and dp/drho|T.
Dome-interior homogeneous solutions and extrapolated mixture qualities are
retained as mathematical diagnostics and excluded as physical references.

The original independent resolution remains **1e-5 Pa / 1e-8 J/kg**. At that
resolution one-ULP endpoint neighbors remain endpoint-unresolved. No exact
phase sign is claimed experimentally at a distance smaller than those criteria.

To distinguish arithmetic at a boundary much finer than that double-precision
resolution, a separate mpmath implementation evaluates the **unchanged ammonia
Helmholtz EOS**, including its power, Gaussian and GaoB terms. Every coefficient,
constant and input is promoted from its exact binary64 value. No fitting or EOS
replacement occurs. Its independent fixed-P saturation, fixed-rho/u homogeneous
and coexistence roots use separate equations and arithmetic from CoolProp.
Its validation against fresh native DT has p differences <=4.65e-7 Pa and
caloric differences <=4.66e-10 J/kg at the recorded validation coordinates.
All 73 roots are repeated at 90 versus 65 decimal digits; pressure changes are
below 1.86e-53 Pa. Full equilibrium p/g and caloric residuals are retained.

These are converged roots of the same mathematical EOS, **not experimental
ammonia accuracy to nanopa**. Arbitrary-precision arithmetic resolves the sign
of rounding effects in that mathematical model; it does not relax the original
reference criteria or certify a new operating envelope.

Distinct local homogeneous seeds at T±.01 and T±1 K converge to the same local
rho/u root for each original failing inventory examined; maximum T spread is
3.41e-13 K. Positive cv supports local uniqueness on that branch. This is not
a global uniqueness proof. Coexistence can have an additional homogeneous
algebraic solution with different stability, which is why root convergence alone
is insufficient. There is no evidence here that an otherwise converged stable
DU recovery chooses a distant competing stable root.

## Native mechanism 1: an inaccurate saturation decision threshold

The executed full-VLE path is:

`DmassUmass -> mass-to-molar conversion -> HSU_D_flash -> legacy region check
-> saturation_D_pure -> caloric comparison -> HSU_D_flash_twophase
-> final QT_INPUTS -> OutOfRangeError`.

`HSU_D_flash` calls `saturation_D_pure` at the specified density to determine
whether u is above the saturation value at that density. Its ancillary seed
for the saved .001 J/kg subcooled-liquid failure is:

- T=345.5558178868783 K;
- rhoL=30623.369169019494 mol/m³;
- rhoV=1647.046275076595 mol/m³;
- damping omega=1, maximum iterations=200.

The trace captures every density/temperature evaluation, pressure and chemical
potential residual, Newton increment and saturation exit. No retry is needed
for these original failures. The saturation routine evaluates at one coordinate,
advances its local tau/density variables, and terminates using the prior residual
norm <=1e-9. Its SatL/SatV objects remain at the earlier evaluated coordinates.

For the .001-liquid fixture:

| Quantity | Captured or independently solved value |
|---|---:|
| Advanced local T | 345.56367340330524 K |
| SatL/SatV cached T at exit | 345.5636734370032 K |
| Saturation termination residual norm | 8.707984222591074e-10 |
| Exact internal input u minus independent saturation u | +4.2557268528e-5 J/kg |
| Input u minus cached saturation u used for dispatch | -5.0070453602e-5 J/kg |
| Cached saturation-u error | +9.2627722130e-5 J/kg |

The independently solved saturation at the **actual internal molar density**
includes mass/molar conversion rounding. The advanced local T is only about
3.24e-13 K from this reference; the retained evaluated T is 3.37e-8 K away.
Thus the comparison's sign is directly demonstrated to be wrong for the resolved
subcooled liquid. The stable fixed-rho/u homogeneous root exists, but that solver
is never dispatched. Changing the homogeneous initial guess or B1 PH precision
cannot fix a solver that this path bypasses.

The two other resolved subcooled-liquid failures show the same sign reversal.
The hf one-ULP neighbor has the same stale threshold mechanism, with its true
side unresolved at the original caloric resolution. Its high-precision
mathematical sign is recorded separately. This is a missing final saturation
state consistency/decision-accuracy issue in DU's legacy support routines;
it is not a regression in the preserved B4B PT correction.

## Native mechanism 2: unphysical final quality after a converged quality residual

Legacy two-phase recovery solves Qo-Qd=0 over approximately
195.495–405.55 K using Brent, then calls `update(QT_INPUTS,resid.Qd,HEOS.T())`.
This residual has algebraic roots even when the implied mixture quality lies
outside the physical interval. For the misclassified liquid above it converges
to Qd=-1.826556176446871e-12. A converged negative-quality mixture is not its
stable physical solution.

All seven original full-VLE failures terminate Brent on the captured condition
`abs(fb) < 2*DBL_EPSILON*abs(b)`, at iteration 10. At these temperatures that
threshold is about 1.53461e-13. Their final quality residuals range from about
2.88e-16 to 2.22e-15 in magnitude. The returned Brent temperature and final
residual-evaluated temperature are identical in these seven cases; ignoring
Brent's return is therefore **not** their observed failure mechanism.

The vapor-side failures return Qd=1.000000000000002,
1.0000000000000018 and 1.0000000000000024. Two have physical equilibrium roots
just below Q=1 in the high-precision fixed-inventory calculation. The remaining
upper neighbor is mathematically infinitesimally on the homogeneous side;
its caloric dispatch compares equal at binary64 precision. All remain
endpoint-unresolved at the original independent resolution. In either event,
the unvalidated computed Q is passed into QT's strict check.

The exact exception location is pinned
`HelmholtzEOSMixtureBackend.cpp:1547`, `QT_INPUTS` quality validation. The
underlying type is `OutOfRangeError`; the C API reports an error string and the
Python research wrapper raises `ValueError`. No raw DU state exists after this
exception and no adapter decision may be claimed for that update.

This differs from failure to find a thermodynamic root: a root exists, residual
iteration terminates, then a nonphysical quality is refused. Three resolved
liquid inputs fail first at phase dispatch; the vapor endpoint cases fail first
at the unresolved decision/final-quality numerical interface. No clamp is
proposed as an adequate scientific validation of either case.

Across all 73 unique fixed inventories, default 8.0 recovery returns for all;
forcing the full-VLE path fails 21. These are additional retained combinations,
not a replacement count for the seven original candidate-C failures. Newly
constructed independent PH-reference inventories also show full-VLE exceptions
(10 of 21 labeled records), while default recovery returns. This separates the
inverse defect from a claim that only historical PH inputs were invalid.

## Browser mechanism: strict support check after accurate raw recovery

Captured browser execution uses the unchanged loader/adapter. For each original
rejection, raw DU returns, `convert` calls the table PH guard successfully, then
`adapter.mjs:8`, `sat`, rejects `p_bar>35` **before any SAT EOS call**. Its error
is `Outside accepted pressure domain`, faultKind `domain`. The originating
adapter PH calls pass. Both browsers capture this sequence independently.

The legacy table engine has its own inherited log-pressure bracketing epsilon;
that is why its guard passes these tiny differences. It is **not** the rejecting
check and is not changed. The strict adapter saturation check is the owner of
these seven browser rejections. No internal WASM execution trace is claimed.

All seven raw browser recoveries meet the original canonical requirements:
maximum |ΔP|=7.6554715633e-7 Pa, |Δh|=1.5134e-9 J/kg,
|ΔT|=5.6844e-13 K. These are successful numerical recoveries followed by failed
adapter calls; the entire accepted backend operation still fails.

High-precision fixed-inventory pressures distinguish two mechanisms:

- The .001-liquid and .99e-9 upper-vapor diagnostic inventories have mathematical
  EOS pressure **below** 35 bar, by approximately 2.5810e-9 and 8.2429e-10 Pa.
  Raw DU returns **above** the limit. Numerical inverse/EOS evaluation drift
  changes the guard outcome.
- The other five exact rounded inventories have mathematical EOS pressure
  **above** 35 bar, by approximately 7.04e-10–7.72e-7 Pa. An arbitrarily accurate
  recovery of these same inventories still encounters the strict limit.
  They originated from supported requested PH states. PH coordinate accuracy,
  h-P/rho consistency and the accepted binary64 M/U/V construction produce
  this representational displacement. It is not evidence of a resolved
  operational physical excursion, but the exact mathematical inventory is
  on the unsupported side of the unchanged strict envelope.

The guard correctly refuses the number it receives. Its `domain` classification
alone does not prove that a physically intended trajectory left support. A
mechanism that merely improves DU convergence will not eliminate all five
rounded-inventory boundary cases. Conversely, labeling them all legitimate
physical-domain stops would hide the numerical origin and the two opposite-side
recoveries. No rounding down, hidden epsilon, increased maximum or successful
`domain stop` relabeling occurs in B5.

## Canonical arithmetic, conditioning and boundary sensitivity

Every inventory preserves the accepted operation order:

```
V = .003 / 5
M = rho * V
U_kJ = M * (h / 1000) - 100 * (P / 1e5) * V
rho_DU = M / V
u_DU = (U_kJ / M) * 1000
```

V is actually 0.0006000000000000001 m³, bits `3f43a92a30553262`.
M/V and U/M rounding are measured, not algebraically removed. The independent
pressure attribution separates PH EOS pressure, PH caloric inconsistency,
rho reconstruction rounding, U construction rounding, fixed-inventory physical
pressure and final raw-DU error. Its homogeneous derivative decomposition is
not applied as a stable-mixture derivative at coexistence.

Liquid dp/du|rho near these fixtures is about 366 Pa per J/kg, much larger than
the roughly 8 Pa per J/kg vapor response. Thus tiny caloric/EOS arithmetic
errors can move pressure by many pressure ULPs without approaching 0.1 Pa.
The density sensitivity and cv are recorded per inventory. The saturation
classification error above is larger than ordinary inventory rounding: its
~9.26e-5 J/kg threshold error reverses a ~4e-5 J/kg physical separation.
This is not a loss of a stable root through negative cv or compressibility.

The separately labeled sweep contains 21 states: liquid, mixture and vapor at
exactly 35 bar, one Pa ULP below/above, the exact saved inward pressure probe
3499999.65 Pa, and 3499990, 3490000 and 3400000 Pa. Its generated h coordinates
are **diagnostic inputs**, not replacements for saved fixtures or accepted FDs.

At 3,500,000 Pa one pressure ULP is 4.6566128731e-10 Pa. The representable
neighbors convert to 34.99999999999999 and 35.00000000000001 bar. A Pa->bar->Pa
round trip moves those neighbors one additional Pa ULP outward. It does not
collapse either into 35. Native and browser results at these inputs retain
the actual round trips. Saved original P=35 bar itself converts exactly.
For the original seven rejections, Pa->bar preserves the side of the boundary;
conversion rounding contributes last bits but is not the originating reason
that their raw pressure exceeds the limit.

Both browsers reject four supported boundary sweep recoveries (two at exact P
and two one Pa ULP inside) and two of the three deliberately unsupported above-
boundary recoveries. All three above-boundary PH adapter calls reject. The raw
DU recovery of the above-boundary mixture can fall inside and pass its recovery
guard; that is retained as a numerical observation, never counted as a supported
PH input or accepted physical pass. Farther-inward sweep cases have no browser
pressure-guard rejection. Native full-VLE exceptions can still occur inside the
support envelope: their cause is the inverse path, not the 35-bar guard.

Explicit DU-coordinate perturbations at ±1 and ±16 ULP are retained separately
for a liquid inverse failure, a vapor endpoint failure and a browser liquid
rejection. All eight perturbations of each liquid example fail full VLE and
return on the default path. The endpoint failure switches success/error with
ULP direction (three of eight fail full VLE). No accepted finite-difference
perturbation, inventory, solver guess or tolerance is changed.

## Original scientific budgets and historical 7.2

Across 1,668 raw EOS audit records, 144 exception records remain errors (87 in
the three native8 build/interface combinations and 57 native7.2); no exception
is treated as a pass. Every returned recovery passes the original canonical
and normalized local mass/energy checks in this finite ledger. Largest
canonical differences including historical B4B upper-quality inventories and
7.2 returns are about .00305634 Pa / .000108958 J/kg / 2.56446e-7 K. The
largest local normalized mass/energy residuals are 1.047e-14 / 1.108e-14,
versus 1e-11. Original failing-PH energy mismatch in the B4C candidate cases
is at most 1.816e-15. These results do not excuse any adapter rejection.

Fresh independent EOS values at returned DU coordinates differ from getters
by at most about 2.36e-7 Pa, 6.99e-10 J/kg h and 1.40e-9 J/kg u. This finite
sample provides no evidence of another accepted-state PT-style stale caloric
cache in successful DU recovery. The demonstrated inconsistency occurs in the
legacy saturation decision's intermediate state. Endpoint/two-phase audits
use equilibrium rather than a homogeneous mean-density interpretation.

The historical matching 7.2 wheel replays all 250 identical inputs and 84
saved-PH request records. It throws the same quality-range error on 57 records,
representing 19 unique inventories, and returns on the other 193. Its EOS and
canonical checks are retained. This proves persistence across versions at the
interface level; **7.2 internals were not instrumented**. Its precise internal
attribution is not claimed from the 8.0 source trace. The preserved browser7.2
scalar interface is not needed for this native historical comparison.

Standalone limits remain strictly <10 Pa / <50 J/kg / <.01 K; canonical limits
remain <=.1 Pa / <=.1 J/kg / <=1e-4 K; local nonlinear scale remains 1e-11.
Accepted conservation (<1e-8 kg, <1e-6 kJ), thermal, temporal, event, finite-
difference, Newton and TR-BDF2 budgets remain byte-for-byte unchanged. No coupled
trajectory was run in B5, so no new conservation or complete A2 pass is claimed.

## Limits, loader separation and next decision

This is a bounded diagnostic investigation, not a general EOS sweep. No
critical-region, mixture-fluid, non-ammonia or global root-uniqueness claim is
made. Independent references use the same EOS; no new experimental dataset is
introduced. High-precision boundary signs depend on that mathematical EOS and
its exact constants, while the original independent uncertainty criteria remain.
Browser full-VLE configuration is not exposed by the preserved binding, so no
browser full-VLE execution is fabricated. Native/browser internal paths remain
distinct. Historical7.2 source causality and physical iPad validation remain open.

The inherited rejected-PT loader reference-count defect did not interfere:
B5's browser default raw recoveries do not throw C++ exceptions, and the observed
support failures are JavaScript adapter errors. Original rejected-PT cases and
loader files are preserved by hash. They were not rerun or repaired. No loader
cleanup error is interpreted as a thermodynamic failure.

Setup failures/attempts are retained: initial sandbox proxy isolation, WebKit
host-library warnings resolved with the same six hashed WPE dependencies,
and an auditor dictionary-indexing error corrected without changing evidence
or a scientific criterion. Instrumentation was extended from phase logging to
explicit Brent termination logging; the first trace and binary remain archived.
All individual bounded runs completed; no speculative functional fixes were
compiled. Reproduction commands, deadlines and artifact roles are in BUILD.md.

The smallest justified corrective work is **B5A: legacy native DU saturation
state consistency and physically validated phase/endpoint recovery**, with its
submechanisms independently gated. **B5B: numerical-boundary versus domain-exit
classification/representation policy** must remain a separate reviewed change.
A B5A success alone cannot certify exact-boundary adapter recovery. Detailed
owners, alternatives, risks and future complete A2 gates are in
[REPAIR_PROPOSALS.md](REPAIR_PROPOSALS.md). Approval is required before either
corrective milestone. The production model, UI, protected branches and hosting
remain untouched.
