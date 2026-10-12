# Stage 2B — five/nine-section coupled DX evaporator

**Qualification blocked; uncommitted and unpushed.** The approved historical
negative assertion is corrected, and the isolated nine-section implementation
passes the original-fixture scientific checks described below. The new extended
operating scenario misses the unchanged independent-EOS phase-event budget.
Stage 2B is not a qualified milestone. No tolerance, algorithm, property inversion,
physical equation, boundary or fixture has been changed to remedy the failure.
Downstream qualification and benchmarking are held for user direction.

Repository `cdehek/Ammonia-sim`, branch `experimental/dx-fv-stage-3`.
HEAD and remote remain starting restore
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. Identity, clean starting checkout,
ancestry through A1/A0/Stage 2A/documentation restores and accepted A2 CI were
verified. https://github.com/cdehek/Ammonia-sim/actions/runs/38109562003 is
completed/success at that exact SHA, all four jobs successful. No applicable
AGENTS.md was found. No new hosted run exists because no commit was pushed.

## Blocking scientific result

The additional 360 s cold scenario removes air load and feed pressure drive at
120 s (load 0, inlet 3.5 bar/h=500), reverses the feed-side pressure gradient at
180 s (3.3 bar/h=500), then restores load 1 kW/feed 4 bar/h=500 at 240 s.
Outlet stays 3.5 bar/h=1700. This uses existing prescribed boundary and signed
donor transport physics, not compressor/valve/shutdown control physics.
Both meshes complete the full schedule at all three JS tolerances without stops.
The vapor crossing during pressure-drive removal fails the independent timing
budget; the subsequent wetting crossing after restoration is much closer.

| Mesh | JS resolved vapor event s | Independent EOS event s | Absolute error ms | Budget ms |
| --- | ---: | ---: | ---: | ---: |
| 5 | 146.383507171434 | 146.382180250900 (fine) | 1.326921 | <1 |
| 9 | 146.911304327853 | 146.909931932368 (coarse; fine interrupted at gate) | 1.372395 | <1 |

The five-section comparison uses its completed fine Radau reference. The actual
independent audit exits nonzero on its phase-event assertion; pressure, enthalpy,
fluid and thermal sampled errors remain within their budgets. This demonstrates
that the observed difficulty is not exclusive to nine sections. The new five
path preserves original mathematics and matches accepted A2 bit for bit across
all 20 original fixture/option replays; a separate legacy-source replay of this
new extended case has not been performed, so the underlying cause is not yet
assigned to a pre-existing property limitation or an implementation defect.
The five-section Radau own-refinement event difference is 2.41938e-8 s; maximum
own-refinement pressure/enthalpy differences are 1.56342e-10 bar and
1.75771e-6 kJ/kg. Independent reference uncertainty is far too small to explain
the 1.326921 ms discrepancy.

The nine resolved event differs from the coarse EOS event by 1.372395 ms.
If EOS own-refinement meets its unchanged 1 microsecond requirement, the fine
EOS discrepancy is at least 1.371395 ms, still over budget. Otherwise the reference
refinement gate itself fails. Thus both required gates cannot pass simultaneously
for this captured result. The already-running fine EOS calculation was interrupted at this gate after
the completed five-section fine-reference comparison confirmed failure. Its
coarse result and logs are retained; no fine nine result is fabricated.
Recorded nine-section resolved bracket width is 24.933 microseconds and its
signed saturation-margin slope is 51.589 kJ/(kg s). Nominal/tight/resolved slopes
are about 50.3/50.6/51.6: this is a sharp crossing, not evidence for discarding it
as a grazing event. Linear bracket uncertainty cannot explain 1.37 ms.

At five sections, nominal/tight/resolved vapor-event discrepancies versus fine
EOS are 0.544926/1.186122/1.326921 ms. Nine nominal/tight/resolved times are
146.910515616/146.911161169/146.911304328 s. Tighter JS integration therefore
approaches a trajectory whose event disagrees more with direct EOS; the nominal
pass cannot substitute for the required resolved comparison. Property-source
initial inventories/interpolation, nonlinear precision and accumulated temporal
error are unresolved contributors. No cause is claimed proven from these clocks.

