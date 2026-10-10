# Roadmap A0 — diagnostic-only nonlinear investigation

Starting handoff: `9a231b1ed5da1dce07f3d613aeb79336ce8541c7`.
Accepted Stage 2A-CI: `adbab1d5587471105a351f3467e0bb812effb148`.
Branch: `experimental/dx-fv-stage-3`, repository `cdehek/Ammonia-sim`.

The user approved three new diagnostic files and subsequently an explicit
observer-only exception in `coupled-implicit.cjs`. No other existing file may
change. This investigation ends at evidence delivery and user review. No
derivative, inversion, timestep-policy, tolerance, physical-equation, integration,
Stage 2B or production change is authorized.

## Observation and equivalence contract

The existing optional derivative event now copies each successfully evaluated
probe's residual vector and records the original coordinate, perturbed coordinate
and actual floating-point difference. Branch-rejected evaluations retain their
own residual; failed evaluations have no residual. The requested perturbation
remains distinct from the actual representable coordinate difference. No
residual or property evaluation is added by this recording, and the solver still
divides residual differences by its original requested `step`.

The harness loads immutable baseline model/solver source from the handoff using
`git show` and compiles it in memory with ordinary dependencies. It compares:

1. Original uninstrumented solver.
2. Extended solver with diagnostics disabled.
3. Extended solver with diagnostics enabled, including deliberate consumer
   mutation of detached probe residual copies after analysis.

Equality covers hashes of every state field and every sampled record, including
cells, energies, physical ledgers, events, boundary records, accepted/rejected
traces, stop state and numerical work counters. It also compares public engine
call counts. All five original cases run at nominal settings; reversal additionally
runs the existing tight/reference settings. Output schedules and integration
intervals are unchanged. The separate original coupled suite qualifies all five
cases at all existing accuracy regimes and independent step refinement.

The `--replay` phase reconstructs the original accepted state at one second using
the original output schedule, then tries detached 0.5 s and 0.025 s intervals for
cold, warm and reversal. The original, extended-unobserved and observed trial
paths must return identical results or identical errors and identical work.
Uncommitted trials must leave the accepted snapshot unchanged. These replays also
compare every recorded iteration, probe outcome and line-search decision with
the original observer after removing only the newly added fields.

## Independently derived thermal columns

Let `z` be the eleven thermal-energy increments, `C_i` the physical capacities,
`w` the endpoint weight and `d` the stage interval. At fixed PH, thermal rates are
affine, `F = A E + b(PH)`. Every thermal link contributes `-G/C_from` and
`+G/C_to` to the source row, with opposite contributions to the destination row.
Each tube/refrigerant link adds `-G_tr/C_tube` to the tube diagonal.

The unscaled thermal residual derivative is `I - d*w*A`. Divide each row by its
existing physical residual scale. Refrigerant mass rows are zero. Refrigerant
energy row `i` has tube-column derivative `-d*w*G_tr_i/C_tube_i`, divided by that
fluid-energy row's scale; all other thermal columns in that row are zero.

The comparator checks all eleven columns across all 21 rows against the actual
evaluated probe residual difference divided by the **requested** perturbation,
exactly as the original solver constructs its Jacobian. Thermal derivative error
is additionally expressed as output-temperature residual per input-temperature
increment: multiply by the row residual scale and column capacity, then divide
by the row capacity. Fluid energy derivatives are reported in kJ/K. Relative
error is defined only for analytically nonzero entries; unexpected zero entries
are reported separately.

The independent Python audit derives capacities and conductances directly from
the declared physical geometry, independently assembles signed balances, and
checks selected captured trial evaluations. It imports neither JavaScript solver
nor comparator. Its derivative-defect action uses observed accepted thermal
coordinate displacements between iterations. This is a diagnostic linear action,
not the unavailable unrounded Newton direction, nor proof of a counterfactual
solver trajectory.

The audit also infers the temperature difference used by each selected PH probe
from its captured tube-residual difference. It compares that difference with
independently algebraically inverted base/probe PH temperatures. This matched
finite-difference comparison includes inversion and residual-arithmetic roundoff;
it is not an assertion of an exact continuous derivative across table knots.

