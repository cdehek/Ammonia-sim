# Proposed boundary-outcome contract — for review, unimplemented

The hard maximum remains **3,500,000 Pa = 35 bar absolute**. A state whose
actual returned pressure exceeds it is refused. Accuracy within 0.1 Pa is a
different requirement and cannot authorize that state. Conversely, a refused
computed pressure alone does not establish an intended physical trajectory exit.

The supported design is a **fail-closed evidence contract**, combining options
1 and 4 in [OPTIONS.md](OPTIONS.md). It reports what failed and what is known;
it does not make boundary recovery successful. Classification is allowed to
remain uncertain. A complete automatic physical diagnosis from today's MVU
arguments is impossible, as the exact input collisions demonstrate.

## Separate facts before assigning an outcome

Retain four independent facts: (1) support of an explicit requested input, if
known; (2) whether a raw inverse returned and passed its numerical/phase gates;
(3) support of the actual returned coordinates and, where independently known,
the exact inventory's same-EOS state; (4) whether a physical trajectory exit is
independently established. Each fact has `yes`, `no`, or `unknown` evidence.
An unknown must never be coerced to yes. Numerical and physical uncertainty are
different, even if both prevent acceptance.

Proposed semantic outcomes follow. These are not current `faultKind` values.
The existing interface capabilities are detailed in [INTERFACES_AND_A2.md](INTERFACES_AND_A2.md).

| Class | Definition and required evidence | Permitted inference and operator meaning | Existing information and missing information | Scientific status and solver effect | Relationship to faults |
|---|---|---|---|---|---|
| A — confirmed physical-domain exit | Independent, adequately resolved supported-model/trajectory evidence establishes an excursion beyond a support boundary. Bind the proof to the current accepted state, physical direction, trial interval, boundary and model version. Preserve A2's independently rechecked thermal outward-direction proof. Refrigerant proof must distinguish an unsupported direction from a failed inverse. | “The supported operating envelope has been exceeded.” A diagnostic EOS nanopa sign alone is insufficient. A model proof means a model-domain exit; claiming a measured real plant excursion additionally requires measurement uncertainty. | Stateless adapter has neither trajectory nor rates, accepted-state identity, proof nor physical measurement uncertainty. Caller has direction and accepted state but currently trusts a `domain` recovery error too broadly. | Refuse the trial; preserve rollback and protective domain-stop under original rules. Never install a partial property state or advance by an uncertified trial. | `domain` is appropriate only with qualifying context/proof for a physical-exit assertion. Existing generic `domain` does not provide that proof. |
| B — numerical recovery failure | No raw inverse state, nonfinite output, inadmissible branch/quality, or failure of applicable original numerical, thermodynamic or conservation requirements. Record which gate failed and actual residuals. | “A reliable property state could not be calculated.” No inference of physical impossibility or domain exit. Positive derivatives or a small algebraic residual alone do not prove a physical root. | Loader supplies finite raw properties or an Error; it does not supply a numerical error bound or stable-branch certificate. Adapter has inputs but omits independent validation and loses exception details. | Refuse/reject trial, halve under existing rules, preserve exact rollback; persistent failure can end at a solver stop. It is not a supported recovery or successful domain stop. | Explicit numerical `solver` compatibility kind; distinguish property inverse failure from Newton iteration failure in evidence. Do not invent `nonlinearResidual` to trigger A2 growth learning. |
| C — boundary uncertainty / representational conflict | Raw state is otherwise accurate but refused at strict support, or support/branch evidence is insufficient; includes a supported originating PH state whose exact rounded inventory is mathematically outside. Record uncertainty and any demonstrated mechanism separately. | “Calculation stopped at a boundary that cannot be accepted; a physical excursion has not been established.” Previous PH acceptance does not authorize the rounded DU state. | MVU has exact M,V,U and raw result locally, but no verified origin, physical intent, branch certificate or error bound. It can report a strict support refusal honestly. It cannot infer a PH-derived origin from these inputs. | Failed/unresolved operation. Refuse, rollback and retry under original numerical failure rules; halt as numerical/unresolved if persistent without independent domain proof. Uncertainty cannot generate a property state, wet flag, or plant event. | Proposed `solver` compatibility kind plus structured `boundary-unresolved` reason. Existing adapter currently says `domain` for seven cases. A live change requires separate review. |
| D — supported successful recovery | Actual returned state satisfies all required property accuracy, admissibility, conservation and strict support gates; explicit original requested input, if present, is supported. Independent requirements are also met; no unresolved applicable qualification gate. | “A supported state was recovered.” This means success of this operation, not backend qualification or a promise of future progression. | Adapter returns properties, original inventory and two residual fields on success. These are necessary but do not alone establish independent phase/reference accuracy. Full standalone/coupled evidence is external. | Only this class permits ordinary accepted-property use. Trial acceptance still requires all original Newton, temporal, phase-event, thermal and conservation checks. | Ordinary successful return, no failure kind. An error, C state, or unqualified endpoint must never take this path. |
| E — independently unsupported input | An explicit original requested coordinate lies outside support, or an exact supplied inventory has independently resolved unsupported status with adequate evidence. This is an input claim; it is not automatically a trajectory claim. | “The requested input is outside supported properties.” A one-ULP-above explicit PH input remains unsupported even if inventory rounding or DU output moves inward. | Explicit PH receives P/h and can apply strict comparisons. MVU receives no original P/h; arbitrary DU needs independent inventory evidence. It cannot reconstruct a lost request. | Refuse input/trial. Initialization or edit rejection must not install it. Follow original rollback rules. Domain-stop reporting requires A-level trajectory evidence, not just this class label. | `domain` may describe explicit PH input rejection, while evidence must say input scope, not plant exit. A stateless DU unsupported-input finding without trajectory proof should use numerical/refusal compatibility or await caller proof; feeding E blindly into A2's MVU domain proof is unsafe. |