## Approved historical test correction

The user approved the narrowly scoped change in `coupled-test.cjs`: the obsolete
nine-section exclusion is now a seventeen-section exclusion. The complete file
is audited byte-for-byte against A2 with only that exact expression replaced.
Five and nine are the only supported configurations. Seventeen remains rejected
with an explicit configuration error; no seventeen-section simulation exists.
The raw original five-section scientific suite passes after this correction.
New Stage 2B tests separately exercise positive nine-section numerical behavior.
Earlier interrupted workers and the obsolete-assertion failure remain evidence
of the initial authorization gate, not scientific passes or numerical regressions.

## Architecture and physical invariants

The existing prescribed-heat refrigerant, standalone thermal and joint coupled
factories remain separate. Only the joint model and its Newton implementation
change. The historical transport, conservation, hydraulics, thermodynamic
recovery, thermal geometry and time-control modules remain untouched.

The coupled model selects five by default and nine explicitly through
`sectionCount:9` in its construction configuration. Five retains its original
model identifier and settings. Nine contains nine conservative M/U/fixed-V
cells, nine tube energies, nine fin energies and one finite-air energy. Its
joint solve has eighteen alternating PH coordinates followed by nineteen
thermal-energy increments: **37 coordinates and 37 equation rows**.

Previously fixed assumptions were the five-state configuration guard,
eleven-node/21-row exact thermal matrix, ten-coordinate thermal offset,
five-entry tube/refrigerant ledger, diagnostic PH/thermal split and recorded
section count. Those dimensions now follow the constructed cells/thermal graph.
The original stage balance, dense solve, perturbations, damping, thirty-iteration
limit, canonical recovery, acceptance, retry and atomic fine-step installation
are retained. A1 exact columns and A2 growth remain independent opt-ins; the
failure-aware policy itself is unchanged.

Both meshes reuse the validated physical allocation modules:

| Invariant | Five and nine |
| --- | --- |
| Refrigerant volume / bore / length | 0.003 m³ / 0.020 m / 9.5492965855 m |
| Tube capacity | 4.87014 kJ/K |
| Fin capacity | 4.2460087439 kJ/K |
| Finite-air capacity | 4.308 kJ/K; unchanged fixed-mass/fixed-volume closure |
| Tube/refrigerant conductance | 0.60 kW/K total; 0.12 or 0.0666666667 per section |
| Air/tube / air/fin / fin/tube conductance | 0.03455989393 / 0.87846470417 / 2.0 kW/K total |
| Hydraulic boundary restrictions | K=1000 inlet, K=2 outlet; no added internal K |
| Hydraulic lengths | Half-cell boundaries, full-cell internal faces; total length invariant |

Tube/fin mass, area, capacity and conductance use physical length fractions;
fractional fin equivalents are not rounded. Summed homogeneous-state viscous
and inertial hydraulic resistance equals the unchanged whole-tube resistance
on both meshes. Signed shared-face mass/bulk-donor enthalpy transport and
same-stage equal-and-opposite tube/refrigerant exchange remain unchanged.

Original finite-difference columns and original timestep growth remain the
default. No new correlation, property inversion, domain extension, tolerance,
line search, physical equipment, air model or heat source is introduced.

## Conservative initialization

Uniform PH construction retains the original path. A new `initialProfile`
accepts contiguous piecewise-constant physical PH bins on normalized [0,1].
For each new cell, it integrates density and internal-energy density over
physical overlap lengths, using the unchanged property engine. The canonical
cell M/U/V is retained; pressure is only a recovery guess. Recovered PH is
recorded as provenance without reinitializing its integrated inventories.
Explicit cell PH states and a physical profile are mutually exclusive.

