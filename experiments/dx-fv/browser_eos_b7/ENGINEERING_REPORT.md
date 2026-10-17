# Research B7 — B5A Gate A browser/WASM qualification

**FOCUSED BROWSER GATE A PASS**

**Gate 1 PASS — BUILD AND ABI VERIFIED. Gate 2 PASS — FOCUSED BROWSER GATE A PASS.**
The accepted native correction recovers original inventories 146, 151 and 152
as stable homogeneous liquid in actual Chromium **151.0.7922.34** and desktop
WPE WebKit **26.5**. The compiled repaired path is observed directly; default
superancillary success is not used as evidence of Gate A activation. Four original
endpoints remain unqualified. This is a limited experimental result through an
isolated full-VLE harness, not complete EOS/backend, Gate B, accepted A2 or
production qualification.

## Checkpoint and preservation

Branch: `research/browser-eos-b7-gatea-wasm-qualification-20261017`.
The initially empty workspace was cloned at exact B6
`f6227de0760d81994c60497869f5c6013a9d403f`. HEAD and the clean tree were checked
before creating B7. The delivery commit is the commit containing this report;
README gives its full-SHA retrieval command and the delivery response supplies it.

All **2,147** starting tracked-file SHA256 values are preserved. The audit
independently verifies **143** archived native/browser identities, **102** sealed
B6 files, five scientific patch digests and all **12** accepted A2 snapshots
against Git objects at `be9eb35a4ddf5098e685182f8104685127c6a6ee`. Root `engine.js`
is byte-identical to accepted A2. All **33** initial remote identities, including
HEAD, protected branches and PR #3 refs, are retained. Separate PR #3 metadata
records base `0473d32f62db992fde0f581d116e1bd0c8e7d8ed`, head
`d4422425750a1d3c4e432cc103ac42ead40b7cc6` and merge identity
`f440560fccfa45421ec2bf679bac32df10df63ae`. Final preservation checks compare all
protected refs and historical bytes. Only B7 additions are authorized for commit
and push; production, accepted code, prior research, UI, Live Plant, release and
hosting are untouched. No PR, merge or deployment is created.

## Exact scientific source and matched builds

Pinned upstream: CoolProp 8.0.0 commit
`ae81610e7d23efc57f9d051c8e70a4d66e87537f`, tree
`ca49b8c34df0dae93dcc7fe07e2815a10d967662`.
The four original B1/B4A/B4B/B4C patches reconstruct **all 1,782** accepted B4C
tracked source hashes. An independently copied external tree receives the
preserved Gate A patch once. All A1 source hashes match the accepted native
manifest. Exactly `VLERoutines.h`, `VLERoutines.cpp` and `FlashRoutines.cpp` differ
from B4C; the other **1,779** files remain identical.

Original Gate A patch SHA256, checked from actual repository bytes:
`2f4b9e675b98a59f3846ede09b767698090083934e080bc11790b723c9d90eeb`.
All four inherited patches remain reverse-applicable unchanged. Generic Newton
and Brent, EOS constants, fluid JSON, QT validation, pressure support, conservative
arithmetic and non-DU behavior retain their source identities. There is no Gate B
algorithm. The independently verified three A1 files are transferred into the
common external build tree, and the complete A1 manifest is verified again.

Toolchain: emsdk `389a68bc35dcff7ebae4614e1615099dafda00d1`, Emscripten **4.0.12**
at `6f625bd62ee64f4f8cd11476774741b961e4a2d5`, pinned LLVM/linker, CMake **4.4.4**,
Ninja **1.13.2**, Python **3.12.14**. All nine dependency contents and Git pins
match their accepted digests. Original Release O3/NDEBUG/C++17, Embind/JS
exceptions, ES6/module and memory-growth settings are retained, with no fast-math.
Caches, compile/link recipes, tool binary digests, generated-header hashes and
logs are delivered. The common build tree reuses unchanged objects. At most two
compiler jobs run; full builds are bounded to 900 s and diagnostic increments to
300 s. All EOS builds finish within their bounds. A dependency-download
configuration timeout and its bounded successful continuation are retained.

Matched native comparisons execute the independently hash-verified original
B5A native B4C control and A1 archives on this host; no new native compile is
claimed. Fresh/reused C API replay covers every fixed record and both paths, with
all handles freed. Native binary identities are in `native-artifact-identities.json`.

| Scientific WASM | SHA256 | Bytes |
|---|---|---:|
| Rebuilt B4C control | `cbd0df37784aa4c8fb90e094904823e869da8075eca54f8767ad1a44599fd771` | 9,196,646 |
| Exact Gate A candidate | `2af8363686c402d6dcd9775355e829a5f3257de56372f290c66ed9285db8db45` | 9,196,872 |

All four generated JS files, including diagnostics, hash to
`ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217`.
Diagnostic WASM hashes and logging-only patches are separately identified in
`artifacts-with-diagnostics.json`. No diagnostic binary is substituted for a
scientific artifact. Diagnostic source adds logging in two translation units,
without extra EOS evaluation or generic solver instrumentation; complete exact
uninstrumented source restoration is verified afterward.

