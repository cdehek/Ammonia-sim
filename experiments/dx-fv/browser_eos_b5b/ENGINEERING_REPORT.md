# B5B — 35-bar boundary classification and recovery contract design

**CONTRACT DESIGN SUPPORTED**

The evidence supports a specific narrow design: preserve strict refusal,
separate requested-input support, raw numerical recovery, accepted adapter
operation and physical trajectory proof, and propagate numerical/unresolved
failure without asserting a physical exit. Only a supported, fully qualified
property result may be used successfully. Implementation and validation remain
pending, including a separate scientific review of the property-to-A2 failure
interface. Exact-boundary successful recovery is not established by this design.

No functional source, adapter, loader, backend or accepted solver changes occur.
There is no pressure tolerance, support expansion, alternative compiled backend,
Gate B implementation, complete A2 campaign, merge, deployment or production/UI/
Live Plant/Cloudflare action. Stop for engineering review and explicit approval.

## Checkpoint and preservation

Starting branch: `research/browser-eos-b5a-gate-b-feasibility-20261016`.
Exact starting HEAD: `14b8b386148c687fcb549d5f17003fa9e63fbca8`, clean before
creating `research/browser-eos-b5b-boundary-contract-design-20261016`.
The delivery SHA is the commit containing this report, given in the delivery
response and `git rev-parse HEAD`. No self-referential commit value is embedded.

All **1838 starting tracked files** have a pre-experiment SHA256 manifest.
All additions are under `experiments/dx-fv/browser_eos_b5b/`. The start audit
independently verifies **143 historical artifact identities**, including native
archive/decompression hashes and JS/WASM hashes, all five inherited patch
digests, all protected commit objects and **12 accepted A2 dependency copies**
against Git objects at `be9eb35a4ddf5098e685182f8104685127c6a6ee`. Root
`engine.js` also matches accepted A2. Final audit compares every historical file
and every starting remote ref; the only allowed new remote head is B5B.

B1 44-bit PH, B4A liquid phase, B4B PT/cache, B4C upper-quality and B5A Gate A
patches remain intact. Historical source manifests, fluid/reference evidence,
fixtures, reports and property artifacts are byte-preserved. This milestone
does not reconstruct all external CoolProp source trees or dependency builds;
their inherited verification receipts remain evidence with their original scope.
Only the pinned ammonia JSON is downloaded, checked against its historical
SHA256, and evaluated by the unchanged B5 high-precision diagnostic. No CoolProp
build occurs. Accepted A2, B1/B2/B3/B4A/B4B/B4C/B5/B5A/Gate B and UI checkpoints,
main, PR #3, release and all other starting refs are protected.

The required B5 engineering/failure/proposal reports, Gate A report, Gate B
feasibility/formulation/endpoint uncertainty, B4C report/loader/adapter and
browser evidence, accepted A2 contract, dependency closure, domain tests and
rollback source were read before interpretation. Audit/reproduction procedures
and execution setup notes are in [README.md](README.md).

## Exact original browser reproduction

Chromium **154.0.8037.57** and desktop WPE WebKit **26.5** reproduce each of
their own seven original failures, preserving original fixture names, ledger
keys and all inventory/output bits. There are fourteen identities and seven
unique inventories. Inputs are decoded from B5's immutable bit patterns,
**never regenerated**. The authoritative historical control is the preserved
B4C candidate JS/WASM and original research adapter. Candidate WASM SHA256:
`8c690c741d33d26f758a825ed5e4043af50cfc52a1e8587d8a5fb93732c026c5`.

Each originating adapter PH call passes. Each raw DU returns. Each table PH
guard passes. Each strict `sat(s.p/1e5)` comparison throws
`Error: Outside accepted pressure domain`, `faultKind:'domain'`, **before any
SAT EOS call**. A successful raw inverse is therefore followed by a failed
complete adapter operation. No failure is counted as an accepted recovery.

The exact ledger contains requested PH input, actual PH getters, M,V,U, rho/u,
all bits, actual raw p/T/rho/h/u/s/Q, independent returned-coordinate EOS checks,
original canonical differences, Pa/bar conversion and complete error trace.
See [MATRIX.md](MATRIX.md), `fixed-inputs.json`, `fixed-inventory.csv`, both
browser replays and `seven-case-analysis.json` under `evidence/`.

For the original seven, maximum canonical differences remain
**7.655471563339233e-7 Pa**, **1.5133991837501526e-9 J/kg** and
**5.684341886080801e-13 K**. Independently evaluated maximum normalized mass and
energy residuals are **7.77697e-17** and **5.61967e-16**, within 1e-11. These
measure numerical accuracy, not strict support acceptance.

