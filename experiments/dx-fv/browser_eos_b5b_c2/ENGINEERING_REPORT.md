# B5B-C2 — exact-inventory numerical certification feasibility

**CONDITIONALLY FEASIBLE**

A validated **local homogeneous** pressure enclosure is demonstrated with
unchanged EOS coefficients and exact rational conserved inputs. A complete
pressure **and physical-branch** certificate is not demonstrated. Browser
certificate portability and original scientific qualification remain unresolved.
All 37 complete diagnostic outcomes are **UNRESOLVED**. Neither inward recovery
is repaired, accepted as qualified, or converted into physical trajectory proof.

Branch: `research/browser-eos-b5b-c2-inventory-certification-feasibility-20261016`.
Parent: exact `7809d08be67eab7cb9b537b1c1199b456b2da122`, checked clean before
branch creation. The delivery SHA is the commit containing this report, reported
by `git rev-parse HEAD` and in the delivery response; a commit cannot contain its
own SHA. All additions are under this directory. No EOS, adapter, accepted A2,
C1 implementation, loader, support policy, production integration, merge or
deployment changes occur. Stop for engineering review and explicit approval.

## Preservation

Before numerical experiments, all **1,937** starting tracked files were hashed,
all **143** archived native/browser artifact identities independently verified,
all five scientific patch digests checked, and all **12** accepted dependency
snapshots compared with Git objects at
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. C1 wrapper, propagation patch,
rollback implementation, reports and evidence remain byte-identical. Its Gate 1
and Gate 2 PASS results remain historical results, not C2 certification results.
Every remote head and PR #3 head/merge ref was recorded read-only. The final
audit checks those refs and all historical bytes again.

A later independent reconstruction of pinned upstream CoolProp
`ae81610e7d23efc57f9d051c8e70a4d66e87537f` applies all five inherited patches
and matches **1,782** Gate A source hashes. Each patch passes reverse applicability.
No reconstructed source is compiled or installed. Dependency manifests are
preserved; no new dependency-tree/build verification is claimed. The original
ammonia JSON matches SHA256
`4d451fadbe6eb1c2441169c599890cf7cd6edc818918f23959e2afb20a881e14`.
The unchanged browser candidate WASM remains
`8c690c741d33d26f758a825ed5e4043af50cfc52a1e8587d8a5fb93732c026c5`.
Receipts: `evidence/baseline.json`, `source-verification.json`,
`historical-file-hashes.json`, `refs-before.txt`, `final-preservation.json`.

All eight requested reports were read, together with B5's independent evaluator,
Gate B formulation, the historical adapter/loader, accepted thermodynamics,
C1 diagnostic envelope and preservation code. The scientific question here is
stronger than the existing support check: support of a returned floating-point
pressure does not establish support of the exact stored inventory.

## Exact reproduction and a material input-interpretation finding

Chromium **154.0.8037.57** and desktop WPE WebKit **26.5** reproduce all original
seven inventories and both inward controls with **identical original raw getter
bits**. All seven complete historical MVU calls refuse; both inward controls
return. The unchanged C1 wrapper retains those outcomes, with the seven
`boundary-unresolved`/`solver` failures and physical exit unproved. Originating
PH calls for both hazards are separately replayed in both engines using saved
input bits. All original M/U/V construction bits repeat.

The historical high-precision implementation actually certifies neither target:
it supplies Level-1 convergence evidence at **rounded binary64 rho_DU/u_DU**.
C2 retains that exact interpretation and additionally solves for **exact rational
M/V and 1000 U_kJ/M**, and for the mass-equivalent **rounded internal molar inputs**.
They are three different mathematical problems. No input is substituted in a
backend call. The following are signed Level-1 diagnostic pressures, Pa above
3,500,000; validated local enclosures independently agree with their homogeneous
signs. Physical branch evidence remains Level 1.

