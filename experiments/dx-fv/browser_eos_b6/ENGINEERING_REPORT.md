# B6 rejected-PT loader exception and lifecycle repair

**FOCUSED LOADER REPAIR PASS**

**Gate A PASS — ROOT CAUSE CONFIRMED. Gate B PASS — FOCUSED LIFECYCLE REPAIR.**
The legitimate property refusals remain errors. The isolated loader corrects
an unacquired native exception-reference release, preserves the original
saturation-proximity message, finishes runtime exception bookkeeping and permits
the tested subsequent supported updates without changing their scientific bits.
This does not qualify the overall EOS backend or complete A2 model.

## Checkpoint, preservation and decision order

Starting HEAD is exactly P1 `75e015fd3455e75fa85074e8748bc01eb8973624`; the
checkout was clean before creating
`research/browser-eos-b6-rejected-pt-loader-repair-20261016`.
All changes are additions under `experiments/dx-fv/browser_eos_b6/` relative to
that checkpoint. All **2044** starting tracked-file SHA256 values are preserved.
The audit rechecks **143** native/browser artifact identities (including native
archive decompression), **12** accepted A2 snapshots and **five** scientific
patches. Accepted root engine.js is byte-identical to A2. The fifth patch is
B5A's native-only liquid repair; B6 does not put it into browser WASM.

The actual B4C candidate WASM hashes to
`8c690c741d33d26f758a825ed5e4043af50cfc52a1e8587d8a5fb93732c026c5`,
and generated JS to
`ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217`.
No CoolProp rebuild, new WASM, coefficient/flash/source intervention or reference
replacement occurs. The ten mandatory sources/reports were read; their hashes
are in `reviewed-source-index.json`. Relevant preserved tests and actual generated
exception machinery were inspected before the repair decision.

The pre-edit design commit is
`6b1c69b82ed90ee113689f713cd10e31a089eef5`. The complete four-instance Gate A
receipt was sealed in **183295983435deea4d59a926dac8b8d86666123c**, before the
candidate existed. `verify-results.py` checks its absence in both trees.
The delivery SHA is the final commit containing this report, supplied by the
final response/branch HEAD; it cannot be self-embedded in its own Git tree.

Twenty-seven protected remote heads/tags are recorded at start and compared
before push. Separate read-only PR #3 head/merge observations also match their
pinned P1 values; the final audit checks those too. Production main, A2, all
other research refs, release candidate, UI and Live Plant are untouched. The
post-push clean/ref check is retained outside the commit to avoid self-reference.

## Gate A: primary rejection versus secondary assertion

The exact historical browser ledgers contain two affected P/T pairs at six
sequence positions per browser: three PT calls for each affected PH fixture.
`historical-rejected-pt.json` retains fixture identity, all preceding operations,
exact request bits, phase status, historical errors and fresh direct errors;
CSV is a flat companion. Inputs are extracted from saved results, not regenerated
from new saturation calculations or rounded approximations.

The unchanged historical loader, unchanged generated JS/WASM and unchanged
historical 47-case lifecycle run in **two separate instances per engine**.
Chromium 154.0.8037.57 and desktop WPE WebKit 26.5 reproduce all six secondary
assertions in every instance. All six are incorrectly surfaced cleanup failures,
each hiding a legitimate saturation-proximity PT refusal. Fresh direct updates
retain that primary refusal instead. No rejected PT is accepted as a state.

For example, P=30298.937123458254 Pa and T=218.262937027359 K are refused by
the existing 1e-4-percent saturation-pressure ambiguity rule. The raw escaping
object is a CppException with excPtr, native type/name and the original message.
Its live header has referenceCount=0, caught=0 and rethrown=0. The loader restores
the stack, then calls decrementExceptionRefcount at zero, asserting in WASM
libcxxabi line 149. Its catch never reaches the intended normalized Error throw.

This is **not demonstrated double cleanup by Embind**. The low-level exception
was never adopted as a counted catch reference. Generated Embind invocation does
not finish that escaping native catch. Neither the presence of excPtr nor the
existence of a decrement helper proves ownership. The generated CppException
also has no automatic destructor/finalizer for this native allocation.

