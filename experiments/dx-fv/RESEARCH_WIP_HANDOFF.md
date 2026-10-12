# Ammonia Lab — unqualified research preservation and fresh-conversation handoff

**Read this first. This branch is a preservation snapshot, not a qualified Stage
2B milestone or an adopted property method.** Current authorization ends with
this handoff. The next conversation should obtain mathematical review and the
user's decision before new fitting, simulations, numerical changes or integration.

Repository: `cdehek/Ammonia-sim`.
Dedicated branch: **`wip/dx-fv-stage2b-property-research-20261012`**.
Accepted experimental branch: `experimental/dx-fv-stage-3`, still
**`be9eb35a4ddf5098e685182f8104685127c6a6ee`** (accepted A2).
The preservation commit SHA is supplied in delivery and the review-package
manifest; a commit cannot contain its own SHA. Never infer qualification from
the existence of this WIP commit.

This document supersedes current-status/authorization statements in the older
reports. Their text, including statements that work was uncommitted, interrupted
or awaiting an earlier decision, remains unchanged historical provenance.
`RESEARCH_WIP_EVIDENCE.json` captures the original dirty status, exact 32 research
paths and their hashes, compact numerical evidence and remote-ref snapshots.

## Verification and immutable restores

Before preservation, local HEAD and remote accepted branch were A2; the working
tree had **3 modified files and 29 untracked research files**, all under
`experiments/dx-fv/`. All **211 pre-existing tracked/untracked files** were hashed
and remain byte-identical. No applicable AGENTS.md was found. Accepted A2 hosted
CI was reread through GitHub: completed/success, four successful jobs
(prototype, spatial-resolution, nine-section-resolution, browser-performance):
https://github.com/cdehek/Ammonia-sim/actions/runs/38109562003 .

| Qualified restore | Exact SHA | Status |
| --- | --- | --- |
| Coupled Stage 2A implementation | `adbab1d5587471105a351f3467e0bb812effb148` | Accepted isolated five-section physics/numerics, documented limits |
| Stage 2A documentation handoff | `9a231b1ed5da1dce07f3d613aeb79336ce8541c7` | Historical handoff |
| A0 diagnostics | `31f641dfb81722dfb3b7cfdb8be14856fe70052e` | Accepted diagnostic research, no solver substitution |
| A1 exact thermal columns | `c2de1f0808048f6be6f3e912cd0fcffa9a646cf0` | Accepted optional efficiency experiment |
| A2 failure-aware growth | `be9eb35a4ddf5098e685182f8104685127c6a6ee` | Accepted optional performance milestone with limitations |

Ancestry through these restores was verified. Earlier refrigerant/spatial/thermal
restores remain in `RESTORE_POINTS.md`; no existing refs are reset or rewritten.
Protected refs observed immediately before preservation:

* Main: `0473d32f62db992fde0f581d116e1bd0c8e7d8ed`.
* PR #3 head, `v0.5.5-stage-1`: `d4422425750a1d3c4e432cc103ac42ead40b7cc6`.
* PR #3 merge ref: `f440560fccfa45421ec2bf679bac32df10df63ae`; PR open/unmerged.
* Accepted experimental branch: the A2 SHA above.

Only the new WIP ref is pushed. The original DX scientific workflow matches
pushes to `experimental/dx-fv-stage-3`; the application workflow matches main or
PR activity. A WIP push does not trigger either push filter. No workflow dispatch,
workflow edit or hosted WIP qualification is implied or authorized here.

## What is qualified, and what is not

Historical prescribed-heat refrigerant, standalone tube/fin/air and five-section
coupled milestones remain qualified within their tested domains and intervals.
A1 exact thermal columns and A2 failure-aware growth are independently selectable
research options. **Defaults remain five sections, finite differences, original
timestep growth and original property interpolation.** The accepted branch is
unchanged; this WIP branch is not a replacement default.

The nine-section candidate supports only 5/9 sections. Nine has 9 canonical
M/U/fixed-V volumes, 9 tube energies, 9 fin energies and 1 finite-air energy:
18 PH plus 19 thermal coordinates, **37 equations**. Same physical equipment:
0.003 m³ refrigerant, 0.60 kW/K total tube/fluid conductance, unchanged total
geometry, capacities, other conductances and hydraulic closure. Signed shared-face
mass/bulk-donor enthalpy and same-stage paired heat integrals are retained.
Nonuniform initialization integrates physical inventory/energy over overlap
intervals; it does not interpolate cell-center PH to claim conservation.

