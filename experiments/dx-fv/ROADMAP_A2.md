# Roadmap A2 — controlled failure-aware timestep growth experiment

**Status: locally qualified isolated TR-BDF2 experiment; both options remain opt-in.**
Starting commit `c2de1f0808048f6be6f3e912cd0fcffa9a646cf0`, branch `experimental/dx-fv-stage-3`, repository `cdehek/Ammonia-sim`.
The original finite-difference Jacobian and original timestep controller remain the defaults. All established acceptance contracts pass. The broader nominal adaptive backward-Euler diagnostic remains a separately documented failure; it is not presented as qualified.

## Policy and boundaries

The only changed existing file is `coupled-model.cjs`. New files are
`roadmap-a2.cjs`, `audit_roadmap_a2.py` and this report. Historical sources,
Newton solver, time-control helper, tables, fixtures, references, workflows,
application source and restore commits remain unchanged.

The explicit option is `timestepGrowth: 'failure-aware'`. Omission or
`'original'` retains the original proposal controller. A1's
`thermalJacobian: 'exact'` remains independently selected; A2 does not select it.
The policy is inactive when `adaptive: false`.

Exact decision rules:

1. Learn only from caught errors with `faultKind === 'solver'`, a finite
   `nonlinearResidual`, and no `domainCause`. The current Newton iteration-budget
   and nonreducing line-search failures meet that definition. Generic recovery,
   property and domain-probe failures are excluded.
2. Retain the original failed-trial halving and minimum-step/stop logic. Remember
   a pending nonlinear failure and the most recently failed interval.
3. After the next fully accepted retry, install its full trial interval as a
   temporary proposal ceiling. The two accepted half steps and all temporal,
   event, property, residual and conservation requirements are unchanged.
4. Compute the original error-based proposal. Limit it by that ceiling only
   when it would exceed the ceiling; do not raise an accuracy-limited proposal.
5. Four subsequent successful trials at or above `ceiling*(1-1e-12)` earn a
   25% increase, capped at the existing `maxStep`. Smaller output-clipped or
   accuracy-limited accepted trials do not earn increases. Another learned
   failure restarts recovery. Once the ceiling reaches `maxStep`, clear the
   difficulty history and return to unrestricted original growth.
6. Valid scheduled/manual boundary patches clear difficulty history. Invalid
   mixed patches leave both physical state and history unchanged. Phase-event
   refinement and newly committed phase crossings also clear history. Accuracy
   rejection clears the success streak without learning a convergence ceiling.
   Domain-related and other caught failures clear history and retain original
   rejection/domain-evidence classification.
7. Optional history is per-state and survives reporting calls. It is absent
   from default states/records. Its counters describe proposal behavior, not
   physical support. Stops retain original state freezing and evidence rules.

The policy adds no property/residual evaluations for proposal decisions. Growth
history is metadata, not a physical ledger or domain boundary. There are no
changes to physical balances, conductances, Newton limits, line search,
property inversion, nonlinear/thermal tolerances, temporal budgets or rollback.


## Seeded phase-event investigation

The previously failing assertion required a cumulative count of exactly one
nonlinear failure after manually seeding one historical entry and advancing the
warm fixture for two seconds. Deterministic investigation distinguishes that
synthetic entry from Newton evaluations. FD/A2 has four actual failures and a
seeded cumulative counter of five; exact/A2 has three actual failures and a
seeded cumulative counter of four. Unseeded A2 has the same real failures.
Original-controller FD/exact controls reproduce those same initial failures.

All real failures occur at the initial accepted state, time zero, before any
phase event. FD fails trials 0.5, 0.25, 0.125 and 0.0625 s; exact fails 0.5,
0.25 and 0.125 s. Each reaches the unchanged iteration-30 budget with fluid
norm already below 1e-11 and thermal closure above 1e-12 K. FD thermal closures
are 6.832206e-12, 3.198916e-12, 1.651235e-12 and 1.082123e-12 K; dominant
residual rows are 16, 16, 18 and 12. Exact thermal closures are 6.020051e-12,
3.314687e-12 and 1.652364e-12 K, with dominant rows 16, 16 and 18. Independently
replaying each failed trial at its detached accepted state reproduces its
classification and message. Every failure halves its next trial and preserves
all accepted physical state, ledgers, clocks, phase/boundary events and counts.

The synthetic seed changes metadata only. It does not change `nextStepSeconds`;
this diagnostic therefore begins with the original 0.5 s proposal. The four
real FD failures are existing initial Newton behavior, not failures introduced
by A2 regrowth or a phase reset. No failure is suppressed or accepted as a valid
numerical trial.

