# PCHIP bounded coupled-trajectory investigation

**Diagnostic evaluation complete; PCHIP remains unqualified and opt-in.**
The original extended-event discrepancies improve to approximately 0.012 ms on
both meshes without changing the event definition or 1 ms requirement. Most
extended-state accuracy measures improve, with slightly worse pressure accuracy.
The liquid PH property regression persists. A matched-inventory liquid transient
has better temperature/heat-transfer accuracy but slightly worse pressure/enthalpy
accuracy, and exposes an existing compressed-liquid pressure limitation in both
interpolation paths. No adoption, algorithm change, commit or push follows.

Repository `cdehek/Ammonia-sim`, branch `experimental/dx-fv-stage-3`, HEAD
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. All **197 pre-existing files**,
including uncommitted Stage 2B work, the phase investigation and PCHIP candidate,
are byte-for-byte preserved. The original interpolation, finite-difference
Jacobian and original timestep policy remain defaults. A1/A2 stay independent
options; they were not enabled in these comparisons. Frozen references, original
fixtures, production tables/source, workflows and prior reports remain unchanged.

## Bounded scope and matching

Two scenarios, with the same geometry, M/U/V initialization, thermal energies,
boundaries, settings and output schedules between original and PCHIP:

* **Existing extended cold prefix, 0–150 s.** Original samples
  0.01/0.2/1/5/15/30/60/120/120.1/150 s; original 120 s feed-drive removal and
  air-load removal, with later 180/240 s boundaries retained but unreached.
  Four resolved runs compare original/PCHIP at five/nine sections. Two additional
  PCHIP tight runs provide focused temporal evidence.
* **Sealed liquid diagnostic, 0–0.1 s.** Uniform p=32.65314902038559 bar,
  h=686.779725665 kJ/kg, the preceding property study's worst liquid point.
  Tube/fin/finite-air initial temperatures are 343.42777804386204 K, approximately
  1 K above the fixed-PH EOS fluid temperature. Air load is zero; all existing
  hydraulic faces are closed. Samples 0.001/0.01/0.05/0.1 s. This is a diagnostic
  property-conditioning probe, not a proposed evaporator operating fixture or
  sustained liquid-feed scenario. No new system controls or hydraulic model.

TR-BDF2, original Newton/line-search limits and all tolerances are unchanged;
resolved/tight settings are the existing `accuracyOptions(1e-8/1e-7)`.
Existing optional trace recording is enabled identically to classify actual
Newton failures and timestep decisions, without extra residual/property calls.
Both original prefixes match saved default records exactly after removing only
trace metadata. Candidate settings, configurations and initial canonical arrays
are independently asserted equal to original ones. The previously accepted
five-source full-prefix reproduction remains preserved.

The established extended EOS pathway initializes specified PH using direct EOS;
its initial inventory differs slightly from the interpolated table in **both**
JS paths. Initial total JS/EOS M is 0.059547958945/0.059547787681 kg and U is
28.723979472496/28.723893840358 kJ. These are property-initialization differences,
not mass/energy conservation residuals. No initial inventory is changed to favor
PCHIP. The new liquid references instead initialize **exactly the same canonical
M/U and thermal energies** as both JS paths, isolating the recovery/evolution
comparison. Five/nine equipment totals remain the same, to allocation roundoff.

## Independent EOS evidence

Original five/nine frozen and saved fresh cold EOS samples are equal and remain
read-only. Existing fine five-section extended evidence is reused. For nine,
one separate fine Radau continuation from the preserved direct-EOS 120 s cold
checkpoint ends at 150 s; its first event matches the prior targeted fine clock
exactly. No accepted reference is regenerated or replaced. New liquid evidence
uses independently assembled Python balances with direct CoolProp HEOS, Radau,
rtol 1e-8/1e-10, maxstep 0.01/0.005 s and the established absolute tolerances.
It does not import the JS integrator or PCHIP implementation.

| Reference convergence | Five | Nine |
| --- | ---: | ---: |
| Extended event coarse/fine difference | 24.194 ns | 11.091 ns |
| Extended maximum pressure difference | 1.5634e-10 bar | 2.3378e-10 bar |
| Extended maximum enthalpy difference | 2.7874e-7 kJ/kg | 1.4020e-6 kJ/kg |
| Extended maximum fluid-T difference | 1.6920e-8 K | 1.3029e-8 K |
| Liquid maximum pressure difference | 5.6133e-12 bar | 5.6133e-12 bar |
| Liquid maximum enthalpy difference | 1.0346e-11 kJ/kg | 1.0346e-11 kJ/kg |

All reference convergence checks retain their original budgets, including <1 µs
events. The preserved reference's existing flash fallback and passive-ledger
Jacobian overflow warnings are retained in the new evidence, not suppressed or
reclassified. All solves complete without domain events and pass independent
reference conservation checks.

