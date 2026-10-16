# Numerical certification strategies and false-certification threats

Every candidate must target exact external M/U/V and unchanged binary64 EOS
constants/reference. Pressure proof and physical branch proof are separate.
No method below alone establishes original scientific qualification.

## Candidate comparison

| Candidate | Exact pressure enclosure and numerical root proof | Phase, saturation and endpoints | Native/WASM validity and likely cost |
|---|---|---|---|
| Directed-rounding intervals | Yes if **all** basic arithmetic, coefficients, rational conversions, powers and transcendentals are enclosed. Forward pressure at an approximate root alone gives no inverse-root proof. | Couple to a validated homogeneous bracket or coexistence box; bound q/w and saturation sides. Dependency inflation can make near-endpoint tests unresolved. Intervals alone do not reject metastability. | Native fenv does not certify libm; JS/WASM has no general rounding-mode interface. Software intervals/validated transcendentals needed. Extra endpoints/evaluations, possible subdivision and precision escalation; bounded local boxes can be inexpensive, broad boxes costly. |
| Verified scalar root bracket | Proves existence from continuity and opposing enclosed residual signs. An enclosed positive cv proves local homogeneous uniqueness. Direct interval pressure encloses the exact root. **Demonstrated locally in C2.** | Not valid as mixture inversion. Needs a separate stable-branch certificate; a dome-interior root can pass. Near saturation, certify the inequality or return unresolved; exact endpoint equality requires proof. | Three interval EOS evaluations per local attempt in this prototype. Uses native Arb balls; no WASM implementation measured. Root-search and branch costs additional. |
| Interval Newton / Krawczyk | Can prove local existence and uniqueness under the actual inclusion/nonsingularity hypotheses. A point inverse Jacobian may precondition but is not the proof. Can handle coupled coexistence equations. | Must enforce separated endpoints, valid T/q/w, endpoint stability and stable coexistence topology. A box for an algebraic mixture does not prove global physical selection. Degeneracy near criticality or q sign uncertainty remains unresolved. | Constant-size 2–4 dimensional verified linear algebra plus many interval EOS/derivative evaluations and possible subdivision. Outward transcendental/Jacobian evaluation needed. Native and WASM require matching validated arithmetic; not implemented here. |
| Compensated binary64 | Error-free transforms can improve sums/products; an explicit, proved remainder bound can contribute to an enclosure. Compensation alone gives neither root existence nor uniqueness. Cannot remove upstream EOS/input conversion error. | Must still evaluate branch inequalities rigorously; cancellation at endpoints can remain dominated by EOS error. Cannot reject a metastable root by small residual. | TwoSum/TwoProd require documented rounding, subnormal, overflow and contraction assumptions. Reassociation/fast-math can invalidate them. A few arithmetic operations per term for sums; enclosing transcendentals/whole inverse adds work. No certified implementation demonstrated. |
| Double-double | More digits improve separation; ordinary double-double is not an interval proof. Needs error bounds for every operation, constants, division/powers/transcendentals and solver. | Endpoint sign/branch could become resolvable, but physical selection remains a separate proof. A high-accuracy metastable root is still wrong. | Basic arithmetic is portable in principle with controlled IEEE operations; libraries differ in transcendental guarantees. Several to tens of f64 operations per scalar operation, more for validated transcendentals; no measured browser implementation. |
| Localized higher precision | High precision **with rigorous ball/interval bounds** can enclose pressure and residual/Jacobian boxes. Repeated mpmath digits alone are Level 1. | More precision can resolve q/w signs in a validated coexistence box, but cannot replace stable-branch/topology evidence or original physical reference. C2 higher-precision coexistence remains diagnostic. | Native Arb/MPFR-style backends plausible. WASM software arithmetic/library port required. C2 local ball work ~15 ms through Python; this is not a compiled-browser forecast. |
| Residual/Jacobian pressure bound | Potentially yes via a theorem whose bounds hold over an enclosing region and whose existence/root-selection conditions are established. A point condition number or first-order correction alone is insufficient. | Must use the appropriate homogeneous or coexistence equations and enclose branch inequalities on the same region. Cannot continue a homogeneous Jacobian through a phase boundary. | Could reduce work with analytic derivatives and small matrices; rigorous evaluation and derivative extrema may dominate. No complete bound for ordinary CoolProp getters is currently available. |
| Hybrid fast path + rigorous near-boundary verification | Scientifically valid if the fast path produces a **defensible enclosure**, including conversion and branch uncertainty. Escalate when it cannot decide, not when an arbitrary epsilon says “near”. | Need a valid branch proof on the fast path too; pressure distance alone does not screen metastability or unresolved endpoints. Escalated unresolved results stay unresolved. | Potentially pays multiprecision only for difficult inputs. Requires a verified cheap bound and a bounded worker verifier. Memory, hit rate and latency are unmeasured. No accepted policy change is implemented. |

All “yes” entries assume correct interval software and a correct mapping of the
original EOS, not merely use of an interval datatype. Real powers over positive
domains require validated log/exp or a proved alternative. GaoB denominators,
Planck-Einstein caloric functions and derived constants must be included. The
caloric reference term must remain unchanged. Interval Jacobians must be valid
over the entire chosen box. Compiler behavior is part of any arithmetic proof.

## Branch and metastability proof obligations