Five cell phase events occur during each warm replay. FD/A2 event clocks are
approximately 0.005375289, 0.129526731, 0.453291738, 0.899492101 and 1.501363449 s.
At every observed post-event attempt, the ceiling, pending failure and recovery
coordinates are cleared. Next proposals match the original error-based factor,
including increases and decreases. The independent Python audit reconstructs
every proposal/retry, release and reset from the traces and agrees with the
complete final growth history. Its six replay records have worst independent
combined-energy residual 7.283489e-10 kJ and section-mass residual 5.933656e-13 kg.

Repeated diagnostic runs are identical; enabling observation preserves states,
records, decisions and public property counts. The same controls against the A1
ancestor are identical. The coupled-model algorithm SHA256 is unchanged across
the investigation: `929be63391a11efe3769f356e12e77afb62111672349069af7cf1562f42bf91e`.
Only A2 test/audit/report files changed during diagnosis.

The unsupported exact-one assertion was replaced with behavior checks: the
counter equals the seeded entry plus observed real failures; failures roll back
and halve; phase resets clear stale history; subsequent proposals follow the
original growth factor; no domain rejection is fabricated; conservation,
recovery, temporal error, phase brackets and trajectory/event budgets all pass.
No expected failure count is hardcoded. The corrected test passes both Jacobian
modes. General qualification and runtime evidence are reported separately below.


## Numerical qualification

All four configurations completed the unchanged coupled suite against both frozen and freshly regenerated independent direct-EOS references: five original fixtures, ten additional numerical checks and seven intentional stop/rollback scenarios per execution. Fresh generation has zero boundary-flash fallbacks and is byte-identical to the frozen reference. Untimed frozen/fresh results are identical for each configuration.

The original assertions cover temporal and maximum-step refinement, direct EOS, equilibrium, zero exchange, reference-offset invariance, fixed-step TR-BDF2 and backward-Euler order, physical allocation, phase events, domain clocks, atomic accepted-state installation and stop freezing. Backward-Euler fixed-step observed orders are 0.96312 and 0.98119; TR-BDF2 orders are 2.01275 and 2.01406. Neither required method test was removed.

Every configuration also passed control/mixed-patch rollback and actual Chromium/WebKit numerical execution. The default historical domain regression passes; exact/original and both A2 options each pass all 36 A1 domain/probe-classification/rollback cases. Supported fixture runs have no new stops or domain rejections. Browser versions are Chromium 151.0.7922.34 and WebKit 26.5. These are scientific blank-page executions, not application integration or UI performance claims.

Independent original accounting audits pass for all eight frozen/fresh archives (150 records each). The additional A2 Python audit reconstructs proposals, retries, release/reset history and signed conservation independently from physical capacities and recorded ledgers; it imports no JavaScript solver or controller helper.

Its four-configuration comparison contains 600 output records. Worst independent section mass, fluid-energy, node-energy and combined-energy residuals are 9.11648534e-12 kg, 3.42205908e-09, 4.01465527e-11 and 5.44022782e-09 kJ.

Unchanged limits: mass <1e-8 kg; every required energy ledger <1e-6 kJ; fluid nonlinear residual ≤1e-11; thermal closure ≤1e-12 K. The original same-table temporal, direct-EOS and phase-event budgets are enforced by the established suites. There is no tolerance relaxation.

| A2 configuration | Maximum suite mass kg | Maximum combined energy kJ | Maximum accepted fluid residual | Maximum accepted thermal closure K |
| --- | ---: | ---: | ---: | ---: |
| fd-aware | 1.94236863e-10 | 6.05192838e-08 | 9.80293952e-12 | 9.99883054e-13 |
| exact-aware | 1.94441204e-10 | 6.05793673e-08 | 9.90163918e-12 | 9.99966315e-13 |

Observed maxima in the last two columns cover all converged Newton solves in the fully observed nominal reversal, including successful solves within ultimately rejected trials; failed solves are recorded separately and never accepted.

| Fixture | FD/A2 EOS pressure bar / enthalpy kJ/kg / fluid K / thermal K / event s | Exact/A2 EOS errors in same order |
| --- | --- | --- |
| cold | 3.437202e-06 / 0.001732985 / 0.0001343644 / 5.652395e-05 / 0 | 3.437202e-06 / 0.001732985 / 0.0001343644 / 5.652395e-05 / 0 |
| warm | 2.674185e-06 / 0.006277058 / 0.001093644 / 6.893774e-05 / 4.125833e-05 | 2.672986e-06 / 0.006276325 / 0.001093768 / 6.893762e-05 / 4.142732e-05 |
| load-step | 3.437202e-06 / 0.001732402 / 0.0001343644 / 4.977045e-05 / 0 | 3.437202e-06 / 0.001732402 / 0.0001343644 / 4.977045e-05 / 0 |
| feed-step | 3.437202e-06 / 0.001732402 / 0.0001343644 / 5.727786e-05 / 0 | 3.437202e-06 / 0.001732402 / 0.0001343644 / 5.727786e-05 / 0 |
| heat-reversal | 3.928489e-05 / 0.005164615 / 0.000718339 / 8.434698e-06 / 0 | 3.928424e-05 / 0.005164462 / 0.0007182805 / 7.791705e-06 / 0 |