An input can have multiple facts: an unsupported requested PH input can also
have a numerical inverse error. Preserve both. For a primary result, E takes
precedence over any apparently successful inward result; A requires a separate
verified proof; B takes precedence when an inverse or numerical requirement
fails; C is the conservative fallback; D requires all applicable affirmative
evidence. An unsupported input is never “rescued” by D. A verified A proof may
coexist with B, but B is not itself that proof.

The two numerical wrong-side originals **pass** their original canonical and
nonlinear budgets. Calling them canonical inverse failures would be false.
Operationally all seven are C: refusal with a demonstrated mathematical
mechanism (`numerical-wrong-side`, two; `rounded-inventory-conflict`, five).
Those subtypes come from offline exact-inventory analysis, not today's adapter.
Their mathematical sign does not confer physical certainty below the original
reference resolution. B remains available for actual inverse/phase/residual
failures, including the inherited QT exceptions.

## Proposed failure record and ownership

A future versioned record would carry the following, explicitly **new** fields:

```
schemaVersion, operation, inputScope, inputBits, inventoryBinding
rawRecovery: returned | failed
rawCoordinatesBits?                 // diagnostic only; not a returned state
checks: {canonical, nonlinear, phase, support, independentReference}
requestedInputSupport: supported | unsupported | unknown
returnedCoordinateSupport: supported | unsupported | unknown
exactInventorySupport: supported | unsupported | unresolved | unknown
physicalTrajectoryExit: confirmed | unproved
reason, mechanism?, evidenceReferences[], uncertaintyComponents[]
```

Each check is `pass | fail | unresolved | unmeasured`, with units, method,
limits and actual values. Record the boundary and measured comparison exactly;
do not introduce a pressure margin. References are immutable, typed and scoped
to input, EOS and caller context. No field above exists implicitly in today's
MVU signature. No `rawCoordinatesBits` payload is a successful property return.

The adapter owns raw-versus-accepted separation, exact unit conversion facts,
input identity and strict support refusal. CoolProp owns flash status and actual
getter coordinates, not plant intent. A caller owns explicit original PH context,
trajectory identity, rates and trial lineage. An independent numerical verifier
owns any certified bound; a diagnostic label must not claim to be such a verifier.
The accepted solver owns acceptance, rejection and domain-stop proof. UI wording
must consume those semantics without manufacturing operational protection logic.

