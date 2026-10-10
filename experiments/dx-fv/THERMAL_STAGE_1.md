# Stage 1 — standalone tube/fin/air thermal network

Authorized scope: standalone constant-property thermal storage and numerical qualification only. This stage starts at `5d92e8bd3e4a2ce2e1fdb39c7e4318c22b156654`, preserving spatial milestone `c105584311ca4a539c8410bf02ae0519b2bc8448` and every earlier restore point. It does not couple to refrigerant or change existing DX transport, hydraulics, properties, application/UI, profiles, controllers, main or PR #3. Refrigerant coupling requires separate explicit approval.

## Physical and energy contract

`thermal-geometry.cjs` supplies configurable illustrative inputs and five/nine thermal allocations. `thermal-network.cjs` supplies `createIntegrator(options)`, with `create(config)`, `advance(state, seconds)`, `update(state, boundaryPatch)`, `record(state)` and uncommitted `trial(state, dt)`. Constant positive capacities and active conductances are required. An explicitly disconnected test topology omits links; no zero-capacity dynamic node is permitted. The geometry factory rejects section counts other than five/nine. Small generic networks are numerical test fixtures, not finer coil meshes.

The unchanged refrigerant geometry is only a dimensioning basis: 0.020 m bore, 0.003 m³ volume, 9.5492965855 m length. There are **no refrigerant states or refrigerant heat links**. Proposed future `G_tr=0.60 kW/K` appears only as inactive metadata; active `G_tr=0`.

| Illustrative input or derived quantity | Value |
| --- | ---: |
| Tube outside diameter / wall thickness | 0.024 / 0.002 m |
| Carbon-steel density / specific heat / conductivity | 7850 kg/m³ / 0.470 kJ/(kg·K) / 45 W/(m·K) |
| Tube mass / capacity | 10.362 kg / 4.87014 kJ/K |
| Aluminum fins: count / outside diameter / hole / thickness | 1910 / 0.080 / 0.024 / 0.0002 m |
| Fin density / specific heat / conductivity | 2700 kg/m³ / 0.900 kJ/(kg·K) / 205 W/(m·K) |
| Fin mass / capacity | 4.7177874932 kg / 4.2460087439 kJ/K |
| Exposed fin / bare tube / inner tube area | 17.5692940833 / 0.6911978786 / 0.600 m² |
| Constant illustrative air convection coefficient | 50 W/(m²·K) |
| Total air→tube / air→fin / fin→tube conductance | 0.03455989393 / 0.87846470417 / 2.0 kW/K |
| Air volume / fixed mass / internal-energy capacity | 5 m³ / 6 kg / 4.308 kJ/K |
| Air cv / cp | 0.718 / 1.005 kJ/(kg·K) |

Material numbers are rounded engineering assumptions, not measured/manufacturer data. Fin mass excludes tube holes; exposed tube area excludes fin collars. Effective contact conductance represents unresolved spreading/contact resistance. Fin conductivity is declared material metadata, not a distributed conduction calculation. There is no fin-efficiency correction, axial conduction or phase-dependent heat-transfer correlation.

The air node is dry, perfectly and instantaneously mixed, fixed-volume/fixed-mass ideal-gas sensible storage using **cv**. It is not a constant-pressure refrigerated room. If inferred, ideal-gas pressure is `m/V * (cp-cv) * T * 1000 Pa`, not an airflow boundary or pressure state. The constant coefficient assumes forced convection over the declared exposed areas; no fan, airflow velocity/distribution or correlation is inferred. Ventilation, fan electrical heat, humidity, latent heat, frost and natural-convection fallback are absent.

Each signed link is computed once: `Q = G*(T_from-T_to)`. The same integrated link is subtracted from the source and added to the destination. Reverse heat flow is permitted. A prescribed-temperature reservoir replaces its dynamic node and contributes measured signed external energy; its temperature edits do not reset metal energy. Finite-node loads are explicit external inputs. Closed-network external energy is exactly zero. No hidden sink or energy correction is applied.

## Allocation and initialization

Uniform homogenization represents the physical 1910 fins as 382 equivalents per five-section cell and 1910/9 equivalents per nine-section cell, without rounding. Net volume, mass, capacity, exposed area and radial conductance use identical physical length fractions; their sums remain invariant. The single finite-air node remains unchanged.

An initial tube/fin profile is a temperature or contiguous piecewise-constant bins covering normalized physical `[0,1]`. Each section receives the **integral of energy density over its physical interval**, then recovers temperature. No old cell-center interpolation is used. Constant capacities are the only supported material closure; variable-cp integration/inversion is deferred.