Tube/fin profiles use the existing validated energy-integral initializer. No
old cell-center pressure, enthalpy, temperature or quality interpolation is
used as a conservation argument. Within-cell homogenization can change recovered
PH, quality and derived liquid inventory; those effects still require trajectory
and spatial analysis. Initialization is conservative for M/U/thermal energy,
not a claim that every nonlinear phase observable is invariant.

| Initialization | Five | Nine |
| --- | ---: | ---: |
| Uniform cold total mass kg | 0.05954795894499106 | 0.05954795894499106 |
| Uniform cold internal energy kJ | 28.723979472495532 | 28.723979472495536 |
| Nonuniform mass kg | 0.040657681063082325 | 0.040657681063082325 |
| Nonuniform internal energy kJ | 22.765716568438055 | 22.76571656843805 |
| Nonuniform total canonical thermal energy kJ | 170.47634593902006 | 170.47634593902004 |

The nonuniform physical profile uses p=3.5 bar with h=500/600/700 kJ/kg on
[0,.27]/[.27,.64]/[.64,1]. Tube temperatures are 273.15/290 K on [0,.43]/[.43,1];
fin temperatures are 278.15/288 K on [0,.61]/[.61,1]; finite air starts at
293.15 K. These are new isolated research inputs, not changes to any established
fixture or a proposed dry-outlet operating condition.

## Completed original-fixture qualification

Both meshes' four configurations (FD/original, exact/original, FD/A2, exact/A2)
pass all five unchanged fixtures at 1e-6/1e-7/1e-8 regimes: **120 integrations**,
full original 120 s cold/warm and 60 s load/feed/reversal intervals and schedules.
Raw five and dimension-adapted nine full historical coupled suites pass original
zero-exchange, equilibrium, step-cap refinement, fixed BE/TR order, canonical
recovery, reference-energy gauge, conservation, intentional-failure and rollback
assertions. New adapters change dimensions in memory, not scientific limits.
Controls pass on both meshes/all options; nine domain/probe/rollback and A2 reset
rules pass. All four nine modes retain established fixed-step BE/TR orders.
The separately documented broader adaptive-BE limitation stays deferred unchanged.

All 20 immutable-A2/new-five fixture/option replays match physical states,
records, solver work and public property calls exactly. Five extra default-mode
traced replays match complete accepted/rejected timestep sequences. Full nine
observer on/off equivalence was queued but is held at the blocker; it is not
claimed completed. Numerical acceptance remains scaled fluid residual <=1e-11,
thermal closure <=1e-12 K, all established canonical recovery, mass <1e-8 kg and
energy <1e-6 kJ requirements. The unchanged accepted-stage code enforces these;
recorded states and independent accounting remain within budget.

An independent physical unit-energy incidence-matrix audit checks **197,787**
assembled entries across all eleven/nineteen thermal columns and all 21/37 rows,
including refrigerant-energy coupling, cold/warm, reversal, zero exchange,
closed relaxation, successful/failing uncommitted trials and BE/TR stages.
Maximum scaled discrepancy is **7.10543e-15**. Thermal residual derivative is
`I-dt*weight*dR/dE`; tube contribution to fluid-energy rows is
`-dt*weight*G/C`, mass rows zero, with original row scaling. Thermal scale is
C*0.1 K; trapezoidal weight 1/2 at gamma*dt, final BDF weight
(1-gamma)/(2-gamma), BE weight 1. Paired energy derivatives cancel.

All **80** frozen/fresh EOS original-fixture comparisons pass across both meshes
and all modes. The new Python pathway independently assembles M/U, hydraulics,
thermal balances and signed ledgers with CoolProp HEOS and SciPy Radau; it imports
no JS numerical implementation or property table. Original frozen five evidence
regenerates byte for byte. New nine physical cases reproduce exactly; its
separate frozen JSON SHA256 is
`aea169071ae03da085c26fae38dee5ae6962b4c7a84964c5eec098817737587b`.

