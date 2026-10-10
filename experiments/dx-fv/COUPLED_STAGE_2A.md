# Stage 2A — initial five-section coupled DX thermal prototype

Starting restore commit: `dd0ca33cc834e2056ebede756f8cf59ed1157a07`. Standalone thermal restore: `f3bd30a216e1165bad675dafd4ad6726af8567c8`. Every earlier milestone and frozen scientific reference remains an unchanged ancestor/file. The final Stage 2A restore SHA is reported in the delivery message; a commit cannot contain its own SHA.

## Authorized scope and physical closure

This is a separate factory, `createCoupledModel(engine, options)`, under `experiments/dx-fv/`. It permits exactly five refrigerant cells, five tube nodes, five fin nodes and one finite-air node. Five remains a provisional working mesh; neither the preserved five- nor nine-section prescribed-heat mesh is spatially converged. It does not alter `evaporator.cjs`, its historical prescribed heat, any existing solver/property/hydraulic module, the standalone thermal network or its tests/references. Production, main, PR #3, Live Plant, UI, profiles, controllers and application behavior are unchanged. Nine-section coupled work, extensive operating qualification and integration/performance decisions remain Stage 2B and are not authorized by this milestone.

The original bore, volume, connections, donor-density resistance relation and signed bulk-donor enthalpy transport are reused unchanged. The historical heat inputs are **not** also applied: this factory's inherited `heatKW` is identically zero and cannot be changed through its boundary API.

All illustrative Stage 1 material/geometry/capacity assumptions remain the same. Tube/fin capacity and area use physical length fractions. The finite air has fixed mass 6 kg, fixed volume 5 m³ and internal-energy capacity 4.308 kJ/K using cv; it remains dry and perfectly mixed. It is not a constant-pressure refrigerated room. Convection remains the illustrative fixed forced-convection 50 W/(m²·K), without an inferred velocity/fan/correlation, fin efficiency, ventilation, humidity, frost or axial conduction.

The newly active **total effective, uncalibrated constant conductance** is `G_tr=0.60 kW/K`, distributed by physical length (`0.12 kW/K` per refrigerant cell). It relates lumped tube temperature to bulk refrigerant temperature, incorporating unresolved radial/film resistance. The separately reported radial-wall conductance is not added in series again. There is no phase-dependent conductance, dryout correction, artificial phase selection or suction-protection trip. Zero conductance is permitted solely for limiting-case verification; other values and coupled meshes are rejected.

For each cell, `Q_tr = G_tr*(T_tube - (T_refrigerant_C + 273.15))`. The Celsius/Kelvin conversion is explicit. One signed stage value/integral is added to refrigerant U and subtracted from tube energy. Negative heat transfer is physical reversal, not a clipped exception.

The differential balances are:

* Refrigerant M: unchanged signed adjacent mass-flux difference.
* Refrigerant U: unchanged signed adjacent enthalpy-flux difference plus Q_tr.
* Tube E: air-to-tube plus fin-to-tube minus Q_tr.
* Fin E: air-to-fin minus fin-to-tube.
* Air E: declared external load minus all air-to-metal transfers.

The combined energy change equals inlet/outlet signed enthalpy transport plus external air load. Every internal heat link cancels. There is no additional friction heat sink/source, hidden refrigerant reservoir, energy correction or temperature clipping. This Stage 2A coupled factory supports finite air only; it does not introduce a prescribed-temperature coupled reservoir.

## Initial cases and interface

The user confirmed these temperatures during implementation:

| Case | Initial refrigerant PH in every cell | Tube / fin / air K | External air load |
| --- | --- | --- | --- |
| Cold | 3.5 bar absolute / 500 kJ/kg | 273.15 / 273.15 / 278.15 | 1 kW |
| Warm | 3.65 bar absolute / 1650 kJ/kg | 293.15 / 293.15 / 293.15 | 1 kW |