Verbatim generated source slices, actual import/export inventory, pinned
Emscripten 4.0.12 implementation, live callback traces, original/final messages,
stack values, memory and subsequent operations establish the mechanism.
Control and observation-only historical lifecycle rows match exactly.

## Narrow correction and lifetime contract

The new `loader.mjs` is a complete isolated historical copy with an exact saved
diff. Historical loaders and WASM stay unchanged. The historical controlA default
selection is preserved; all B6 qualification explicitly selects candidateB.
Final source checks repeat original sequences, workers and default equivalence. It captures the artifact's
existing generated begin-catch/end-catch imports and marks actual native thrown
object identities through its generated throw/rethrow/resume callbacks.
A WeakSet holds those identities without keeping them strongly alive.

On evaluate failure it decodes the original meaning, restores the entry stack,
consumes a proven native identity once and executes the matched generated catch
pair. Begin-catch acquires count zero→one and adjusts uncaught bookkeeping;
end-catch releases the owned reference, invokes the destructor/frees storage,
pops catch state and clears exceptionLast. It does not simply remove cleanup or
add a blind increment/decrement pair. Unexpected cleanup failure remains visible
as an AggregateError retaining the primary diagnostic.

The outward interface remains a normalized JS Error with the original message.
For native escapes it additionally carries an immutable native-name/
representation snapshot, without an actionable stale native pointer. It does
not expose a live exception handle or retain the raw native object as cause.
Synthetic numeric throws, forged excPtr objects, ordinary JS Errors and binding
validation errors receive no native cleanup. Unknown values cannot manufacture
native ownership or physical-domain proof.

High-level PropsSI is different: C++ handles the primary refusal internally with
its own generated catch pair and returns nonfinite scalar output. The loader's
finite check then raises its existing `EOS returned a nonfinite property` error;
there is no escaping native exception to adopt. Instrumentation retains the
internal primary error; the public finite-check Error does not invent an
unavailable native type. Its generic text is inherited interface behavior, not
a second native cleanup or a successful property state.

Stack restoration is still required for escaping low-level update. Exception
storage is on the heap and remains valid across that restore. The historical
harness additionally makes two direct fresh updates outside evaluate, each
leaving 2928 bytes of stack use and an unhandled exception. Gate A preserves
those bypasses; B6's public evaluate contract does not claim to repair arbitrary
raw module/state callers. There is no hidden reset. After a failure, getters
are never used to construct an accepted state; the next supported update must
establish the complete state normally.

## Actual browser and lifecycle verification

For each engine the candidate and control replay all original primary-state
operation sequences and all six exact rejected positions. **315 original
supported operations** retain their bits. Final uninstrumented and diagnostic
candidate outputs/messages agree. Diagnostic cleanup enters at count zero and
ends at count one; no freed header is read.

The additional matrix contains **16 sequences × fresh/reused = 32 variants per
engine**: PT success chains, repeated/alternating failures, PH/DU recovery,
genuine PQ coexistence, stable liquid/vapor transitions, nonfinite input,
negative pressure, low/high supported interfaces, creation/disposal and bounded
alternation. It executes **312 supported and 286 rejected operations** per
candidate engine, with **310 fresh-object bit comparisons**. The long sequence
has 128 rejected/supported alternations in each fresh/reused variant. Every
candidate call restores its entry stack. All expected failures refuse, without
secondary assertions or a successful partial object.

Supported low-level versus high-level PT differs by only
5.820766091346741e-11 Pa in pressure, zero h/T in this sample, within original
budgets. Equivalent rejected PT is separately observed at both interfaces.
Four clearly labeled JS-origin injections include a number and excPtr lookalikes;
none triggers native catch/refcount cleanup. Separate prevalidation, unknown-mode,
post-native nonfinite-output and disposed-object errors retain honest refusal.

All created comparison states are deleted through Embind. Direct repeated
`delete()` refuses with BindingError before native double deletion. Evaluate
on a deleted object preserves the deleted-pointer diagnostic through its normal
Error normalization; it receives no native cleanup. No invalid reuse is allowed.

Each actual worker variant executes 64 alternating failures/recoveries plus
PH/DU/PQ. Supported worker/main-thread values agree; error serialization retains
the candidate diagnostic and refuses honestly. Main-thread timers continue.
Final ABI diagnostics run 16 additional rejections: historical uncaught count
is **0→16**, while candidate count and observed catch depth are **0→0** after
every rejection and after a high-level refusal. This corroborates bookkeeping
cleanup rather than inferring it from memory size or throughput.

