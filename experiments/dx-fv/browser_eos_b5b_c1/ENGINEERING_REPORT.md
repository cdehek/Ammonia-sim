# B5B-C1 — fail-closed boundary classification and A2 propagation

**FOCUSED CONTRACT IMPLEMENTATION PASS**

**Gate 1: PASS. Gate 2: PASS.** This is an isolated classification and failure
propagation result. It does not qualify exact-boundary acceptance, the backend,
complete A2 trajectories, or physical iPad performance.

The new branch is
`research/browser-eos-b5b-c1-failclosed-propagation-20261016`, starting from exact
`26df10c1f486b60978646e9c8819fc0054cb9465`. The final delivery commit is the
commit containing this report; use `git rev-parse HEAD` or the delivery response.
The pre-implementation Gate 1 decision was separately committed as `95f7881`,
before any functional source existed on this branch.

## Preservation and scientific review

The starting checkout was clean and exactly B5B. All **1,877** historical tracked
files have a starting SHA256 manifest. All **143** archived native/browser
artifact identities and **12** accepted A2 dependency copies were independently
reverified. All starting remote refs, including main, PR #3, UI, demo release
and every protected research checkpoint, are recorded. Final preservation checks
cover both local protected refs and remote refs. Only this additive research
directory changes; no production, accepted source, UI, Live Plant or hosting
file is modified. No merge, deployment, EOS build or source repair occurs.

[GATE1_DESIGN.md](GATE1_DESIGN.md) is the pre-edit ownership and contract review.
It traces raw CoolProp result/exception → unchanged browser loader → historical
stateMVU/convert/sat → thermodynamics → fluidCall → Newton/probes → rejection
and halving → floor evidence → rollback → record/stop. It documents A physical
exit, B numerical recovery failure, C unresolved boundary, D supported success
and E unsupported explicit input, including information gaps and permitted use.

The current property interface cannot prove a physical trajectory exit or
recover missing PH provenance from arbitrary M/U/V. The old minimum-step
refrigerant rule accepted a domain-labeled recovery error as proof. That inference
is invalid for these property failures. C1 preserves the independent thermal
proof byte-for-byte, and removes the use of unproved property refusal as exit
evidence in the experimental path. No new refrigerant proof issuer, pressure
certificate or high-level refrigeration protection is introduced. No proof
from the accepted table backend is borrowed to certify the CoolProp adapter.

## Exact experimental intervention

`adapter.mjs` wraps the **unchanged historical adapter**. Its property calls and
every guard still execute the original code. It captures call-local input bits,
raw primary results, observed exception/source and strict support outcome when
the complete operation throws. Raw rejected coordinates are diagnostics only.
On successful calls, it returns the historical result without changing a field.

The runtime distinguishes direct requested PH/sat input refusal (E, compatible
`domain`) from unproved recovered-coordinate support refusal (C, compatible
`solver`) and observed numerical exceptions (B, compatible `solver`). Every
property refusal explicitly says `physicalTrajectoryExit:unproved`. E is input
scope; it cannot itself establish a trajectory stop. No new top-level faultKind
is introduced. No microscopic pressure threshold or fixture filter exists.

All twelve A2 dependencies were copied and checked against Git objects at
`be9eb35a4ddf5098e685182f8104685127c6a6ee` before editing. Nine remain identical.
Only three experimental copies differ, plus one diagnostic helper:

- `thermodynamics.cjs`: explicit-input metadata, numerical default for unknown
  property exceptions, preservation and recovery scoping of failure diagnostics.
- `coupled-implicit.cjs`: retained property cause and diagnostics through failed
  derivative/line-search handling; actual nonlinearResidual remains untouched.
- `coupled-model.cjs`: trace/observer/stop transport, exclusion of unproved
  property failures from refrigerant exit proof and Newton growth learning,
  safe evidence-gathering failure retention, and honest record/outlet diagnostics.
- `failure-contract.cjs`: structured diagnostic helpers; no state/proof factory.

[a2-error-propagation.patch](a2-error-propagation.patch) is the complete applicable
A2 patch, including the new helper. The wrapper is its complete, separate source.
No FD, line-search, Newton, temporal, phase-event, thermal, conservation or
commit arithmetic changes. Unknown legacy property-domain errors are conservatively
numerical inside this experimental thermodynamics path; protected original
factories remain untouched. The legacy generic refrigerant branch is not a new
physical proof API. This candidate makes no promise to diagnose a genuine
refrigerant crossing when independently sufficient evidence is unavailable.