For an initial classification-only implementation, **retain refusal** and emit
explicit `solver` numerical/unresolved failures for recovery support failures
whose physical exit is unproved. Attach raw diagnostics before `convert` throws.
Do not claim a “near” boundary from an arbitrary magnitude threshold: without a
certificate even a larger recovery refusal may remain unproved. Known explicit
unsupported requests still fail. Preserve an independently established true
domain exit. This is a proposal, not an implemented fault mapping.

The existing `faultKind` channel can protect refusal and distinguish coarse
solver/domain failures, but cannot carry all five meanings by itself. Evidence
must survive `thermodynamics.ph`, `fluidCall`, Newton wrapping, rejection tracing,
minimum-step proof, stop construction and recording. Changes to those meanings,
especially refrigerant `domainEvidence`, require a **separate scientific contract
review**. Merely adding a new string kind while A2 expects `domain`/`solver` is
not a complete implementation.

## Provenance is explanation, not a support exemption

An optional originating certificate must bind exact requested P/h bits and
units, actual PH backend result bits, accepted PH guard evidence, EOS/fluid and
reference convention, artifact/source identity, M/V/U bits, every operation and
rounding step, operation-order version, and caller generation/cell/stage/trial
identity. Recompute the inventory using the accepted binary64 operation order
and check all bits before trusting the relationship. Protect certificates using
an immutable factory-owned object or authenticated channel; a bare hash detects
mismatch but does not authenticate an issuer. Cross-process/worker transfer
needs validation of a serialized certificate and trusted issuer/version.

Any inventory update, cell/trial change, artifact/reference change or boundary
edit invalidates the originating relation until recomputed. Prevent replay of a
certificate for a prior trial, another cell, or a numerically equal but differently
scoped request. A pressure guess, fixture name or previous accepted state is
not a certificate. Direct DU input has `origin=direct-DU`, no inferred PH origin.
Missing, stale, mismatched or untrusted metadata restores unknown provenance;
it must not restore success. Verified origin still cannot prove that its rounded
inventory is inside support. It only justifies a representational explanation.

## Numerical certificates, distinct from physical/reference resolution

A future bound must enclose the actual fixed-inventory stable EOS solution.
Use outward-rounded intervals with verified EOS/transcendental arithmetic and
unchanged binary64-promoted coefficients/reference convention. Enclose inverse
residual evaluation and the Jacobian, establish the relevant root's existence
and local uniqueness/admissibility, and separate homogeneous branches from
equilibrium endpoint equations. Positive cv and compressibility are necessary
local evidence, not a global stable-branch proof.

For exact binary64 M,V,U, there is no uncertainty in the stored numbers.
Reconstruction rounding is a known change from the originating state, not a
free interval within which the inventory may be rewritten. The certificate
must include the exact division/mass-to-molar conversion semantics it certifies.
Any separate physical input uncertainty stays separately labeled. Likewise,
EOS evaluation error, inverse residual error, operation rounding and independent
thermodynamic reference/model uncertainty must not be summed into a convenient
acceptance epsilon.

An enclosure wholly inside the unchanged bound can support a numerical inside
claim, only with the other gates. An enclosure wholly outside establishes
mathematical unsupported inventory, not automatically a physical trajectory
exit. A straddling enclosure yields C. At an exact endpoint a sufficient proof
must allow equality and stable coexistence; never demand homogeneous derivatives
across a real phase change. Existing lower pressure, temperature floor, bounded
table availability, subcooling/superheat and thermal limits need their own
arguments. This milestone provides converged high-precision diagnostics, **no
rigorous interval implementation or runtime certificate**.

The offline prototype uses the inherited `1e-5 Pa` reference resolution only as
a conservative uncertainty screen, never as an allowed excess over 35 bar.
It withholds independent D classification from two historically accepted
boundary-mixture rows while preserving their observed success. That screening
is a proposed diagnostic policy, not a newly imposed accepted requirement or
proof that those historical operations failed. Adopting any stricter runtime
certificate requirement also needs scientific review.
