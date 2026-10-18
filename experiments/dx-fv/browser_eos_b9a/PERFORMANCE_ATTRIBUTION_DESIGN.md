# B9A pre-optimization attribution design

Frozen before implementation. Start: B9 b1a65c9365879d6e97eff649e56371df3907e86e.
Only additive B9A files. Accepted source and literal B9 package remain unchanged.

## Question and controlled workload

Do not select a cause in advance. Test solver/property work, observational
diagnostics, copying, transport, initialization, and mixed causes. Use exactly
B9's frozen cold/warm fixtures, settings, checkpoints 0/.0001/.0005/.001 s and
requested advances .0001/.0004/.0005. No horizon extension. Exact in-owner
state/record/attempt/property-count comparisons precede performance claims.

Mode A imports the untouched B9 service/client for the original control. Mode B
uses the same package, settings, observer and original record generation; only
detached response construction, retained diagnostic access and transport differ.
Mode C is conditional on B parity and measured diagnostic cost. No reduced audit
run will be described as full diagnostic qualification.

## Actual source boundaries

Use performance.now around externally accessible original calls without editing
source bodies or inserting arithmetic into model code. Timed calls use try/finally
so refusals remain counted. Costs are inclusive unless explicitly exclusive.

| Boundary | Attribution and limitation |
|---|---|
| loader('properties.json') | Original JSON parse plus loader dispatch; not engine creation |
| createEngine | Original engine construction; separate from parse |
| createCoupledModel / model.create | Factory / five-section initialization separately |
| engine.ph, sat, stateMVU | Original public property calls; nested work included; internal lexical sat calls cannot be separated by this wrapper |
| thermodynamics exported factory methods | PH validation and M/U/V recovery inclusive; nested engine calls must not be added again |
| coupledNewton export | Newton solve including residual/FD/line-search work |
| supplied evaluate callback | Actual original residual evaluation inclusive of thermal coupling and PH work |
| implicit.solveLinear export | Linear solve only |
| model.trial export | Explicit trial probe only; advance closes over lexical trial so wrapper does not isolate its internal calls |
| observeAttempt callback | Callback/push overhead only; excludes original diagnostic event construction |
| model.advance | Original full trial/retry/commit and final record; no isolated commit/retry/line-search timing claim |
| model.record | Original recovery/accounting plus JSON record clone; cannot call this pure copying |
| structuredClone(state/attempts/response) | Identified scientific-state, trace and cache-copy boundaries |
| exact / JSON.stringify | Evidence tagging / full comparison serialization, measured outside physics |
| payload projection | Detached operator extraction only; never feeds model |
| postMessage | Synchronous enqueue/clone boundary; not isolated wire transit |
| RTT minus service | Dispatch, queues, clone and handling combined; not pure transport |
| receive / render | Main handling / DOM mutation separately; RAF after mutation is render scheduling upper bound |

Finite-difference Jacobian and line-search diagnostic events supply exact work
counts. Their lexical loops, thermal accounting, trial rejection/retry and atomic
accepted commit have no independently hookable timing boundary in the unchanged
package. Report their containing solve/advance cost and explicit unisolated status.
Do not infer individual elapsed costs from event counts. Optional browser sampling
profiles may supplement, but cannot replace actual boundary measurements.

Instrumentation changes exported references only in a separate attribution
loader BEFORE dependent modules are evaluated. It delegates each call exactly
once, with original receiver, arguments, results and thrown values. Compare the
instrumented run bit-for-bit against an uninstrumented run. Report instrumentation
overhead from three interleaved uninstrumented/instrumented runs. No global array
or JSON monkeypatching. Headline matched benchmarks use minimal boundary timers.

## Diagnostic, lifecycle and memory boundaries

Measure original observer event collection as included in Newton; callback push
separately. Record diagnostic construction remains inside original functions.
Measure original full state/attempt/cache cloning independently and isolated
post-run repeated clone/exact/serialization operations on detached evidence.
Never deduct a microbenchmark cost as if it were an exact in-solver component.

Worker creation, service-module evaluation, dynamic scientific import, table
parse, engine/factory/model construction, initial original record, first operator
projection, first receipt, DOM mutation, next frame, disposal acknowledgement,
termination and fresh-worker restart are distinct boundaries. Module evaluation
before a worker can receive requests is included in creation-to-first-receipt,
not claimed isolated. Every restart creates original initial conditions. Warm
HTTP/OS caches are uncontrolled; fresh worker is not cold-machine startup.

Track 256-response count cap, eight-pending cap, retained recent diagnostic count,
estimated JSON bytes (not actual structured-clone wire bytes), browser-child RSS
and exposed heap only. RSS sums shared pages and is not per-worker heap. No leak
or leak-freedom claim. Test cache exhaustion, failure replay, expiration, session
replacement, disposal and navigation. No authoritative buffer transfers.

## Predeclared matched campaign and stop

Both actual Chromium and desktop WebKit. Three sequential interleaved rounds,
orders A/B, B/A, A/B; each block fresh page/context; each fixture fresh worker
then fresh-worker restart. If C is justified, collect a separate three-mode
campaign A/B/C, C/A/B, B/C/A and disclose its reduced diagnostic scope. No concurrent
physics campaigns. 10 ms heartbeat, RAF intervals, real acknowledgement button
clicked by independent automation every ~50 ms. Preserve median/p95/max, all
outliers, failed attempts and browser versions. Report startup, service, end-to-end,
payload, clone, render, input, scheduling and memory individually. No product of
unrelated timing ratios; no sustained real-time claim from .001 s trajectories.

Commands have 30 s deadlines; browser stages 120–300 s; setup 420 s. Stop on any
scientific mismatch, swallowed error, serialization mutation, altered rollback,
need to edit protected source or weakening of acceptance. Optional B7 is deferred
unless all mandatory gates have passed. Final commit/push only the authorized
branch and stop for engineering review; operator integration remains NO-GO.