## Original seven and false-acceptance controls

Chromium **154.0.8037.57** and desktop WPE WebKit **26.5** each reproduce their
own seven original saved inventories, without regeneration or substitution.
Control is the exact preserved B4C candidate JS/WASM with the historical
adapter. Candidate uses that same WASM and loader, with only reviewed wrappers
and isolated error-propagation copies. WASM SHA256 is
`8c690c741d33d26f758a825ed5e4043af50cfc52a1e8587d8a5fb93732c026c5`.

All seven original PH calls retain their historical results. All raw DU output
bits remain unchanged. All seven complete MVU calls remain refused; no candidate
state is returned and no physical-domain proof is asserted. Runtime reason is
`boundary-unresolved`. Independent immutable B5B mathematical evidence supplies
the **two numerical wrong-side** / **five rounded-inventory conflict** explanation
in the report matrix, never in a runtime lookup or pressure band.

Maximum seven-case canonical differences remain **7.655471563339233e-7 Pa**,
**1.5133991837501526e-9 J/kg**, **5.684341886080801e-13 K**. Numerical accuracy
does not override strict support. Exact inputs, raw pressure bits, Pa/bar support
sides, residuals and independent sign references are in
`evidence/classification-matrix.json` and the replay files.

Both browsers replay the 21 saved B5 pressure diagnostics plus the separately
labeled three inherited B5B +100 Pa controls. Exactly 35 bar and the neighboring
Pa ULP requests, liquid/vapor/interior mixture, meaningful interior and exterior
states retain historical behavior. All independently unsupported explicit PH
requests refuse, including the outward-ULP mixture whose separately constructed
MVU inventory later returns inward. No requested PH pressure is inferred from MVU.
Supplemental tests preserve exact .3/35-bar guards, outward bar ULP refusal,
temperature floor/subcool/superheat refusal and actual loader nonfinite refusal.

The two exact saved inward controls, `webkit-ledger-69` and `webkit-ledger-76`,
**still return** in control and candidate, with their original bits. Their
independently resolved mathematical inventory pressures exceed the hard limit
by about **2.94076e-7 Pa** and **2.50420e-10 Pa**, while raw recovery returns
inside. Runtime numerical information has no verified pressure enclosure and
cannot decide these mathematical signs. C1 does **not** prevent or resolve these
inherited hazards. A general independently justified numerical certification
method is required; they remain explicit exact-boundary qualification blockers.
A supported-looking returned pressure is not proof about the exact inventory.

## A2 propagation, genuine protection and rollback

The shared integration harness completes **24 scenarios** with actual archived
native properties, Chromium and desktop WebKit. It runs the actual accepted
Newton, hydraulics, thermal transport and TR-BDF2 code, with the documented
classification changes. The ordinary supported nonzero-exchange candidate/control
case has identical accepted cells, thermal state, ledgers, events and settings.

Numerical, unresolved, explicit-input, legacy domain-text, untyped-domain and
line-search-wrapped faults exercise transient and persistent refusal. Every
rejected trial is compared with the original accepted JSON snapshot. Persistent
failure also preserves cell/thermal/ledger object identity and nextStepSeconds.
Each persistent .001-second run uses **20 rejected attempts and 19 halvings**
to **1.9073486328125e-9 s**, then the unchanged 1e-9 floor prevents another
halving. The trial count is 20; the adjacent attempted sizes have exactly dt/2
relation. No failed property state supplies the next trial.

No property failure invents a nonlinearResidual. A deliberately failed real
Newton line-search test retains its genuine residual of 1 and its property cause;
the candidate does not use that refusal to teach growth history. Successful
probe alternatives retain original signed-probe/line-search behavior.

The matched synthetic A2 replay of a **real preserved property error** reproduces
the old erroneous `domain` stop and candidate `solver` stop, with identical
rejection counts and exact rollback. These are explicitly fault-injection
experiments using actual property errors, not claims that an observed plant
trajectory reached those seven inventories.

Independent actual thermal cases at **200 K** and **400 K** retain the original
rechecked exact-boundary outward-direction `domain` stop. A false thermal claim
at an interior state fails recheck and stops numerically. Independently verified
thermal exit remains a domain stop even when a property failure coexists.
Initialization and unsupported edits refuse without installation. Stops freeze
future advancement/edits. Failure preparing the second detached half-commit
installs neither half. If accepted-state property re-evaluation is unavailable,
the solver retains the honest stop, and record **throws with diagnostics** instead
of returning invented sections or raw rejected properties.