Default inlet/outlet reservoirs remain 4 bar / 500 kJ/kg and 3.5 bar / 1700 kJ/kg. Default construction selects the approved cold configuration. Both startups are qualified through 120 s. Separate 60 s initial cases apply air load 1→2→1 kW or inlet pressure 4→4.3→4 bar at exactly 15/30 s. Sealed heat reversal starts warm refrigerant against the approved cold metal/air, using the original closed-face behavior, and observes transfer reversal over 60 s. It is an isolated conservation fixture, not a new shutdown controller.

```js
const engine = require('../../engine').createEngine(require('../../properties.json'));
const {createCoupledModel} = require('./coupled-model.cjs');
const {fixture} = require('./coupled-fixtures.cjs');
const model = createCoupledModel(engine);
const state = model.create(fixture('warm'));
const result = model.advance(state, 120);
```

The API exposes `create`, uncommitted `trial`, `advance`, atomic `update`, `record` and settings. Updates permit supported inlet/outlet PH states and finite external air load only. Capacities, geometry, mass, energy, topology, conductance and reference convention cannot be reset through updates. Scheduled patches are validated before creation and become visible at an advance ending exactly on the transition. No accepted interval straddles a scheduled change.

Tube/fin temperature profiles retain the Stage 1 physical-energy integral initialization. Arbitrary thermal reporting references never enter canonical energy, heat transfer, conservation residuals or error norms. Refrigerant thermodynamic reference conventions remain unchanged.

## Joint implicit numerical system

Canonical states are refrigerant M/U/fixed V plus thermal energies anchored computationally at 273.15 K. The 21 nonlinear coordinates are ten pressure/enthalpy coordinates and eleven thermal-energy increments. `coupled-implicit.cjs` is a new variable-aware damped Newton solver. Pressure, enthalpy and energy columns use their own perturbations, with fluid derivative samples inside the current constitutive branch. The original alternating-PH Newton solver is untouched.

Every stage evaluates all hydraulic and thermal rates at current stage states. TR-BDF2 uses gamma `2-sqrt(2)` and the established positive shared quadrature weights. Every solved stage independently recovers PH from M/U/V and checks consistency with its solve coordinates. Full-step and both half-step candidates must pass recovery before acceptance. The accepted two halves are prepared against detached ledgers/events, then installed together; there is no extrapolation or split refrigerant/thermal advance.

Exact PH evaluations are cached only within a single stage at identical pressure/enthalpy pairs. This avoids repeating unchanged property work for thermal-column probes; it does not lag properties, reuse changed states or modify the property table. Residual-evaluation counters count nonlinear calls, not individual EOS/property calls.

Adaptive controls retain the original refrigerant M/U/PH absolute-plus-relative scales and maximum component norm. Thermal energies use `C*(temperatureAbsoluteK + rtol*50 K)`. Nominal rtol is 1e-6 and absolute temperature tolerance 1e-4 K, with maximum trial 0.5 s and minimum retry 1e-9 s. Tight/reference settings refine tolerance, maximum step and phase-crossing brackets separately. There is also a same-tolerance 0.025 s maximum-step comparison.

Nonlinear fluid balance tolerance remains 1e-11 in the established scaled residual. Thermal nonlinear closure has a separate **absolute 1e-12 K residual budget**; the adaptive 50 K scale is not used to excuse unresolved late-relaxation exchanges. The iteration limit is 30, and ordinary failed trials reduce the step. Fixed-step backward Euler supplies a first-order comparison; TR-BDF2 supplies the expected second-order smooth-fixture comparison.

Stops distinguish numerical solver failure, temporal-accuracy exhaustion and independently corroborated supported-domain exit, with refrigerant/thermal source evidence. Every stage remains in the original bounded property domain and thermal 200–400 K support. A failed PH probe does not alone prove a physical exit. Exhausted small-step conservative direction checks run regardless of the numerical failure label; branch-aware Newton may fail without ever making an unsupported probe. These checks corroborate domain evidence without accepting that predictor or charging its heat. An exact thermal boundary with an outward derivative is detected before a tiny residual can fall below the nonlinear tolerance. Stopped states reject edits and freeze further advancement.