EOS errors use each established refined 1e-8 reference-regime run, as required. Bounds remain pressure <1e-4 bar, enthalpy <0.05 kJ/kg, temperatures <0.01 K and event clock <0.001 s.

All 14 complete A1 ancestor comparisons pass exact state, record, ledger, event/history, work and public-property-call equality, including reversal at all three tolerance regimes and both Jacobians. Explicit original-policy selection also equals omission. The default gains no growth-history fields. Observer-enabled and disabled A2 nominal reversal runs have identical states, records, decisions, work and property counts; deliberate mutations of detached observer arrays do not affect calculation.

Historical prescribed-heat, temporal, thermal, three/five spatial, three/five/nine resolution and warm-domain tests pass. All 13 existing application numerical suites pass without modifying application files; generated validation outputs were redirected outside Git. The existing build was evaluated with its root write replaced by a byte-equality check in memory, and generated output matches the protected index exactly. The hosted unchanged workflow separately exercises default numerical, application/browser and historical fresh-reference regressions.

## Four-configuration work comparison

Each accepted trial commits two half steps. Iterations equal linear solves in these runs. Property counts below are actual public engine invocations: PH / saturation / mass-volume-energy recovery. Internal nested engine calls are not separately observable and are not silently included. Residual evaluations are distinct from these property calls.

Original intervals and schedules are unchanged: cold/warm 120 s; load/feed/reversal 60 s; load/feed boundaries at 15 and 30 s; original output cadence in every path.

| Fixture, nominal 1e-6 | Configuration | Accepted | Rejected | Newton failures | Iterations / linear solves | Residual evaluations | PH / saturation / MUV calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| cold | baseline | 321 | 5 | 0 | 4635 | 103926 | 302372 / 330037 / 14725 |
| cold | exact | 321 | 5 | 0 | 4635 | 52941 | 200402 / 228067 / 14725 |
| cold | fd-aware | 321 | 5 | 0 | 4635 | 103926 | 302372 / 330037 / 14725 |
| cold | exact-aware | 321 | 5 | 0 | 4635 | 52941 | 200402 / 228067 / 14725 |
| warm | baseline | 444 | 33 | 0 | 7847 | 175498 | 505029 / 544969 / 21520 |
| warm | exact | 446 | 33 | 0 | 7869 | 89434 | 333380 / 373490 / 21610 |
| warm | fd-aware | 444 | 33 | 0 | 7847 | 175498 | 505029 / 544969 / 21520 |
| warm | exact-aware | 446 | 33 | 0 | 7869 | 89434 | 333380 / 373490 / 21610 |
| load-step | baseline | 212 | 5 | 0 | 3271 | 73264 | 212211 / 230621 / 9830 |
| load-step | exact | 212 | 5 | 0 | 3271 | 37283 | 140249 / 158659 / 9830 |
| load-step | fd-aware | 212 | 5 | 0 | 3271 | 73264 | 212211 / 230621 / 9830 |
| load-step | exact-aware | 212 | 5 | 0 | 3271 | 37283 | 140249 / 158659 / 9830 |
| feed-step | baseline | 280 | 13 | 0 | 4288 | 96094 | 278918 / 303638 / 13260 |
| feed-step | exact | 280 | 13 | 0 | 4288 | 48926 | 184582 / 209302 / 13260 |
| feed-step | fd-aware | 280 | 13 | 0 | 4288 | 96094 | 278918 / 303638 / 13260 |
| feed-step | exact-aware | 280 | 13 | 0 | 4288 | 48926 | 184582 / 209302 / 13260 |
| heat-reversal | baseline | 962 | 922 | 921 | 42073 | 1231654 | 3125421 / 3213861 / 49940 |
| heat-reversal | exact | 985 | 947 | 946 | 43441 | 792507 | 2282597 / 2373767 / 51750 |
| heat-reversal | fd-aware | 1297 | 89 | 88 | 19489 | 466684 | 1223290 / 1334270 / 59080 |
| heat-reversal | exact-aware | 1283 | 87 | 86 | 19193 | 248262 | 785114 / 894919 / 58465 |
| All five | baseline | 2219 | 978 | 921 | 62114 | 1680436 | 4423951 / 4623126 / 109275 |
| All five | exact | 2244 | 1003 | 946 | 63504 | 1021091 | 3141210 / 3343285 / 111175 |
| All five | fd-aware | 2554 | 145 | 88 | 39530 | 915466 | 2521820 / 2743535 / 118415 |
| All five | exact-aware | 2542 | 143 | 86 | 39256 | 476846 | 1643727 / 1864437 / 117890 |