| Mesh | Original-case maximum EOS pressure bar | h kJ/kg | Fluid K | Thermal K | Event s |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5 | 3.92849e-05 | 0.00627706 | 0.00109377 | 6.89377e-05 | 4.14273e-05 |
| 9 | 3.92844e-05 | 0.0064536 | 0.00114331 | 7.02614e-05 | 2.24476e-05 |

Direct-EOS budgets remain p <1e-4 bar, h <0.05 kJ/kg, fluid/thermal T <0.01 K,
events <0.001 s. Same-table nominal/tight versus resolved budgets remain
p <5e-5, h <0.05, T <0.01/0.001 K and events <0.001 s. Independent Radau
own-refinement retains p <1e-7, h/fluid T <1e-4, thermal T <1e-5 and events
<1e-6 s. Global/per-section and node conservation are checked separately from
trajectory differences; EOS density/u differences at common initial PH are not
ledger residuals. Sealed initial JS/CoolProp mass differs about 6.18e-8 kg
(7.56 ppm) from property-source inventory differences, not lost mass.

SciPy numerical-Jacobian factor overflow warnings remain in logs. In the fresh
original nine reference, captured large factors are only passive ledger columns
37–93 (RHS independent of those coordinates), not physical columns. Physical
cases reproduce exactly and refinement/budget checks pass. This diagnostic is
not extrapolated to extended logs lacking column-specific capture. Initial new
Python dimension/adapter syntax errors and environmental launch interruptions
remain retained, not represented as scientific passes.

## Nonuniform and extended conservation

Both meshes use the same physically integrated nonuniform initial profile above,
with no cell-center PH/temperature interpolation as a conservation argument.
Uniform profile initialization agrees with ordinary initialization. Nonuniform
three-tolerance trajectories and independent EOS samples are recorded separately.
The standard-library accounting audit independently reconstructs global/cell
M/U, thermal-node E and paired face/link budgets from physical capacities.
Original-matrix audit: 1,550 records; maximum mass 3.473e-11 kg, fluid energy 1.7813e-08 kJ, node energy 4.01466e-11 kJ and combined energy 5.44022e-09 kJ. Separate completed extra-case accounting: 156 records; maxima mass 5.38338e-11 kg, fluid energy 3.02074e-08 kJ, node energy 3.55656e-11 kJ and combined energy 1.24498e-08 kJ. Passing balances do not override the failed event-accuracy gate.

| Mesh / additional case | EOS pressure bar | h kJ/kg | Fluid K | Thermal K | Event ms | Reference |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 5 / nonuniform | 1.22348e-06 | 0.00397299 | 0.000201144 | 5.53314e-05 | 0 | fine |
| 5 / extended pressure-drive removal/reversal/restoration | 3.4372e-06 | 0.00658677 | 0.00100822 | 0.000180633 | 1.32692 | fine |
| 9 / nonuniform | 1.09449e-06 | 0.00393402 | 0.000198612 | 5.65014e-05 | 0 | fine |
| 9 / extended pressure-drive removal/reversal/restoration | 3.3796e-06 | 0.0065681 | 0.000710294 | 0.000296506 | 1.3724 | coarse; fine interrupted at gate |

The pressure-removal/reversal intervals are costly. Targeted nine nominal replay
finds failures dominated by refrigerant-energy row 1: the first 0.05 s proposal
at 120 s fails near fluid residual 0.00787; a 0.004338 s proposal at 148.708 s
fails near 1.02e-10 while thermal closure is satisfied. This differs from the
sealed heat-reversal thermal-closure mechanism. Donor-branch sensitivity,
property precision and controller history remain hypotheses, not proven remedies.
Supported local Newton failures remain retries, not physical domain boundaries.

No sustained dry-outlet fixture is added. At 3.5 bar, hg≈1601.489 kJ/kg,
feed h=500 and flow≈0.01536 kg/s require about 16.9 kW to reach dry vapor;
the established external load is 1 kW. Startup stored energy is transient.
The additional dry crossing occurs during pressure-drive removal; it is not
claimed feasible sustained dry operation under the original feed/load.
Wet outlets remain valid observations and fixtures are not altered to hide them.