## Mathematical attribution, conservative arithmetic and evidence levels

Fresh independent **65/90-digit** roots of the same unchanged EOS reproduce
all seven B5 mathematical pressure signs. The .001-liquid and hg+0.99e-9-band
inventories lie below Pmax by approximately **2.5810e-9** and **8.2429e-10 Pa**,
while binary64 returns above. The other five exact inventories lie above by
approximately **7.04e-10–7.72e-7 Pa**. Their raw recoveries are accurate but a
perfect inverse of those exact inventories still conflicts with the strict
maximum. A new pressure guess cannot resolve that conflict.

All seven browser inventories have independently resolved stable homogeneous
liquid/vapor branches; their extrapolated coexistence roots are excluded.
This is distinct from Gate B's four endpoint inventories. The accepted sequence
is reproduced exactly, including each binary64 rounding:

```
V = 0.003 / 5
M = rho * V
U_kJ = M * (h / 1000) - 100 * (P / 1e5) * V
rho_DU = M / V
u_DU = (U_kJ / M) * 1000
```

Each operation's exact rational rounding error and result bits are recorded.
Requested PH pressure, actual PH getter pressure, independent mathematical EOS
at returned PH rho/T, PH caloric consistency, mass reconstruction, U construction,
exact inventory root, binary64 DU error and final support comparison remain
separate. B5's detailed differential attribution is reused and labeled. Its
homogeneous sensitivity decomposition is not applied across equilibrium changes.
No polished value is fed back into an accepted or experimental functional model.

One pressure ULP is **4.6566128730773926e-10 Pa**. Pa→bar preserves the support
side for all seven. The neighboring Pa values convert to
34.99999999999999/35.00000000000001 bar and round-trip another Pa ULP outward.
Unit conversion contributes rounding but does not originate the original seven
rejections. Pmax itself converts exactly.

Evidence levels must not be confused: converged high-precision mathematical EOS
signs resolve arithmetic; actual binary64 properties determine observed adapter
behavior; independent scientific/reference resolution does not establish physical
certainty at nanopa. Original independent resolution remains **1e-5 Pa / 1e-8
J/kg**. Precision repetition is convergence evidence, not a rigorous interval
certificate or experimental ammonia validation at those digits. No real plant
pressure excursion is inferred from these microscopic signs.

## False rejection, false acceptance and lost provenance

Both engines reproduce all **21 saved B5 PH boundary diagnostics** exactly,
then evaluate three separately labeled +100 Pa liquid/mixture/vapor diagnostics.
All generated raw recoveries meet original canonical/nonlinear budgets. Farther-
inside cases return; all +100 Pa cases refuse and independently have fixed-
inventory pressure approximately +100 Pa outside. Support is tested independently
of numerical accuracy. Lower-pressure and temperature guard predicates are also
preserved and exercised in clearly labeled isolation tests.

At exactly 35 bar and one inward Pa ULP, liquid/vapor recovery refusals demonstrate
the intended supported-PH false-rejection problem; mathematical inventory signs
separate inverse error from representation. One outward Pa ULP is unsupported
as an explicit PH request in every phase, yet its mixture MVU operation returns
after rounding inward. An inward DU result cannot authorize that original input.

Two additional **saved** controls (`webkit-ledger-69`, `webkit-ledger-76`) show
the exact-inventory false-acceptance hazard independently: mathematical fixed P
is outside by approximately **2.94076e-7** and **2.50420e-10 Pa**, but actual
browser raw P is inside by **3.49246e-7** and **3.25963e-9 Pa**, and the actual
adapter returns. Both engines reproduce the saved bits; fresh 65/90-digit roots
repeat the outside signs. These are mathematical support hazards, not physical
excursion proofs. The known +100 Pa unsupported states are all refused.

The liquid and mixture exact/inward/outward PH triplets each construct identical
M/V/U bits despite distinct original requested-pressure support classes. That
non-injective mapping proves existing MVU arguments cannot recover lost original
PH provenance. MVU also lacks rates, trial lineage and physical intent. Pressure
guess is unused. The [interface analysis](INTERFACES_AND_A2.md) identifies each
loss and rejects fixture-name/previous-P inference.

## Contract, alternatives and diagnostic prototype

[CONTRACT_PROPOSAL.md](CONTRACT_PROPOSAL.md) specifies A confirmed physical-domain
exit, B numerical recovery failure, C boundary uncertainty/representational
conflict, D supported success, and E independently unsupported input. For each,
it defines evidence, permitted inference, operator meaning, current information
gaps, scientific status, fault compatibility and rollback effects. All unknowns
fail closed; only D can supply successful property use. A/E input-vs-trajectory
scope is explicit. All seven originals remain C, with the two/five mechanisms
retained; they are not misreported as canonical residual failures.

