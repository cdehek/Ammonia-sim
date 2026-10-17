# Failure, transport and rollback matrix

PASS for the focused tested paths in actual Chromium and desktop WebKit.
Baseline accepted table physics and isolated C1 failure physics remain separate.
No error becomes a successful refrigerant state. See `failure-lifecycle-audit.json`,
`c1-*.json.gz`, `lifecycle-*-final.json.gz`, `errorsbench-*.json.gz`, `memory-*.json`
and optional `b7-*-phase-getter.json.gz` for individual evidence.

| Case | Tested result / retained meaning |
|---|---|
| Supported nonzero exchange | Unchanged B6 subset runs original C1/control factories; accepted cells/energies/ledgers/events/settings equal; original budgets pass |
| Transient synthetic property refusal | Actual unchanged C1 wrapper emits the failure; existing harness injects it into real Newton PH work; two failed trials, original halvings then supported progress to .0011 s |
| Persistent synthetic refusal | Numerical solver stop, unconfirmed physical exit; 20 attempts/19 halvings; final attempted dt=1.9073486328125e-9 s; original floor 1e-9 s |
| Retry/proposal semantics | Original floor, 30-iteration Newton, line search, signed FD, TR-BDF2 and growth behavior unchanged; no latency-dependent step |
| Existing C1 rejected-trial rollback | Original harness checks accepted JSON at every failed trial, cell/thermal/ledger reference identity, original proposal after rejected advance, retained stop freeze |
| B9 additional worker-owned exact rollback | Exact binary64 accepted spec/cells/M/U/V/energies/initial state/clock/ledger/events/schedule/accepted-step values before/after all 20 refused trials; original individual cell, cells-array, energies and ledger references retained INSIDE worker |
| Failed accepted-state record | Additional persistent MVU refusal retains solver stop and original available diagnostic, throws recordFailure; no fabricated sections/property object |
| Independently proven 200 K exit | Original exact-boundary/outward-direction recheck; domain stop; accepted physical state rolled back |
| Independently proven 400 K exit | Same original independent proof; domain stop distinct from numerical property refusal |
| JS-origin Error | Pointer-free name/message crosses test-worker envelope as refusal |
| Actual native/WASM PT exception | Optional B7 uses unchanged reviewed loader; original text/native name retained, generated catch ownership completed before serialization; stack delta 0, uncaught/catch-depth baseline retained |
| Original 35-bar refusal | Optional default B7/C1 complete operation refuses as boundary-unresolved/solver; exact original input identity retained; trajectory exit unproved |
| Native exception after-error success | Original supported PH bits restored by a NEW valid update after rejected PT; no getters from rejected update |
| Unsupported request/command/order/version | Explicit refusal before scientific dispatch; no accepted time advance |
| Duplicate advance, concurrent and replay | Client coalesces identical pending request; owner replays completed response cache; original .0001 request advances once |
| Duplicate altered content | Explicit mismatch refusal |
| Stop during pending solve | FIFO stop acknowledged after entire synchronous requested advance returns; physical model.stop remains unchanged; no mid-Newton cancellation claim |
| Requests after scheduling stop | Advance refuses, snapshot remains last accepted state |
| Stop/dispose pending work | Already running advance completes; disposal acknowledges its accepted clock and drops owner/cache references |
| Disposed request | Refuses; client ends session and rejects pending requests |
| Initialization failure | Invalid original fixture refuses with null scientific clock/state; safe disposal |
| Failed worker module fetch | Actual missing module produces worker error; no successful session |
| Failed WASM fetch | Optional B7 loader reports actual HTTP 404; no initialized state |
| Stale session / older display version | Deterministic injected late envelopes cannot install a display; newer accepted data retained |
| Reset/restart | New session/worker and exact original initial conditions; old session IDs cannot install results |
| Crash / emergency termination | Pending promise rejects. Last received accepted clock reported; in-flight work unknown/unrecoverable. This is session loss, NOT solver rollback |
| Actual navigation/unmount | Actual panel pagehide terminates pending disposable worker; new page remains uninitialized; no accepted state fabricated |
| Repeated sessions | Matched timings plus three main/three worker memory cycles complete in both engines; explicit owner disposal and worker termination |

Synthetic C1 faults are NOT naturally reached plant EOS failures. The actual C1
wrapper receives a synthetic refusing EOS and retains its true stateMVU operation,
exact input bits, original text, numerical class and unproved trajectory status.
The preserved subset deliberately routes that error into Newton; stage/section
lineage records the injection location without changing the original operation.
B9's additional bit-exact refusal originates in actual MVU reconstruction calls.
Optional B7 separately routes a REAL rejected PT through C1 with explicit synthetic
dispatch labeling; it is not misrepresented as a natural DU flash failure.

Existing subset equality uses its original JSON test arithmetic. Additional B9
checks use binary64 tags, covering signed-zero identity where present. Structured
clone cannot retain references across realms. No cross-realm identity claim is
made. Ordinary stop/counter/diagnostic bookkeeping is excluded from physical
rollback as in the original algorithm; physical spec/events/clock are included.

Error transport keeps operation, original available message, faultKind,
propertyCause/domainCause, section/stage, input bits, retry evidence, accepted
clock/version, record refusal and proof status. Errors serialize as immutable
plain data. Native exception headers, pointers, callback args, module/state
handles and live Error objects never cross the boundary. B7 observational ABI
callbacks remain local; only count/catch outcomes and stack difference are sent.

These focused tests do not requalify all historical C1 scenarios, natural
refrigerant-domain exits, every phase event or arbitrary direct raw WASM use.