## Extended event and state results

The same terminal-cell bulk dew crossing, h−hg(p_bulk)=0, heats from wet to vapor.
It is cell 4 over x/L=[0.8,1] for five, cell 8 over [8/9,1] for nine. Each mesh
is compared to its own reference, not to a different mesh's section index.
These are the previously established well-conditioned crossings.
Both paths preserve all five/nine recorded section-crossing identities and their
order, without missing or spurious events; independent event timing here is
checked for the terminal crossing supplied by the reference pathway.

| Mesh | EOS event s | Original event s / error ms | PCHIP event s / error ms |
| --- | ---: | ---: | ---: |
| Five | 146.382180249400 | 146.383507171434 / +1.326922 | 146.382192206338 / **+0.011957** |
| Nine | 146.909931921277 | 146.911304327853 / +1.372407 | 146.909943791908 / **+0.011871** |

Both PCHIP clocks meet the unchanged <1 ms gate; both original clocks fail it.
The PCHIP tight/resolved event differences are 0.140808/0.142679 ms. Maximum
tight/resolved pressure differences are below 5.3e-7 bar, enthalpy below
4.2e-4 kJ/kg, fluid/thermal temperature below 1e-5 K. These pass the existing
focused tight temporal budgets; they are not the full refinement matrix.

Maximum sampled discrepancy against direct EOS over the prefix:

| Measure | Five original → PCHIP | Nine original → PCHIP |
| --- | ---: | ---: |
| Pressure, bar | 3.4372e-6 → 3.4781e-6 | 3.3796e-6 → 3.4203e-6 |
| Enthalpy, kJ/kg | 0.006490 → 0.006267 | 0.006455 → 0.006224 |
| Fluid temperature, K | 1.3436e-4 → 2.5386e-5 | 1.3679e-4 → 2.4965e-5 |
| Tube/fin/air temperature, K | 6.1784e-5 → 6.1023e-6 | 6.5552e-5 → 6.9095e-6 |
| Total liquid inventory, kg | 2.2777e-7 → 1.3183e-7 | 2.2913e-7 → 1.3227e-7 |
| Outlet quality, wet samples | 1.6550e-6 → 7.8674e-7 | 1.6675e-6 → 8.1547e-7 |
| Summed tube/fluid heat integral, kJ | 5.2476e-4 → 4.8725e-5 | 5.2478e-4 → 4.8504e-5 |
| Summed instantaneous tube/fluid heat, kW | 4.6363e-5 → 1.3177e-5 | 4.6818e-5 → 1.3067e-5 |

Pressure maximum error worsens about 1.2%, while the other listed measures improve.
All sampled candidate p/h/fluid-T/thermal-T errors remain inside the unchanged
1e-4 bar / 0.05 kJ/kg / 0.01 K / 0.01 K direct-EOS budgets. These aggregate
maxima do not establish improvement at every state. Quality comparisons cover
wet values; dry single-phase quality remains undefined. Wet outlet observations
are preserved, without claiming dry-outlet operation or spatial convergence.
Original/PCHIP maximum direct differences in liquid inventory are approximately
1.54e-7 kg, outlet quality 8.96e-7/8.52e-7 and accumulated heat 0.000503/0.000508 kJ.

## Liquid regression: consequential but not a simple trajectory deterioration

At fixed PH, the documented regression persists in the transient. Initial
temperature error is -0.603114 mK original versus -1.140942 mK PCHIP; at 0.1 s,
each path evaluated against EOS at its own recorded PH gives approximately
-0.836614 versus -1.257018 mK. No compensating correction or branch change.

Against the independently evolved **same M/U physical inventory**, the result
differs because true EOS pressure and enthalpy are themselves different from
the interpolated recovery. Final errors are nearly identical between meshes:

| 0.1 s liquid result | Original | PCHIP |
| --- | ---: | ---: |
| Maximum fluid-T error | 0.710158 mK | 0.296593 mK |
| Maximum thermal-node T error | 7.4293 µK | 1.5135 µK |
| Bulk pressure error | about +0.032550 bar | about +0.032622 bar |
| Enthalpy error | about +0.00614393 kJ/kg | about +0.00617616 kJ/kg |
| Accumulated heat-transfer error | 3.7150e-5 kJ | 7.7162e-6 kJ |
| Total heat transferred | 0.05925569 kJ | 0.05928512 kJ |

Direct-EOS transferred heat is 0.05929284 kJ. The candidate changes accumulated
heat by approximately 2.9434e-5 kJ (0.050% of the original), improving its EOS
agreement. Pressure and enthalpy errors worsen by approximately 7.2e-5 bar and
3.22e-5 kJ/kg. All cells remain liquid, total liquid inventory stays approximately
1.583330437 kg, with only conservation-roundoff differences. There is no actual
outlet flow in this sealed probe; its reported port-PH quality is a diagnostic
only, not an operational outlet. Port-quality differences are about 2.52e-8.