## Fresh exception-ABI review and real path activation

EXCEPTION_ABI.md records the new review. Both scientific and both diagnostic
modules have independently parsed import/export names, signatures and memory
limits matching the historical artifact. Generated exception and environment
source slices are equal, and actual SDK runtime source hashes match B6's preserved
source. This finding follows inspection of these artifacts, not the version label.

Each artifact runs 16 low-level native PT escapes in each engine. Live CppException
headers start at referenceCount/caught/rethrown **0/0/0**. The required stack
restore is **2,928 bytes**. Generated begin-catch acquires the reference and fixes
uncaught bookkeeping; end-catch sees count **1**, destroys/releases storage and
returns catch depth and uncaught count to **0**. High-level internal catches are
separate. The exact B6 WeakSet identity/consume-once cleanup remains compatible;
no new lifecycle algorithm is introduced. Synthetic JS errors and forged pointers
are not adopted. Historical controlA selection and explicit hash-verified B7
qualification identities are tested independently.

The original bindings expose no configuration setter. B7 appends the existing
`COOLPROP_ENABLE_SUPERANCILLARIES=false` process-environment setting through the
module's existing WASI environment imports. It changes neither EOS source nor
exports, equations, inputs, guards or budgets. It is an explicit isolated harness
mechanism, not qualification of a previously unmodified general full-VLE browser
entry point. The default interface remains superancillary.

Actual logging shows config=0, `other=iUmolar`, `HSU_D_flash`, legacy dispatch,
`saturation_D_pure`, and candidate `polish_du=1`; control has polish=0. Default
instances show config=1 and no saturation-D entry. All seven cases in both paths
and engines have exact logging-on/off/standard-output parity, fresh and reused.
Candidate final evaluated T/rhoL/rhoV equal both cached substates and the caloric
decision's coordinates. The unchanged scientific artifacts reproduce those
results. Gate 1 passes only after these independent checks.

## Seven original failures and focused physical results

FAILURE_MATRIX.md retains all original rho/u binary64 bits. The control reproduces
all seven original full-VLE QT refusals. The candidate recovers exactly the three
independently resolved original liquids. No PH rerun constructs a replacement
inventory. The full 250-record conservative constructions are independently
checked against their actual preserved B4B/B4C/native/browser originating records,
including separate historical independent-reference inventories.

For 146, 151 and 152, original-PH canonical maxima across both browsers are:

| Quantity | Observed maximum | Original limit |
|---|---:|---:|
| Pressure | 6.2771141529e-7 Pa | <=0.1 Pa |
| Enthalpy | 1.0477378964e-9 J/kg | <=0.1 J/kg |
| Temperature | 3.4106051316e-13 K | <=1e-4 K |
| Fresh-EOS normalized mass/energy residual | 6.5145330321e-16 | <=1e-11 |

Native A1 and both browsers agree exactly in sampled p/h/T values. Acceptance
uses the original scientific tolerances, not a new cross-compiler bit-identity
rule. Fresh independent unmodified EOS states confirm energy/mass closure,
getters and positive liquid stability derivatives. Independent saturation roots
repeat at 65 and 90 digits using the unchanged separate EOS evaluator. Final
pressure/gibbs residuals meet 1e-5 Pa / 1e-8 J/kg, the liquid caloric separations
have resolved positive signs, and cached caloric errors stay below 1e-8 J/kg.
Q=10000 is the original homogeneous DU sentinel, not a mixture fraction; actual
coexistence returns require 0<=Q<=1.

148 remains an invalid-Q QT refusal; 162 returns numerical liquid but its physical
phase remains unresolved; 164 and 165 remain invalid-Q refusals. The native A1
dispositions reproduce in both engines. No new endpoint is certified from a raw
return or small residual. No Q clamp, forced vapor fallback, changed density,
energy substitution, pressure movement or loosened reference rule is used.

## Wider ledger, regressions, lifecycle and compatibility

All **250 original records / 73 unique pairs** run on both paths, both artifacts,
both engines, fresh/reused, preserving individual identities. The original-path
raw error count changes **29→9**; replaying all 250 on full VLE gives **63→10**;
default path gives **0→0**. These are raw error counts, not physical qualification
counts. Default control/candidate results are exact, including the original 167
default-path records. Every returned record passes original applicable numerical,
quality and fresh-EOS checks and agrees with matched native behavior. All
exceptions remain separately recorded. The separate **21** saved independent
inventories run without regeneration: full-VLE raw errors **10→3**, default zero;
independent-root comparisons and fresh EOS closure pass without upgrading any
unresolved phase status. Actual native fresh/reused replay agrees too.

The unchanged original focused auditor passes all **86** base fixtures and **344**
signed probes: B1 precision, B4A near-saturation liquid, B4B PT/cache consistency,
B4C upper-quality vapor, true coexistence/endpoints and supported pressure cases.
Default/full-VLE PH bases/probes are exact control versus candidate; original
full-VLE signed budgets are also independently reapplied. PH/PS/PU and DH/DS/DP
saved shared-caller matrices preserve control/candidate and fresh/reused behavior,
including existing errors. Homogeneous derivatives are never required across
a real phase transition or an originally excluded endpoint.