| Saved control | Actual binary64 recovery | Historical rounded-DU root | Exact M/U/V root | Rounded internal-molar root |
|---|---:|---:|---:|---:|
| webkit-ledger-69 | −3.49245965481e−7 | +2.94076290925e−7 | +3.04967661516e−7 | +3.18857513513e−7 |
| webkit-ledger-76 | −3.25962901115e−9 | +2.50420072426e−10 | +4.66917128521e−11 | −6.18740630714e−10 |

The exact conserved-inventory hazards therefore persist. Control 76 also shows
that an internal-coordinate enclosure can prove the **wrong external claim**:
its internal molar target is inside while its exact external inventory is outside.
This is not a pressure correction to apply at runtime.

There is a further necessary distinction in the original seven. The historical
**two inside/five outside** split is reproduced at rounded DU, unchanged.
At exact rational M/U/V, ledger **64** changes from −2.58101716514e−9 Pa to
**+3.22972603677e−9 Pa**. The exact-M/U/V split is therefore **one inside/six
outside**; ledger 75 is inside at −1.45517845677e−9 Pa. Keeping two/five while
calling it exact conserved-inventory mathematics would silently change the
target. No historical evidence is edited or reclassified in its original scope.
All seven runtime refusals and C1 meanings remain unchanged.

[MATRIX.md](MATRIX.md) presents every row. `evidence/inventory-arithmetic.json`
retains exact rational operation errors, input/output bits and molar conversions
for all nine primary inventories. Every raw p/T/h/s/rho/u/Q getter is retained
in both browser replays; native comparison additionally records native phase.
Exact M/U/V bits for the hazards are:

| Control | M | U_kJ | V |
|---|---|---|---|
| 69 | `3fd406de00d710be` | `406b448176d039b2` | `3f43a92a30553262` |
| 76 | `3f913c19a47fa406` | `40394d3fa3941ea6` | `3f43a92a30553262` |

Use the machine-readable bits as authoritative; display decimals are never
reparsed to reconstruct saved inputs.

## What was actually proved

The standalone `local_enclosure.py` uses python-flint **0.8.0**, FLINT **3.3.1**
Arb ball arithmetic, including rigorous transcendental evaluation. All rational
inputs and binary64 coefficient values are enclosed before operations. It
evaluates the same power, Gaussian, GaoB and ideal caloric terms with analytic
cv, separately from the inherited mpmath evaluator.

For a proposed positive-temperature interval at a fixed exact density:

1. Enclose u(T_low)−u* and u(T_high)−u* with strictly negative/positive signs.
2. Enclose cv=du/dT over the **whole** interval and require a positive lower bound.
3. Check positive density/temperature, finite evaluations and nonzero GaoB
   denominators. The expressions are continuous on that box.
4. The intermediate-value theorem establishes existence. Positive cv over the
   interval establishes uniqueness **within that interval at that density**.
5. Evaluate pressure over the entire density/temperature ball. Serialize exact
   rational outward endpoints, rather than treating rounded display text as proof.

The root estimate and the chosen `1e-30 K` trial radius are **proposals only**;
neither is a support tolerance or assumed error bound. Both endpoint signs and
the derivative bound must independently succeed. A bad seed fails. Wider
intervals may straddle the boundary and remain unresolved.

There are **81 local enclosures**, repeated at **192 and 256 bits**, covering
27 homogeneous rows × three target interpretations. The exact-inventory local
pressure signs for both hazards are outside. Their local pressure widths are
far smaller than the gaps. Their admissible homogeneous branches are supported
by independent high-precision coexistence/stability diagnostics, **not rigorous
phase enclosures**. The prototype therefore deliberately returns **UNRESOLVED**,
never `CERTIFIED_MATHEMATICAL_OUTSIDE` or `CERTIFIED_MATHEMATICAL_INSIDE`.