The compressed-liquid pressure discrepancy is **already present at t=0 in both
paths**, +0.022832154 bar, and grows to about 0.033 bar. Both fail the established
1e-4 bar absolute EOS pressure budget when applied to this diagnostic. This is
not a candidate-induced domain or convergence failure and is not declared a
qualified new fixture. At the initial PH, table density differs from EOS by
-4.4267 ppm and specific U by approximately -2.74e-5 kJ/kg. Small constitutive
differences can have appreciable pressure effects in compressed-liquid M/U
recovery. A temperature-only change leaves those density/energy approximations
untouched at fixed PH. Their detailed contribution is not fully separated here.

Thus the liquid PH regression genuinely affects heat input and state evolution,
but does **not** produce worse temperature/heat-transfer accuracy in this one
matched-inventory transient. It still worsens PH accuracy and slightly worsens
bulk p/h accuracy. The comparisons hold different independent state variables
fixed; neither can replace the other. No general liquid qualification follows.

## Conservation and computational cost

Independent signed-ledger accounting verifies per-cell/global mass <1e-8 kg,
fluid/node/combined energy <1e-6 kJ, along with the original fluid nonlinear
1e-11 and thermal-closure 1e-12 K criteria. Worst per-cell mass is 3.511e-11 kg,
per-cell fluid energy 1.801e-8 kJ, node energy 4.689e-12 kJ and combined energy
5.528e-9 kJ. Canonical density/internal-energy recovery criteria remain unchanged.
No accepted-state/domain stops occur. No ledger, rollback or acceptance rule is
changed. Full failure-injection/control/browser qualification is not claimed.

Resolved 0–150 s work, original → PCHIP:

| Measure | Five | Nine |
| --- | ---: | ---: |
| Accepted trials (two installed half steps each) | 2359 → 2328 | 2418 → 2391 |
| Rejected trials | 459 → 416 | 354 → 322 |
| Actual Newton-failure trials | 382 → 354 | 249 → 227 |
| Newton iterations / linear solves | 68258 → 66036 | 76852 → 75211 |
| Residual evaluations | 1524192 → 1473942 | 2943377 → 2879551 |
| PH calls | 4273403 → 4133734 | 8320846 → 8136875 |
| Explicit saturation calls | 4481603 → 4338199 | 8706208 → 8516603 |
| M/U/V calls | 112300 → 110105 | 207486 → 204156 |
| Observed integration/record runtime | 47.836 → 46.714 s | 115.032 → 115.676 s |

Property counters count actual public engine calls including attempts, separately
from residual calls; they do not count each private interpolation/bisection inside
a PH/MUV call. Both methods use the same counters. Newton failures are identified
from recorded solver rejection classification and finite nonlinear residual;
other solver failures are zero. Temporal rejections are 77→62 / 104→94;
event rejections 0→0 / 1→1; domain rejections zero.

Residual work decreases 3.30%/2.17%, but the nine-section elapsed time increases
0.56%. One long run per configuration is insufficient to claim a runtime gain or
estimate variability. Opposite original/candidate ordering is used across meshes;
no concurrent numerical job runs during these measurements. Timings include
identical diagnostic traces, integrations and output recording, and exclude
engine/model initialization and final evidence serialization. They are not
production-device performance qualification.

The liquid probe has nine accepted trials, zero rejected/Newton-failure trials
in every case. Five iterations/residuals are 109/2452 → 111/2496; nine are
111/4272 → 109/4196. Five interleaved measured pairs per mesh after one warm pair,
same Node process and unchanged workload, give original/PCHIP median runtimes
186.984/185.263 ms (five), 341.699/332.934 ms (nine). Ranges are broad:
133.378–273.159 / 106.717–238.264 ms and
191.008–363.854 / 195.942–361.045 ms. No robust speed advantage is established.
An earlier pilot timing set overlapped environment inspection and is retained
but excluded; reported `timing-clean` runs have no concurrent workload.

## Interpretation and next decision

The extended event improves for a physically meaningful reason: the saturation
temperature bias no longer accumulates the same heat-transfer error. Improvement
also appears in thermal states, fluid temperature, inventory and enthalpy, not
just the event clock. Pressure accuracy and runtime do not improve uniformly.

The candidate has consistent saturation/PH/PT/MUV temperature anchors and unchanged
h/quality phase definitions within its approximate EOS. This does not make it a
fully thermodynamically consistent approximation. The previous property study's
liquid PH gate remains failed, and this study exposes a pressure-accuracy issue
in compressed-liquid recovery already shared by the original path. Conservation
alone cannot certify property fidelity.