| Reversal refinement | Configuration | Accepted | Rejected | Newton failures | Iterations / solves | Residual evaluations | PH / saturation / MUV |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1e-07 | baseline | 963 | 907 | 906 | 41816 | 1220579 | 3099069 / 3187454 / 49845 |
| 1e-07 | exact | 973 | 918 | 917 | 41883 | 764432 | 2197724 / 2286864 / 50200 |
| 1e-07 | fd-aware | 1302 | 87 | 86 | 19523 | 466892 | 1224581 / 1335976 / 59295 |
| 1e-07 | exact-aware | 1318 | 89 | 88 | 19703 | 255098 | 801829 / 914639 / 60070 |
| 1e-08 | baseline | 976 | 727 | 725 | 36139 | 1039819 | 2637940 / 2726210 / 49190 |
| 1e-08 | exact | 1014 | 796 | 794 | 38805 | 693593 | 1976174 / 2068279 / 51505 |
| 1e-08 | fd-aware | 1342 | 86 | 84 | 19822 | 473265 | 1237786 / 1352631 / 61125 |
| 1e-08 | exact-aware | 1349 | 87 | 85 | 20017 | 257213 | 806617 / 922107 / 61490 |

All 15 fixture/tolerance regimes complete in all four configurations. Cold/warm/load/feed A2 accepted/rejected intervals and work equal the corresponding original-controller path at all three regimes. Only reversal learns a convergence restriction in this matrix. This equality is established from the traces, not inferred from aggregate rejection counts.

Nominal FD/A2 adds 335 accepted trials (670 half steps); exact/A2 adds 298 (596 half steps). MUV calls increase by 18.30% and 12.98%, respectively. FD/A2 reduces residual evaluations by 62.11%, iterations/solves by 53.68% and PH calls by 60.86%. Exact/A2 relative to exact/original reduces evaluations by 68.67%, iterations/solves by 55.82% and PH calls by 65.60%. These work reductions are not runtime percentages.

## Failure histories and trajectory differences

| Nominal reversal configuration | Newton failures | Same-state repeated failures | Successful retry immediately regrows | Next grown proposal fails |
| --- | ---: | ---: | ---: | ---: |
| baseline | 921 | 196 | 723 | 531 |
| exact | 946 | 238 | 703 | 473 |
| fd-aware | 88 | 2 | 0 | 0 |
| exact-aware | 86 | 0 | 0 | 0 |

The FD/original statistic reproduces A0: 531 of 723 successful-retry regrowth proposals fail again. A2 removes immediate regrowth after learned nonlinear recovery by construction; it does not fix Newton convergence. Real nominal failures remain (88 FD, 86 exact), classified and recorded normally. Every observed failure rolls back and halves; none is relabeled as a supported-domain boundary.

All remaining observed reversal failures reach the unchanged iteration-30 budget in superheated vapor. Their dominant rows are tube-energy rows 10, 14 and 16. Fluid norms are already below 1e-11; thermal closure is still above 1e-12 K. No phase crossing explains these late-relaxation failures. This confirms the persistence of the underlying thermal-closure convergence difficulty; it does not establish a sole PH-inversion cause.

| Configuration | Failure clocks s | Failed trial intervals s | Fluid norm range | Thermal closure range K |
| --- | --- | --- | --- | --- |
| fd-aware | 0.36868163–59.466396 | 0.04252196–0.18263043 | 8.6016077e-13–2.8628753e-12 | 1.0007259e-12–2.3516546e-12 |
| exact-aware | 0.27736572–59.523729 | 0.052240117–0.1039209 | 1.0479115e-12–2.8690129e-12 | 1.0017883e-12–2.2895145e-12 |

| Reversal regime | Comparison to FD/original | Max pressure bar | Enthalpy kJ/kg | Fluid K | Thermal K | Link-integral kJ | Event s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1e-06 | exact | 4.280915e-08 | 6.781926e-06 | 2.820799e-06 | 4.96898e-06 | 8.582728e-09 | 0 |
| 1e-06 | fd-aware | 2.989142e-08 | 4.731802e-06 | 1.968182e-06 | 3.475242e-06 | 6.003424e-09 | 0 |
| 1e-06 | exact-aware | 2.307307e-08 | 3.629151e-06 | 1.5101e-06 | 2.663856e-06 | 4.606294e-09 | 0 |
| 1e-07 | exact | 3.226702e-08 | 5.199346e-06 | 2.160445e-06 | 3.738313e-06 | 6.464333e-09 | 0 |
| 1e-07 | fd-aware | 5.048607e-08 | 8.041038e-06 | 3.343464e-06 | 5.860465e-06 | 1.012298e-08 | 0 |
| 1e-07 | exact-aware | 5.050851e-08 | 8.041244e-06 | 3.343631e-06 | 5.860448e-06 | 1.012952e-08 | 0 |
| 1e-08 | exact | 5.861571e-09 | 9.386397e-07 | 3.925824e-07 | 9.650809e-07 | 1.122924e-09 | 0 |
| 1e-08 | fd-aware | 1.452402e-08 | 2.3454e-06 | 9.804956e-07 | 2.480158e-06 | 2.889808e-09 | 0 |
| 1e-08 | exact-aware | 1.398388e-08 | 2.19299e-06 | 9.182945e-07 | 2.361887e-06 | 2.751394e-09 | 0 |