## EOS, numerical budgets and C1 compatibility

Four original B1/B4A/B4B/B4C controls and their original signed probes retain
identical control/candidate outputs, derivatives and phase labels, and match the
corresponding historical scientific fields exactly. Saturated liquid/vapor,
interior PQ and stable homogeneous liquid/vapor controls retain their bits.
Twenty actual archived-native PH samples reproduce their historical values
exactly; two native PT refusals recover through the C API and free the handle.
Actual browser/native comparisons and original independent reference data are
retained; no new resolution or physical phase certificate is asserted.

The independent audit reapplies **13 original applicable same-branch signed FD
checks per engine**. Maximum normalized mass/energy contamination is about
2.17e-14 / 6.25e-14, below 1e-11. Cross-phase and endpoint-excluded homogeneous
slope assertions remain excluded under their original scientific rules.
Maximum homogeneous requested p/h residual is 5.47e-7 Pa / 6.57e-8 J/kg;
maximum normalized independent energy mismatch is 4.39e-14. The 20 focused
canonical recoveries, including cross-phase probes, have maximum differences
0.00085717 Pa / 1.18e-6 J/kg / 9.30e-11 K. Original tolerances are unchanged:
canonical <=0.1 Pa / <=0.1 J/kg / <=1e-4 K; normalized fluid residual <=1e-11;
standalone strictly <10 Pa / <50 J/kg / <0.01 K; independent reference resolution
1e-5 Pa / 1e-8 J/kg. Complete reference/phase qualification is not inferred from
small differences.

The **unchanged C1 wrapper** receives the B6 candidate. All seven original
35-bar errors and raw DU/PH bits reproduce exactly, including call-scoped C1
diagnostics. Both inward hazards also retain their bits and qualification-blocker
status. A labeled harness dispatch injection makes a C1 DU operation encounter
an actual rejected PT call: C1 classifies the error as numerical/solver, records
no raw accepted state and leaves physicalTrajectoryExit unproved. No PT
calculation is represented as a genuine DU physical failure.

An extracted existing C1 A2 subset runs five scenarios twice per engine: supported
control/candidate equality, transient refusal, persistent refusal with original
halving/floor/exact rollback/stopped-state behavior, and genuine thermal exits
at 200 K and 400 K. One run uses the original boundary error; one uses the actual
PT error under the labeled dispatch injection. All **ten scenarios per engine**
pass, preserving original conservation, thermal, Newton, temporal and nonlinear
assertions. The subset changes selection only inside B6's harness. No C1 adapter,
accepted dependency or solver semantics are modified; no full A2 campaign runs.

## Performance, limitations and review stop

`PERFORMANCE_AND_MEMORY.md` and raw samples report bounded matched costs,
initialization, deletion, worker latency, actual errors and memory limitations.
WebKit's rejected-call sample is about 1.33× control, and its candidate worker
has a 367-ms maximum observed heartbeat gap. These observations are retained;
there is no performance threshold, speedup claim or smooth-response guarantee.
The candidate performs the required cleanup rather than taking the historical
assertion path. Linear memory remains 56,360,960 bytes, which is not a leak proof.

The repair is tied to the audited JS exception ABI and tested evaluate paths;
future artifact/runtime ABI changes need a new audit. Bounded source-level
ownership and lifecycle evidence do not prove every possible browser heap or
arbitrary direct module API use safe. Setup/harness failures remain in
`EXECUTION_NOTES.md` and raw logs. No scientific acceptance criterion is relaxed.

All blockers in `RESEARCH_BLOCKERS.md` remain: seven 35-bar refusals, both inward
hazards, four Gate B endpoints, unqualified B5A Gate A browser repair, missing
P1 equilibrium topology/convex-envelope proof, complete backend/A2 and physical
iPad qualification. No production/UI/Live Plant, merge, deployment or hosting
change occurs. Recommended next scientific decision is independent review of
P1's bounded equilibrium-topology/supporting-tangent obligation, not automatic
C3 or browser certification. Stop now for engineering review and explicit
approval before any subsequent milestone or integration.
