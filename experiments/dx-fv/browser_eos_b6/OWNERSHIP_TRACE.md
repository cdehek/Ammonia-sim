# Source and actual-call ownership trace

Read `ROOT_CAUSE_AND_REPAIR_DESIGN.md` for the pre-edit contract. The exact
historical generated source is indexed by byte offset in
`evidence/generated-js-trace.json`, and its complete file remains unchanged in
`../browser_eos_b4c/vendor/candidateB/coolprop.js`.

| Path | Initial owner and cleanup | Loader action required |
|---|---|---|
| Low-level PT update → generated throw/resume → Embind invoker → evaluate catch | Live uncaught allocation; count 0; JS CppException alone owns no counted reference | Restore entry stack, enter generated catch, exit generated catch exactly once |
| High-level PropsSI same PT refusal | C++ catches internally; generated begin/end already acquire/release, scalar returns nonfinite | Finite-output JS error; no extra native release |
| Nonfinite request / unsupported mode | JS validation before native update | Existing stack restore; propagate JS error, no native release |
| Nonfinite output after completed scalar | Native invocation returned; no escaping native exception | Propagate finite-check error; no native release |
| Embind BindingError (e.g. disposed state) | JS binding validation; no native exception allocation | Propagate; no native release |
| Numeric thrown pointer | Not produced by this artifact's actual traced calls | Never infer ownership from number; synthetic diagnostic only |
| Object with excPtr | Genuine CppException here, but property alone is insufficient | Require identity provenance from this module's actual generated callbacks |

Live header layout is corroborated by generated ExceptionInfo (24-byte prefix)
and pinned cxa_exception.h (first wasm32 size_t is referenceCount). Instrumentation
reads only live headers at throw/catch/pre-release, never after end-catch/free.
Pinned libcxxabi source line 149 and actual WASM RuntimeError agree. No assertion
is attributed to generic Emscripten behavior or guessed from the helper's name.

The actual-call records retain original and final messages, raw own keys/name/
constructor/excPtr, callback order, exact requests, stack, memory, next operations,
disposal and separate browser instances. Historical control and observation-only
copies produce identical lifecycle rows. Direct fresh update bypasses in the
historical test are explicitly outside evaluate's cleanup contract.
