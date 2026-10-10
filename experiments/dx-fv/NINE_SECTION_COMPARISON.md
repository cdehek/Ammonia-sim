# Controlled 3/5/9-section comparison

## Recommendation and limits

Retain **five sections as the interim performance baseline** and **nine as the isolated accuracy reference** for further physical-model work. Three remains the historical screening baseline. No tested count is demonstrated sufficient for charge, distributed liquid inventory or startup phase timing. Nine is not a converged truth and is not being connected to Live Plant.

Steady outlet intensive variables change much less than inventory and startup timing. Sufficiency therefore depends on the observable and a declared tolerance: agreement between these meshes is evidence of resolution sensitivity, not an error bound against the continuum or real equipment. Another mesh could help numerical order assessment, but this stage does not authorize 17 or more sections. The next recommended development is a separately approved thermal-boundary/model design, rather than automatically increasing resolution or adding a trip.

Restore point `7bf0c326414a7d8b7e51f553a273a0041fe1e827` is retained as an unchanged ancestor. All work is confined to experimental tests, diagnostics, references, documentation and the experimental CI workflow. The evaporator, solver, thermodynamic recovery, conservation modules, property table, Live Plant, UI, equipment profiles, production files, main and PR #3 are unchanged. No branches are merged.

## Matched physical-system contract

All three meshes have V=0.003 m³, diameter=0.020 m, length=9.5492966 m, Darcy f=0.02, constant viscosity=1e-5 Pa·s and inlet/outlet K=1000/2. Refinement changes cell lengths/volumes and their half-cell boundary/full-cell internal connections, not total length, volume or restrictions. Nine-cell volume is 0.0003333333 m³. Summed linear/quadratic resistances at a homogeneous reference state equal the same full-tube analytic resistance on all meshes. Internal connections add no new local K.

Cold initialization is uniformly 3.5 bar / 500 kJ/kg; warm initialization uniformly 3.65 bar / 1650 kJ/kg. Equal total M/U and uniform spatial initial inventory are asserted, not obtained by redistributing an old mesh. Reservoirs start at 4 bar / 500 kJ/kg and 3.5 bar / 1700 kJ/kg. Total heat and source integrals match exactly: uniform Q/N or the cell integral of q(x)=Q(0.5+x), x∈[0,1].

Original scenarios remain: warm startup (12 kW), cold wet startup (18 kW), 18→12→18 kW at 15/30 s, feed pressure 4→4.3→4 bar at 15/30 s, graded 18 kW startup, and uniform 12/18 kW plus graded 18 kW one-hour runs. Separate **0/6/12 kW warm-source diagnostics** vary only the declared external source; they are not calibration or cross-source spatial-convergence evidence.

Forty-five overlap bins (LCM of 3,5,9) compare conservative piecewise-constant M/U/liquid inventory at common locations. They are an accounting grid, not a 45-cell simulation. Terminal bulk states reside at different centers (x=5/6,9/10,17/18). Their pressure differences do not represent a common physical point. The new diagnostic outlet trace uses the unchanged upwind donor enthalpy at the common imposed 3.5-bar port, with T/quality/superheat recovered from the existing EOS. It adds no dynamic outlet state or vapor selection. Unsupported trace recovery is marked explicitly, never repaired. Phase-event times below refer to the qualified **terminal-cell saturation crossing**, while common-port wet/dry states are compared in the sampled trajectories. A separate exactly localized port event is not claimed.

Total imposed pressure drop is 0.5 bar (0.8 during increased feed); whole-tube friction-only drop is compared separately. Partial cell-center spans are retained as diagnostics but excluded from claims of pressure-drop convergence.

## Temporal and independent qualification

Adaptive conservative TR-BDF2 uses relative tolerances 1e-6/1e-7/1e-8, step caps 0.5/0.25/0.125 s, and event brackets 0.002/0.0005/0.0001 s on each mesh. A separate 1e-7 run halves only the maximum step. Canonical M/U acceptance, rejection rollback, supported-domain recovery and frozen domain stops remain unchanged. Spatial transient differences use tight 1e-8 runs. Warm comparison outputs are only matched at completed valid shared times; no post-stop continuation is fabricated.

[NINE_RESULTS.json](NINE_RESULTS.json) records exact temporal errors, signed spatial differences, contraction ratios, final inventory fields and solver work. Full trajectories are CI artifacts. Each same-mesh refinement asserts phase sequence/count agreement, bounded state/profile errors and unchanged failure classification.

