# B6 pre-edit decision

**Gate A: ROOT CAUSE CONFIRMED.** This design precedes every functional B6
loader change. The commit containing this design is the Gate A commit; its full
identity will be recorded in the later delivery receipt. Starting commit is
`75e015fd3455e75fa85074e8748bc01eb8973624`.

## Reproduced mechanism

The unchanged B4C loader and unchanged candidate WASM reproduce **six secondary
assertions per browser instance**, in two independent Chromium instances and two
independent desktop WPE WebKit instances. Each saved sequence has two consecutive
PT attempts after PH, then PH, PH, DU, PT, PH. The two original affected fixtures
are the low-pressure B4A liquid approach and the 350000-Pa liquid endpoint.
All six errors in each historical browser ledger are secondary assertions; none
is merely the intended refusal. Separate fresh direct update errors retain the
primary saturation-proximity refusal. Every saved input is extracted without
regeneration, with binary64 bits in `evidence/historical-rejected-pt.json`.

For example, P=30298.937123458254 Pa and T=218.262937027359 K are refused because
the temperature's saturation pressure is within the existing 1e-4-percent PT
ambiguity rule. That rule is unchanged. The full original error text is retained
in actual-call evidence; the surfaced historical error instead asserts
`exception_header->referenceCount > 0` at libcxxabi line 149.

The loader calls `decrementExceptionRefcount` at zero. This is an **unacquired
reference release**, not demonstrated double release after an automatic binding
cleanup. The assertion executes inside WASM libcxxabi, induced by the loader's
incorrect use of the binding ABI. The catch block does not reach its intended
`throw new Error(message)`. A visible later successful PH call does not establish
sound exception ownership: the native allocation and generated exceptionLast /
uncaught-exception bookkeeping are left unresolved.

## Actual pinned ownership contract

`evidence/generated-js-trace.json` contains verbatim source slices and byte
offsets from the preserved JS, whose SHA256 is
`ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217`.
The WASM SHA256 is independently verified as
`8c690c741d33d26f758a825ed5e4043af50cfc52a1e8587d8a5fb93732c026c5`.
Pinned Emscripten 4.0.12 source at compiler commit
`6f625bd62ee64f4f8cd11476774741b961e4a2d5` is preserved with provenance.

1. `__cxa_allocate_exception` zero-fills the header, including referenceCount.
2. Generated `__cxa_throw` initializes metadata, creates CppException with
   excPtr/name/message, sets exceptionLast and increments uncaughtExceptionCount.
   It does **not** acquire a reference. CppException has no finalizer/automatic
   release. The raw thrown value here is an object, not a number.
3. Generated invoke trampolines restore their local stack and signal C++ landing
   pads. The observed low-level update path eventually invokes resumeException
   and escapes Embind. Its generated invoker contains a direct invoker call and
   ordinary argument-destructor code afterward, with no JS catch that adopts
   the escaping exception. No begin_catch occurs for these escaping PT errors.
4. The loader sees a live, uncaught native exception, count=0, caught=0,
   rethrown=0. Read-only live header observations agree in both engines.
5. Generated `__cxa_begin_catch(ptr)` marks caught, reduces uncaught count, clears
   rethrown, pushes exceptionCaught and increments the reference to one.
6. Matched generated `__cxa_end_catch()` clears setThrew, pops that catch,
   decrements the owned reference, invokes the actual exception destructor,
   frees the allocation and clears exceptionLast. These are the artifact's
   existing JS import callbacks, not guessed C++ exports.

High-level PropsSI differs: C++ handles the same primary error internally through
its generated catch machinery and returns nonfinite output. The loader's finite
check raises a JS Error. That path must receive **no extra native catch or
reference release**. PropsSI native type information is not available at its JS
finite check and must not be fabricated.

## Stack and state contracts

The loader's entry stack capture/restore is required for an escaping update;
the measured entry and catch differ by 2928 bytes on the primary fixtures.
Restoration does not release heap-allocated exception storage. Preserve the
existing restore before completing native catch. The header and error meaning
remain valid across that restore. The historical full lifecycle also makes two
fresh direct updates outside the loader: each leaves a 2928-byte stack decrement
and an unhandled exception. Those are harness bypass observations, **not** a
reason to change supported calculations or to claim the loader owns all direct
module calls. B6's repaired contract covers `evaluate`, not arbitrary callers
using exposed raw module/state APIs. Direct callers still own their own catch
and stack discipline; no automatic state reset is added.

A rejected update leaves partial state internals. Do not read getters to construct
an accepted state after failure. The next supported update must establish its
complete state through the existing update API. Test fresh/reused equality;
only then permit tested reuse. Dispose through Embind `delete()` exactly once.
Deliberate post-delete access should give BindingError without native cleanup.

## Minimal proposed correction

In a new B6 loader copy, retain the original artifact import callbacks for
begin_catch/end_catch. Observe only the real generated throw/rethrow/resume
callbacks to mark their exact thrown object identities in a WeakSet. Re-throw
those objects unchanged from the callbacks. On evaluate failure, decode the
message before cleanup, restore the entry stack as before, and **only for an
identity marked by that module's generated native throw path**, consume the mark
and call the matched generated begin/end pair once. Convert the original message
into the outward JS Error, preserving an immutable native name/representation
snapshot without an actionable stale native pointer. Keep cleanup failure
visible with the original diagnostic if cleanup unexpectedly fails.

This provenance test avoids treating numeric values, forged excPtr objects,
BindingError or ordinary JS Errors as owned native exceptions. No header probing
or refcount manipulation belongs in the final uninstrumented candidate. The
observation-only copy will record begin at zero and end at one; it must never
read the freed header afterward. Unknown JS-origin throws preserve their error
meaning and receive no native cleanup. Numeric/native representations not
produced by this exact artifact are diagnostic synthetic coverage only, never
claimed as observed CoolProp paths.

Do **not** simply omit decrement (allocation/bookkeeping leak), merely add
increment/decrement (uncaught bookkeeping/exceptionLast still stale), call raw
free (misses destructor/bookkeeping), or suppress the assertion. No generated
JS/WASM rebuild or modification is justified.

## Risks and acceptance tests

This is deliberately tied to this JS exception ABI; a future Emscripten/WASM-EH
artifact needs a new ownership audit. The callback pair must be available or
initialization must fail honestly. Provenance must not admit synthetic pointers,
and consumed identities must not be released twice. Generated C++ internal
catches must remain independent. WeakSet retains no exception strongly. Cleanup
must clear bookkeeping through existing callbacks rather than hide a fault.

Gate B must replay all six original sequence positions, exact saved P/T bits,
two actual engines, main/worker, recovered versus fresh states, unchanged
uninstrumented versus diagnostic candidate, PT/PH/DU/PQ and saturation controls,
post-delete refusal, prevalidation/nonfinite-output/BindingError paths, explicitly
synthetic JS errors (including numeric and excPtr lookalikes), repeated failures,
and bounded performance/memory observations. Preserve supported scientific bits
and original canonical/standalone/nonlinear/reference budgets. Use original
signed finite differences and an existing focused C1 A2 fault subset. Seven
35-bar refusals and the two inward hazards keep their original statuses.

The correction operates only after a failed property call and at exception
creation callbacks; it never changes any successful native input/output or EOS
operation. It does not retry, reset state, substitute P/T, change coefficients,
flash/phase decisions, thresholds, accepted A2, C1 classification or P1 proofs.
Thus it has no mechanism to repair thermodynamics; unchanged successful bits
must still be demonstrated. All broader boundary, phase and model blockers
remain. Stop after this authorized B6 milestone for engineering review.