These are trajectory differences, not conservation residuals. Conservation is checked independently against each path’s own signed physical ledgers. The experimental sequences are allowed to differ; all original temporal, EOS, phase-event and domain budgets still pass.

## Controlled Node 22 runtime

One complete warm-up workload per configuration and five measured four-path blocks ran in one Node 22 process after every qualification worker exited. Orders are baseline/exact/exact-aware/fd-aware, exact/fd-aware/baseline/exact-aware, fd-aware/exact-aware/exact/baseline, exact-aware/baseline/fd-aware/exact, then the first order again. Thus the first four blocks balance positions and ordered adjacent pairs.

Each configuration uses identical fixtures, intervals, schedules and output/conservation checks. The timer includes engine/factory/state creation and all advances and output checks. Hashing, JSON evidence serialization and diagnostics are outside the timer. No parallel qualification timings or cross-environment A1 timings are used. Every repetition has identical physical state/record hashes, work and public calls, and timed work/calls match nominal qualification.

Hardware: {"platform": "linux", "arch": "x64", "kernel": "6.18.44", "cpu": "INTEL(R) XEON(R) PLATINUM 8573C", "cgroupCpuMax": "200000 100000"}.

| Workload | Configuration | Median s | Minimum–maximum s | Sample SD s |
| --- | --- | ---: | --- | ---: |
| cold | baseline | 3.9686 | 2.3100–4.3466 | 0.8384 |
| cold | exact | 2.2064 | 1.3438–2.2480 | 0.3843 |
| cold | fd-aware | 2.7817 | 2.5308–3.7338 | 0.4639 |
| cold | exact-aware | 1.6639 | 1.3236–2.7449 | 0.5597 |
| warm | baseline | 5.3739 | 4.2717–7.9627 | 1.3613 |
| warm | exact | 3.4754 | 2.6250–4.2121 | 0.6363 |
| warm | fd-aware | 5.6764 | 4.5527–6.7340 | 0.8809 |
| warm | exact-aware | 3.5269 | 2.5911–5.1742 | 1.0116 |
| load-step | baseline | 2.4158 | 1.6191–2.7663 | 0.4690 |
| load-step | exact | 1.4035 | 0.9514–1.9101 | 0.3897 |
| load-step | fd-aware | 2.1410 | 1.6922–2.3309 | 0.2684 |
| load-step | exact-aware | 1.6768 | 0.9328–2.3599 | 0.5913 |
| feed-step | baseline | 2.9452 | 2.1214–4.2358 | 0.8268 |
| feed-step | exact | 1.7961 | 1.2465–2.2881 | 0.3904 |
| feed-step | fd-aware | 2.6952 | 2.1988–3.9060 | 0.7813 |
| feed-step | exact-aware | 2.5260 | 1.2462–3.5120 | 0.8065 |
| heat-reversal | baseline | 44.9234 | 32.0068–48.4955 | 6.7674 |
| heat-reversal | exact | 35.8204 | 23.8311–42.9045 | 7.0967 |
| heat-reversal | fd-aware | 18.9967 | 13.7695–19.9510 | 2.5972 |
| heat-reversal | exact-aware | 12.9780 | 8.8178–16.1039 | 2.7631 |
| total | baseline | 61.9122 | 42.3290–65.0964 | 9.3223 |
| total | exact | 45.2138 | 29.9978–50.7581 | 8.1380 |
| total | fd-aware | 33.4708 | 24.7439–33.9609 | 3.9143 |
| total | exact-aware | 23.1607 | 14.9114–26.1391 | 4.5744 |