## Same-table PH inversion sensitivity

The comparator algebraically inverts each supported piecewise-linear enthalpy
segment of the unchanged property table. It preserves saturation handling and
uses no extrapolation. This calculation is never an engine/solver replacement.
Floating-point interpolation and algebraic inversion retain a roundoff floor;
this is not a higher-fidelity EOS or an exact real-arithmetic oracle.

At each observed PH iterate, let `deltaT = T_algebraic - T_runtime`. With all other
states and known quadrature terms held fixed, the endpoint sensitivity is:

* Refrigerant energy residual shift: `+d*w*G_tr*deltaT` kJ.
* Tube energy residual shift: `-d*w*G_tr*deltaT` kJ.
* Tube closure shift: `-d*w*G_tr*deltaT/C_tube` K.

The paired energy shifts cancel. The report compares the measured closure shift
with the actual signed tube residual, including whether its magnitude increases
or decreases. A row moving inside the budget in this calculation does not imply
the whole stage would converge: other rows, inventories, derivatives, prior
stage terms and canonical recovery would also respond to an actual inversion
change. No such counterfactual integration is performed. The coarser canonical
M/U/V recovery inversion remains a separate post-convergence mechanism.

## Nonlinear failures and regrowth

Every attempted interval is recorded with its accepted-state start time, proposed
duration, rejection cause and work. Counts distinguish solver failure, temporal
rejection and event rejection. A successful retry followed by growth is counted
only when an immediately preceding solver failure occurred at the same accepted
state, the retry succeeds, and the following proposal is larger. The following
proposal's solver outcome is then counted separately. Sample/end-time clipping
is retained; no hypothetical controller is substituted.

The preserved Stage 2A-R failed-Newton archive remains unchanged, including its
SHA256 `c1ca2203fcf6026d2da70d5331c1bb5ac49ffe74a29997ce2cf8bdbcfe3a30fc`.
The existing independent archive audit supplies the complete historical
iteration/line-search checks. New selected archives supply the newly authorized
evaluated vectors; older archives cannot provide those missing vectors.

## Numerical evidence — qualified Node 22 run

All seven full-trajectory comparisons passed exact equivalence, including
deliberate mutation of detached probe vectors. All six detached replays passed
original/extended/observed result, error, work and internal-decision comparisons.
Coarse warm and reversal trials at one second exhausted the original 30-iteration
budget; their 0.025 s replays converged. None of these trials was committed.

| Case / relative tolerance | Accepted / rejected trials | Residual evaluations | Newton iterations | Public PH calls |
| --- | ---: | ---: | ---: | ---: |
| cold / 1e-06 | 321 / 5 | 103,926 | 4,635 | 302,364 |
| warm / 1e-06 | 444 / 33 | 175,498 | 7,847 | 505,021 |
| load-step / 1e-06 | 212 / 5 | 73,264 | 3,271 | 212,203 |
| feed-step / 1e-06 | 280 / 13 | 96,094 | 4,288 | 278,910 |
| heat-reversal / 1e-06 | 962 / 922 | 1,231,654 | 42,073 | 3,125,413 |
| heat-reversal / 1e-07 | 963 / 907 | 1,220,579 | 41,816 | 3,099,061 |
| heat-reversal / 1e-08 | 976 / 727 | 1,039,819 | 36,139 | 2,637,932 |

### All eleven thermal-energy columns

The following maxima cover all seven observed trajectories, including both
successful and failed solves. Every column was evaluated 140,069 times, for
1,540,759 thermal probes overall. Every analytically zero entry remained exactly
zero in these measurements, including all refrigerant mass rows and fin/air
columns in refrigerant energy rows.