```js
const {createIntegrator} = require('./thermal-network.cjs');
const {createThermalConfig} = require('./thermal-geometry.cjs');
const model = createIntegrator();
const state = model.create(createThermalConfig({sectionCount: 5}));
const result = model.advance(state, 300); // closed relaxation, no G_tr
```

Boundary patches allow node `loadsKW`, existing `reservoirs` temperatures and existing positive `conductancesKWK` only. Capacities, geometry, mass, temperatures, topology, schedule and energy reference cannot be reset through updates. Invalid mixed patches are atomic. A stopped state rejects edits and remains frozen on subsequent advancement.

## Integration, reference invariance and stops

The physical canonical coordinate is thermal energy at a fixed computational anchor 273.15 K. Stage equations solve **energy increments** with the exact constant-C/G Jacobian. Reporting energies use the independently configured arbitrary `energyReferenceK`; changing it never changes canonical energies, physical recovery, fluxes, residual scaling or step decisions. Negative reference energies are valid. Reporting-only large offsets must not be subtracted to form conservation residuals.

Adaptive TR-BDF2 uses gamma `2-sqrt(2)`, paired stage quadrature and full-step versus two-half-step error divided by three. Accepted states are the two halves without extrapolation. Backward Euler is available for independent first-order comparison. Exact linear solves replace nonlinear Newton iterations because the standalone approved equations are linear; existing DX solver/transport files remain unchanged.

Nominal settings: maximum trial 0.5 s, minimum retry 1e-9 s, temperature absolute tolerance 1e-4 K, relative tolerance 1e-6, fixed characteristic temperature scale 50 K, linear residual budget 1e-9 K. The per-node error denominator in energy units is `C*(temperatureAbsoluteK + relativeTolerance*50 K)`. Temperature and constant-capacity energy errors are equivalent; no raw reference-dependent energy magnitude enters the norm. Tight/reference settings independently reduce tolerance and step cap. Fixed-step analytic order tests and a same-tolerance 0.025-s cap refinement qualify temporal behavior separately.

Every implicit stage and both proposed accepted halves must recover within the declared **200–400 K** range before any physical state/ledger/time is committed. Configured test domains may narrow, but never extend, that range. Unsupported candidates reduce the step. Exhaustion distinguishes accuracy, solver and confirmed thermal-domain stops. A domain classification includes the original trial evidence and an independently evaluated outward temperature rate at the last accepted state; unconfirmed numerical failure remains a solver stop. Diagnostic evidence never becomes state or heat input.

Scheduled changes are validated at creation, stop timesteps exactly at their boundary times, and become visible immediately when an advance ends at that time. No accepted interval straddles a scheduled discontinuity. Trial evaluation is pure. Rejection preserves all energies, ledgers, clocks and boundary-event evidence; a stop freezes the last supported state.

## Boundary fixtures and domain interpretation

Initial closed fixture: tube 273.15 K, fins 283.15 K, air 293.15 K. Total capacity is 13.4241487439 kJ/K. Closed equilibrium is approximately 282.7312471906 K.

| Fixture | Duration / expected result |
| --- | --- |
| Closed unloaded relaxation | 300 s; energy-derived equilibrium, no heat sink |
| Finite air +1 kW | 120 s; conservative maximum-temperature bound 321.0051532 K |
| Air load 1→2→1 kW at 15/30 s | 60 s; exact total input 75 kJ |
| Prescribed air reservoir 293.15→303.15→283.15 K at 15/30 s | 60 s; signed external reservoir ledger |
| Connected finite air +1 kW | Request 2000 s; expected supported-domain stop near 1566.702614 s |
| Isolated finite air +1 kW | Exact 400 K boundary at 460.3098 s |
| Isolated finite air −1 kW, initially 273.15 K | Exact 200 K boundary at 315.1302 s |

A finite air/metal network cannot absorb an indefinite positive load within a finite range. The connected 1 kW network must reach a boundary before its energy-weighted mean reaches 400 K (approximately 1574.233181 s). A correctly conserved, refined, evidence-preserving expected domain stop **passes its verification case**. It identifies the supported-model boundary; it is neither an invented equipment trip nor automatic physical-model failure. No unsupported continuation or temperature clipping is permitted.

## Independent qualification and reproduction

