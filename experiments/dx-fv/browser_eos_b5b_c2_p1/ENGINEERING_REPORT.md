# B5B-C2-P1 engineering report

**PARTIAL PHASE CERTIFICATION**

The missing saturation equations and local phase inequalities can be rigorously
enclosed with the unchanged ammonia EOS. Complete stable-equilibrium selection
for the two primary exact inventories is still conditional on an unproved
convex-envelope/topology obligation. Zero complete physical-branch certificates
are issued. This is not original scientific or browser qualification.

## Preservation and scope

The starting SHA is exactly `7c75d9538d57080a01dffbf7e06128a27e2b9ccd` on the
requested C2 branch, with a clean working tree before P1 branch creation.
All additions are under `experiments/dx-fv/browser_eos_b5b_c2_p1/` on
`research/browser-eos-b5b-c2-p1-phase-certification-20261016`.
All **1,996** starting tracked files were SHA256 hashed and retained in the Git
checkpoint. All **143** historical native/browser artifact identities, **five**
scientific patch digests and **12** accepted A2 snapshots were independently
verified. The accepted root `engine.js` is byte-identical to A2
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. All protected remote refs, including
main, PR #3, UI, demo candidate, Live Plant and research branches, were recorded
read-only before experiments. Final verification instructions are in README.

The accepted scientific implementation, EOS/reference, adapter, loader, C1,
accepted A2, production and UI files are unchanged. No new CoolProp source is
downloaded, reconstructed or compiled; no WASM build, merge or deployment occurs.
The single-branch repository clone initially lacked the unrelated UI Git object;
it was fetched read-only to complete the inherited audit. No protected ref moved.

All nine requested reports were read. `PROOF_OBLIGATIONS.md` was written before
new numerical prototypes. Initial arithmetic availability was Python 3.12.14,
mpmath 1.3.0, SymPy 1.14.0, NumPy 2.3.5 and SciPy 1.17.0; python-flint was absent.
The isolated `/tmp` environment installs python-flint 0.8.0, reporting FLINT
3.3.1. Arb, GMP/MPFR and inherited code/artifact hashes are recorded. NumPy,
SciPy and SymPy are not used by the certification calculation.

## Primary results and the remaining obligation

Exact saved M/U_kJ/V hex inputs are decoded directly, never reconstructed from
printed decimals. The unchanged inherited homogeneous bracket/cv proof repeats
for all nine originals at 192 and 256 bits. The following values are display
approximations of rigorous rational intervals retained in evidence:

| Primary inventory | Exact-M/U/V homogeneous p−max (Pa) | Historical raw p−max (Pa) | New whole-temperature coexistence inequality |
|---|---:|---:|---|
| webkit-ledger-69 | +3.049676615158225e-7 | −3.49245965481e-7 | d*−rhoL approximately +2.91112944666e-8 kg/m³ |
| webkit-ledger-76 | +4.6691712852129e-11 | −3.25962901115e-9 | d*−rhoV approximately −1.82264244374e-7 kg/m³ |

For 69, M=`3fd406de00d710be`, U_kJ=`406b448176d039b2`.
For 76, M=`3f913c19a47fa406`, U_kJ=`40394d3fa3941ea6`.
Both have V=`3f43a92a30553262`. Full exact d*,u* and pressure endpoints are in
`c2-reproduction.json` and `phase-matrix.json`.

The new uniform parameterized two-density contraction proof validates pL=pV
and gL=gV for **every** T in each entire homogeneous root interval. Positive
endpoint stability and disjoint densities are checked over the full boxes.
The local saturation densities for 69 are approximately 521.5319010449952 and
28.05137732886883 kg/m³; for 76 they are 521.5319003177706 and
28.05137758234070 kg/m³. The relative density inequalities have rigorous signs.
Their saturation contraction norm bounds are about 3.92e-24, strictly below one.

