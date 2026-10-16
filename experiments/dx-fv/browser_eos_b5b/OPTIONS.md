# Alternative designs and engineering recommendation

All options retain strict support refusal, exact input inventory, original
equations/reference convention, original scientific budgets and phase
admissibility. Smaller exception counts are not an acceptance criterion.

| Option | Owner / information needed | Scientific value and feasibility | Risks / false positives and negatives | Performance and native/browser implications |
|---|---|---|---|---|
| 1. Strict rejection with truthful classification | Research adapter stateMVU/convert/sat; error wrapping at loader and accepted thermodynamics boundary. Capture exact input and raw-before-guard data. Caller owns physical proof. | Immediately feasible to report “recovered coordinate refused, physical exit unproved.” Existing MVU cannot identify originating PH or prove the two/five split on its own. Narrow conservative classification is supported; detailed mechanism needs offline reference or new evidence. | Wrongly calling every recovery refusal a physical exit is false positive domain reporting. Calling every raw return success permits false acceptance. Conservatively unproved failures can halt genuinely unsupported states numerically rather than diagnose their physical cause; they still refuse them. | Small bounded copying/validation overhead expected, not measured. No EOS recompilation intrinsically required for adapter diagnostics; native wrappers need equivalent typed status. Loader cleanup is independent. |
| 2. Explicit verified originating provenance | Stage/initialization inventory factory and versioned adapter interface. Needs immutable exact-bit relationship, trusted origin, artifact and trial/cell identity; see contract proposal. | Can establish supported origin and arithmetic lineage, including independently unsupported request. The exact input collisions prove this is genuinely new information. It can distinguish direct DU from PH-derived DU; cannot certify current rounded inventory support. | Stale, forged or unrelated certificates; previous accepted P mistaken for current support. A “supported-origin => success” rule rationalizes an invalid result and is rejected. Missing metadata must not become success. | Constant-size data per inventory; lifecycle/worker serialization and retention costs unmeasured. Native/WASM bindings need identical bit/units semantics and trusted ownership. Separate scientific/interface review required. |
| 3. Certified numerical boundary classification | Independent verifier or EOS numerical kernel plus adapter/caller certificate interface. Needs rigorous evaluation/residual/Jacobian bounds, stable branch evidence, exact conversion semantics, independent physical/reference uncertainty separately recorded. | Could establish inside/outside/unresolved mathematically without an arbitrary epsilon. Repeated 65/90-digit roots support diagnostics but do not supply a verified interval algorithm. No implemented certificate is demonstrated here. | An incomplete bound can falsely certify support or phase. Inventory rounding is not allowable input freedom. A mathematical outside proof is not physical excursion proof. Endpoint conditioning and branch topology need independent treatment; no universal tolerance across phases/boundaries. | Potentially substantial EOS work and outward-rounded transcendental implementation; native/WASM rounding, compiler flags and interval portability must be qualified. Costs unknown; Python diagnostic timings cannot predict production cost. Further numerical research, not narrow classification implementation. |
| 4. Explicit unresolved propagation | Adapter emits refusal with explicit numerical/unresolved reason; caller preserves it to trial rejection, retry and terminal stop. Uses existing solver compatibility only where truthful; reviewed typed contract for full propagation. | Scientifically defensible default whenever evidence is insufficient. Does not need a guessed pressure radius or a successful alternative flash. Persistent exact-inventory conflict is allowed to stop progression honestly. | May retain avoidable false rejection or miss a physically true exit diagnosis when proof is absent. It never accepts the unsupported result. Poor wrapping can still turn numerical errors into domain proofs or drop evidence; floor/initialization/record paths require focused tests. | Cheap metadata handling expected, but no live implementation benchmark. No claim of improved simulated duration. Native/browser error behavior must be deliberately aligned, not inferred from native success. |

## Selected next action, only after review and explicit authorization

The narrowest corrective milestone is **isolated truthful failure classification
with strict rejection**, combining options 1 and 4. First approve the versioned
failure semantics and their A2 consumption in a separate scientific contract
review. Then a separately authorized implementation may capture exact inventory
and raw diagnostics, refuse the unchanged strict condition, and retain an
unproved numerical/boundary outcome through the caller. Keep the current accepted
solver untouched until its interface meaning is explicitly reviewed.

This solves misreporting: a recovered numeric coordinate outside support is no
longer by itself asserted to be a physical trajectory exit. It does **not** solve
exact-boundary accepted recovery, the five exact-inventory conflicts, two wrong-
side recoveries, endpoint qualification, rejected-PT cleanup, full backend
qualification or any operational protection. It needs no originating metadata
to say “physical exit unproved”; it needs verified PH lineage for the more specific
representational-origin claim, and independent trajectory evidence for A.

Proposed source owner is the research property adapter and a reviewed property-
failure envelope between its caller and A2, with preservation of loader numerical
exception status. No CoolProp solver change is necessary to report this narrow
truth. No pressure epsilon, clamp, replacement inventory, preferred input echo,
EOS edit or source backend repair is part of the recommendation.

True unsupported requests remain refused. True resolved model-domain exits
remain protective stops. The main residual false-negative risk is incomplete
physical diagnosis, never acceptance of an unknown state. Main false-positive
risks are an untrusted proof, lost input scope, or legacy default-to-domain
wrapping. Both require tests. Reporting an honest numerical halt may shorten
progression relative to an imaginary fallback; no supported progression result
is sacrificed by refusing invalid states.

Estimated scope: small adapter diagnostic/error work plus a medium-risk caller
interface change; broad scientific certification remains a separate large task.
An exact line/day estimate is not supported by this diagnostic-only run. The
scientific risk is moderate because changing `domain` semantics affects A2's
direction proof, growth resets, stop type and retained evidence even when every
refusal and physical ledger is preserved. A superficially tiny faultKind edit
is therefore not adequate implementation scope.

Required acceptance gates for that future work:

1. Pre-edit review of typed outcomes, input-vs-trajectory scope, proof issuer,
   complete error/wrapping path and stop semantics. Prove no new success path.
2. Exact seven cases in native/historical-browser controls and the actual new
   Chromium/WebKit candidate; preserve original raw values and strict refusal.
   Use existing artifacts for controls; qualify any new candidate by provenance.
3. Original B1/B4A/B4B/B4C focused numerical/phase/cache/FD gates, both boundary
   signs, direct DU and PH origins, stale/untrusted certificates, real out-of-
   support inputs, lower/temperature protections, and every retained exception.
4. Tests showing unsupported input remains refused even if raw P rounds inward;
   no numerical error or boundary uncertainty becomes an A proof. A true
   independently resolved exit still produces the original protective stop.
5. Focused accepted A2 failure/probe/direction, exact rollback, stop freezing,
   initialization, boundary-edit and record-path tests under original numerical
   settings. Physical ledgers/clock/events cannot change on failure. This would
   be a separately authorized validation step, not a B5B execution.
6. Preserve separate Gate B, Gate A browser and loader blockers. Full accepted
   A2 qualification and broader native/WASM/physical Safari testing remain later
   gates after essential property qualification, with no production integration.

No implementation of this recommendation is authorized or started here.