| Workload | FD/A2 ÷ FD/original median (range) | Exact/A2 ÷ exact/original | Exact/A2 ÷ FD/original | Exact/original ÷ FD/original |
| --- | --- | --- | --- | --- |
| cold | 0.677763 (0.636686–1.324480) | 0.958566 (0.740149–1.234251) | 0.532942 (0.382794–0.668786) | 0.555979 (0.517185–0.609352) |
| warm | 1.214376 (0.682301–1.328841) | 1.014832 (0.797967–1.680520) | 0.656309 (0.422105–0.884814) | 0.614518 (0.526512–0.735965) |
| load-step | 0.818526 (0.611733–1.437849) | 0.980409 (0.877849–2.372307) | 0.694099 (0.576112–0.853098) | 0.587624 (0.359607–0.790682) |
| feed-step | 0.942936 (0.519094–1.841208) | 1.327402 (0.999800–2.232087) | 0.829130 (0.587459–0.947597) | 0.587576 (0.371459–0.909856) |
| heat-reversal | 0.422869 (0.285212–0.500644) | 0.361151 (0.302486–0.462818) | 0.275496 (0.231287–0.382084) | 0.825559 (0.738632–0.888697) |
| total | 0.546638 (0.380112–0.732214) | 0.497083 (0.475741–0.588274) | 0.374090 (0.345119–0.462628) | 0.779737 (0.708682–0.786416) |

Ratios are computed within each interleaved block before taking the median; quotients of separate per-path medians are not substituted. Values above one are measured slowdowns. Five samples describe this workload/environment, not a universal speed guarantee.

Raw elapsed seconds, measured block order:

| Workload | Baseline | Exact | FD/A2 | Exact/A2 |
| --- | --- | --- | --- | --- |
| cold | 2.310022, 4.346617, 4.104249, 3.149242, 3.968583 | 1.343798, 2.248006, 2.223911, 1.918997, 2.206448 | 3.059579, 2.767431, 2.781710, 3.733780, 2.530783 | 1.323582, 1.663859, 2.744864, 1.573819, 2.115027 |
| warm | 4.271664, 5.325823, 5.373883, 7.962733, 5.847788 | 2.625016, 3.919621, 3.475382, 4.212085, 3.078930 | 5.676364, 6.733982, 6.525914, 5.432978, 4.552707 | 2.591064, 4.493197, 3.526928, 3.361106, 5.174205 |
| load-step | 1.619055, 2.647930, 2.046292, 2.415801, 2.766262 | 0.951396, 1.429761, 1.403484, 1.910131, 0.994766 | 2.327956, 2.140975, 2.330939, 1.977396, 1.692214 | 0.932757, 2.105739, 1.234876, 1.676806, 2.359891 |
| feed-step | 2.121412, 2.945188, 2.514844, 3.460987, 4.235754 | 1.246491, 1.796084, 2.288147, 1.936325, 1.573411 | 3.905960, 2.695194, 2.371338, 3.702700, 2.198754 | 1.246242, 2.526027, 2.383059, 2.570281, 3.511991 |
| heat-reversal | 32.006850, 48.495540, 42.147658, 44.923412, 48.278006 | 23.831116, 35.820360, 34.795397, 38.705921, 42.904526 | 16.024027, 19.133261, 19.950951, 18.996697, 13.769462 | 8.817774, 11.216366, 16.103929, 13.978689, 12.978032 |
| total | 42.329003, 63.761098, 56.186925, 61.912174, 65.096393 | 29.997818, 45.213832, 44.186321, 48.683459, 50.758081 | 30.993886, 33.470843, 33.960851, 33.843551, 24.743921 | 14.911419, 22.005188, 25.993656, 23.160699, 26.139145 |

## Conclusions and review boundary

For the complete five-fixture workload, median paired runtime reductions are 45.34% for FD/A2 versus FD/original and 50.29% for exact/A2 versus exact/original. Exact/A2 versus the original FD baseline saves 62.59%. Reversal-specific paired reductions are 57.71% and 63.88%.

The policy provides a meaningful measured net benefit on the difficult reversal workload, including the additional accepted steps and recovery calls. Every total-workload pair is faster: FD/A2 ratios are 0.380112–0.732214 and exact/A2 versus exact/original ratios are 0.475741–0.588274. Reversal-specific ratios are also below one in every pair.

Measured regressions include the warm FD/A2 paired median at 1.214376 (21.44% slower) and feed-step exact/A2 at 1.327402 (32.74% slower). Some individual non-reversal pairs are substantially slower, including load-step exact/A2 at 2.372307. Numerical work and trajectories are unchanged in those comparisons; these timings do not isolate controller overhead from runtime variability, GC or execution-order effects. These cases have no rejection-saving benefit. The experiment earns no general claim of benefit for fixtures without nonlinear failures.

Recommend retaining A2 as an optional qualified research configuration for review, rather than promoting either option to the default. Its four-success/25% release constants are a controlled experimental choice, not an optimized or universal controller. Late-stage thermal-closure difficulty remains, and PH inversion is unchanged. Boundary/event resets and eventual ceiling release are tested; no permanent artificial cap is introduced. No additional solver optimization or backward-Euler remedy is proposed as part of A2.