The three-variable volume-eliminated mixture formulation also proves local
algebraic coexistence roots at each exact inventory. Ledger 69 has Q about
−1.70513e-12; 76 has Q about 1.00000000087462. These continuations are rigorously
inadmissible. This excludes those particular roots, not every possible competing
state outside their small boxes. No quality is clipped or snapped.

Consequently both primary rows have `CONDITIONAL_PHASE_PROOF`: **if** the selected
coexistence curve is the equilibrium convex envelope and all relevant competitors
are covered/excluded as specified in `BRANCH_AND_TOPOLOGY.md`, the enclosed roots
are stable liquid/vapor and their exact equilibrium pressures are outside.
That hypothesis is **not proved or imported as a justified external theorem**.
Only the local roots and inequalities are unconditional numerical certificates
under the stated arithmetic/formula assumptions. The complete physical answer
remains unresolved. The expected topology has category C evidence only.

## Evidence levels and separate statuses

| Required status | Result |
|---|---|
| Local homogeneous root proof | Demonstrated for both primary inputs and all nine historical originals; uniqueness only within brackets |
| Coexistence proof | Demonstrated locally, including uniform full-temperature coverage; not global equilibrium optimality |
| Phase/branch proof | Primary stable-side inequalities demonstrated; complete primary equilibrium branch conditional/unresolved |
| Competing-phase exclusion | Relevant local inadmissible continuations excluded; all relevant competitors not excluded |
| Exact-inventory pressure proof | Rigorous outside pressure at both enclosed homogeneous roots; equilibrium interpretation conditional on branch selection |
| Original scientific qualification | Unresolved/unchanged; Level 2 does not confer Level 3 |
| Browser portability | Not demonstrated; no interval WASM/browser implementation or physical iPad test |

Level 1 comprises independent high-precision equations, residuals and seed/
precision repeats. Level 2 comprises the explicitly scoped IVT/contraction
arguments with rigorous arithmetic. Level 3 still requires every original
independent-reference, phase, browser, numerical, conservation and coupled
solver condition. These distinctions apply to every table and JSON output.

## Focused matrix and adversarial results

The matrix has **17** cases: the two hazards, seven original browser refusals,
three optional Gate B endpoint controls (148,162,165), and five separately
generated diagnostic controls. It contains **16** homogeneous proofs, **16**
parameterized saturation proofs and **17** mixture-root proofs at each of two
precisions. The generated interior mixture deliberately bypasses homogeneous
inversion. No fourth-variable solver or third formulation is attempted.

The generated liquid (335 K, about 34 bar), vapor (365 K, about 34 bar), exterior
liquid (335 K, about 36 bar), and mixture (344 K, Q approximately 0.5) have
validated local roots, endpoint stability and meaningful phase/pressure margins.
The requested **fully stable-equilibrium positive controls remain unqualified**
because their global branch gate has the same missing dependency. Calling them
independently proved stable would overstate the experiment.

The generated dome-interior homogeneous root has positive cv and local
compressibility and a rigorous local root. A separately validated mixture at
the **same exact d*,u*** has 0<Q<1 and entropy higher by an interval around
**0.0705894733111526 J/kg/K**. Under standard additive bulk-phase equilibrium
thermodynamics this rules out the homogeneous root as the stable equilibrium.
It does not prove that this competitor is the global entropy maximum.

Thirteen adversarial/incomplete-proof controls retain: invalid non-enclosing
box; singular preconditioner; equal-density trivial root; negative density;
zero/nonfinite T; an interval failing whole-temperature parameter coverage;
bad homogeneous seed; validated Q<0 and Q>1 continuations; a validated box
whose quality overlaps zero; the positive-derivative wrong-phase homogeneous
root; and pressure-inside/local-stability success without topology proof.
None becomes a physical-branch success. Failed numerical proposals remain
NUMERICAL_FAILURE, never an asserted physical model-domain exit.