`generate_thermal_reference.py` independently assembles temperature-coordinate linear balances and an augmented SciPy matrix exponential, including integrated link/load energies. It imports no JavaScript solver or geometry. Shared declared input assumptions do not make this measured equipment validation. A separate closed-form two-node solution qualifies both flow directions; direct three-node and nonuniform five/nine references qualify larger systems. New frozen thermal references are separate from every historical scientific reference.

Acceptance: per-node/combined residual ≤1e-6 kJ; nominal temperature error <0.01 K, tight <0.001 K; domain-clock comparisons <1 ms for the connected monotone case and <1e-7 s for the exact isolated-air case. The report separates link-integral accuracy from ledger conservation. Reference-energy regression requires identical accepted **and rejected** timestep traces and physical states for references −1,000,000 / 273.15 / +1,000,000 K.

```sh
node experiments/dx-fv/thermal-test.cjs /tmp/thermal-results.json
python experiments/dx-fv/generate_thermal_reference.py /tmp/thermal-reference-fresh.json
DX_THERMAL_REFERENCE_PATH=/tmp/thermal-reference-fresh.json node experiments/dx-fv/thermal-test.cjs /tmp/thermal-fresh-results.json
node experiments/dx-fv/thermal-cost.cjs /tmp/thermal-cost-results.json
node experiments/dx-fv/thermal-browser.cjs /tmp/thermal-browser-results.json
```

Use the established independent-reference environment: Python 3.12, NumPy 2.5.3, SciPy 1.16.2; legacy references additionally need CoolProp 7.2.0. Browser harnesses use the unchanged Playwright 1.62.1 dependency. All existing application numerical/browser, prescribed-heat, temporal, spatial, warm-domain, frozen/fresh reference, cost and deterministic build checks remain required and unchanged. The existing CI workflow is preserved; it does not automatically invoke the new thermal commands. Adding thermal CI steps outside this directory requires separate approval.

Numerical results are in `THERMAL_RESULTS.json`, fresh-reference agreement and historical regression evidence in `THERMAL_REGRESSION_RESULTS.json`, and observational cost in `THERMAL_COST_RESULTS.json` / `THERMAL_BROWSER_RESULTS.json`. Performance includes fresh-process Node peak RSS/retained heap/state bytes and Chromium/WebKit timing; it makes no iPad, main-thread UI or coupled-refrigerant performance claim.

## Qualified numerical results

| Check | Observed result |
| --- | --- |
| Independent matrix-exponential temperature error, nominal / tight / reference | 0.000639705 / 0.000144980 / 0.0000325313 K maximum |
| Same nominal tolerance, independent 0.025-s step cap | 0.0000685887 K maximum |
| Independent two-node analytic heat exchange, either direction | 0.000657319 K maximum |
| Combined / per-node conservation residual | 1.76442e-10 / 3.31966e-11 kJ maximum |
| Nominal integrated-link trajectory error versus expm | 0.001090252 kJ maximum; distinct from conservation residual |
| Fixed-step TR-BDF2 observed order | 2.00459 / 2.00224 |
| Fixed-step backward-Euler observed order | 0.98812 / 0.99402 |
| Connected 1 kW supported-domain clock error versus expm/root | Below 3.7e-10 s on both meshes |
| Isolated heating/cooling domain clocks | Within 1.4e-9 s of exact solution |
| Allocation and arbitrary energy-reference checks | Passed, including physical nonuniform energy integrals and identical accepted/rejected traces |

All nominal/tight/reference/max-step cases pass without relaxing the contract. Expected domain stops retain the supported energies and ledgers; separate forced accuracy/solver/domain cases verify full rollback and frozen evidence. Domain-clock agreement in these simple monotone linear fixtures is not a universal event-timing guarantee.

Historical qualification reran all 13 numerical suites, 16 Chromium suites, seven WebKit suites, frozen/fresh prototype and time references, frozen/fresh three/five spatial validation, 3/5/9 validation and fresh reference replay, warm-source diagnostics, all existing isolated browser/cost harnesses and deterministic build checks. The initial concurrent WebKit run failed the unchanged `training-ui.cjs:34` pause-button assertion; a complete unchanged rerun passed all seven suites. This failure is recorded, not attributed conclusively to host contention or hidden by changing assertions. No application change was made.

Browser setup used temporary rootless system libraries. The Playwright system-library-cache preflight was bypassed because relocated libraries are absent from the system cache; actual WebKit/Chromium execution and every test assertion still ran. Cost samples ran on a shared host and show scheduling/JIT variability. These environmental details and raw measurements are retained in the regression/cost reports.

This milestone ends after validated standalone delivery. No subsequent coupling, parameter calibration or transport change is implied.