Independent CoolProp 7.2.0 shooting validates nine discrete steady states; direct-EOS conserved-M/U SciPy 1.16.2 Radau solves validate warm startup and 0/6 kW diagnostics on every mesh, with Radau itself refined from 1e-8 to 1e-10. These references bypass the JavaScript property table and solver. They share the same EOS source and physical closures, so they validate numerical implementation, not experimental equipment accuracy or continuum spatial accuracy.

A fresh reference regeneration is checked against the saved qualified evidence: actual steady/source-diagnostic states are replayed directly; tight-startup bounds use the triangle inequality after a stringent fresh/frozen reference agreement check. This avoids repeating expensive identical trajectories simply to change a reference-file path. Existing historical suites retain their original fresh-reference checks. Four direct-EOS D/U flashes in the expanded reference path needed its existing fixed-density D/T root fallback; recovered internal energy is checked, and this is unrelated to extending the prototype's domain.

## Quantitative spatial findings

The generated tables below use the actual prototype results, not hypothetical finer-mesh extrapolation.

| Heat fixture | Mesh | Total mass (g) | Liquid mass (g) | Port h (kJ/kg) | Port T (°C) | Port superheat (K) | Tube friction ΔP (bar) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 12 kW uniform | 3 | 17.13691 | 8.58749 | 1293.75419 | -5.33846 | 0.00000 | 0.01786246 |
| 12 kW uniform | 5 | 19.15358 | 10.61381 | 1293.81535 | -5.33846 | 0.00000 | 0.01793282 |
| 12 kW uniform | 9 | 20.78903 | 12.25681 | 1293.85652 | -5.33846 | 0.00000 | 0.01798021 |
| 18 kW uniform | 3 | 12.46751 | 4.33730 | 1703.07963 | 36.28586 | 41.62432 | 0.02439615 |
| 18 kW uniform | 5 | 14.37429 | 6.06999 | 1702.82152 | 36.17525 | 41.51371 | 0.02418753 |
| 18 kW uniform | 9 | 15.99838 | 7.57987 | 1702.65109 | 36.10222 | 41.44068 | 0.02404963 |
| 18 kW graded | 3 | 14.95592 | 6.82692 | 1699.68789 | 34.83244 | 40.17089 | 0.02175368 |
| 18 kW graded | 5 | 17.49944 | 9.20400 | 1699.16922 | 34.61031 | 39.94877 | 0.02133932 |
| 18 kW graded | 9 | 19.46682 | 11.06237 | 1698.90082 | 34.49560 | 39.83406 | 0.02112344 |

| Observable | Fixture | Δ3→5 | Δ5→9 | Absolute-change ratio |
| --- | --- | ---: | ---: | ---: |
| Total mass (g) | 12 kW uniform | 2.01667 | 1.63546 | 0.8110 |
| Liquid mass (g) | 12 kW uniform | 2.02632 | 1.64300 | 0.8108 |
| Distribution M L1 (g) | 12 kW uniform | 2.98614 | 2.27257 | 0.7610 |
| Port enthalpy (kJ/kg) | 12 kW uniform | 0.06116 | 0.04117 | 0.6733 |
| Total mass (g) | 18 kW uniform | 1.90678 | 1.62409 | 0.8517 |
| Liquid mass (g) | 18 kW uniform | 1.73269 | 1.50987 | 0.8714 |
| Distribution M L1 (g) | 18 kW uniform | 2.73217 | 2.19360 | 0.8029 |
| Port enthalpy (kJ/kg) | 18 kW uniform | -0.25811 | -0.17043 | 0.6603 |
| Total mass (g) | 18 kW graded | 2.54352 | 1.96739 | 0.7735 |
| Liquid mass (g) | 18 kW graded | 2.37707 | 1.85838 | 0.7818 |
| Distribution M L1 (g) | 18 kW graded | 3.74942 | 2.73963 | 0.7307 |
| Port enthalpy (kJ/kg) | 18 kW graded | -0.51866 | -0.26840 | 0.5175 |

| Terminal-cell phase event | Three (s) | Five (s) | Nine (s) | Δ5→9 / Δ3→5 magnitude |
| --- | ---: | ---: | ---: | ---: |
| cold wet startup: heating | 1.983952 | 1.798686 | 1.611079 | 1.0126 |
| load loss and restoration: cooling | 15.382958 | 15.470447 | 15.540803 | 0.8042 |
| load loss and restoration: heating | 31.096484 | 31.124951 | 31.123073 | 0.0660 (sign reversal) |
| feed increase and decrease: cooling | 15.355830 | 15.428301 | 15.487460 | 0.8163 |
| feed increase and decrease: heating | 30.929367 | 30.979843 | 31.003518 | 0.4690 |
| graded heat cold startup: heating | 2.224739 | 2.014857 | 1.805463 | 0.9977 |