An additional actual native shared-caller replay covers **624** records. Numeric
native/browser comparisons pass the original p/h/T limits. Eleven original
default-path endpoint controls have different native/browser phase labels
(44 comparisons across two artifacts/two engines). Every corresponding browser
value is exactly its archived B4C browser value; control/candidate are unchanged.
Those endpoint labels remain unqualified, rather than being forced into a phase
identity requirement or counted as new physical successes. There is no such
difference at the three resolved Gate A liquids. `shared-native-audit.json`
retains every difference and exact original input identity.

The final quality census also finds **44 invalid raw DP endpoint returns / 11
path-input identities**, identical between control/candidate. All eight full-VLE
DP endpoint inputs reproduce the preserved native invalid qualities; three
default DP endpoint inputs have browser rounding outside [0,1] where native gives
an endpoint value. The strict scientific audit **refuses every one**. These are
supplemental raw DP diagnostics, never accepted model states, and DP physical
qualification is **FAIL / NOT QUALIFIED**. No originally qualified DU or focused
B1/B4A/B4B/B4C state regresses. `quality-disposition.json` retains the failed
admissibility checks without clipping Q or treating small violations as valid.
This focused Gate A pass does not qualify the shared DP interface or erase these
additional backend blockers.

For each artifact/engine, B6's **47** original sequences retain **315 supported
operations** exactly and the **six** primary rejected PT positions honestly.
The additional **32** fresh/reused sequence variants preserve stack, disposal,
supported recovery and error meaning. JS-origin injections receive no native
cleanup. Actual workers repeat all 47 original sequences, all six rejected
positions, 64 rejected/supported alternations and the original seven full-VLE
inventories; main/worker values and error meanings agree exactly.

Unchanged C1 code retains all **seven original default browser refusals** and
their diagnostics in each engine. Additional full-VLE diagnostics produce the
same adapter split in control/candidate: **four refusals / three inherited
unqualified returns**. Changing internal raw recovery is not an exact-inventory
support certificate. Both inward hazards remain unqualified. The unchanged bar
guard refuses actual outward bar ULP inputs. No support epsilon or inward pressure
rounding is added. `support-attribution.json` keeps raw recovery, adapter outcome,
rounded-DU mathematics and exact M/U/V local-root attribution separate. It retains
C2's two-inside/five-outside rounded split versus one-inside/six-outside exact
split, without claiming a global physical branch proof or trajectory exit.

After essential properties and main/worker lifecycle checks pass, the existing
unchanged B6/C1 A2 subset runs **10 scenarios per engine**: supported nonzero
exchange, transient and persistent real-property fault experiments, exact
rollback and independently established thermal exits at 200/400 K. Persistent
failure preserves accepted values/object identity through **20 attempts / 19
halvings** to 1.9073486328125e-9 s and the original 1e-9 floor. Original aggregate,
section, thermal, temporal and nonlinear assertions pass. PT fault dispatch is
explicitly harness-injected; it is not a claim of an observed plant trajectory
or genuine DU thermodynamic failure. No Gate B endpoint substitution or full A2
campaign occurs.

All budgets remain: canonical <=0.1 Pa / <=0.1 J/kg / <=1e-4 K; normalized
mass/energy <=1e-11; standalone strictly <10 Pa / <50 J/kg / <0.01 K; independent
reference resolution 1e-5 Pa / 1e-8 J/kg. Accepted five-section mass <1e-8 kg,
energy <1e-6 kJ, thermal closure 1e-12 K, Newton/TR-BDF2/FD settings, exact
rollback and protective domain-stop rules are retained in unchanged sources.

## Performance, remaining blockers and review stop

PERFORMANCE_AND_MEMORY.md retains five interleaved matched rounds per workload,
raw return/refusal counts, initialization, memory and worker latency. No ratio
is assigned to control failure versus candidate success. Linear memory grows
22,544,384→56,360,960 bytes at factory creation and remains at the latter observed
size. This is not a leak proof. Maximum campaign main-thread heartbeat gaps are
**1,505.2 ms Chromium / 1,775 ms WebKit**; worker campaigns record **76.8 / 94 ms**.
These are material responsiveness observations, separate from numerical
correctness. Physical Safari/iPadOS and production responsiveness are untested.

Remaining qualification blockers are four Gate B phases, original 35-bar
refusals, both inward false-acceptance hazards, inherited full-VLE boundary
returns, the P1 equilibrium/topology/convex-envelope obligation, full EOS/backend
and full A2 qualification, broader fluids/regions, physical devices and long-term
performance/lifecycle coverage. A raw supported-looking pressure resolves none.
The invalid raw DP diagnostics and shared endpoint phase-label differences remain
explicit additional limits on broader caller qualification.

Recommended next scientific milestone: independent engineering review of B7,
then a separately authorized bounded review of the four unchanged Gate B phase
decisions and their reference-resolution requirements. Exact-inventory support
certification still requires the independent P1 branch/topology obligation.
No new algorithm, further source repair, C3, full A2 qualification or integration
is started. Stop for engineering review after the isolated commit/push audit.