Reported completed Stage 2B original-fixture evidence includes 120 integrations,
80 frozen/fresh independent EOS comparisons, five-default A2 equivalence, geometry,
conservation, temporal, control/domain/rollback tests and research browser execution.
These are **passing subsets**, not complete Stage 2B acceptance. Extended events
failed; full nine observer equivalence, final extra-case spatial projection,
full fresh-five replay, controlled timing/memory and final complete qualification
were held. An application WebKit capacity-release click timed out under concurrent
load; its unchanged serial replay and remaining browser queues were held.

Saturation-only PCHIP, all static reconstruction candidates, extended liquid
EOS-pressure accuracy and the full Stage 2B milestone remain **unqualified**.
No new method has been integrated into the accepted coupled solver.

## Attempted investigations and scientific outcomes

| Investigation | Established finding | Failed/incomplete requirement |
| --- | --- | --- |
| Nine-section Stage 2B | Same equipment and conservative initialization; original-fixture suites pass | Extended dew clocks fail strict 1 ms; remaining qualification held |
| Phase-event diagnosis | Same bulk terminal dew event in JS/EOS; sharp crossing; original accepted five-source reproduces issue; accumulated saturation-T bias dominates | No correction or qualification claimed |
| Saturation-only PCHIP | Frozen-knot monotone T interpolation greatly improves saturation-T accuracy | Fixed-PH liquid T accuracy regresses; h/rho representation unchanged |
| Bounded original/PCHIP trajectories | Extended event error falls to ~0.012 ms; most state/heat metrics improve | Liquid T regression persists; ~0.033 bar liquid pressure discrepancy persists/slightly worsens |
| Joint property diagnosis | Coupled h/rho interpolation dominates canonical pressure error; inversion/units/reference/geometry are not main causes | Negative compressibility and three canonical roots in supported liquid |
| Static potential/joint-field reconstruction | Potentials enforce Maxwell; bounded projection reduces energy-value noise; monotonic fields improve sampled values | No candidate satisfies stability, consistency, uniqueness and pressure accuracy together |

The terminal dew event is **h-hg(p_bulk)=0**, wet→vapor, not imposed-port superheat.
It occurs in cell 4 over x/L=[0.8,1] for five, cell 8 over [8/9,1] for nine.
Each mesh is compared with its own EOS reference, not matching section indices.

| Mesh | Converged EOS s | Original JS s / error ms | Saturation-PCHIP JS s / error ms |
| --- | ---: | ---: | ---: |
| 5 | 146.382180249400 | 146.383507171434 / +1.326922 | 146.382192206338 / +0.011957 |
| 9 | 146.909931921277 | 146.911304327853 / +1.372407 | 146.909943791908 / +0.011871 |

Reference refinement differences are only tens of nanoseconds; crossing slopes
are ~51.64/50.54 kJ/(kg s), not grazing. Native event localization contributes
sub-microsecond errors. The independent temperature-component diagnostic ablation
reproduces ~98% of post-120-second property timing shift. It is causal evidence,
not a complete thermodynamic substitute. Spatial clock difference ~0.528 s is
separate from each mesh's ~1.3 ms numerical disagreement.

The frozen table has 241 log-pressure rows at 0.3–35 bar, liquid subcooling
0–30 K in 1 K increments and vapor superheat 0–250 K in 2 K increments. Missing
cold liquid entries stay unsupported. Saturation T is rounded to 8 decimals;
h/s/rho to 7. `engine.js` uses linear T/h/s and log-density interpolation.
Single-phase recovery inverts h or density over offsets, then canonical recovery
solves `u=h-100*p/rho`. Canonical inventories obey `U=M*h-100*p*V`.

At p=32.65314902038559 bar, h=686.779725665 kJ/kg, original liquid PH T error is
-0.603114 mK, saturation-only PCHIP -1.140942 mK. At fixed PH, h/rho/u remain
unchanged: improving T removes a beneficial error cancellation without repairing
joint h/rho. Saturated-liquid h bias contributes ~79% of offset error in this probe.

The short sealed liquid inventory already has +0.022832154 bar EOS pressure error
before integration. At 0.1 s its constitutive component is +0.032638925 bar;
total trajectory error is +0.032550071 bar, including a small evolution term.
Native-versus-exact original-surface inversion error is ≤1.086e-9 bar, far smaller.
EOS u mismatch ~0.008615 kJ/kg divided by isochoric du/dp ~0.263957 kJ/(kg bar)
predicts the constitutive shift. Correcting h or rho alone can worsen the cancellation.
Accepted five-source reproduces the probe exactly. Earlier qualified fixture
coverage had 198 wet/52 vapor samples and **zero fully subcooled liquid samples**;
it did not establish universal liquid-table accuracy or derivative stability.