## Spatial results: qualified original cases

`preliminary-spatial.json` compares common x/L=.1,.3,.5,.7,.9 and common physical
ports. Extensive M/U, liquid M and tube/fin E are integrated by overlap into
45 accounting intervals, not a simulated finer mesh; PH, quality and temperatures
use piecewise-constant cell reconstructions with physical interval provenance.
It retains pressure/enthalpy profiles, tube/fin and finite-air temperatures,
liquid inventory, common-port signed flow/enthalpy budgets, heat and phase clocks.
Final extended-case projection was held at the accuracy blocker.

| Original endpoint | Total mass 5 / 9 kg | Liquid mass 5 / 9 kg | Liquid difference | Outlet h 5 / 9 kJ/kg |
| --- | ---: | ---: | ---: | ---: |
| cold / 120 s | 0.049376076 / 0.050061861 | 0.040998208 / 0.041687059 | 1.6802% | 567.051840 / 567.045718 |
| warm / 120 s | 0.048488997 / 0.049225566 | 0.040106941 / 0.040846800 | 1.8447% | 574.565947 / 574.580468 |
| load-step / 60 s | 0.046307950 / 0.047182485 | 0.037915540 / 0.038793983 | 2.3168% | 594.478581 / 594.363083 |
| feed-step / 60 s | 0.047524436 / 0.048326594 | 0.039137811 / 0.039943553 | 2.0587% | 583.109129 / 583.034488 |
| heat-reversal / 60 s | 0.008172754 / 0.008172754 | 0.000000000 / 0.000000000 | both zero | 1629.581531 / 1629.581531 |

Independent EOS five/nine trajectories corroborate the 1.7–2.3% open-flow liquid
inventory differences. Cold midpoint h is 540.078904/537.091161 kJ/kg despite
similar outlet h, total heat 1.02786799/1.02786584 kW and finite-air temperature
271.134848/271.134773 K. Warm midpoint vapor crossing at common x/L=.5 is
0.4532625/0.6116574 s. Terminal bulk-cell crossings 1.5013424/1.6622764 s are
not equal-position clocks because terminal cells span different physical intervals;
port quality is independently sampled at identical boundaries. Sealed reversal
has zero flow and spatially uniform trajectories; its approximately 11 K
superheat is not flowing-dry qualification. Four open-flow endpoints remain wet,
port quality approximately .1921/.1980/.2135/.2046 for cold/warm/load/feed.

Nine exposes inventory and phase-progression sensitivity hidden by similar
outlet/heat totals. Five cannot support a claim of resolution-independent
inventory/phase fronts from this comparison. Nine is a higher-resolution
comparison, not proof of spatial convergence, calibrated equipment accuracy or
physical truth. No seventeen-section or finer implementation exists. Full Stage
2B readiness and next-stage conclusions are withheld at the extended event gate.

## Work counts; controlled timing not executed

Counts are reproducible numerical work, not a demonstrated runtime improvement.
Actual public ph/sat/stateMVU entries are counted separately from residual calls;
private nested table operations inside the protected engine are not claimed as
individually observed calls. Linear solves equal recorded Newton iterations.
All original fixtures retain their full intervals/output schedules. Concurrent
qualification wall times cannot serve as performance comparisons.

| Mesh / option | Accepted / rejected totals (five fixtures) | Newton failures | Iterations = solves | Residual evaluations | Public property entries |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5 / baseline | 2219 / 978 | 921 | 62114 | 1680436 | 9156352 |
| 5 / exact | 2244 / 1003 | 946 | 63504 | 1021091 | 6595670 |
| 5 / fd-aware | 2554 / 145 | 88 | 39530 | 915466 | 5383770 |
| 5 / exact-aware | 2542 / 143 | 86 | 39256 | 476846 | 3626054 |
| 9 / baseline | 2331 / 1003 | 912 | 67694 | 2884472 | 15237584 |
| 9 / exact | 2351 / 1032 | 925 | 68574 | 1618908 | 10334940 |
| 9 / fd-aware | 2718 / 182 | 91 | 46044 | 1797631 | 10303620 |
| 9 / exact-aware | 2711 / 195 | 88 | 46031 | 921548 | 6812680 |