All 162 pressure/cv enclosures contain the separate 90-digit results. Five
additional DT points compare the independent analytic ball implementation with
the inherited EOS and numerical differentiation. Tests also retain bad-seed,
negative-density, boundary-straddling and dome-interior algebraic-root cases.
The last case has a valid local enclosure and positive cv but an incorrect
homogeneous physical branch. It still returns UNRESOLVED. These finite tests
support implementation correspondence; they are not a machine-checked proof of
the evaluator/library/compiler or of global EOS topology.

No coupled interval coexistence solver, certified saturation comparison,
global competing-phase exclusion, lower/temperature support certificate or
original-reference qualification engine is delivered. A local pressure sign
cannot fill those gaps. [FORMULATION.md](FORMULATION.md) defines the exact
problem and proof obligations; [STRATEGIES.md](STRATEGIES.md) compares methods.

## Independent controls and evidence levels

The focused matrix has **37 rows per browser**: nine primary inventories,
21 preserved PH boundary/interior probes, three inherited +100 Pa controls,
and four original Gate B endpoints. It includes liquid, vapor and genuine
equilibrium at meaningful inward pressures, explicit outward requests, exactly
35 bar and adjacent representable PH pressures. PH support and reconstructed
DU support remain separate. The matrix preserves different PH requests mapping
to identical conserved inventory bits.

All 37 have actual native and browser raw outcomes, historical adapter outcomes,
exact input bits, high-precision mathematical references and explicit original
qualification status. Rounded DU and exact M/U/V roots repeat at 65/90 digits;
internal molar roots use 90 digits. Primary exact-inventory homogeneous roots
also repeat with ±1 K displaced seeds. Mixture endpoints have independently
evaluated positive cv/cp/compressibility and coexistence residuals, but no
validated branch certificate. Gate A archived native endpoint checks retain
three actual QT exceptions and one liquid return; all four remain unqualified.

One initial diagnostic attempt, B5-sweep-19, fails while trying an unnecessary
homogeneous/saturation calculation for a genuine mixture. It is retained in
`references.json`. `equilibrium-supplement.json` solves its applicable physical
coexistence equations at both precisions and preserves that initial failure.
No failing row is removed. No homogeneous Jacobian is used to certify a mixture.

The nine primary and 24 PH diagnostics meet unchanged canonical budgets. The
independent returned-state EOS mass/energy checks for all 37 meet the unchanged
1e−11 local normalized limits. Passing those checks does not reverse strict
refusal, resolve Gate B phase qualification or qualify a full A2 trajectory.
All 37 also meet the original standalone numerical budgets against the exact
inventory reference: maximum differences are 8.15e−7 Pa, 1.86e−9 J/kg and
2.47e−13 K. Maximum 65/90-digit pressure change is 4.93e−54 Pa. These numerical
comparisons are retained in `scientific-audit.json`, with full qualification false.

Three evidence levels remain distinct everywhere:

- **Level 1 — HIGH_PRECISION_DIAGNOSTIC:** independent equations/evaluation,
  elevated precision, repeated roots/seeds and residual checks. These diagnose
  the likely branch/sign. Small residuals and agreeing digits are not enclosures.
- **Level 2 — certified numerical enclosure:** rigorous arithmetic and an
  existence/uniqueness argument for the stated target and region. C2 demonstrates
  this only for a local homogeneous root and its pressure. The complete
  branch/support certificate is unresolved.
- **Level 3 — original scientific qualification:** independent reference,
  phase, canonical, nonlinear, conservation and simulator requirements. Neither
  a nanopa same-EOS sign nor a Level-2 local enclosure establishes this level.

No calculation proves experimental ammonia properties to nanopa accuracy, or an
actual physical plant-domain excursion. The pressure separations are below the
original independent reference resolution of 1e−5 Pa.

## Cost and portability

Each local attempt uses three interval EOS evaluations, including cv. On this
host, 81 attempts at 256 bits have median **15.03 ms**, range **13.39–26.10 ms**;
192 bits have median **15.14 ms**. Timing includes Python loops, coefficient
lifting, ball work and diagnostic endpoint serialization. It excludes root
search, initialization, rigorous phase validation, competing-root exclusion,
all original numerical gates, transfers and worker startup. Whole multi-target
reference cases have median 0.949 s, with different work and incomplete branch
proofs. These are bounded diagnostic observations, not performance forecasts.