| Column | Maximum relative nonzero-entry error | Maximum thermal derivative error K/K | Maximum refrigerant-energy derivative error kJ/K |
| --- | ---: | ---: | ---: |
| tube-0 | 5.24675e-07 | 4.34462e-09 | 1.45421e-09 |
| fin-0 | 6.95046e-08 | 5.43439e-09 | 0 |
| tube-1 | 5.24675e-07 | 4.34542e-09 | 1.45421e-09 |
| fin-1 | 6.95046e-08 | 5.43474e-09 | 0 |
| tube-2 | 5.24675e-07 | 4.34462e-09 | 1.45424e-09 |
| fin-2 | 6.67741e-08 | 5.43439e-09 | 0 |
| tube-3 | 5.24675e-07 | 4.34542e-09 | 1.4542e-09 |
| fin-3 | 7.43545e-08 | 5.43439e-09 | 0 |
| tube-4 | 5.27252e-07 | 4.34542e-09 | 1.45436e-09 |
| fin-4 | 6.67741e-08 | 5.4566e-09 | 0 |
| air | 4.93267e-07 | 1.71616e-09 | 0 |

In nominal failed reversal solves, relative error is at most 3.03482e-7,
physical thermal derivative error 3.38520e-9 K/K, and refrigerant-energy derivative
error 5.98522e-10 kJ/K. Actual/requested thermal coordinate perturbations differ
by at most 1.09318e-11 relatively in those solves.

The independent audit examined 373 consecutive-iteration thermal displacement
pairs in selected trials. Across the 165 pairs with fluid norm <=1e-11 and
current thermal closure <1e-10 K, the largest thermal derivative-defect action
was **3.54938e-21 K**, nine orders below the required closure. Across all sampled
pairs it reached 1.57094e-10 K while still far from closure. This does not bound
unaccepted full Newton directions or a modified trajectory. It is evidence
against thermal-column error being the primary late-stagnation mechanism in
these captured trials.

### Stage-weighted PH sensitivity

| Reversal regime | Maximum same-table inverse temperature difference K | Maximum endpoint tube-closure shift K | Failed-final tube points exceeding 1e-12 K sensitivity / total |
| --- | ---: | ---: | ---: |
| 1e-06 | 4.54854e-10 | 5.14425e-12 | 3277 / 4605 |
| 1e-07 | 4.54873e-10 | 4.10317e-12 | 3253 / 4530 |
| 1e-08 | 4.54859e-10 | 2.05165e-12 | 2525 / 3625 |

Cold, load-step and feed-step are mixtures at the observed iterates and have
zero same-table inverse-temperature discrepancy in this comparison. Warm
control reaches 8.00862e-13 K endpoint closure sensitivity.

At the nominal maximum, the accepted-state trial starts at 29.1859891252 s,
proposes 0.3135025221 s, and has stage interval 0.1836455256 s with weight 0.5.
Cell 3 has p=3.4884037850 bar and h=1624.16491953 kJ/kg. Its actual signed
closure is +4.60255e-12 K; the fixed-state algebraic-inverse endpoint shift is
-5.14425e-12 K. That individual row would move inside the budget in this
sensitivity calculation, without establishing convergence of the whole stage.

At nominal failed final iterates, 2,145 of 4,605 tube points move from outside
inside the budget under this fixed-state sensitivity; 1,615 have increased
absolute residual magnitude. Both directions occur. This rules out treating
quantization as a one-way bias or simply subtracting a correction.

The independent matched PH-probe audit finds:

| Probe kind | Temperature-difference discrepancy K | Temperature finite-difference discrepancy | Stage closure discrepancy K |
| --- | ---: | ---: | ---: |
| pressure | 8.22073e-10 | 0.00234325 K/bar | 4.11313e-12 |
| enthalpy | 8.94899e-10 | 5.42811e-05 K/(kJ/kg) | 5.38641e-12 |

These maxima occur in captured reversal probes. They include the actual residual
arithmetic as well as the inversion discrepancy. The independent algebraic
inverse agrees with the JS comparator to 8.17124e-14 K on the 2,795 audited
points. Explicit Celsius-to-Kelvin addition changes the sampled stage sensitivity
by at most 3.16072e-16 K. Those roundoff differences are much smaller than the
measured inversion-associated stage effects.

### Failed proposals and regrowth