The seven historical browser refusals are unchanged. C2's corrected split is
preserved: rounded DU **two inside/five outside**, exact M/U/V **one inside/six
outside**. Ledger 64 changes mathematical side when the target changes; only
75 is exact-M/U/V inside. No historical browser result is revised. Gate B's
independent-reference phase qualifications remain unresolved; C2 exact M/U/V
is separately labeled from its original rounded-DU mathematics.

## Independent arithmetic verification and cost

Both precisions independently satisfy full-box residual, Jacobian, strict
inclusion and contraction hypotheses. Five separate exact DT points audit
p,u,s,g and six analytic derivatives against independently differentiated
mpmath expressions. **208** additional derivative comparisons cover corners
of two primary parameterized saturation boxes and two mixture boxes, including
temperature parameter endpoints. Original volume/energy and alternate g
expressions are checked independently. All 17 diagnostic roots repeat at
65/90 digits and displaced seeds. These finite checks support correspondence;
they do not prove the whole evaluator, library or compiler.

An initial audit incorrectly demanded nested independently rounded Arb balls.
Their fixed-size radius representation means precision changes can shift a hull
without producing set nesting: all 33 endpoint/root boxes and 22 pressure hulls
in this run are nonnested in that strict sense. Both enclosures remain valid.
The corrected audit **revalidates every exact rational 192-bit proof box at
256 bits**, with its original parameter interval and whole-box Jacobian. All
**33** pass. The earlier failure/log and initial run remain preserved. No claim
of monotone interval widths or precision agreement as proof is made.

The final 17-row run takes about **17.73 s**, and independent verification
about **4.34 s**, excluding environment setup and preservation work. At 256 bits,
combined per-case validation has median **64.30 ms**, range **17.41–76.93 ms**;
the mixture-only control costs less work. These are bounded Python/Arb timings
including serialization, not optimized native/browser forecasts. Individual
attempts have 20-second deadlines; none times out. No arithmetic escalation
beyond 256 bits is needed. Initial and final runs are retained, not hidden.

## Scientific and operational consequences

All original contracts remain unchanged; the separate audit lists them.
For the nine historical primary rows, rigorous same-EOS local-root comparisons
bound raw recovery differences by about 6.55e-7 Pa, 1.57e-9 J/kg and 2.27e-13 K,
well within the original numerical limits. Those passes cannot establish phase,
override strict support or manufacture independent reference accuracy.
The primary pressure gaps are below the original 1e-5 Pa reference resolution.
No experimentally validated ammonia or measured plant pressure at those digits
is claimed. No new full A2/browser qualification campaign is run.

An eventual complete phase/support certificate could expose the two inward
hazards by checking exact stored inventory rather than the returned f64 pressure.
This experiment supplies stronger local evidence but does not implement that
detector. Mathematical outside evidence concerns the pinned EOS inventory;
numerically unresolved means insufficient approval evidence; a physical model
exit needs accepted independent trajectory/direction proof; a measured excursion
also needs plant measurements and uncertainty. They are different statements.

C1 semantics stay intact: boundary refusal remains refusal, numerical failure
does not prove physical-domain exit, genuine independently proved exits remain
protective, rollback stays exact, and raw diagnostic values never construct an
accepted state. No refrigeration high-pressure trip is manufactured.

## Stopping decision and next milestone

The two allowed formulations succeed locally. The essential remaining obstacle
is the equilibrium convex-envelope/topology proof, beyond these bounded root
tubes. The experiment stops at that obligation rather than expanding into global
EOS topology, critical-region research or a new precision campaign. Failure to
complete this proof here does not show mathematical impossibility.

Recommend **parking further certification and browser porting**, pending an
independent mathematical review that specifies one bounded topology/supporting
tangent dependency. Prioritize the separate rejected-PT loader repair under a
new authorization; no repair is started here. Do not begin C3, WASM intervals,
Gate B functional repair, full A2 qualification or physical iPad testing.

Commit/push only the named P1 branch, verify clean tree, all historical bytes
and protected remote refs, then stop for explicit engineering review.