**Recommendation: retain PCHIP as unqualified evidence and seek a focused joint
property-consistency design/audit before the full Stage 2B matrix.** Investigate
how temperature, enthalpy and density interpolation and PH/MUV recovery can remain
coherent across saturation and liquid branches using immutable samples and
unchanged physical balances. Do not apply a liquid temperature compensation,
change initialization to improve clocks, restrict phase definitions, relax the
property/pressure gate or assume these two cases establish general qualification.
Any new property method needs separate approval. A full qualification matrix is
premature until the intended liquid-accuracy/consistency contract is resolved.

Warm startup, feed/load disturbances, heat reversal, additional durations,
optional A1/A2 combinations, full temporal/cap refinement, rollback/control/domain
and Chromium/WebKit suites remain required for any later qualification. No
broader BE scenario, next milestone or application integration starts here.

## Files, evidence and reproduction

Only four new files:
`pchip-trajectories.cjs`, `pchip_trajectory_reference.py`,
`audit_pchip_trajectories.py`, `PCHIP_TRAJECTORY_INVESTIGATION.md`.
Evidence lives separately in `/tmp/ammonia-pchip-trajectory-evidence/`.
`audit.json` states **evidenceAuditPassed=true, candidateQualified=false**;
individual files retain work, phase histories, initialization, state samples,
warnings and timings. The prior failed exact-clock diagnostic assertion is
preserved: duration arithmetic produced 0.010000000000000002 s. Only the new
script's clock check was corrected to four machine epsilons; no scientific
acceptance tolerance or solver timestamp was altered.

Node 22.23.3, Python 3.12.14, CoolProp 7.2.0, SciPy 1.16.2, NumPy 2.5.3;
Linux 6.18.44, Intel Xeon Platinum 8573C, two-CPU quota. Use the pinned runtimes
and repository root; output paths must be separate from preserved evidence:

```sh
NODE=/tmp/ammonia-stage2b-runtime/node-v22.23.3-linux-x64/bin/node
PYTHON=/tmp/ammonia-stage2b-runtime/python/bin/python
OUT=/tmp/ammonia-pchip-trajectory-replay
mkdir -p "$OUT"
for pair in '5 five' '9 nine'; do
  set -- $pair
  "$NODE" experiments/dx-fv/pchip-trajectories.cjs extended "$OUT/extended-$2-linear.json" "$1" linear
  "$NODE" experiments/dx-fv/pchip-trajectories.cjs extended "$OUT/extended-$2-pchip.json" "$1" pchip-log-pressure
  "$NODE" experiments/dx-fv/pchip-trajectories.cjs extended "$OUT/extended-$2-pchip-tight.json" "$1" pchip-log-pressure 1e-7
  "$NODE" experiments/dx-fv/pchip-trajectories.cjs liquid "$OUT/liquid-$2-linear.json" "$1" linear
  "$NODE" experiments/dx-fv/pchip-trajectories.cjs liquid "$OUT/liquid-$2-pchip.json" "$1" pchip-log-pressure
  "$PYTHON" -B experiments/dx-fv/pchip_trajectory_reference.py liquid "$OUT/liquid-$2-eos-coarse.json" "$1" "$OUT/liquid-$2-linear.json" 1e-8 .01
  "$PYTHON" -B experiments/dx-fv/pchip_trajectory_reference.py liquid "$OUT/liquid-$2-eos-fine.json" "$1" "$OUT/liquid-$2-linear.json" 1e-10 .005
  # Run timings separately, with no other numerical/environment task running.
  "$NODE" experiments/dx-fv/pchip-trajectories.cjs liquid-timing "$OUT/liquid-$2-timing-clean.json" "$1" linear
done
"$PYTHON" -B experiments/dx-fv/pchip_trajectory_reference.py extended "$OUT/extended-nine-eos-fine.json" 9 /tmp/ammonia-stage2b-evidence/nine-fresh-reference.json 1e-10 .025
# The pre-investigation manifest belongs to the saved candidate snapshot.
"$PYTHON" -B experiments/dx-fv/audit_pchip_trajectories.py \
  /tmp/ammonia-pchip-trajectory-evidence /tmp/ammonia-pchip-trajectory-evidence/audit.json
```

Original saved/frozen EOS comparisons, new reference convergence, independent
accounting, targeted temporal checks, default-prefix equivalence, syntax checks
and `git diff --check` pass. The property gate and liquid absolute EOS pressure
gate do not pass. These failures remain explicit. No full qualification or hosted
CI run is claimed. Report/evidence archives are outside Git; workspace retention
is not guaranteed. Stop for review before further methods or qualification.