| Reversal regime | Solver failures / halved retries | Consecutive same-state failures | Successful retry followed by growth | Grown proposal fails |
| --- | ---: | ---: | ---: | ---: |
| 1e-06 | 921 / 921 | 196 | 723 | 531 |
| 1e-07 | 906 / 906 | 190 | 712 | 528 |
| 1e-08 | 725 / 725 | 69 | 654 | 492 |

For nominal reversal, 531/723 immediately grown proposals fail (73.44%).
Those 531 failures are 57.65% of all 921 solver-failed trials. This confirms
repeated proposal/retry work, not a universal monotone convergence ceiling.
Different regimes change tolerances and step caps together; this table is not
an isolated tolerance experiment. Cold/warm normal runs have zero solver
failures; their ordinary rejections remain temporal/event driven.

## Conclusions and ranked next experiments

**Confirmed:** thermal finite-difference columns have small measurable rounding
error; PH inversion-associated temperature differences and matched PH-probe
discrepancies produce stage-residual effects of the same order as, or larger
than, the strict closure budget; timestep regrowth repeatedly repeats expensive
30-iteration failures. Observation does not change numerical behavior.

**Unresolved:** these diagnostics do not establish a sole cause, prove that a
higher-precision PH inverse would remove failures, quantify a changed Newton
direction or demonstrate a speedup. Canonical M/U/V inversion is separate and
occurs after stage convergence. Fluid-column conditioning, nonlinear coupling
and line-search behavior can still matter. Selected near-closure displacement
evidence does not exclude thermal-derivative effects on other trial directions.

1. **Exact thermal-energy columns only, retaining the original path.** This is
   the smallest structurally safe solver experiment: all eleven columns across
   all 21 rows, identical residual function, PH evaluation, method, budgets and
   timestep controller. The evidence suggests modest impact on late stagnation,
   but it directly tests that hypothesis and removes known probe work. If the
   iteration trace were unchanged, nominal reversal would omit 462,803 thermal
   residual probes (37.58% of residual evaluations) and their 925,606 public
   inlet/outlet PH calls. This is a conditional work estimate, not a measured
   speedup or prediction of the altered trace.
2. **Failure-aware step growth as a separate experiment.** The repeated-failure
   cost is confirmed. A bounded local growth policy could avoid it while keeping
   the existing error/event/domain guards. It needs reset/recovery rules and
   independent validation of changed timestep sequences; its net benefit must
   include any additional accepted steps.
3. **Isolated, consistent same-table PH precision experiment.** This targets the
   stronger measured residual-scale discrepancy, but has greater implementation
   and qualification scope. Temperature, density and other returned properties
   must remain mutually consistent; replacing only T is unacceptable. Preserve
   the historical engine/table and keep canonical recovery separately assessed.
4. **Algebraic thermal elimination within joint stages.** Consider after the
   simpler comparisons. It must reconstruct all states/exchanges, check the full
   joint residual, and preserve canonical recovery, support and rollback.

Every experiment requires new explicit approval for its exact files, candidate
path, unchanged validation budgets and delivery gate. No remedy is implemented
or selected for implementation by A0. No tolerance relaxation is recommended.

## Numerical safeguards

All original acceptance budgets remain unchanged: mass <1e-8 kg; refrigerant,
thermal-node and combined energy <1e-6 kJ; fluid nonlinear norm <=1e-11; thermal
closure <=1e-12 K. Original temporal/direct-EOS accuracy, event, stage-recovery,
rollback and domain criteria remain in their unchanged tests. No scientific
reference or existing evidence file is overwritten.

## Reproduction

Use a real checkout containing the immutable handoff object, Node 22.23.3,
Python 3.12, CoolProp 7.2.0, NumPy 2.5.3, SciPy 1.16.2 and Playwright 1.62.1.
Set up dependencies using the existing handoff instructions. Use temporary
outputs so every frozen reference and result remains intact.