Nine reversal FD/original is 952 accepted/913 rejected/912 Newton failures;
exact/original is 965/926/925. FD/A2 is 1339/92/91 (387 extra accepted trials),
exact/A2 is 1325/89/88. Exact columns remove work while slightly increasing
failure count; A2 reduces failure work at a cost of more accepted steps.
Neither is promoted. Extended nominal five/nine is 3854/3016 versus 5210/4316
accepted/rejected trials, with 2943/4200 Newton failures. Resolved five/nine is
6575/2875 versus 8494/4434, with 2740/4225 Newton failures. Full per-case/mode
iterations, property-call categories and residual counts are in the matrices.

Five measured interleaved timing blocks with warm-up, runtime variability and
fresh-process memory measurements were prepared but held; no efficiency or
memory-use result is claimed. As a numerical-payload estimate only, nine exact
columns contain 703 numbers (5624 float64-equivalent bytes) plus a temporary
361-number rate matrix (2888 bytes); dense 37x37 matrix storage is 10952 bytes,
excluding JS overhead. The approximately 18 MB diagnostic archive is separate
storage, not normal performance/memory. No interval was shortened to claim gain.

## Regression status, protected scope and decision gate

Completed: 21 application numerical/historical scientific regression commands,
12 compatibility commands, eight frozen/fresh reference generator commands,
six fresh historical regression commands; coupled Chromium/WebKit scientific
coverage for both meshes and all four modes; Chromium application UI suite;
first six WebKit application UI tests. A protected WebKit capacity-release click
then timed out under concurrent CPU load. Failure logs/manifest remain retained;
the unchanged serial replay and remaining four historical browser suites were
held at the scientific blocker. Build output matched the protected bundle and
root-generated numerical JSON was redirected outside Git; the temporary UI export
was retained outside Git and removed from the working tree. No source/assertion
or timeout was changed to remedy the UI failure.

Also held: full nine observer equivalence, final extra-case projection, full fresh
five coupled-suite replay, controlled performance/memory and final complete audit.
Incomplete/interrupted queue outputs are not represented as passed. The extended
independent audit exits nonzero on the actual five-section 1.326921 ms event
error. Previous interim audits explicitly predate that completed scenario.
The original default and independently selectable A1/A2 options remain intact.

Exact eight-file change set, all under `experiments/dx-fv/`:

* `coupled-model.cjs` — dimensions and conservative profile initialization.
* `coupled-implicit.cjs` — dynamic diagnostic split and exact-column indexing.
* `coupled-test.cjs` — approved negative guard 9→17 only.
* `coupled-stage2b.cjs` — new qualification/adapters/comparisons/measurement harness.
* `generate_coupled_stage2b_reference.py` — separate independent EOS pathway.
* `coupled-stage2b-reference.json` — new nine-section standard-fixture reference evidence.
* `audit_coupled_stage2b.py` — independent accounting/Jacobian/EOS/source checks.
* `COUPLED_STAGE_2B.md` — this blocked investigation report.

The latest independent source guard verifies all 179 other pre-existing tracked
files unchanged and coupled-test byte-for-byte with exactly the approved expression
replacement. No workflow, historical solver/test/fixture/report/frozen reference,
property data, production/application engine/UI/equipment/test/build, main or
PR #3 changes. No commit, push, merge, default promotion or subsequent stage.
Hosted CI remains the accepted starting A2 run; no new hosted qualification claim.