The Arb operations execute in a native compiled library through Python. A direct
C++ certificate implementation or compiled WASM verifier was **not** built.
The actual browser measurements are historical property replay only, using
56,360,960 bytes of WASM linear memory; they are not certificate timings/memory.
C1 timings are classification-wrapper timings. Neither predicts a browser
multiprecision implementation. Desktop WebKit is not physical Safari/iPadOS.

WASM ordinary f64 round-to-nearest and JavaScript Math functions do not provide
the directed transcendental interface needed by a naive interval port. A
software validated arithmetic library, or a separately proved rounding/error
implementation, would be necessary. Native fenv support alone does not prove
libm transcendental rounding. Reassociation, fast-math, FMA contraction and
underflow behavior must be controlled/tested for any error-transform design.
An Arb-style integer/ball implementation is a plausible candidate; its actual
build, artifact identity, WASM results, cost and worker behavior remain unmeasured.

[RUNTIME_AND_INTERFACE.md](RUNTIME_AND_INTERFACE.md) evaluates always certify,
validated fast path, selective fail-closed contract and no demonstrated runtime
certificate. No trigger based on an arbitrary pressure epsilon is proposed.

## Gates and next decision

| Gate | Decision | Evidence and missing work |
|---|---|---|
| A — mathematical certification | **UNRESOLVED** | Local homogeneous root/pressure enclosures demonstrated. Full relevant physical branch, coexistence/endpoints and competing-phase exclusion not certified. |
| B — binary64/runtime feasibility | **UNRESOLVED** | Native multiprecision local proof works. Ordinary binary64 pressure is insufficient; validated browser arithmetic, full algorithm and cost not demonstrated. |
| C — original scientific qualification | **UNRESOLVED** | No limit is weakened. Level-2 local proofs can be additional evidence, but endpoint/reference, full property and A2 requirements remain open. |

The narrowest next milestone is a separately reviewed **validated local phase
verification feasibility experiment**: interval coexistence/saturation root
boxes with explicit branch/topology and endpoint inequalities, first for a
bounded 35-bar neighborhood, at the exact rational M/U/V target. Require genuine
mixture and metastable counterexamples and an independent proof review before
considering any browser port. No acceptance integration or C3 is started here.

## Scientific requirements and separate blockers

All original requirements remain unchanged: canonical <=0.1 Pa/<=0.1 J/kg/
<=1e−4 K; normalized fluid mass/energy <=1e−11; standalone strictly <10 Pa/
<50 J/kg/<0.01 K; independent resolution 1e−5 Pa/1e−8 J/kg. The maximum remains
exactly **35 bar absolute**. Lower pressure 0.3 bar, 195.495 K property floor,
table availability, 30 K subcooling/250 K superheat, accepted signed finite
differences, phase admissibility and exact conservative M/U/V remain protected.
Five-section mass/energy conservation, finite tube/fin/air accounting, Newton,
TR-BDF2, domain stops and exact rollback are byte-preserved, not rerun as a full
qualification campaign. Original aggregate conservation <1e−8 kg/<1e−6 kJ and
thermal closure 1e−12 K remain intact.

B5A Gate B's four endpoints remain unresolved under the original independent
phase reference. Gate A's focused native repair still lacks browser qualification.
The rejected-PT loader cleanup/reference-count defect is neither exercised as a
repair campaign nor fixed. Full spatial/temporal/property-domain/conservation/
controller/rollback/event/long-duration A2 qualification remains pending.
Physical iPad testing remains pending. No UI, Live Plant, Cloudflare or protected
checkpoint changes occur. No support tolerance, clamp, inventory rewrite,
substituted state, unproved certificate success, merge or deployment occurs.

Stop for engineering review and explicit approval.
