# Runtime feasibility and proposed diagnostic attachment

This document is a design proposal. No new runtime acceptance, fault kind,
certificate consumer, adapter behavior or A2 change is implemented.

## Four possible architectures

| Option | Scientific strength and semantics | Work/cost/memory | Portability, responsiveness and evidence |
|---|---|---|---|
| A — always certify | Strong if every recovery has exact-target pressure, admissible branch, full support and all original numerical/physical checks. Pressure-only success is insufficient. | At least a validated inverse/branch proof per recovery. C2 local component uses three ball EOS evaluations after root search; equilibrium/global phase work additional. Multiprecision libraries and scratch memory add unmeasured size/heap. | Native local component exists; full native and WASM certificate not demonstrated. Synchronous use could harm training responsiveness. Worker queue/deadline/cancellation design and measured throughput required. |
| B — fast path plus verification | Valid only with an independently justified cheap uncertainty/error bound and branch evidence. Escalation is triggered by inconclusive **proof**, including phase uncertainty, not arbitrary returned-p epsilon. | Cheap verified enclosure on each call; full verifier when inconclusive. Extra EOS/derivative evaluations and escalation frequency unknown. Both arithmetic paths/libraries may increase memory. | Requires reproducible native/browser bounds and rigorous browser transcendentals. Worker escalation can preserve UI timers but may delay simulation steps. No complete bound or browser cost demonstrated. |
| C — selective fail-closed envelope | Accept only recoveries with all required certificates; unresolved stays refused. Restricting the accepted operating envelope may require separate scientific contract approval. A valid formerly supported state must not silently become unsupported. | Potentially bounded verifier budgets with more unresolved outcomes. State coverage, refusal rate and worker memory unmeasured. Original recovery and solver checks still required. | Portable software arithmetic plausible. New unresolved behavior can stop trajectories and affect training continuity. No changed policy is authorized here. |
| D — no practical runtime certificate demonstrated | Preserve strict checks and truthful C1 failure semantics. Existing supported-looking inward hazards remain explicit qualification blockers. This does not assert that strict checks certify inventory support. | No new verifier runtime cost. Existing property/classification cost unchanged. | Current B4C browser control remains reproducible; no new browser qualification follows. Engineering can retain blockers until a complete proof/cost experiment succeeds. |

The justified present operational position is D while mathematical feasibility
work remains open. A/B/C are candidates for separately reviewed work, not policy
adoptions. Option B is potentially attractive after a validated bound and branch
method exist. A point residual or empirical maximum error from saved tests cannot
serve as its universal uncertainty bound.

## Actual measurements and excluded costs

`evidence/performance.json` retains all summary definitions; per-attempt timings
are in `local-enclosures.json`. At 256 bits the local homogeneous proof has 81
attempts, median 15.03 ms, maximum 26.10 ms. It evaluates interval EOS/cv three
times and includes Python dispatch, repeated coefficient lifting and endpoint
serialization. It excludes root search and all phase/global support proof.
This is not an optimized direct C++ benchmark. High-precision diagnostic case
times include a different mix of solves and cannot estimate compiled browser cost.

Actual historical property replays run in Chromium and WPE WebKit. The observed
B4C memory is 56,360,960 bytes. This is **not** the memory footprint of a numerical
certificate. No C2 browser certificate code, worker latency, certificate memory,
training throughput or physical-iPad measurement exists. C1's classification
performance/lifecycle observations remain valid in their original scope and are
not reused as numerical-certification timings.

No new WASM backend build is justified before the missing physical-branch proof
is resolved. A later small standalone arithmetic portability experiment should
use identical exact-rational fixtures, compare enclosed rational endpoints rather
than expecting bit-identical midpoints, pin compiler/library artifacts, and
exercise cancellation, worker cancellation/deadlines, overflow/underflow and
serialization. Acceptance depends on valid containment and signs, not matching
ordinary backend pressure bits. Worker delivery must not allow stale results to
become current after a newer trial has started.

## Proposed future certificate fields

Attach a versioned optional object to the existing structured diagnostic
envelope. It is additional evidence, never a property state or physical proof.

```
schemaVersion, trustedIssuer, methodVersion
inventory: {M_bits, U_kJ_bits, V_bits, units, exactRationalTarget, identity}
eos: {fluid, originalJSON_SHA256, binary64CoefficientConvention,
      sourceCommit, sourcePatchHashes, evaluatorHash,
      backendJS_SHA256, backendWASM_or_native_SHA256}
reference: {convention, leadConstantBits, offsetStateIdentity}
arithmetic: {library, version, artifactHashes, precision,
             roundingAssumptions, compilerBuildIdentity}
root: {equationsVersion, enclosingRegion, existence,
       uniquenessScope, competingBranchExclusion}
phase: {branch, evidenceMethod, endpointEnclosures,
        qualityEnclosure, stabilityConditions, topologyScope}
pressure: {unit: "Pa", lowerExactRational, upperExactRational}
support: {boundaryIdentity, maxPa: 3500000,
          lowerPressureEvidence, temperatureAndTableEvidence}
status: CERTIFIED_MATHEMATICAL_INSIDE |
        CERTIFIED_MATHEMATICAL_OUTSIDE | UNRESOLVED | NUMERICAL_FAILURE
validityConditions[], independentEvidenceIdentity
scope: {simulationGeneration, cell, acceptedStateIdentity,
        trial, substep, stage, propertyOperation, requestNonce}
physicalTrajectoryExit: unproved
```

These fields are **proposed**, not an implemented C2 protocol. Level-1 results
must carry `HIGH_PRECISION_DIAGNOSTIC` evidence type and may not occupy a
certified success field. Local C2 pressure bounds explicitly say local root
only, phase false, complete status UNRESOLVED. Missing phase/root/support fields
are not positive evidence. The hard maximum is an exact boundary, not an epsilon.

Exact input values and artifact/reference identity must be checked on issuance
and consumption. Bind trial/cell/stage and accepted-state generation even if
two numerical triples are equal. Any inventory edit, new trial, stage change,
reference setter, source/artifact change or support contract revision invalidates
the appropriate certificate. A hash detects mismatch; it does not authenticate
the issuer. In-process issuer-owned immutable objects or an authenticated worker
channel with validated serialized evidence are necessary. A fixture name, pressure
guess, previous PH result or prior accepted state is not an issuer.

## Relationship to C1 and accepted A2

Preserve C1's current structured failures exactly. Numerical failure remains
`solver` with physical exit unproved. Boundary uncertainty remains fail-closed.
Unsupported explicit PH remains refused in input scope. Genuine independently
proved physical-domain exit remains protective. Exact rollback, original retries
and all nonlinear/temporal/conservation rules remain in force.

A future mathematical OUTSIDE certificate is an exact-input mathematical finding;
it does not automatically supply a trajectory exit proof. INSIDE cannot override
an original adapter refusal, an independently unsupported explicit PH request,
an unresolved physical phase reference, a failed canonical/nonlinear check or
another original support condition. A separate reviewed integration decision is
needed before any certificate influences runtime acceptance. An UNRESOLVED or
NUMERICAL_FAILURE finding supplies no thermodynamic state, wet flag, physical
event, invented residual or permission to retry with modified inventory.

If A2 consumes such evidence later, preserve the underlying property operation
and scope through thermodynamics, fluidCall, Newton/probes, rejection/halving,
floor evidence, stop and record. The accepted state/ledger/thermal objects must
still roll back exactly. No stale accepted-state proof may be used for a failing
trial. C2 implements none of those attachments or consumption paths.