Reassess solver readiness and return to the requested coupled-evaporator physics priorities after review. No A3, PH inversion change, Stage 2B, nine-section coupled implementation, production integration, application change or merge is included.

## Deferred exploratory adaptive backward-Euler limitation

While the original qualification was running, an additional A2-specific test
was introduced for **adaptive backward Euler**, nominal accuracyOptions(1e-6),
cold/warm/reversal samples through one second. This broader method check is
outside the established five-fixture TR-BDF2 matrix; the original suite tests
backward Euler's fixed-step order on a smooth sealed fixture instead. It applied
direct-EOS bounds to a nominal run, whereas the established suite applies direct
EOS bounds to its refined 1e-8 reference run after same-table temporal refinement.
This was an unnecessary expansion and a misapplication of the existing
comparison protocol; the failed check is retained rather than hidden.

Cold passed that supplemental check. Warm failed on the **first configuration,
FD Jacobian and original controller**, before testing A2 for warm. Independent
read-only replay from the accepted A1 Git source and current default source
produces identical complete accepted states, records, histories and errors.

| Original-controller nominal adaptive BE warm diagnostic | Error | Bound applied by supplemental test |
| --- | ---: | ---: |
| Pressure, at 0.01 s, section 0 | 1.056419605e-4 bar | <1e-4 bar |
| Enthalpy, at 1 s, section 2 | 0.1557175315 kJ/kg | <0.05 kJ/kg |
| Refrigerant temperature maximum | 0.0099458775 K | <0.01 K |
| Thermal temperature maximum | 0.0008324835 K | <0.01 K |

Other enthalpy violations occur at 0.2 s/section 0 and 1 s/section 1. The replay
reaches every requested sample without a stop and meets the unchanged nonlinear
and conservation budgets. It demonstrates a pre-existing nominal adaptive-BE
accuracy limitation under those applied bounds; it does not identify an A2
policy defect. No refined BE study or same-table BE temporal comparison has been
performed, so no claim that proper reference-regime BE qualification passes is
made. No assertion was changed to accept these errors.


The retained broader adaptive-BE diagnostic is explicitly outside the resumed acceptance gate and remains failing. Investigation of it is deferred by the review decision. This does not overlap or replace the established fixed-step BE order contract, which passes unchanged in every qualified suite. It is not silently discarded, relabeled as passed or used to justify weaker limits.

## Environment, storage and reproduction

Node 22.23.3, Python 3.12.14, CoolProp 7.2.0, numpy 2.5.3, scipy 1.16.2, Playwright 1.62.1. System-default Node 24 is not used. Browser binaries and dependencies were reused from the qualified temporary runtime. Numerical evidence is generated only outside the repository under `/tmp/ammonia-a2-evidence/`.

Normal A2 states contain one small growth-history object; default states contain none. Trace/observer archives are excluded from timing. File sizes below describe serialized diagnostic storage, not measured JavaScript heap overhead:

| Evidence | Bytes |
| --- | ---: |
| compare.json | 80388392 |
| baseline.json | 10070 |
| phase-diagnosis.json | 32444104 |
| observed.json | 845178 |
| performance.json | 79160 |
| fd-aware final history, compact JSON | 232 |
| exact-aware final history, compact JSON | 233 |

From the repository root, with Node 22 and the listed Python dependencies selected:

```bash
mkdir -p /tmp/ammonia-a2-evidence
node experiments/dx-fv/roadmap-a2.cjs rules /tmp/ammonia-a2-evidence/rules-qualified.json
node experiments/dx-fv/roadmap-a2.cjs phase-diagnosis /tmp/ammonia-a2-evidence/phase-diagnosis.json
python experiments/dx-fv/audit_roadmap_a2.py /tmp/ammonia-a2-evidence /tmp/ammonia-a2-evidence/phase-audit.json --phase-only
node experiments/dx-fv/roadmap-a2.cjs baseline /tmp/ammonia-a2-evidence/baseline.json
node experiments/dx-fv/roadmap-a2.cjs compare /tmp/ammonia-a2-evidence/compare.json
node experiments/dx-fv/roadmap-a2.cjs observed /tmp/ammonia-a2-evidence/observed.json
python experiments/dx-fv/generate_coupled_reference.py /tmp/ammonia-a2-evidence/fresh-reference.json
for choice in baseline exact fd-aware exact-aware; do
  node experiments/dx-fv/roadmap-a2.cjs suite "/tmp/ammonia-a2-evidence/$choice-frozen.json" "$choice" coupled-test
  DX_COUPLED_REFERENCE_PATH=/tmp/ammonia-a2-evidence/fresh-reference.json node experiments/dx-fv/roadmap-a2.cjs suite "/tmp/ammonia-a2-evidence/$choice-fresh.json" "$choice" coupled-test
  for kind in frozen fresh; do
    python experiments/dx-fv/audit_coupled_results.py "/tmp/ammonia-a2-evidence/$choice-$kind.json" "/tmp/ammonia-a2-evidence/$choice-$kind-audit.json"
  done
  node experiments/dx-fv/roadmap-a2.cjs suite "/tmp/ammonia-a2-evidence/$choice-controls.json" "$choice" coupled-controls
  node experiments/dx-fv/roadmap-a2.cjs suite "/tmp/ammonia-a2-evidence/$choice-browser.json" "$choice" coupled-browser
done
node experiments/dx-fv/coupled-domain-test.cjs /tmp/ammonia-a2-evidence/baseline-domain.json
node experiments/dx-fv/roadmap-a1.cjs domain /tmp/ammonia-a2-evidence/exact-domain.json
node experiments/dx-fv/roadmap-a2.cjs domain /tmp/ammonia-a2-evidence/fd-aware-domain.json fd-aware
node experiments/dx-fv/roadmap-a2.cjs domain /tmp/ammonia-a2-evidence/exact-aware-domain.json exact-aware
python experiments/dx-fv/audit_roadmap_a2.py /tmp/ammonia-a2-evidence /tmp/ammonia-a2-evidence/qualification-audit.json --qualification-only
# Stop all other numerical/browser workers before timing.
node experiments/dx-fv/roadmap-a2.cjs performance /tmp/ammonia-a2-evidence/performance.json 5
python experiments/dx-fv/audit_roadmap_a2.py /tmp/ammonia-a2-evidence /tmp/ammonia-a2-evidence/audit.json
```

