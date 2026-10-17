# New B7 generated-ABI compatibility review

**Compatible with the reviewed B6 lifecycle algorithm. No cleanup adaptation.**

The rebuilt control, exact A1 candidate and both logging-only variants were
independently audited before the main scientific matrix. Their complete generated
JS SHA256 is the historical B6 wrapper identity
`ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217`.
All four WASM identities differ and are explicitly retained. Compiler version
equality alone was not used as compatibility evidence.

`abi-generated-source.json` contains actual source slices and offsets for native
throw/resume, CppException, begin/end catch, exception reference helpers, Embind
invokers/trampolines and WASI environment callbacks. `wasm-abi-inventory.json`
parses every actual import/export and function signature, not just JS spellings.
All names/signatures and memory limits match the B6 artifact. Memory is unshared,
initial 344 pages (22,544,384 bytes), maximum 32,768 pages (2 GiB), with original
growth settings. New heap/type/string addresses are not assumed to be stable ABI
identities. Actual SDK libexceptions/libcxxabi source bytes also match the
preserved B6 source; tool/commit identities are retained separately.

## Low-level native escape

Actual low-level update errors are **CppException objects**, with excPtr and
native name/message. Generated throw/rethrow/resume callbacks establish their
object identity. They do not acquire a counted catch reference. The observed
live header has a 24-byte prefix and referenceCount=0, caught=0, rethrown=0.
The object has no automatic finalizer that adopts/releases the allocation.

For each of four B7 modules in each engine, 16 primary rejected PT calls are
observed. The loader restores its entry stack; these original fixtures require
2,928 bytes of restoration. Exception allocation is on the heap and remains live
across that restore. The matched generated `__cxa_begin_catch` import acquires the
reference, marks the catch and fixes uncaught bookkeeping. Immediately before
`__cxa_end_catch`, live count is 1 and uncaught count is 0. End-catch releases the
owned reference, calls the destructor, frees native storage, clears exceptionLast
and pops the catch. No freed header is subsequently read. Baseline and final
uncaught/catch-depth observations are 0/0 for every module/engine pair.

The uninstrumented B7 loader retains B6's WeakSet identity tracking and consume-once
generated catch pair. It does not infer ownership from excPtr or a number, blindly
increment/decrement, suppress an assertion, free raw memory or retry a property.
Only loader mappings, explicit artifact hashing, isolated runtime configuration,
test-pair/fresh-state utilities and optional read-only observation are added.
`loader-vs-B6.diff` is the complete difference. The outward native diagnostic is
immutable and contains no actionable stale native pointer or raw native cause.

## Different exception owners

| Observed path | Required ownership behavior |
|---|---|
| Low-level native update escape | Decode primary meaning, restore entry stack, consume proven native identity, generated begin/end pair exactly once |
| High-level PropsSI refusal | C++ already catches internally; nonfinite output triggers ordinary JS finite-check Error, with no extra native catch |
| Input validation / unknown test pair | JS Error, no native cleanup |
| Deliberately injected JS number, Error or excPtr lookalike | No native identity adoption or refcount operation |
| Nonfinite output after completed call | JS finite-check Error, no fabricated native type |
| Deleted Embind object / repeated delete | BindingError semantics, no native cleanup or accepted state |

Original rejected PT meaning survives as the saturation-pressure proximity error.
Each artifact/engine replays all six historical sequence positions, supported
follow-up calls, 32 additional fresh/reused variants, direct-versus-high-level
behavior and disposal. Worker tests repeat the historical sequences, synthetic
errors and 64 alternations. The independent auditor verifies 315 historical
supported operations per module/engine retain their bits; the original six
refusals remain errors. Supported requests establish a new complete state before
getters are accepted; a rejected update never supplies an accepted raw state.

This contract covers the loader's tested evaluate paths and isolated fresh-state
helper. Arbitrary users bypassing the loader through raw module/state APIs still
own their stack and catch discipline. There is no universal raw-call repair or
automatic reset. Future generated-ABI changes require another audit. Historical
B6 evidence for its old WASM remains unchanged and valid in its original scope.

Receipts: `abi-*-corrected.json`, `gate1-audit.json`, `regression-audit.json`,
`worker-audit.json`, `lifecycle-*-serialized.json`, `workers-*.json`. Initial
harness failures and their corrections are retained in EXECUTION_NOTES.md and logs.