[OPTIONS.md](OPTIONS.md) compares strict rejection with better classification,
verified origin provenance, numerical certification and explicit unresolved
propagation, including source owners, integrity, uncertainty components, false
positives/negatives, portability, cost and feasibility. No arbitrary epsilon is
selected. A certificate must bind exact bits/EOS/reference/caller context and
cannot turn supported PH origin into current inventory support.

The justified standalone prototype reads preserved evidence and emits **no
thermodynamic states**. It reports **15 C, 6 E, 12 D and 3 B** research rows:
seven originals, two inward-error controls, 24 PH diagnostics and three inherited
Gate B QT exceptions. There is no observed A physical trajectory proof in this
milestone. Six separately labeled hypothetical contract samples include stale/
wrong-EOS evidence, unverified proof, residual failure and inward recovery from
an unsupported request. Hypothetical A is not an experimental result.

The prototype conservatively withholds independent D classification from two
historically accepted boundary-mixture rows; it preserves their observed success
and does not declare them historical failures. This proposed uncertainty screen
is not an implemented accepted requirement or a numerical bound. Native endpoint
exceptions remain errors; no Gate B state is qualified. The prototype never
overrides the adapter, changes live faultKind, edits an inventory or feeds a
reference state into a solver. It is not a deployable runtime classifier.

## Accepted A2 implications and recommendation

The existing interface can transmit coarse solver/domain refusal, but its current
semantics cannot preserve the full distinctions. Unlabeled PH errors default to
domain in `thermodynamics.ph`; unlabeled MVU errors reach a solver fallback.
At the minimum-step direction proof, A2 treats any refrigerant recovery domain
error as confirmation of exit. A microscopic numerical/representational error
can therefore be mistaken for physical proof. Its independently rechecked exact
thermal outward-direction protection remains valid and must be preserved.

Trial rejection, original halving, detached two-half-step commit preparation,
exact rollback, retained stops and unchanged wet/superheat derivation are traced
in [INTERFACES_AND_A2.md](INTERFACES_AND_A2.md). No coupled numerical experiment
or full domain/rollback campaign is run. Persistent unresolved inventory may
halt numerically and cannot promise long-duration progression. Initialization,
boundary edits, accepted-state evidence and recording paths also require future
tests; relabeling one error does not complete propagation. No new wet-suction
or high-level protection behavior is invented.

Recommend a separately reviewed, isolated **classification-only correction with
strict refusal**, options 1+4. It solves unjustified physical-exit reporting;
it does not solve exact-boundary successful recovery. The adapter should retain
raw/input diagnostics and mark unproved recovery support failures numerical/
unresolved. Caller changes to domain proof or fault meaning require a separate
scientific contract review before implementation. Preserve genuine physical
protection, explicit unsupported-input rejection and exact rollback. The detailed
acceptance gates and scope/risk estimate are in OPTIONS.md. No next milestone
is authorized or started by this delivery.

## Unchanged budgets and separate blockers

Canonical <=0.1 Pa / <=0.1 J/kg / <=1e-4 K; normalized fluid mass/energy <=1e-11;
standalone strictly <10 Pa / <50 J/kg / <0.01 K; original independent resolution;
all signed finite differences, phase branches, section/aggregate conservation
(<1e-8 kg, <1e-6 kJ), thermal closure <=1e-12 K, Newton 30, line search and
TR-BDF2/adaptive budgets remain unchanged. No new aggregate conservation or
trajectory result is claimed. Support remains 0.3–35 bar, bounded table
availability, 195.495 K floor, 30 K subcooling / 250 K superheat and accepted
thermal 200–400 K. Source hashes preserve the original requirements exactly.

- **Gate B:** four endpoint inventories remain scientifically unresolved under
  original independent-reference/branch certification, despite mathematical
  branch signs. No B5B result repairs or qualifies them.
- **Gate A browser:** native focused repair passed; no qualified Gate A WASM/
  browser candidate exists. B4C controls cannot qualify that native-only repair.
- **Rejected-PT loader:** original exception cleanup/reference-count assertions
  and six rejected sequence cases per browser remain in historical evidence.
  They are not rerun or repaired here; no PT rejection campaign is needed.
- **Full backend:** complete accepted A2 qualification, broader shared-source
  implications, worker/memory/offline qualification and physical Safari/iPadOS
  validation remain pending. Desktop WebKit is not physical Safari evidence.

The preservation audit and post-push delivery check establish an additive,
isolated research result. It supports truthful failure semantics, not backend
qualification or accepted exact-boundary recovery.