Terminal-cell phase events retain the original signed saturation-margin/bracket logic. The outlet-port diagnostic recovers bulk donor enthalpy at the imposed outlet pressure; it is not an additional inventory, vapor selector or protected suction state. Unsupported port diagnostics remain marked. Grazing/multiple crossings within a substep and arbitrary output-batching invariance are not claimed.

## Independent qualification and reproduction

`generate_coupled_reference.py` independently derives geometry/capacities and implements a conserved-state RHS using direct CoolProp D/U recovery and SciPy Radau. It imports no JavaScript/table/integrator. It integrates signed face/link budgets separately and refines rtol 1e-8→1e-10 and step cap 0.1→0.025 s. Scheduled changes split reference integration exactly. Its new `coupled-reference.json` is separate from every prior frozen reference. This independent computational pathway shares the table's CoolProp EOS source and declared closures; it is not independent measured equipment validation.

`coupled-test.cjs` separately reports:

1. JavaScript nominal/tight error versus a tightly resolved same-table run, plus independent maximum-step refinement.
2. Continuous-time direct-EOS reference refinement and JavaScript/direct-EOS trajectory differences, which include table and initialization differences.
3. Pointwise table interpolation errors at the reference's matched PH values. These are not confused with JavaScript temporal error.
4. Per-cell/per-node/global conservation, independently rebuilt heat budgets, exact scheduled input and visible outlet diagnostics.
5. Zero-exchange equivalence to unchanged prescribed-zero-heat refrigerant and standalone thermal models; closed relaxation; equilibrium; signed reversal; fixed-step order; reference-energy invariance.
6. Solver/accuracy/domain stops before and after accepted ledgers, injected second-half recovery failure, atomic mixed edits, frozen states and support/scope guards.
7. Zero-exchange loaded thermal-domain clocks versus the independent Stage 1 matrix-exponential/root reference, at two timestep caps.

`audit_coupled_results.py` is a separate Python standard-library accounting audit. It reconstructs thermal energy changes from temperatures and independently derived physical capacities, and checks signed face/link budgets without importing either numerical solver. `coupled-browser.cjs` executes the five initial cases in blank Chromium/WebKit pages, without application/UI integration or a device/performance qualification.

`generate_coupled_domain_reference.py` separately checks the sealed saturated-vapor pressure-edge direction using direct EOS. At 35 bar with 400 K metal, the paired 0.12 kW/K cell exchange sends its 1-microsecond diagnostic to approximately 35.000030073 bar. This beyond-grid value is diagnostic evidence only, never runtime state or a property-domain extension. The new separate `coupled-domain-reference.json` freezes that reference.

```sh
node experiments/dx-fv/coupled-test.cjs /tmp/coupled-results.json
python experiments/dx-fv/generate_coupled_reference.py /tmp/coupled-reference-fresh.json
python experiments/dx-fv/generate_coupled_domain_reference.py /tmp/coupled-domain-reference-fresh.json
DX_COUPLED_REFERENCE_PATH=/tmp/coupled-reference-fresh.json node experiments/dx-fv/coupled-test.cjs /tmp/coupled-fresh-results.json
python experiments/dx-fv/audit_coupled_results.py /tmp/coupled-results.json /tmp/coupled-audit.json
node experiments/dx-fv/coupled-browser.cjs /tmp/coupled-browser-results.json
node experiments/dx-fv/coupled-controls.cjs /tmp/coupled-control-results.json
```

Use Node 22, Python 3.12, CoolProp 7.2.0, NumPy 2.5.3, SciPy 1.16.2 and the unchanged Playwright 1.62.1 installation. Coupled test/browser failures preserve partial evidence in a separate `.failure.json` without suppressing the nonzero exit status.