```sh
node experiments/dx-fv/roadmap-a-diagnostics.cjs /tmp/a0.json /tmp/a0-probes.jsonl.gz
node experiments/dx-fv/roadmap-a-diagnostics.cjs /tmp/a0.json /tmp/a0-probes.jsonl.gz --replay
node experiments/dx-fv/roadmap-a-diagnostics.cjs /tmp/a0.json /tmp/a0-probes.jsonl.gz --memory
python experiments/dx-fv/audit_roadmap_a_diagnostics.py /tmp/a0.json /tmp/a0-probes.jsonl.gz /tmp/a0-audit.json
python experiments/dx-fv/audit_coupled_diagnostics.py experiments/dx-fv/COUPLED_R_DIAGNOSTICS.json experiments/dx-fv/COUPLED_R_FAILED_NEWTON.jsonl.gz /tmp/a0-preserved-audit.json
node experiments/dx-fv/coupled-test.cjs /tmp/a0-coupled-frozen.json
python experiments/dx-fv/generate_coupled_reference.py /tmp/a0-coupled-reference.json
DX_COUPLED_REFERENCE_PATH=/tmp/a0-coupled-reference.json node experiments/dx-fv/coupled-test.cjs /tmp/a0-coupled-fresh.json
python experiments/dx-fv/audit_coupled_results.py /tmp/a0-coupled-frozen.json /tmp/a0-frozen-audit.json
python experiments/dx-fv/audit_coupled_results.py /tmp/a0-coupled-fresh.json /tmp/a0-fresh-audit.json
node experiments/dx-fv/coupled-domain-test.cjs /tmp/a0-domain.json
node experiments/dx-fv/coupled-controls.cjs /tmp/a0-controls.json
node experiments/dx-fv/coupled-browser.cjs /tmp/a0-browser.json
```

Also run the established application/build, prescribed-heat, temporal/spatial and
standalone thermal regressions listed in `DEVELOPMENT_HANDOFF.md`. The existing
hosted workflow remains unchanged and does not invoke the new A0 harness/audit;
the A0 evidence is separately reproduced using these commands.

## Diagnostic cost and evidence retention

Public `ph`, `sat` and `stateMVU` calls are counted through transparent wrappers
identically in all three paths. Nested calls inside engine implementations are
excluded. Residual evaluations, iterations and linear solves are separate work
counts. Diagnostic comparator property calls use a separate engine and are not
charged to the integration path.

Recorded probe residuals add 21 copied numbers per successful evaluation plus
coordinate fields and object overhead. Selected early/late successful/failed
attempts are compressed outside the repository; full-run probe metrics are
aggregated, while all attempt-level work/regrowth entries are retained. Archive
bytes and peak serialized attempt size measure storage, not exact JavaScript
heap allocation. Numeric-array payload estimates exclude array/object overhead.
No speedup or normal-operation wall-time comparison is claimed; concurrent
shared-runner validation is unsuitable for such a claim.

The optional `--memory` phase runs the same nominal reversal workload in two
fresh Node processes, first the original uninstrumented solver and then the
extended solver with a minimal diagnostic consumer. It checks identical state,
record and work hashes, and reports each process's peak RSS separately. This
single paired memory observation includes runtime/allocator variation and the
whole optional observer; it excludes A0 comparator/serialization IO. It is not
a universal heap bound or a speed benchmark.

The report and audit retain evidence digests. Generated JSON/gzip files are
temporary artifacts outside the repository, as authorized. The final delivery
reports the new commit SHA and actual hosted regression status.

## Qualified recording costs

The paired fresh-process nominal reversal run has identical state/record hashes,
1,231,654 residual evaluations, 42,073 Newton iterations/linear solves,
3,125,413 public PH calls, 3,213,848 public saturation calls and 49,935 public
canonical-recovery calls in both processes.

| Measurement | Observed |
| --- | ---: |
| Original uninstrumented peak RSS | 155,396 KiB (151.754 MiB) |
| Minimal-observer peak RSS | 158,664 KiB (154.945 MiB) |
| Paired RSS difference | 3,268 KiB (3.191 MiB) |
| Maximum live copied probe numbers in one nominal attempt | 21,168 |
| Float64-equivalent payload of those copied numbers | 169,344 bytes (excludes headers/objects) |
| Largest serialized nominal attempt | 928,917 bytes |
| Selected 20-trial gzip archive | 850,120 bytes |