**Approval needed:** choose the handling of this newly exposed extended-event
limitation before further work. Recommend a narrowly bounded, diagnostic-only
investigation: reproduce this event with immutable A2 five-section source and
compare matched initial M/U versus matched PH and local property/EOS behavior,
while preserving full recorded qualification trajectories and every budget.
This would distinguish initialization/property-source error from numerical
integration/implementation effects; it would not substitute properties, derivatives,
timesteps or altered boundaries into accepted integration. Any numerical correction
would require a separate proposal/approval. Alternatively, explicitly decide
whether this new scenario is to be deferred as an unqualified limitation while
finishing the original envelope; it cannot be silently omitted or labeled passed.
No remediation or narrowed qualification envelope is assumed authorized.

## Environment, evidence and reproduction

Node 22.23.3; Python 3.12.14; CoolProp 7.2.0; NumPy 2.5.3; SciPy 1.16.2;
Playwright 1.62.1; Chromium 151.0.7922.34; WebKit 26.5. Runtime under
`/tmp/ammonia-stage2b-runtime/`; Xeon Platinum 8573C, Linux 6.18.44,
two-CPU cgroup quota. System Node 24 was not used for scientific execution.
Evidence: `/tmp/ammonia-stage2b-evidence/`, not guaranteed persistent across
workspace replacement. Key files: `five-frozen.json`, `nine-frozen.json`,
`five-compare.json`, `nine-compare.json`, `baseline.json`, `baseline-history.json`,
`geometry.json`, `columns.json`, `preliminary-spatial.json`,
`five-extra.json`, `nine-extra.json`, `extended-five-reference.json`,
`extended-nine-reference.json.partial.json` (fine run interrupted at the gate),
`extended-event-gate.json`, `extended-gate-diagnosis.json`,
`extended-qualification-audit.log`, `extra-accounting.json`,
`blocked-source-guard.json`, all queue manifests/logs and
`browser-queue.failed-concurrent.json`. Original frozen five reference SHA256:
`f455a712e7fbedbb17b4cc65a792f7898d793bd18132fabc471871fc6000ce3b`.

Commands from repository root using the specified runtimes:

```sh
mkdir -p /tmp/stage2b-evidence
node experiments/dx-fv/coupled-stage2b.cjs geometry /tmp/stage2b-evidence/geometry.json
node experiments/dx-fv/coupled-stage2b.cjs columns /tmp/stage2b-evidence/columns.json
node experiments/dx-fv/coupled-test.cjs /tmp/stage2b-evidence/five-frozen.json
node experiments/dx-fv/coupled-stage2b.cjs suite /tmp/stage2b-evidence/nine-frozen.json baseline 9 coupled-test
node experiments/dx-fv/coupled-stage2b.cjs baseline /tmp/stage2b-evidence/baseline.json baseline 5
node experiments/dx-fv/coupled-stage2b.cjs baseline-history /tmp/stage2b-evidence/baseline-history.json baseline 5
node experiments/dx-fv/coupled-stage2b.cjs compare /tmp/stage2b-evidence/five-compare.json baseline 5
node experiments/dx-fv/coupled-stage2b.cjs compare /tmp/stage2b-evidence/nine-compare.json baseline 9
node experiments/dx-fv/coupled-stage2b.cjs extra /tmp/stage2b-evidence/five-extra.json baseline 5
node experiments/dx-fv/coupled-stage2b.cjs extra /tmp/stage2b-evidence/nine-extra.json baseline 9
python experiments/dx-fv/generate_coupled_stage2b_reference.py /tmp/stage2b-evidence/extended-five-reference.json 5 extended
python experiments/dx-fv/generate_coupled_stage2b_reference.py /tmp/stage2b-evidence/extended-nine-reference.json 9 extended
python experiments/dx-fv/audit_coupled_stage2b.py /tmp/stage2b-evidence /tmp/stage2b-evidence/audit-output.json
```

With complete extended data it is expected to fail the unchanged phase gate;
`--complete` additionally requires all held tests and benchmark evidence and is
not a shortcut to qualification. New reference generation outputs belong outside
Git. Existing references and all other established test assertions remain unchanged;
only the explicitly approved 9→17 configuration assertion is modified.