Nine-mesh nominal versus tight maximum errors: 7.62e-6 bar, 0.01438 kJ/kg, 0.00605 K, 76.7 microseconds in phase timing, 2.34e-7 kg inventory-profile L1 and 0.814 microseconds in warm-domain time. Worst hour-long global residuals across all meshes are 2.65e-9 kg and 8.49e-7 kJ; per-cell limits remain 1e-8 kg / 1e-6 kJ.

The five-to-nine total-inventory increases are 8.54% (wet uniform), 11.30% (dry uniform) and 11.24% (graded dry). Liquid-mass increases are 15.48%, 24.87% and 20.19%. These remain too large to establish charge accuracy.



At dry uniform steady operation, common physical thirds contain:

| Mesh | Inlet third M (g) | Middle third M (g) | Outlet third M (g) |
| ---: | ---: | ---: | ---: |
| 3 | 6.319934 | 3.742168 | 2.405404 |
| 5 | 7.448570 | 4.197730 | 2.727990 |
| 9 | 8.719655 | 4.402345 | 2.876378 |

The inlet-third change grows from about 1.129 g (3→5) to 1.271 g (5→9), even though the whole-profile L1 difference falls. Integral/norm contraction therefore does not imply that every physical region is converging at the same rate.

Contraction is |difference 5→9| / |difference 3→5|. A value below one shows a smaller observed change; it does not establish asymptotic order. Non-monotonic signed changes are flagged. Different refinement ratios (5/3 versus 9/5) and phase-front positions further limit order inference. Norms compare distributions, not a single scalar value to which Richardson extrapolation can automatically be applied.

Steady inventory changes diminish but remain material. Cold and graded startup dry times show little reduction in consecutive absolute differences. Some disturbance events improve substantially; the load-restoration event is non-monotonic. Thus a single section count cannot be qualified for every observable from this set. Spatial discretization is the dominant demonstrated numerical difference for inventory and phase timing; the much smaller same-mesh temporal errors cannot explain it.

## Warm-start domain investigation

At 12 kW, three cells recover to a wet terminal and continue; five and nine reach the **existing 250 K-superheat property boundary**, not a compressor/equipment trip. The direct-EOS Radau stop times are 0.272579576 s (five) and 0.259380901 s (nine). Both valid trajectories, accepted inventory/energy, fluxes, local source/advection budgets, original stop cause and time-error evidence are retained. Invalid continuation and unmatched events are excluded from convergence claims.

At 0 kW, all meshes stay supported for the tested 2 s. At 6 kW, three/five remain supported through 2 s, while nine reaches the boundary at approximately 0.525503 s; direct-EOS timing agrees within about 2.4 microseconds. At 12 kW the heat diagnostic's five/nine stop-time errors are about 1.3/0.9 microseconds. This is source sensitivity with identical geometry/initial states/transport, not a change made to force the original test to pass.

Initially Q_i/M_i is about **1468.3 kJ/(kg·s) on every mesh**: volume and heat scaling cancel, so refinement does not inadvertently increase specific heating. During blowdown/heating, terminal mass falls. At the five/nine domain stops, last-cell mass is about 0.836/0.464 g and Q_i/M_i about **2870 kJ/(kg·s)**. Local budgets distinguish total energy from energy per mass:

`du_i/dt = [Q_i + (ṁh)_in − (ṁh)_out − u_i(ṁ_in−ṁ_out)] / M_i`.

The source term remains positive as M_i decreases. Total U_i can decrease through outflow while u_i and T_i rise. There is no unexplained mass removal or forced vapor space. Coarse upwind mixing brings cold-feed influence downstream earlier and can soften the hot pulse; the finer model exposes the low-inventory prescribed-heat excursion. Independent integration confirms the discrete-model behavior, not a real equipment overtemperature.