At p=0.3029893712344606 bar, EOS 1 K subcooling, original stored
rho=708.6710262223568 kg/m³ and u=94.48059153610271 kJ/kg have original-surface
roots 0.302985440688, 0.302989370566 and 0.314879847305 bar. EOS recovery gives
0.301747903655 bar. Original/PCHIP isothermal compressibilities are negative
~−8.48e-5 /bar; EOS is positive +5.92315e-5 /bar. This is a representation defect
in a stable liquid region, not a physical domain boundary or a timestep-policy issue.

### Static reconstruction results Astra must scrutinize

All fitting uses unchanged frozen samples; EOS is validation only. Gibbs energy
is used because the samples are on a curvilinear PT grid. With g in kJ/kg, p bar:
`s=-g_T`, `v=g_p/100`, `h=g-T*g_T`, `u=h-p*g_p`.
Stability needs `g_pp<0`, `g_TT<0`, `g_TT*g_pp-g_Tp²>0` (positive kappa, cp, cv).
The potential uses log-pressure/subcooling coordinates and an isolated quintic
saturation coordinate spline, including its derivative terms in physical PT.
Helmholtz is discussed as an equivalent transform only on invertible stable regions;
a separate Helmholtz candidate was **not** fitted or qualified.

* Raw bicubic/biquintic Hermite potentials are rounding-naive negative controls.
  Exact first-jet matching yields Maxwell identities but huge density/curvature
  artifacts, folded density recovery and multiple roots.
* The rounding-bounded biquintic projects discrete gradient integrals onto nodal g.
  Entropy moves within ±5e-8 kJ/(kg K); h/rho knots are retained. The objective
  does not constrain Hessian stability or phase coexistence. Edge weights are
  scale choices, not rigorous integral uncertainty bounds.
* Joint-coordinate PCHIP of h/s/log(rho) is a shape-preserving field comparator,
  distinct from earlier saturation-only PCHIP. Shared coordinates do not make it
  a thermodynamically consistent potential.

All 7,234 supported liquid knots meet source-rounding intervals in direct EOS
checks. Every candidate knot deviation is recorded; the projected entropy maximum
is 5.000000014e-8, only 1.4e-16 evaluation roundoff beyond the nominal half-width.
No original sample changed. Across **30,006 PT states**:

| Representation | Max h error kJ/kg | Max rho error kg/m³ | Negative/nonpositive kappa samples | Other cv failures |
| --- | ---: | ---: | ---: | ---: |
| Original | 0.00614851 | 0.00685081 | 1,045 | No consistent potential |
| Joint-coordinate PCHIP | 0.000115043 | 0.000119254 | 0 | Maxwell still fails |
| Raw bicubic / biquintic | 0.0109413 / 0.0134333 | 22.8534 / 28.7964 | 14,555 / 14,589 | 205 / 142 |
| Rounding-bounded Gibbs | 0.0000269977 | 0.0408705 | 6,105 | 679 |

Projected Gibbs has **nine residual-validated roots** for the reported low-pressure
inventory, compared with the original surface's three. Some raw Brent brackets
converge around density-branch jumps rather than actual energy roots; rejected
brackets remain recorded and are excluded from validated counts. Roundtrip success
does not prove uniqueness. Finite sampling/scanning gives counterexamples, not
global stability or exhaustive-root certificates.

Among 77 PH tests, maximum joint-PCHIP/projected T errors are 14.5932/7.35852 µK;
maximum inventory-equivalent pressure errors are 47.165 Pa / 120.142 kPa.
At the saved high-pressure endpoint, original / joint-PCHIP / projected errors
are +3263.893 / +46.0055 / −131.818 Pa: all fail **10 Pa** there. Joint PCHIP's
Maxwell mismatch reaches 0.00236821 kJ/(kg bar); potential analytic assembly is
at roundoff, yet its stability fails. Potential conditioning and small-step
finite-difference cancellation also need review. No candidate is acceptable.

## Failures and deferred work that must remain visible

The additional adaptive-BE warm check failed identically on accepted A1 and A2
defaults (pressure 1.05642e-4 bar, enthalpy 0.155718 kJ/kg under supplemental
bounds). The user deferred that broader check; original fixed-step BE order
qualification remains required and passed. No new BE acceptance contract is
authorized. The earlier fixed Newton-failure-count phase assertion was corrected
by approved behavior-based checks; actual failures were not suppressed.