Rollback covers cell mass/U/V, all tube/fin/finite-air energies, accepted clock,
initial identities, specification, ledger, physical and boundary events,
schedule index, accepted-step count and unchanged rejected-advance nextStep.
The accepted dependency closure contains no separate controller state; none is
invented. Attempt counters, rejection diagnostics, retained stop and original
failure-aware proposal-history resets are permitted bookkeeping, as in the
original rollback semantics. No rollback tolerance is introduced.

## Numerical regression, lifecycle and performance

All **250** saved B5 native records reproduce their original raw results or
exceptions exactly using archived B4C. Fifteen native wrapper controls preserve
their outcomes, including three actual full-VLE QT exceptions classified B with
no returned raw state. Gate A's seven archived native controls are replayed;
that correction remains native-only and its four endpoint cases unqualified.

Focused B1/B4A/B4B/B4C browser regressions include four original controls and
their signed FD probes, adapter PH/MVU identity, raw canonical recovery and
the supported B4B PT/cache sequence. Each browser passes **13 applicable original
signed same-branch FD mass/energy checks at 1e-11**, plus the original canonical,
independent-coordinate/getter and phase requirements. Cross-phase homogeneous
derivative assertions remain excluded under the original rules. Actual native
and browser A2 records pass original aggregate/section conservation and
independent signed thermal-ledger checks. `scientific-audit.json` records every
applied comparison; it reports zero failures.

All original budgets and support bounds remain intact: canonical <=.1 Pa /
<=.1 J/kg / <=1e-4 K; standalone <10 Pa / <50 J/kg / <.01 K; fluid residual
scale 1e-11; conservation <1e-8 kg / <1e-6 kJ; thermal closure 1e-12 K;
independent resolution 1e-5 Pa / 1e-8 J/kg; original Newton 30, signed FD,
halving/attempt budgets, phase events, finite air and thermal 200–400 K.

Async catches and explicit worker serialization retain the exact diagnostic
envelope. Forty alternating refused/supported updates and fresh/reused objects
show no stale error or rejected-state contamination. Worker results match main
thread input/raw/error bits and supported states. Main-thread timers continue
while the worker loads/runs. WASM memory remains **56,360,960 bytes** across
the measured lifecycle. Heap snapshots are observational, without a leak proof;
WebKit does not expose the Chromium heap API.

Five interleaved 40-ms rounds per group give median candidate/control call-time
ratios about **1.02 / 1.73** (successful/rejected) in Chromium and **1.22 / 3.48**
in WebKit. Failure metadata has measurable cost. Short error-transport timings,
matched A2 supported/retry timings, worker latency and memory observations are
preserved. A2 single-pair times have substantial warm-up/order noise; no speedup
claim or robust throughput qualification follows. Desktop WebKit is not a
physical Safari/iPad result. No full long-duration campaign is run.

## Limits, execution incidents and review stop

The inherited rejected-PT reference-count assertion is neither fixed nor
reinterpreted. Only its established supported PT/cache control is executed;
rejected PT cases remain outside C1. Browser native-exception type details already
discarded by the loader cannot be reconstructed; C1 preserves actual available
message/source/raw data and explicitly leaves unmeasured checks unmeasured.

Gate B endpoints, Gate A browser qualification, mathematical inward-recovery
certification, rejected-PT cleanup, full backend/A2 and physical iPad validation
remain open. Source and artifact hashes preserve all earlier repairs and
limitations. No new numerical enclosure, exact-boundary success or physical
plant excursion at nanopa is claimed.

Execution incidents are retained in `EXECUTION_NOTES.md`: sandbox network/child
process access, WebKit dependency setup, native bridge timeouts and a detached
commit harness injection initially landing in an earlier accuracy-rejected
trial. The latter was corrected using the original static sealed fixture so
the injected failure occurs in the intended second commit preparation. Both
failed browser attempts and earlier passing evidence are retained; no scientific
budget or backend implementation was changed to obtain the pass.

Recommended next milestone: engineering review of this isolated patch and the
operator-facing failure meanings. Exact-inventory boundary certification needs
its own authorized numerical research gate before any full boundary qualification.
No next milestone, production integration or deployment is started. Stop for
engineering review and explicit approval.