The model has no wall energy state, no air-side temperature/UA feedback, no phase slip and no momentum inertia. Prescribed heat does not diminish or reverse when refrigerant becomes hotter than an unspecified heat source. Missing wall storage removes thermal inertia; homogeneous equilibrium/upwind advection and quasi-steady resistances govern the front and blowdown. Those omissions are **structural**, not timestep errors. Their individual quantitative effects cannot be separated while deliberately retaining the same physical assumptions; new wall/air/transport states and qualified data would be required. This stage measures heat-source and spatial sensitivity and does not claim that adding any particular omitted effect would guarantee recovery.

## Performance and memory

[NINE_COST_RESULTS.json](NINE_COST_RESULTS.json) contains three fresh-process repetitions per mesh of five simulated cold-start seconds in 0.1-s calls. Node process maxRSS includes the property table, modules, JIT and temporary allocations. Forced GC measures retained heap separately; it does not affect the integration physics. Serialized state bytes are not total JS object memory. Local concurrent workloads make elapsed time observational; hosted measurements are the release evidence.

Local Node medians were approximately 1.04/1.61/2.08 s for 3/5/9, with peak process RSS 65.1/64.1/82.5 MiB and retained heaps approximately 7.8 MiB each. Persistent state serialization was 2997/4153/6486 bytes. Nine-cell memory use is practical in this isolated test, but complete-circuit/UI/device memory is unmeasured.

Local Chromium startup medians were approximately 484/795/1638 ms, making nine about 2.06× five; a nine-cell 0.1-s call reached about 287 ms. One-hour nine-cell wet/dry runs took approximately 4.6/7.6 s in that concurrent local run. Shared-browser sampled Chromium JS heaps reached about 27 MiB; these are not isolated per-mesh peaks. WebKit does not expose that heap API and is reported as unavailable, not zero. Fresh-process Node maxRSS provides the controlled memory comparison. The hosted Chromium/WebKit artifact reports exact platform-specific timing/work/heap measurements.

Across matched nominal cold/load/feed/graded cases, nine requires 1.73–1.84× five's residual evaluations and about 1.02–1.08× its Newton iterations. This separates larger derivative/linear-system work from nonlinear iteration count. The nine-cell warm case is not a matched-duration cost comparison: it stops early. Its tight 1e-8 qualification used about 841,000 residual calls versus 70,720 nominal; these offline settings are deliberately expensive.

Nominal nine-cell throughput can exceed real time in these fixtures, but hundreds-of-milliseconds synchronous startup calls are not responsive main-thread work. Nine is computationally plausible as a background/isolated component, not demonstrated practical for an iPad-connected full circuit. Worker/bounded scheduling and physical-device checks belong to a separately approved integration stage. Tight offline 1e-8 reference trajectories cost much more than nominal 1e-6 browser runs; they are validation settings, not proposed UI playback settings. No universal steady-state slowdown ratio is assumed because Newton iteration counts differ.

## Next-stage recommendation

Before another automatic mesh increase or circuit coupling, propose an isolated **energy-conserving wall/air thermal-boundary model** with explicit initial thermal states and independently qualified parameters. Design wall heat storage and air-side driving-temperature feedback, audit homogeneous/slip and pressure closures, and define acceptance tolerances separately for outlet intensives, charge, liquid distribution and phase timing. Adding that physics requires fresh approval and is not implemented here.

Retain 3/5/9 comparisons when evaluating a future approved physical model. Five provides an economical baseline; nine is useful for checking sensitivity. If charge accuracy remains the primary target, a separately approved finer comparison may still be necessary after thermal assumptions are qualified. Neither an arbitrary level shutdown nor extension of property limits is justified by these results.

## Reproduce and verify

```sh
node experiments/dx-fv/resolution-test.cjs /tmp/dx-resolution.json
node experiments/dx-fv/warm-domain-test.cjs /tmp/dx-warm.json
node experiments/dx-fv/resolution-cost.cjs /tmp/dx-cost.json
python experiments/dx-fv/generate_spatial_reference.py /tmp/dx-reference.json 3,5,9
node experiments/dx-fv/resolution-reference-check.cjs /tmp/dx-resolution.json /tmp/dx-warm.json /tmp/dx-reference.json /tmp/dx-reference-check.json
node experiments/dx-fv/resolution-browser.cjs /tmp/dx-browser.json
```

Pinned dependencies remain CoolProp 7.2.0, NumPy 2.5.3, SciPy 1.16.2 and the repository Playwright version. Comparison fixture guards reject unapproved meshes before instantiating them. The CI workflow preserves all old numerical, reference, browser-application and source/build checks, adds the new comparisons and uploads diagnostic artifacts even when the nine-section job fails.