Across all seven observed trajectories, the cumulative float64-equivalent probe
vector payload allocated is 494,163,432 bytes. This is allocation volume, **not**
peak live memory: vectors are discarded between attempts except selected archive
records. The paired RSS measurement includes the complete existing optional
diagnostics plus the extension and has only one pair; allocator/runtime variation
prevents treating the difference as a universal bound. The full A0 analysis and
serialization have additional overhead that the minimal-observer measurement
intentionally excludes. No normal solver speedup or recording-time comparison
is claimed.

## Validation, versions and evidence digests

Qualified local runtime: Node 22.23.3, Python 3.12.14, CoolProp 7.2.0, NumPy 2.5.3,
SciPy 1.16.2, Playwright 1.62.1, Chromium 151.0.7922.34, WebKit 26.5, Git 2.52.0,
Linux x86_64. Browser binaries and missing libraries were installed under
`/tmp/ammonia-a0-runtime/`; WebKit's temporary bundle links resolve its overridden
loader path. `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` bypassed only the
system-cache library preflight, not browser execution or scientific assertions.
Hosted regression uses the unchanged normal dependency-install workflow.

Passed local checks:

* All five nominal fixtures and tight/reference reversal equivalence, detached
  probe mutation, schema success/branch-rejection/failure checks, six uncommitted
  replays, and paired memory-workload equivalence.
* Independent A0 Python audit: 20 archived attempts, 9,786 derivative probes,
  5,126 thermal columns, 2,795 inversion-sensitivity points and 924 additional
  replay thermal columns. Full-run work/regrowth arithmetic is checked for every
  attempt; vector-level audit is limited to the selected archives/replays.
* Both complete coupled frozen/fresh suites (five cases, ten additional checks,
  original intentional failure/rollback scenarios). Fresh direct-EOS generation
  has zero fallbacks and reproduces the frozen JSON byte-for-byte; resulting
  coupled evidence is identical after excluding only elapsed-time fields.
* Both independent 150-record coupled accounting audits; worst combined energy
  residual 5.44022e-9 kJ. Full-suite maximum combined energy residual remains
  6.05193e-8 kJ, mass 1.94237e-10 kg and thermal-node energy 3.26204e-9 kJ.
* Coupled domain-classification and adaptive-control/mixed-edit rollback suites.
* All 13 existing application numerical suites; standalone build consistency.
* Original DX, temporal, three/five, three/five/nine and warm-domain regressions;
  standalone thermal numerical qualification.
* Application, coupled and standalone thermal Chromium/WebKit checks.
* Existing full Newton-history audit: 2,552 failed solves, 1,669,542 derivative
  probes and 902,052 line-search probes; preserved archive digest unchanged.
* Output-location guards reject evidence paths inside the repository; no frozen
  file is overwritten. Every existing tracked file other than the explicitly
  authorized observer source remains unchanged.

Digests for the generated evidence from this delivery:

* Selected evaluated-probe archive SHA256: `a1e00e1c829fca1e8599d1e3635a3adedfb2a6087cb6a24f1ce0c9d5818969d8`.
* A0 JSON SHA256: `962ada076c7bf14ae1c0fff54f5b77897dc59f7ed541e1ca25c10a9aaeb320a2`.
* Independent A0 audit JSON SHA256: `b90b6a0496c2983793e7e58ead0d4d7b6c5ee5e25e5df8555c1a2f18ec3b6d5a`.
* Unchanged property table SHA256:
  `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`.

RSS observations and their JSON digest can vary on regeneration. Equivalence is
required within each paired runtime; absolute state hashes are not advertised as
a cross-platform acceptance criterion. No generated JSON/gzip evidence is added
to Git. This delivery commits only the three authorized new files and the
approved observer exception. The exact delivery SHA and actual hosted regression
status are reported separately; a commit cannot embed its own SHA.