Browser commands require installed Playwright Chromium/WebKit and their shared-library dependencies. The A1 starting object must be locally available for ancestor comparison; fetch the immutable object if using a shallow clone, without moving branch refs. Suite adapters select only the factory in memory; all established assertions, fixtures and references stay unchanged. Delegated established suites retain their historical starting-commit headers (the reused A1 domain-case header names A0). Those are case-source provenance, not claims that this run executed at the old commit: actual A2 provenance is the stated A1 parent plus the locked model SHA256 and current four-path harness archives.

The broader exploratory failure remains reproducible separately (expected nonzero exit):

```bash
node experiments/dx-fv/roadmap-a2.cjs methods /tmp/ammonia-a2-evidence/methods.json
```

`methods.json.failure.json` retains the cold partial results and warm failure. `methods-baseline-diagnosis.json` preserves complete accepted-A1/current-default warm replays. `rules.json.failure.json` preserves the superseded unsupported phase-count assertion; `rules-qualified.json` is the corrected acceptance evidence. Deliberately interrupted logs are retained and are not counted as passes.

The final independent audit archives SHA256 digests for all evidence JSON, including exploratory failure files. Selected reproducible evidence digests:

| Evidence | SHA256 |
| --- | --- |
| compare.json | `1c3b49cda443c528525ea6b9e88994f19be44e4399f3b23ee6a493b3a4d7a324` |
| baseline.json | `0962a9dc2495130004bed4c4fad454531ea6a98e03a8079fbdcd632cd979d328` |
| rules-qualified.json | `2fc92c20ca5c6b07ddbdd9d94ebb702e071ce5333d1b46a6df4c57394ede8a1d` |
| phase-diagnosis.json | `6f30f6bdc6c4961ec283861f7ce72fe4da9f253ae75a25ef34a1f1a07efc475c` |
| observed.json | `84873dc7df01d58f183517e9ec2e3330c8e94c5a30ff0e4cc2382784b34d7817` |
| methods.json.failure.json | `89aaa5ca7750b8a52b72522c24a297c519681a914dbdf84b70d956cbd0697a43` |
| methods-baseline-diagnosis.json | `e6ed37af24f1f3f61f3faaac18da169c7e411c28042b0b0ac6380929632d16fa` |
| fresh-reference.json | `f455a712e7fbedbb17b4cc65a792f7898d793bd18132fabc471871fc6000ce3b` |
| performance.json | `43867462f4036fcaef1682c725088bbcdd27f128f2ea7e1188a75534d62a9d22` |

The scientific-source guard checks all 179 tracked files: only `coupled-model.cjs` changes among existing files, and eleven scientific functions remain byte-identical to A1. The A2 model SHA256 remains `929be63391a11efe3769f356e12e77afb62111672349069af7cf1562f42bf91e` throughout phase diagnosis, deferred BE review and resumed qualification. Every restore, property table, fixture, frozen reference and workflow is untouched.

Only the modified isolated model, new A2 harness, independent audit and this report are authorized for commit. Hosted status is reported with the delivered exact commit SHA. The unchanged hosted workflow qualifies the default and historical paths; optional A1/A2 selections are covered by the complete local matrix above, not automatically selected by CI. No default promotion or further development is authorized by this delivery.