Stage 2B's extended event audit exited nonzero. Its browser concurrency timeout,
interrupted queues and held checks remain documented in `COUPLED_STAGE_2B.md`.
The saturation property regression, liquid pressure discrepancy, root ambiguity,
static stability/identity failures, unsupported cold queries, flash fallback
observations and early diagnostic harness failures remain explicit. Passing an
evidence/preservation audit means the evidence is honestly recorded; it does not
qualify a failed scientific method. No limit is relaxed to obtain a pass.

## Recommended decision and Astra review scope

Recommend **independent mathematical review of a rounding-bounded,
stability-constrained common potential formulation**, not adoption of the current
Gibbs implementation. First assess feasibility in the first low-pressure cells,
with all source fields and correlated T coordinates allowed only their demonstrated
rounding intervals, then decide whether a larger static study is justified.
Require physical-Hessian signs, canonical uniqueness, EOS pressure accuracy,
between-constraint certification and compatible saturation/coexistence conditions.
Gibbs fits the data coordinates directly; Helmholtz fits canonical recovery more
naturally but introduces an ill-conditioned irregular density grid. Neither is
assumed feasible or accurate. If frozen data are insufficient, establish that
mathematically before proposing new information or a method.

Read `ASTRA_REVIEW_BRIEF.md` for precise review questions. Astra should examine:
`STATIC_PROPERTY_RECONSTRUCTION.md`, `JOINT_PROPERTY_CONSISTENCY.md`,
`static_property_reconstruction.py`, its qualification/diagnostic/audit scripts,
protected `engine.js` / `properties.json` / `tools/generate_properties.py`,
`thermodynamics.cjs`, plus the coupled/property reports and adapters for dependency
context. The downloadable package contains read-only copies and compact evidence.
No independent Astra review has yet been performed or claimed in this handoff.

No new fitting, solver optimization, default promotion, property-table change,
full multi-hour matrix, Stage 2C, production integration or merge is authorized.
The user remains the decision gate after review. The goal is a common foundation
for evaporators, receivers, compressors and valves, not a 146-second event fix.

## Scientific contracts to preserve

Mass globally/per section <1e-8 kg; refrigerant/thermal-node/combined energy
<1e-6 kJ; scaled fluid nonlinear residual ≤1e-11; thermal closure ≤1e-12 K.
TR-BDF2, 30 Newton iterations, line search, original default timestep policy,
canonical recovery, rollback/atomicity, phase definitions and original fixtures
stay unchanged. Direct EOS: p<1e-4 bar, h<0.05 kJ/kg, fluid/thermal T<0.01 K,
well-conditioned event error<1 ms. All original temporal/refinement/domain/event
and reference-convergence budgets remain as documented; no new universal claim
follows from the original accepted fixture envelope. No 17-section mesh is supported.

## Complete preserved change list

These are the **32 original research paths**, unaltered by preservation:

```text
experiments/dx-fv/coupled-implicit.cjs
experiments/dx-fv/coupled-model.cjs
experiments/dx-fv/coupled-test.cjs
experiments/dx-fv/COUPLED_STAGE_2B.md
experiments/dx-fv/JOINT_PROPERTY_CONSISTENCY.md
experiments/dx-fv/PCHIP_TRAJECTORY_INVESTIGATION.md
experiments/dx-fv/PHASE_EVENT_INVESTIGATION.md
experiments/dx-fv/SATURATION_INTERPOLATION_EXPERIMENT.md
experiments/dx-fv/STATIC_PROPERTY_RECONSTRUCTION.md
experiments/dx-fv/audit_coupled_stage2b.py
experiments/dx-fv/audit_joint_properties.py
experiments/dx-fv/audit_pchip_trajectories.py
experiments/dx-fv/audit_phase_event_investigation.py
experiments/dx-fv/audit_saturation_experiment.py
experiments/dx-fv/audit_saturation_properties.py
experiments/dx-fv/audit_static_properties.py
experiments/dx-fv/coupled-stage2b-reference.json
experiments/dx-fv/coupled-stage2b.cjs
experiments/dx-fv/generate_coupled_stage2b_reference.py
experiments/dx-fv/joint-property-diagnostics.cjs
experiments/dx-fv/joint_property_analysis.py
experiments/dx-fv/joint_property_conditioning.py
experiments/dx-fv/pchip-trajectories.cjs
experiments/dx-fv/pchip_trajectory_reference.py
experiments/dx-fv/phase-event-investigation.cjs
experiments/dx-fv/phase_event_reference_diagnostics.py
experiments/dx-fv/phase_event_table_comparator.py
experiments/dx-fv/saturation-interpolation-test.cjs
experiments/dx-fv/saturation-temperature.cjs
experiments/dx-fv/static_property_diagnostics.py
experiments/dx-fv/static_property_qualification.py
experiments/dx-fv/static_property_reconstruction.py
```