Acceptance retains per-cell/global mass <1e-8 kg and energy <1e-6 kJ, and applies <1e-6 kJ to each thermal node and combined energy. Nominal temperature errors must be <0.01 K and tight errors <0.001 K, with pressure <5e-5 bar and enthalpy <0.05 kJ/kg for same-table temporal comparisons. Well-conditioned event comparisons must be <1 ms. Direct-EOS comparisons have a separately declared pressure allowance 1e-4 bar for table/closure differences, with temperature <0.01 K, enthalpy <0.05 kJ/kg and event <1 ms. These do not relax historical tests or claim a universal property-table error bound.

## Qualified numerical evidence

The checked-in `COUPLED_RESULTS.json` is the final Node 22.23.3 frozen-reference run: five operating cases at nominal/tight/reference settings and independent step refinement, ten additional checks and seven intentional failure scenarios. A second complete run against freshly generated references passes and is identical after excluding wall-clock timings. Both independent Python reference regenerations reproduce their frozen JSON exactly. `COUPLED_AUDIT_RESULTS.json`, `COUPLED_CONTROL_RESULTS.json`, `COUPLED_BROWSER_RESULTS.json` and `COUPLED_REGRESSION_RESULTS.json` retain the complementary evidence. Earlier failed development results are explicitly unqualified.

| Maximum residual over numerical qualification | Observed | Limit |
| --- | ---: | ---: |
| Combined refrigerant/metal/air energy | 6.05193e-8 kJ | 1e-6 kJ |
| Refrigerant energy | 6.04839e-8 kJ | 1e-6 kJ |
| Individual refrigerant-section energy | 3.37490e-8 kJ | 1e-6 kJ |
| Individual thermal-node energy | 3.26204e-9 kJ | 1e-6 kJ |
| Thermal total energy | 1.32104e-10 kJ | 1e-6 kJ |
| Global refrigerant mass | 1.94237e-10 kg | 1e-8 kg |
| Individual refrigerant-section mass | 9.39833e-11 kg | 1e-8 kg |

The independent Python audit reconstructs 150 operating sample records. Its worst combined residual is 5.44023e-9 kJ, worst thermal-node residual 4.01466e-11 kJ and worst instantaneous Q_tr reconstruction difference 3.43789e-9 kW. The larger full-suite maxima above also include limiting, fixed-step and stop fixtures.

| Error comparison | Pressure bar | Enthalpy kJ/kg | Refrigerant temperature K | Metal/air temperature K | Phase-event seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Nominal versus resolved same table | 1.14579e-5 | 0.00414275 | 0.000764648 | 0.0000492594 | 0.0000512383 |
| Tight versus resolved same table | 3.97475e-6 | 0.000871747 | 0.000265205 | 0.00000994155 | 0.00000193162 |
| Resolved JavaScript versus independent direct EOS | 3.92704e-5 | 0.00627706 | 0.00109364 | 0.0000689377 | 0.0000412584 |

Matched-PH interpolation is reported separately: maximum temperature discrepancy 0.00219264 K, relative density discrepancy 9.60305e-6 and internal-energy discrepancy 0.00122439 kJ/kg. These are sampled errors, not global table bounds. Smooth-fixture TR-BDF2 orders are 2.01275/2.01406; backward-Euler orders are 0.96312/0.98119. The zero-exchange loaded thermal-domain clock agrees with the independent 1566.70261392905 s root to better than 1.4e-9 s for both step caps.

The complete reference-energy regression gives identical physical states, ledgers, accepted timestep traces and rejection traces for all tested reporting references. Supplemental traces across all five nominal cases show maximum accepted normalized errors between 0.80714 and 0.91317, always below one. Valid-first/invalid-second mixed boundary patches leave the entire state unchanged. Forced/injected failures preserve the last accepted inventory, energy, ledgers and events, including a second-half recovery failure after both earlier candidate stages converge. The pressure-edge domain stop is separately corroborated by direct EOS; diagnostic extrapolation is not committed.

