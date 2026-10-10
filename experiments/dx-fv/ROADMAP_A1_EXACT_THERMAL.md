# Roadmap A1 — isolated exact thermal Jacobian experiment

Repository: `cdehek/Ammonia-sim`, branch `experimental/dx-fv-stage-3`.
Starting restore: `31f641dfb81722dfb3b7cfdb8be14856fe70052e` (accepted A0).
A0 hosted regression [38086886365](https://github.com/cdehek/Ammonia-sim/actions/runs/38086886365)
completed successfully. Earlier scientific restores, references and reports stay unchanged.

The user approved replacement of the eleven thermal-energy finite-difference
columns in a separately selected experiment. This does not approve PH inversion
changes, failure-aware growth, thermal elimination, Stage 2B, integration or
default promotion. Only `coupled-model.cjs` and `coupled-implicit.cjs` are modified
existing files. New A1 qualification/audit/report files stay in `experiments/dx-fv/`.

## Selection and unchanged baseline

```js
const baseline = createCoupledModel(engine); // Original finite differences.
const experimental = createCoupledModel(engine, {thermalJacobian: 'exact'});
```

`thermalJacobian: 'finite-difference'` explicitly selects the original path.
Omitting the option adds no field to the original settings object. Other values
are rejected. The experiment remains confined to the five-section, 21-coordinate
coupled Stage 2A factory; historical refrigerant and standalone thermal factories
remain unchanged.

For exact mode only, each implicit stage assembles eleven columns once from its
normalized thermal graph, fixed capacities, original physical residual scales and
endpoint quadrature weight. Newton copies these columns into its usual dense
Jacobian. The ten PH columns retain their original evaluated perturbations,
phase-branch checks, shrinking rules and property cache. Dense linear solves,
damped updates, residual evaluations, recovery, acceptance, fine-step commit and
rollback are the original operations.

No thermodynamic call is made by column assembly. The residual equations and
signed link integrals are unchanged. Exact-column diagnostic events contain
detached copies of assembled columns, rather than fabricated probe residuals.
Consumer mutation of those copies must preserve exact-mode results and work.

## Derivation and independent verification

At fixed PH, thermal rates are affine in thermal energy: `F(E)=A E+b(PH)`.
For a link from node `f` to node `t`,
`q=G*(E_f/C_f-E_t/C_t+constant)`. Subtract this rate at `f`, add it at `t`.
The tube/refrigerant exchange also subtracts `G_tr/C_tube` from the tube's
diagonal rate derivative.

For interval `d`, endpoint weight `w`, and original row scale `s_r`, the thermal
block is `(I-d*w*A)/s_r`. Each refrigerant mass row is zero. Refrigerant energy
row `i` has tube-column derivative `-d*w*G_tr_i/(C_tube_i*s_r)`; its fin/air and
other-tube entries are zero. Combined physical energy derivatives sum to one
for a unit thermal-energy increment: all internal exchange derivatives cancel.

Backward Euler uses `w=1`. TR-BDF2 uses `gamma=2-sqrt(2)`, first-stage interval
`gamma*d` and weight `1/2`, then interval `d` and weight
`(1-gamma)/(2-gamma)`. Known prior-stage terms are fixed within the current Newton
solve. Thermal row scales remain `C_i*(1e-12 K)/(1e-11)`.

The independent standard-library Python audit derives physical capacities and
conductances directly from the declared geometry. It applies a unit kJ
perturbation to signed link incidence rather than importing the JavaScript matrix
builder. Captures cover cold, warm, heat reversal, zero exchange and closed
relaxation, both methods, and 0.001/0.5 s trial intervals. Coarse uncommitted
trials may exhaust Newton; those failures are evidence, not accepted integration.
The same starts also capture original finite-difference probe residuals for a
separate comparison with the independently assembled columns.

Preserved budgets include global/per-section mass `<1e-8 kg`, all original
energy budgets `<1e-6 kJ`, scaled fluid residual `<=1e-11`, thermal closure
`<=1e-12 K`, nominal/tight temporal temperatures `<0.01/0.001 K`, temporal
pressure `<5e-5 bar`, direct-EOS pressure `<1e-4 bar`, enthalpy `<0.05 kJ/kg`,
direct-EOS temperature `<0.01 K` and event error `<0.001 s`. The original tests
retain their stricter auxiliary recovery, reference and refinement checks.

## Reproduction

Use Node 22 and the qualified Python reference dependencies from the Stage 2A
handoff. The A0 ancestor must exist locally for the in-memory `git show` baseline.
No checkout/reset is performed. All generated evidence paths must be outside the
repository; the harness guards report and failure-output paths.

```bash
mkdir -p /tmp/ammonia-a1-evidence
node experiments/dx-fv/roadmap-a1.cjs columns /tmp/ammonia-a1-evidence/columns.json
python experiments/dx-fv/audit_roadmap_a1.py /tmp/ammonia-a1-evidence /tmp/ammonia-a1-evidence/assembly-audit.json --assembly-only
node experiments/dx-fv/roadmap-a1.cjs baseline /tmp/ammonia-a1-evidence/baseline.json
node experiments/dx-fv/roadmap-a1.cjs compare /tmp/ammonia-a1-evidence/compare.json
node experiments/dx-fv/roadmap-a1.cjs failures /tmp/ammonia-a1-evidence/exact-failures.json
node experiments/dx-fv/roadmap-a1.cjs suite /tmp/ammonia-a1-evidence/exact-frozen.json exact coupled-test
python experiments/dx-fv/generate_coupled_reference.py /tmp/ammonia-a1-evidence/fresh-reference.json
DX_COUPLED_REFERENCE_PATH=/tmp/ammonia-a1-evidence/fresh-reference.json node experiments/dx-fv/roadmap-a1.cjs suite /tmp/ammonia-a1-evidence/exact-fresh.json exact coupled-test
python experiments/dx-fv/audit_coupled_results.py /tmp/ammonia-a1-evidence/exact-frozen.json /tmp/ammonia-a1-evidence/exact-frozen-audit.json
python experiments/dx-fv/audit_coupled_results.py /tmp/ammonia-a1-evidence/exact-fresh.json /tmp/ammonia-a1-evidence/exact-fresh-audit.json
node experiments/dx-fv/roadmap-a1.cjs suite /tmp/ammonia-a1-evidence/exact-controls.json exact coupled-controls
node experiments/dx-fv/roadmap-a1.cjs domain /tmp/ammonia-a1-evidence/exact-domain.json
node experiments/dx-fv/coupled-domain-test.cjs /tmp/ammonia-a1-evidence/baseline-domain.json
node experiments/dx-fv/roadmap-a1.cjs suite /tmp/ammonia-a1-evidence/exact-browser.json exact coupled-browser
node experiments/dx-fv/coupled-browser.cjs /tmp/ammonia-a1-evidence/baseline-browser.json
node experiments/dx-fv/coupled-test.cjs /tmp/ammonia-a1-evidence/baseline-frozen.json
python experiments/dx-fv/audit_roadmap_a1.py /tmp/ammonia-a1-evidence /tmp/ammonia-a1-evidence/qualification-audit.json --qualification-only
```

The suite adapter compiles the existing test source in memory with an exact-mode
factory. Its existing scientific assertions, fixtures and references are
unchanged. Browser selection is inserted once into the existing blank-page
numerical runner in memory; it does not change any application source. The
historical domain suite requires bitwise equality with the pre-classification
candidate, so it runs unchanged for baseline. Separate A1 boundary tests retain
the classification, conservation and rollback contract without requiring exact
trajectories to match historical floating-point decisions.

Only after other numerical/browser workloads finish, run the timing pairs:

```bash
node experiments/dx-fv/roadmap-a1.cjs performance /tmp/ammonia-a1-evidence/performance.json 5
python experiments/dx-fv/audit_roadmap_a1.py /tmp/ammonia-a1-evidence /tmp/ammonia-a1-evidence/a1-audit.json
```

Performance uses identical original intervals/output schedules and nominal
settings for all five cases, one complete untimed baseline/exact warm-up pair,
then five measured pairs in alternating baseline/exact order. Both paths run in
one Node process on the same hardware, with no optional diagnostics or trace
serialization in timed work. Timed intervals include model creation, advancement,
sample recording and common conservation checks; engine creation, result hashing,
JSON writing, independent audits and column diagnostics are outside those
intervals. The actual public engine-call counters run identically in both paths;
these wrappers introduce common measurement overhead. Nested engine-private
calls are not claimed as separately counted property calls. Residual evaluations,
PH/saturation/canonical-recovery calls and linear solves remain distinct measures.

Variability is reported from raw paired samples, not isolated best-case timing.
Same-process warm-up and interleaving reduce order effects but do not remove
shared-host variation. These are controlled research workload measurements, not
production, UI or device performance claims.


## Numerical results

All fifteen same-table comparisons passed the original budgets. The experimental frozen/fresh suites each passed all five cases, ten additional checks and seven intentional stop/rollback scenarios. Fresh EOS generation used zero fallbacks and reproduced the frozen file byte-for-byte; experimental numerical reports match after removing only timing fields.

| Nominal case | Accepted trials FD → exact | Rejected trials | Newton iterations / linear solves | Residual evaluations |
| --- | ---: | ---: | ---: | ---: |
| cold | 321 → 321 | 5 → 5 | 4,635 → 4,635 | 103,926 → 52,941 |
| warm | 444 → 446 | 33 → 33 | 7,847 → 7,869 | 175,498 → 89,434 |
| load-step | 212 → 212 | 5 → 5 | 3,271 → 3,271 | 73,264 → 37,283 |
| feed-step | 280 → 280 | 13 → 13 | 4,288 → 4,288 | 96,094 → 48,926 |
| heat-reversal | 962 → 985 | 922 → 947 | 42,073 → 43,441 | 1,231,654 → 792,507 |

| Nominal case | Actual public PH calls FD → exact | Saturation calls | Canonical recovery calls |
| --- | ---: | ---: | ---: |
| cold | 302,372 → 200,402 | 330,037 → 228,067 | 14,725 → 14,725 |
| warm | 505,029 → 333,380 | 544,969 → 373,490 | 21,520 → 21,610 |
| load-step | 212,211 → 140,249 | 230,621 → 158,659 | 9,830 → 9,830 |
| feed-step | 278,918 → 184,582 | 303,638 → 209,302 | 13,260 → 13,260 |
| heat-reversal | 3,125,421 → 2,282,597 | 3,213,861 → 2,373,767 | 49,940 → 51,750 |

These counts include the initial sample record. Relative to A0’s nominal diagnostic workload, that adds eight PH calls, thirteen public saturation calls and five canonical recovery calls; integration work and the accepted default trajectory are unchanged. Baseline and exact measurement workloads have the same recording calls. Internal private engine calls are not included in these public counters.

| Reversal regime | Accepted trials FD → exact | Rejections | Newton failures | Iterations / linear solves | Residual evaluations |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1e-06 | 962 → 985 | 922 → 947 | 921 → 946 | 42,073 → 43,441 | 1,231,654 → 792,507 |
| 1e-07 | 963 → 973 | 907 → 918 | 906 → 917 | 41,816 → 41,883 | 1,220,579 → 764,432 |
| 1e-08 | 976 → 1,014 | 727 → 796 | 725 → 794 | 36,139 → 38,805 | 1,039,819 → 693,593 |

Nominal reversal therefore saves 35.6551% of residual evaluations and 26.9667% of public PH calls, while using 3.2515% more Newton iterations/linear solves and 25 more failed Newton trials. The experiment does **not** reduce the original 922 rejections. Tight and reference rejections also increase. Work reductions must not be presented as a Newton-convergence remedy or as equivalent percentage runtime improvements.

The observed exact-mode nominal reversal has 6,365 converged solves. Maximum converged fluid norm is `9.86403e-12`; thermal closure is `9.99958e-13 K`. All 946 failed solves reach iteration 30 in superheated vapor and are tube-row dominated. Their fluid norms are already below budget (maximum `2.65995e-12`); thermal closures range from `1.00022e-12` to `7.02497e-12 K`. Diagnostic recording gives exactly the same states, histories and work as unobserved exact mode. No recovery or timestep remedy is applied.

The independent matrix audit checks 20 trials, 29 captured stage matrices and all 6,699 entries; maximum absolute matrix discrepancy is `4.44089e-16` scaled-residual/kJ. Analytically zero entries are exactly zero. Matched original evaluated finite differences have maximum relative nonzero error `7.32152e-7`, thermal error `1.44385e-9 K/K` and refrigerant-energy error `1.63115e-9 kJ/K`. These are selected-stage checks, not a claim to audit every runtime matrix independently. Constant capacities/links make each stage’s thermal columns independent of its current Newton iterate.

| Largest sampled FD/exact difference over all 15 comparisons | Value |
| --- | ---: |
| Pressure, bar | 4.28091518e-08 |
| Enthalpy, kJ/kg | 3.41940136e-05 |
| Refrigerant temperature, K | 2.82079947e-06 |
| Thermal-node temperature, K | 4.96897962e-06 |
| Phase-event clock, s | 8.05454574e-06 |
| Tube/refrigerant integrated exchange, kJ | 8.0852417e-07 |

Equal trial counts do not imply equal traces. The audit reports actual accepted/rejected interval-sequence equality and the first divergence separately from full trace equality, which also includes normalized-error values. There are no missing/spurious phase events or scheduled boundary changes. All sample times and supported integration intervals remain the original ones.

| Full experimental suite conservation maximum | Value | Budget |
| --- | ---: | ---: |
| Global mass, kg | 1.94441204e-10 | <1e-08 |
| Section mass, kg | 9.40851841e-11 | <1e-08 |
| Refrigerant energy, kJ | 6.05440391e-08 | <1e-06 |
| Thermal energy, kJ | 8.43556336e-11 | <1e-06 |
| Combined energy, kJ | 6.05793673e-08 | <1e-06 |
| Section energy, kJ | 3.37785835e-08 | <1e-06 |
| Thermal-node energy, kJ | 3.33242411e-09 | <1e-06 |

Each independent frozen/fresh accounting audit checks 150 sample records; worst combined-energy residual is `5.43907e-9 kJ`.

| Direct-EOS comparison maximum across all cases | Value | Original budget |
| --- | ---: | ---: |
| Pressure, bar | 3.9276117e-05 | <0.0001 |
| Enthalpy, kJ/kg | 0.00627632506 | <0.05 |
| Refrigerant temperature, K | 0.00109376797 | <0.01 |
| Thermal temperature, K | 6.89376209e-05 | <0.01 |
| Terminal event, s | 4.14273181e-05 | <0.001 |

Node 22 fixed-step TR-BDF2/backward-Euler order checks, zero-exchange relaxation and refrigerant limits, uniform equilibrium, reporting-reference invariance, temporal cap refinement, independent domain-clock refinement, mixed-patch atomicity and stop freezing all retain their original assertions. Separate A1 domain evidence covers 36 initial-boundary, prior-history, injected-probe and signed-exchange cases. Both Chromium and WebKit exact/default numerical suites pass conservation, EOS and phase/schedule-event checks.


## Environment, audit coverage and storage

Qualified local environment: Node 22.23.3, Python 3.12.14, CoolProp 7.2.0,
NumPy 2.5.3, SciPy 1.16.2, Playwright 1.62.1, Chromium 151.0.7922.34 and
WebKit 26.5. Linux x86_64 kernel 6.18.44, Intel Xeon Platinum 8573C; cgroup CPU
quota is `200000 100000` (two CPU equivalents). The performance evidence records
hardware and quota alongside raw measurements. These timings are not compared
with A0's differently instrumented or concurrently run qualification elapsed times.

Both browser engines executed real scientific assertions. Missing libraries and
browser binaries live under `/tmp/ammonia-a0-runtime/`; local
`PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` bypasses only system-cache
preflight. It does not bypass browser execution, reference, conservation or event
checks. The same setup qualified the accepted A0 observer extension.

The full A1 independent qualification audit checks 300 baseline/exact sample
records, all 15 fixture/regime work totals, counter-wrapper equivalence against
unwrapped original qualification suites, exact-path diagnostic equivalence and
actual accepted/rejected interval sequences. Each frozen/fresh independent
accounting audit checks a further 150 experimental records. The matrix audit
covers every row/column in its selected stages; it does not import a JavaScript
engine or solver. The performance audit requires at least five measured pairs,
identical counts and hashes across repeats, and identical nominal work/call counts
between timing and qualification workloads.

Original default full qualification, historical DX/time/thermal suites and all
13 application numerical suites passed. Generated standalone `index.html` is
byte-identical to the protected application file, and protected validation JSON
blobs match the accepted Git versions. Temporary legacy-test output was removed.
Output-location guards, Node syntax checks and Git whitespace checks pass.

Normal exact-mode assembly retains 231 column numbers per stage, with a temporary
121-number rate matrix. Their float64-equivalent numerical payloads are 1,848
and 968 bytes, excluding JavaScript arrays/objects, graph maps and the existing
dense Newton matrix. Optional diagnostics copy another 231 column numbers per
Newton iteration; discarded attempt data and selected JSON evidence have separate
recording/storage costs. No A1 peak-RSS or memory improvement is claimed. Timed
runs have no optional diagnostic vectors, reference/audit or archive work.

The existing workflow is unchanged and does not select the new exact option or
run the new A1 harness automatically. The historical A0 hosted success linked
above is not claimed as hosted exact-path qualification. A1 experimental
qualification is the explicit local Node/Python/browser evidence described here.
Generated evidence stays outside Git. The delivered commit SHA is reported
separately; no commit can embed its own SHA.


## Controlled Node 22 timing results

One complete warm-up pair and five measured pairs completed in a single Node 22 process after all qualification workers exited. The audit verifies every repeated work total, public call total and state/record hash, and matches timing work/calls against nominal qualification. Both paths use the original output schedules.

| Workload | FD median s | FD range s / sample SD s | Exact median s | Exact range s / sample SD s | Median paired exact/FD | Paired ratio range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cold | 2.524 | 2.376–3.305 / 0.377 | 1.671 | 1.467–2.518 / 0.412 | 0.603765 | 0.575869–0.997437 |
| warm | 5.120 | 4.346–5.381 / 0.459 | 2.906 | 2.712–3.224 / 0.224 | 0.588088 | 0.543266–0.697000 |
| load-step | 1.933 | 1.689–2.793 / 0.506 | 1.156 | 0.969–1.592 / 0.248 | 0.573694 | 0.398775–0.730542 |
| feed-step | 2.769 | 2.191–3.518 / 0.603 | 1.885 | 1.286–2.095 / 0.371 | 0.595696 | 0.437599–0.941661 |
| heat-reversal | 43.787 | 33.670–48.333 / 6.082 | 32.749 | 28.055–39.557 / 4.872 | 0.818426 | 0.692483–0.853873 |
| total | 57.722 | 44.304–62.582 / 7.512 | 40.660 | 35.387–48.194 / 5.297 | 0.754428 | 0.675933–0.798746 |

Use the median **within-pair ratio** to summarize relative runtime. Per-path medians can come from different pairs; their quotient is not the reported paired reduction. The nominal reversal median paired runtime reduction is **18.16%**, with individual pairs **14.61–30.75%** lower. The combined five-fixture total has a median paired reduction of **24.56%**, with pairs **20.13–32.41%** lower. Each reversal and total measured pair is faster in exact mode. Cold has one nearly equal pair (0.26% lower), and the wide timing ranges preclude a universal speedup guarantee.

This is a demonstrated runtime reduction for this defined workload/environment, separately from the 35.66% reversal residual-evaluation reduction. The 3.25% iteration/linear-solve increase and additional nonlinear failures remain real costs. No timing comparison uses earlier parallel qualification runs or A0 observer/serialization timings.

Raw seconds below are in measured pair order (AB, BA, AB, BA, AB). Warm-up samples are excluded.

| Workload | FD seconds, five pairs | Exact seconds, five pairs |
| --- | --- | --- |
| cold | 2.375650, 2.886408, 2.524004, 3.305477, 2.520173 | 1.671400, 1.662193, 2.517534, 1.995730, 1.466882 |
| warm | 4.346354, 4.625333, 5.120294, 5.381044, 5.349733 | 2.711833, 3.223855, 2.799782, 3.164525, 2.906327 |
| load-step | 1.688673, 1.707257, 1.932881, 2.793172, 2.547104 | 0.968781, 1.247223, 1.156160, 1.592408, 1.015722 |
| feed-step | 2.223102, 2.191116, 3.283905, 2.769124, 3.517554 | 1.285529, 2.063289, 1.437034, 1.884671, 2.095392 |
| heat-reversal | 33.669886, 39.133272, 47.292386, 48.333153, 43.787181 | 28.749813, 28.055334, 32.749190, 39.557129, 36.062590 |
| total | 44.303664, 50.543386, 60.153470, 62.581969, 57.721746 | 35.387356, 36.251895, 40.659701, 48.194464, 43.546914 |

Actual interval-sequence comparison: all 15 accepted sequences differ; 13 of 15 rejected sequences differ. This does not merely compare normalized-error fields. The independent audit retains the first divergent interval tuple for each regime; unchanged controller code responds to different floating-point solver outputs. All original accuracy, event and conservation criteria still pass.

## Conclusions and review boundary

A1 qualifies as an isolated computational-efficiency experiment. Removing thermal probes produces reproducible reductions in residual/property evaluations and lower measured Node 22 runtimes, without changing physical equations, support or acceptance requirements. The default solver is numerically identical to A0 across all seven complete baseline comparisons.

Exact thermal columns do **not** resolve sealed heat-reversal Newton convergence. Rejections increase in all three tested reversal regimes, and nominal failures still stall in superheated tube rows at the original 30-iteration limit. Approximate thermal columns are therefore not a necessary mechanism for the observed Newton failures in this experiment. PH inversion quantization, PH finite-difference behavior, residual arithmetic and the original regrowth policy remain active; A1 does not establish their individual causal shares or propose a combined fix.

Retain the original finite-difference default pending user review. Exact mode is a qualified optional research path with a measured efficiency benefit and increased failed-trial counts, not a robustness improvement. No PH precision change, failure-aware timestep policy, thermal elimination, tolerance relaxation, Stage 2B, workflow change, application integration or merge is included. Any default promotion or further numerical experiment requires separate approval. A1 stops at this delivery.

## Evidence digests

Generated evidence is temporary and outside the repository. The final full audit passed; all applicable local scientific/application/browser regressions passed.

* `columns.json` SHA256: `8086438937c7d93b6806a6b531f80870552a33e9b1b7d7a7727c54f60382d26f`.
* `baseline.json` SHA256: `0cea5a3b62c17b40efa97017a876c4c2a81a25f334640cabf48a868776931f9c`.
* `compare.json` SHA256: `d9bd959ef8d7751709c998d30be08975b597e1971f06eb92a82946f71c58d34f`.
* `exact-frozen.json` SHA256: `46d8e489d0d68e2b871392e291f3d6799c614a4f863c80fa7e8415a2b330239a`.
* `exact-fresh.json` SHA256: `986e9c501d659d4ed1a8d3dd01949465b6a2edfff05607ee3de6a1e5359a48ed`.
* `exact-failures.json` SHA256: `cdea1890bed4d55b2c78404c1b2b1fe977badc19ac67d87d08beb10a12a3ab33`.
* `performance.json` SHA256: `f9df9f9c17e1abb95aed57ab7ff79b0ba8b87ae30488018bd6c1b282a8d9c54a`.
* `a1-audit.json` SHA256: `bdc5c835e0569073447bdc13a0f23820079ec5b6ae4725ab2ea1deb634b801a8`.
* Unchanged property grid SHA256: `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`.

Absolute timings and timing/audit digests can vary on regeneration. Repeated physics/work equivalence and original scientific budgets must still pass within each qualified runtime.