For homogeneous verification, enclose both the fixed-inventory root and the
relevant coexistence endpoints at its temperature. Prove positive stability
derivatives and the appropriate saturation-side inequality over the box. To
exclude other physically relevant phases, either supply a separately justified
stable EOS topology theorem over the claimed domain or validate the competing
thermodynamic potential/convex-envelope inequalities. A single sampled
coexistence root or positive local derivatives supplies neither argument.

For coexistence verification, use disjoint positive-density endpoint boxes,
exclude their diagonal/trivial root, establish p and chemical-potential equality
and physical q/w, and validate endpoint stability and the selected stable branch.
Quality practically equal to zero/one is not permission to snap it to an endpoint.
If interval quality crosses a physical endpoint, withhold certification unless
an exact endpoint relation is independently proved. Near criticality, lost
endpoint separation or singular interval Jacobians can force UNRESOLVED.

C2 independently solves saturation/coexistence at high precision to diagnose
these questions and retains excluded algebraic continuations. It does not claim
that this numerical selection is a mathematical branch proof. The four Gate B
endpoints retain their original scientific phase uncertainty even if future
mathematical enclosures become available.

## Threat register

| False-certification hazard | Evidence required to exclude it | C2 status |
|---|---|---|
| Inverse converges to metastable/dome-interior homogeneous root | Validated stable saturation/phase inequalities plus competing-branch/topology argument; no inference from cv alone | Explicit adversarial homogeneous enclosure at ledger 148 stays UNRESOLVED |
| Certificate silently uses rounded M/V or u_DU | Exact rational bits-to-input derivation; input-binding audit and bound on every conversion if internal variables are used | Three target interpretations retained; ledger 64/76 sign changes exposed |
| Internal molar target mistaken for external conserved target | Exact rational mass/molar conversion or rigorous transportation bound to external input | Control 76 internal target inside, external outside; never substituted |
| Residual/Jacobian estimate treated as enclosure | Enclosed residual, valid whole-box derivative/Jacobian, actual theorem hypotheses, existence and uniqueness scope | Scalar bracket plus interval cv implemented locally; no point-Jacobian proof claimed |
| Jacobian valid only at center | Automatic/analytic interval derivatives over the full box; singularity/denominator exclusions | Whole-interval analytic cv enclosed; no coupled Jacobian claim |
| libm/Math transcendental is not outward rounded | Proven correctly bounded implementation, including range reduction, underflow and hard-to-round values | Uses native Arb ball functions; ordinary browser Math is not accepted as proof |
| Compiler changes compensated/interval expressions | Verified build flags and operation semantics, artifact hashes, optimization/architecture differential tests appropriate to the proof | No new C++/WASM build. Native Arb identity recorded; full portable proof unresolved |
| Saturation endpoint insufficiently resolved | Validated endpoint boxes and q/w sign/equality enclosures at exact input | Level-1 diagnostic only; endpoints remain unresolved |
| Interval encloses one root but misses another relevant root | Prove claimed domain covers all relevant alternatives or supply validated thermodynamic topology/free-energy argument | Not established; no full certificate emitted |
| Pressure narrow but phase unresolved | Separate mandatory phase evidence with no unknown-to-true coercion | All 37 complete outcomes UNRESOLVED |
| Unsupported inventory recovers inward | Verify original inventory directly; never infer its support from raw p | Both hazards reproduced in both browsers; local exact pressure signs outside |
| Distinct PH requests produce same M/U/V | Preserve explicit request bits/support separately; never infer PH origin from MVU | Boundary triplet collisions retained in matrix.json |
| Coefficients parsed as exact decimals | Lift original parsed binary64 rationals and bind original JSON/artifact/reference | JSON digest and exact promotion checked |
| Reference-energy offset changes without invalidation | Bind lead/reference constants and setter state; reject mismatch | Default unchanged convention only; future invalidation specified |
| Reduced precision/serialization loses outward enclosure | Serialize exact rational outward endpoints with signed units/schema and identity; validate on receipt | Local enclosures retain dyadic rational endpoints; decimal displays nonauthoritative |
| Stale cell/trial/stage certificate reused | Exact inventory, artifact/reference and full caller lineage binding with trusted issuer and invalidation | Interface proposal only; no consumer/API implemented |
| Missing/failed verification silently succeeds | Explicit unresolved/failure values; closed outcome algebra and adversarial checks | No full certified statuses emitted; failed attempts retained |
| Near criticality or GaoB singular box invalidates continuity | Prove domain/denominator/endpoint separation, finite evaluations; subdivide or refuse | Positive-domain/finite/GaoB checks in local proof; no critical-region claim |
| Platform native/browser raw values assumed identical | Execute actual artifacts in both environments and preserve differing bits | Both browser engines measured; native comparison retained separately |
| Mathematical outside sign called physical plant exit | Independent adequately resolved scientific/trajectory evidence with caller scope | PhysicalTrajectoryExit remains unproved in C2 |

No fixture-specific correction, magic band, learned classifier, pressure clamp,
preferred root substitution or inventory repair is proposed. The local bracket
radius is an independently checked proposal, not a hidden support tolerance.

The remaining branch proof is a concrete mathematical gap, not evidence of
fundamental impossibility. Conversely, the existence of a multiprecision library
is not evidence that a practical complete native/browser certificate has already
been established.