At 120 s the imposed-pressure outlet-port quality is **0.1920994 cold / 0.1979679 warm**, temperature 267.81154 K, and superheat zero for both. Both are wet. Warm initially superheated vapor crosses to wet fluid; the independent terminal-cell dry-to-wet time is 1.50138362 s. Outlet-port and terminal-cell diagnostics are distinguished in the JSON.

Chromium 151.0.7922.34 and WebKit 26.5 both execute all five cases and pass conservation/reference/scheduled-transition checks. Their maximum direct-EOS temperature discrepancies are approximately 0.00106 K; terminal-event discrepancies are below 14 microseconds. Local browser libraries were relocated under `/tmp/ammonia-stage1-browser-libs/extracted/usr/lib/x86_64-linux-gnu`, with `LD_LIBRARY_PATH` pointing there and `PLAYWRIGHT_BROWSERS_PATH=/tmp/ammonia-stage1-browsers`. Only Playwright's system-cache host-library preflight was skipped via `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`; both real browser engines and all assertions ran. The hosted existing workflow uses its normal `--with-deps` installation.

Isolated nominal local wall times (single shared runner, including sampled records, not a performance qualification) are 2.52 s cold/120 simulated seconds, 4.38 s warm/120 s, 1.79 s load-step/60 s, 2.20 s feed-step/60 s and **31.22 s sealed heat reversal/60 s**. The reversal requires 962 accepted trials and 922 rejected trials; this is a material nonlinear cost risk, not a failed accepted conservation budget. Cold/warm require 321/444 accepted trials and 5/33 rejected trials. Counters include all attempted nonlinear work. No application realtime or integration decision follows from these measurements.

The independent reference pathway and independent conservation reconstruction qualify numerical behavior. A separate source reviewer is **not yet claimed**: delegation requires explicit user authorization under the active agent instructions, and that question remains pending. The restore commit is therefore a numerically qualified Stage 2A candidate pending that source review and user milestone acceptance.

## Failures, limitations and stage boundary

`COUPLED_DEVELOPMENT_FAILURES.json` retains the initial failed closed-relaxation budget, the wrongly selected forced-accuracy fixture and Node 22 pressure-edge classification failure. The first was corrected by tightening thermal nonlinear closure, without correcting stored energy/ledgers or changing acceptance. The second was a correctly classified coarse Newton failure; the accuracy test now first proves convergence of its linear zero-exchange stages, then verifies temporal rejection at a stricter temperature tolerance. The third removed reliance on encountering an unsupported Newton probe, with the physical direction independently corroborated by direct EOS. Coarse warm 0.5 s stages can still exhaust the iteration budget; adaptive reduction handles those trials. Conservation is independently qualified rather than inferred from solver convergence.

Both approved startups reach 120 s within support, and both outlets are wet there. The warm startup initially has superheated vapor and later crosses to wet fluid. No sustained dry-outlet case is qualified or adopted. The 1 kW air load is not a dry-outlet guarantee; a different dry-case boundary would require independent feasibility analysis and explicit approval before use.

There is no nine-section coupled comparison, hour-long coupled operating qualification, shutdown/restart qualification, performance-based integration decision or full circuit/control model. The existing homogeneous/upwind/quasi-steady hydraulic and property interpolation limitations remain. Finite air and the illustrative constant conductances are uncalibrated approximations. Longer or more extreme inputs may honestly reach support limits; a correctly conserved expected stop is not automatically a failed physical model.

The existing hosted workflow remains unchanged and runs all established application, prescribed-heat, spatial, numerical, browser and standalone thermal checks. It does **not** automatically invoke the new coupled suites; adding that coverage requires separately approved workflow work. Stage 2A delivery ends here and requires user review before Stage 2B or any integration.