Exactly **four** preservation-only files are added, making **36 changed paths**
relative to A2: this handoff, `ASTRA_REVIEW_BRIEF.md`,
`RESEARCH_WIP_EVIDENCE.json`, and `package_wip_review.py`, all in this directory.
Only the first three original paths modify existing tracked source/test files.
`coupled-test.cjs` retains exactly the approved nine→seventeen negative-guard edit.
Every other accepted source, report, fixture, reference, workflow and application
file is unchanged. `engine.js`, `properties.json`, tools/build and application
tests are neither changed nor regenerated.

## Evidence retention and reproducibility

Pinned environment: Node 22.23.3 (system Node 24 is not the qualified runtime),
Python 3.12.14, CoolProp 7.2.0, NumPy 2.5.3, SciPy 1.16.2. Runtime binaries live
under `/workspace/ammonia-joint-runtime/`, are not in Git or the review ZIP.
Existing complete archives remain unchanged:

* `/workspace/ammonia-joint-property-investigation.tar.gz`, SHA-256
  `ba2ecf1582f76a1a3f1bf7a49f151ee04f2de43c203addcc4b335a4bf8a046ad`.
* `/workspace/ammonia-static-property-reconstruction.tar.gz`, SHA-256
  `3dab83358ac2924ef44e07a80da15c25795c9dfcefb93cb76147c1dcffb3c62a`.

The compact ZIP is `/workspace/Ammonia-Lab-Astra-Review-20261012.zip`; a separate
full archival bundle preserves both archives and preservation proofs. They are
downloadable external artifacts, not Git blobs. Large interior/knots/work-trace
JSON and runtime binaries are intentionally excluded from the review ZIP.
Compact numerical evidence is committed in `RESEARCH_WIP_EVIDENCE.json`.

**Availability limitation:** earlier Stage 2B/phase/saturation/trajectory full
multi-hour `/tmp` queues and archives are not present in this current environment.
Their reports, all source/test/reproduction scripts, separate nine reference and
later saved diagnostic states are preserved. Their historical reported results
are not relabeled freshly audited here. Available joint/static raw evidence and
failures are fully retained. No missing artifact is fabricated or expensive matrix
rerun merely to fill the gap.

Package construction is standard-library-only, hashes every archived input and
does not execute a solver:

```bash
python experiments/dx-fv/package_wip_review.py \
  /workspace/Ammonia-Lab-Astra-Review-20261012.zip \
  /workspace/ammonia-joint-property-evidence \
  /workspace/ammonia-static-property-evidence
```

Reproduction scripts for each completed study remain in its report. Some audits
deliberately assert the original A2 HEAD, branch and pre-addition dirty-tree file
lists. **Do not remove those guards or run them on this committed WIP branch and
call a provenance failure a scientific regression.** For faithful replay:

1. In a disposable new clone, check out accepted `experimental/dx-fv-stage-3` and
   verify its HEAD is the exact A2 SHA. Fetch the delivered WIP commit separately.
2. Export only `originalResearchPaths` from `RESEARCH_WIP_EVIDENCE.json` at that
   WIP SHA and overlay them in the disposable accepted checkout. Omit the four
   handoff additions. This recreates the recorded 3-modified/29-untracked state;
   do not reset or move any live/protected refs.
3. Extract supplied evidence beside the disposable repository under the literal
   sibling name `ammonia-joint-property-evidence` required by static scripts.
   Keep its saved inputs unchanged and use a separate output directory for replays.
   The full archives provide original `preserved-files.json` manifests; the ZIP is
   a compact review subset and does not replace complete evidence for every audit.
4. Run only specifically approved focused/static checks with pinned dependencies.
   For example `static_property_qualification.py E`, then
   `static_property_diagnostics.py E`, then `audit_static_properties.py E` after
   installing the original static manifest in E. Do not overwrite retained raw
   evidence; compare regenerated results separately. Expected scientific failures
   and failed controls remain failures; the evidence audit may still pass.

In this preservation task, validation consists of complete source/hash preservation,
scoped diff/assertion inspection, Python/Node syntax checks, package hash/content
verification, commit-parent/file-list verification and protected remote-ref
comparisons. No numerical research or full qualification was rerun.

For a fresh conversation, provide the delivered WIP branch/SHA, this handoff and
the ZIP. Ask for mathematical review first. Resume only after the user decides.
