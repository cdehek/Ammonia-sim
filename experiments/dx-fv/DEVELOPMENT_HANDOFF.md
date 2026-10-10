# Ammonia Lab — development handoff through accepted Stage 2A-CI

**Current status:** the user formally accepted Stage 2A as a **numerically qualified, isolated five-section coupled DX thermal research milestone**, including its documented physical and computational limitations. Qualified source/CI restore: **`adbab1d5587471105a351f3467e0bb812effb148`** on **`experimental/dx-fv-stage-3`**, repository **`cdehek/Ammonia-sim`**. [Accepted hosted CI](https://github.com/cdehek/Ammonia-sim/actions/runs/38069836624) passed all four jobs and every added coupled step.

Current authorization is **documentation and conversation handoff only**. No solver optimization, reference/table change, Stage 2B, new boundary adoption, calibration or application integration is authorized. This document supersedes obsolete approval/CI statements in earlier stage reports; those reports remain unchanged historical evidence. The new documentation commit's exact SHA is supplied in delivery because a commit cannot contain its own SHA. Use that delivered SHA to retrieve this handoff, and the qualified SHA above to identify the accepted implementation.

## Repository and immutable restore points

All experimental milestones below are preserved ancestors. Inspect restores in a disposable detached checkout; never reset or force-push a live branch. Recheck actual remote refs before work: application refs are a snapshot, not permission to move them.

| Restore | Exact SHA | Meaning |
| --- | --- | --- |
| Production/main v0.5.0 | `0473d32f62db992fde0f581d116e1bd0c8e7d8ed` | Protected application baseline |
| Reviewed v0.5.5 release candidate | `e86da1975dd177248a78d40c114bf76123c173ea` | Protected reviewed source |
| PR #3 / preview trigger | `d4422425750a1d3c4e432cc103ac42ead40b7cc6` | Open, unmerged; same source tree as reviewed RC |
| Original three-section backward-Euler DX prototype | `f7b19adb67587d88195d53cee6081c8b014fb9ed` | Frozen prescribed-heat baseline |
| Adaptive TR-BDF2 temporal qualification | `3e2cdbf1c8e1c9c42268a72bda5b0d05cf54f0f5` | Conservative temporal milestone |
| Three/five-section scientific comparison | `52fbb7765a9edd07693116a14172c86fc5f8b34a` | Preserved intermediate scientific commit |
| Completed three/five-section restore | `7bf0c326414a7d8b7e51f553a273a0041fe1e827` | Includes retained application browser coverage |
| Completed three/five/nine spatial milestone | `c105584311ca4a539c8410bf02ae0519b2bc8448` | Provisional five-section baseline; nine comparison |
| Pre-thermal documentation handoff | `5d92e8bd3e4a2ce2e1fdb39c7e4318c22b156654` | Original thermal-design transition |
| Standalone tube/fin/air Stage 1 | `f3bd30a216e1165bad675dafd4ad6726af8567c8` | Uncoupled thermal restore |
| Standalone thermal Stage 1 CI | `dd0ca33cc834e2056ebede756f8cf59ed1157a07` | Frozen/fresh and Chromium/WebKit qualification |
| Initial coupled Stage 2A candidate | `aa9514b0338b6021d9afc4b9f47f88ebdde765da` | Independently source-reviewed candidate |
| Source-review correction and diagnostics, Stage 2A-R | `563ce0fdf99a10991e474121ef9719753f059d9d` | Accepted classification fix; preserved diagnostic evidence |
| Hosted coupled qualification, Stage 2A-CI | **`adbab1d5587471105a351f3467e0bb812effb148`** | **Formally accepted Stage 2A research milestone** |

See [RESTORE_POINTS.md](RESTORE_POINTS.md) for historical CI links. PR #3 is https://github.com/cdehek/Ammonia-sim/pull/3 . Reviewed RC/preview tree: `eda93677513ef420d11008e38255159fd3986578`.

## Project context and protected boundaries

Ammonia Lab is a browser-based ammonia refrigeration simulator for learning and research, with eventual equipment-informed simulation as a future objective. The generated standalone application is `index.html`; runtime units are canonical, with Fahrenheit/psig UI defaults. `engine.js` and `properties.json` supply bounded real-fluid properties. Older dynamic and connected-inventory models, valve/compressor controls, equipment profiles, Live Plant, schematic, history and training remain separate application components. `tools/build.py` embeds application source/data and produces validation reports.

The historical connected DX core selects vapor into an outlet inventory; its known liquid-accumulation/transport failure has **not been fixed in Live Plant by this isolated experiment**. Experimental numerical acceptance is not application integration or approval of Default behavior. Preview deployment is not evidence that application code imports the research model.

During the current handoff, only this file, experimental `README.md` and `RESTORE_POINTS.md` may change. Preserve all other experimental source/tests/fixtures/references/reports and `.github/workflows/dx-fv-experiment.yml`. Protected application files include `engine.js`, `properties.json`, `dynamic-engine.js`, `storage-engine.js`, `valve-engine.js`, `capacity-controller.js`, all other root application engines/controllers, initialization and equipment-profile/schema files, `src/`, `tests/`, `tools/`, `index.html`, `validation.json`, `integration-validation.json`, package files and application workflows. Main, production, PR #3, Live Plant, UI, Default and all profiles/controls remain protected. No merges or finer-than-nine spatial studies are authorized.

## Validated architecture: three separate layers

**Historical prescribed-heat DX:** `conservation.cjs`, `thermodynamics.cjs`, `hydraulics.cjs`, `implicit.cjs`, `time-control.cjs` and `evaporator.cjs` remain unchanged. Refrigerant physical inventories are M (kg), U (kJ), fixed V (m³), with `U=M*h-100*p*V` for p in bar absolute and h in kJ/kg. PH are solve coordinates; canonical recovery uses M/U/V. Signed face mass and bulk-donor enthalpy fluxes are computed once and applied oppositely to neighbors. Liquid, mixture and vapor are transported without artificial vapor selection.

Hydraulics retain the horizontal homogeneous-equilibrium, quasi-steady low-Mach closure `ΔP=a*ṁ+b*ṁ*abs(ṁ)`, where `a=128*μ*L/(π*D^4*ρ)` and `b=(f*L/D+K)/(2*ρ*A²)`. Resistance uses Pa, with explicit bar conversion. Donor density follows flow direction. Boundary half-cell/internal full-cell lengths, μ=1e-5 Pa·s, Darcy f=0.02 and inlet/outlet K=1000/2 are unchanged illustrative assumptions. Pressure loss is not an extra energy sink. No momentum inventory, gravity, slip, choking or new two-phase correlation is introduced.

**Standalone thermal Stage 1:** `thermal-geometry.cjs` and `thermal-network.cjs` implement constant-capacity tube/fin/air energies, signed linear exchanges and external-load/reservoir accounting. There are no refrigerant states or active G_tr links; G_tr remains zero in standalone closed tests. A prescribed-temperature air reservoir replaces its finite node and has an explicit signed external energy ledger. Constant-C/G stages use an exact thermal Jacobian with adaptive TR-BDF2. Standalone five/nine allocation and nonuniform physical-energy initialization are qualified, without altering the refrigerant prototype.

**Coupled Stage 2A:** `coupled-model.cjs` and `coupled-implicit.cjs` form a separate factory with exactly five refrigerant cells, five tube nodes, five fin nodes and one finite-air node. It reuses unchanged transport/property/hydraulic modules. Inherited prescribed `heatKW` is zero and cannot be patched; historical prescribed-heat fixtures remain entirely separate. Total **effective, uncalibrated constant** G_tr=0.60 kW/K is allocated by length, 0.12 kW/K per cell; zero exchange is permitted for limiting tests. The separately reported radial-wall conductance is not added again.

For each cell, `Q_tr=G_tr*(T_tube_K-(T_refrigerant_C+273.15))`. Its same signed stage integral adds to refrigerant U and subtracts from tube E. Air/tube, air/fin and fin/tube links likewise use paired integrals. Negative exchange is physical heat reversal. The combined energy change equals signed inlet-minus-outlet enthalpy transport plus external air load; internal links cancel. There is no hidden sink, friction correction, clipping or fabricated phase/protection state. The coupled factory permits finite air only, not a prescribed-temperature coupled reservoir.

### Illustrative thermal geometry and boundaries

| Total physical quantity | Value / assumption |
| --- | --- |
| Refrigerant bore / total volume / derived length | 0.020 m / 0.003 m³ / 9.5492965855 m |
| Tube outside diameter / wall thickness | 0.024 m / 0.002 m |
| Steel density / cp / conductivity | 7850 kg/m³ / 0.470 kJ/(kg·K) / 45 W/(m·K) |
| Tube mass / heat capacity | 10.362 kg / 4.87014 kJ/K |
| Aluminum fins | 1910; OD 0.080 m, hole 0.024 m, thickness 0.0002 m |
| Fin density / cp / conductivity | 2700 kg/m³ / 0.900 kJ/(kg·K) / 205 W/(m·K) |
| Fin mass / heat capacity | 4.7177874932 kg / 4.2460087439 kJ/K |
| Exposed fin / bare tube / internal tube area | 17.5692940833 / 0.6911978786 / 0.600 m² |
| Air→tube / air→fin / fin→tube conductance | 0.03455989393 / 0.87846470417 / 2.0 kW/K |
| Finite air | Fixed 5 m³ / 6 kg; cv=0.718, cp=1.005 kJ/(kg·K); capacity 4.308 kJ/K |
| Air coefficient | Illustrative constant forced convection, 50 W/(m²·K) |

These are engineering screening assumptions, not manufacturer data. Air is dry, perfectly and instantaneously mixed, fixed-mass/fixed-volume ideal-gas internal-energy storage using cv. It is **not a realistic constant-pressure refrigerated-room model**. No fan/velocity distribution or validated convection correlation is inferred. Contact resistance is effective; fin conductivity is metadata, not a distributed conduction model. No fin-efficiency correction, axial conduction, ventilation, humidity, frost or oil model exists.

Uniform physical homogenization assigns 382 fin equivalents per five-section cell and 1910/9 per standalone nine-section cell, without rounding. Total metal mass, capacity, area and energy are invariant. Nonuniform initialization integrates physical energy density over each interval before recovering temperature; it does not interpolate old cell centers. Coupled nine-section behavior has not been implemented or validated.

The standalone closed fixture uses tube/fin/air 273.15/283.15/293.15 K, zero external load and a 300 s relaxation test, with energy-derived equilibrium ~282.731247 K. Its separate reservoir fixture changes prescribed air temperature 293.15→303.15→283.15 K at 15/30 s over 60 s, with signed external energy accounting. Coupled startup temperatures are listed separately below.

| Qualified coupled fixture | Initial refrigerant in each cell | Tube / fin / air K | Supported tested interval |
| --- | --- | --- | --- |
| Cold startup | 3.5 bar / 500 kJ/kg | 273.15 / 273.15 / 278.15 | 120 s, 1 kW external air load |
| Warm startup | 3.65 bar / 1650 kJ/kg | 293.15 / 293.15 / 293.15 | 120 s, 1 kW external air load |
| Load disturbance | Cold fixture | Cold temperatures | 60 s; load 1→2→1 kW at 15/30 s |
| Feed disturbance | Cold fixture | Cold temperatures | 60 s; inlet 4→4.3→4 bar at 15/30 s |
| Sealed heat reversal | Warm refrigerant, original closed faces | Cold temperatures | 60 s, 1 kW air load |

Default reservoirs remain inlet 4 bar / 500 kJ/kg and outlet 3.5 bar / 1700 kJ/kg. Outlet reservoir h is a donor value only on reverse flow. At 120 s, cold/warm imposed-pressure outlet qualities are **0.1920994 / 0.1979679**, both wet at 267.81154 K and zero superheat. Warm starts dry and becomes wet: nominal terminal-cell vapor crossing ~1.501362 s, independent EOS ~1.501384 s. The sealed reversal ends superheated but is not a flowing dry-outlet qualification. A sustained open dry-outlet fixture requires a feasibility analysis and explicit boundary approval before adoption.

## Numerical contracts and accepted budgets

The joint implicit system has 21 nonlinear coordinates: ten PH coordinates plus eleven thermal-energy increments. Every TR-BDF2 stage evaluates both hydraulic and thermal exchanges at its current stage state, with gamma `2-sqrt(2)` and shared positive stage quadrature. Variable-aware damped Newton uses pressure/enthalpy/energy perturbations and phase-sensitive fluid probes, a finite-difference Jacobian and pivoted dense linear solve. It does not modify the historical solver. Exact PH pairs are cached within one stage only.

Each stage recovers refrigerant PH from conserved M/U/V; full and both half-step candidates must pass recovery. Stage consistency bounds are 1e-6 bar, 1e-4 kJ/kg and 1e-4 K versus PH coordinates; original energy/density recovery requirements remain. Adaptive step doubling divides the second-order difference by three and accepts the two fine half steps atomically. No extrapolated state, split thermal advance or correction energy is installed.

The maximum-component norm covers refrigerant M/U/PH absolute-plus-relative scales and thermal `C*(temperatureAbsoluteK+rtol*50 K)`. Nominal settings: rtol=1e-6, mass absolute 1e-11 kg, energy absolute 1e-8 kJ, pressure absolute 1e-6 bar, enthalpy absolute 1e-4 kJ/kg, temperature absolute 1e-4 K, max trial 0.5 s and min retry 1e-9 s. Tight/reference regimes use rtol 1e-7/1e-8, temperature absolute 1e-5/1e-6 K and caps 0.25/0.125 s; see `accuracyOptions()` for all scales. Event bracket caps are 0.002/0.0005/0.0001 s, distinct from the comparison-error budget below. Same-tolerance 0.025 s refinement is also tested.

The following is the coupled contract, with standalone exceptions explicit. Earlier suites' property/spatial/temporal budgets remain unchanged in their original tests and reports.

| Acceptance quantity | Preserved budget |
| --- | --- |
| Refrigerant global/per-section mass residual | <1e-8 kg |
| Refrigerant global/per-section, thermal per-node and combined energy residual | <1e-6 kJ in coupled tests; standalone energy ≤1e-6 kJ |
| Same-table temporal pressure / enthalpy error | <5e-5 bar / <0.05 kJ/kg |
| Nominal / tight refrigerant and thermal temperature error | <0.01 / <0.001 K |
| Well-conditioned phase/domain-event comparison error | <0.001 s; not a universal grazing-event guarantee |
| Direct-EOS trajectory pressure / enthalpy / temperature / event error | <1e-4 bar / <0.05 kJ/kg / <0.01 K / <0.001 s |
| Nonlinear fluid scaled residual | ≤1e-11; unchanged 30-iteration limit |
| Thermal nonlinear closure | ≤1e-12 K; distinct from adaptive error tolerance |

Independent EOS reference refinement must meet the existing test's pressure <1e-7 bar, enthalpy/temperature <1e-4 kJ/kg/K, thermal temperature <1e-5 K and event <1e-6 s checks. Standalone integrated-link trajectory error <0.01 kJ is distinct from energy conservation. Simple isolated-air domain clocks retain their <1e-7 s budget.

Canonical thermal energies use the fixed computational anchor 273.15 K; arbitrary `energyReferenceK` is reporting only. Tested references −1,000,000 / 273.15 / +1,000,000 K give identical physical states and accepted/rejected timestep decisions. Refrigerant h/u reference conventions are unchanged.

Scheduled patches are validated at construction and applied at exact transition times, without straddling accepted intervals. Boundary edits do not advance time or reset inventories. Rejected attempts preserve accepted cells/energies, clocks, ledgers, events, boundary records/index and accepted counts; diagnostic work/rejection counters may grow. Stops freeze advancement and edits, retaining evidence. Solver, accuracy and corroborated refrigerant/thermal domain stops are distinct. The Stage 2A-R fix rechecks exact-boundary accepted temperature and outward rate independently of the retry floor; 1e-9, 1e-5 and 0.5 s floors, both 200/400 K limits, inward/zero flow, ordinary failures and misleading probes are covered. A failed property/Newton probe alone is not proof of physical exit.

## Independent methods, results and evidence

Historical references use direct CoolProp 7.2.0 / HEOS::Ammonia steady shooting, separate backward-Euler balance solves and SciPy Radau conserved-M/U transients. Standalone thermal references independently assemble temperature-coordinate constant-C/G equations and augmented SciPy matrix exponentials with link/load integrals; independent two-node analytic solutions, three-node references and nonuniform five/nine tests supplement them.

`generate_coupled_reference.py` independently derives geometry and integrates conserved M/U plus thermal energies and signed face/link budgets using direct CoolProp D/U recovery and SciPy Radau. It imports no JS solver/table, splits scheduled changes exactly and refines rtol 1e-8→1e-10 with caps 0.1→0.025 s. `generate_coupled_domain_reference.py` separately verifies the sealed 35-bar pressure-edge direction. `audit_coupled_results.py` reconstructs energy from temperatures/independent capacities and signed budgets using Python's standard library, importing neither solver.

Qualification separates JS temporal error against a resolved same-table trajectory, direct-EOS reference refinement, JS/direct-EOS differences including initialization/property closure, and matched-PH interpolation errors. Sharing the EOS source and physical assumptions means these pathways qualify **numerical consistency**, not measured equipment accuracy or manufacturer calibration.

| Coupled full-suite maximum residual | Observed |
| --- | ---: |
| Global / per-section refrigerant mass | 1.94237e-10 / 9.39833e-11 kg |
| Refrigerant / thermal / combined energy | 6.04839e-8 / 1.32104e-10 / 6.05193e-8 kJ |
| Per-section / thermal-node energy | 3.37490e-8 / 3.26204e-9 kJ |

Nominal/tight same-table refrigerant-temperature errors are 0.000764648 / 0.000265205 K; thermal errors 0.0000492594 / 0.00000994155 K. Resolved JS/direct-EOS errors reach 3.92704e-5 bar, 0.00627706 kJ/kg, 0.00109364 K refrigerant and 0.0000689377 K thermal. Matched-PH temperature discrepancy reaches 0.00219264 K; this is sampled interpolation error, not a global bound or inversion resolution. Smooth-fixture TR-BDF2 orders are ~2.013/2.014, versus backward-Euler ~0.963/0.981. Independent accounting audits each cover 150 records, with combined residual 5.44022e-9 kJ.

Evidence index: [TIME_ACCURACY.md](TIME_ACCURACY.md), [SPATIAL_RESOLUTION.md](SPATIAL_RESOLUTION.md), [NINE_SECTION_COMPARISON.md](NINE_SECTION_COMPARISON.md), [THERMAL_STAGE_1.md](THERMAL_STAGE_1.md), [COUPLED_STAGE_2A.md](COUPLED_STAGE_2A.md), [COUPLED_STAGE_2A_R.md](COUPLED_STAGE_2A_R.md). Preserve `RESULTS.json`, temporal/spatial/nine reports, `THERMAL_*`, `COUPLED_*`, all frozen references and `COUPLED_DEVELOPMENT_FAILURES.json`. Earlier failed development runs and the initial Stage 1 WebKit pause-assertion failure remain recorded as historical evidence; unchanged later qualification passed. Earlier report statements about pending source review or missing hosted thermal/coupled coverage describe their delivery dates, not the current acceptance state.

The authorized independent candidate source review found no high-severity defect or incorrect accepted energy transfer. Its confirmed exact-boundary classification defect was corrected in Stage 2A-R; cost/domain findings remain unresolved limitations. Formal Stage 2A acceptance followed Stage 2A-CI, not the initial candidate alone.

## Outstanding physical, numerical and performance limitations

- **Reversal Newton cost:** nominal sealed reversal has 962 accepted / 922 rejected trials, including 921 Newton exhaustions and one temporal rejection. Tight/reference regimes have 963/907 and 976/727 accepted/rejected trials; tolerance and step caps change together, so these are not isolated tolerance-only experiments. All 2,552 failed Newton solves across diagnostic regimes are superheated vapor and tube-energy dominated, with no failed derivative probes; all exhaust 30 iterations. Cold/warm nominal runs have no failed Newton solves. Repeated line-search stagnation remains a material cost risk.
- **Closure versus property resolution:** failed nominal thermal closures span ~1.00017e-12–4.81654e-12 K while refrigerant residual norms are already below 1e-11. PH inversion's 38 bisections over 250 K have width 9.094947e-10 K; exact piecewise-linear table inversion measures error up to 4.548397e-10 K and plateaus. This is a plausible contributor, not proven sole cause. Accepted solves attain 1e-12 K, but not consistently at larger attempted steps; retries recover supported solutions. Canonical M/U/V inversion is separate (32 temperature bisections; sampled PH-to-recovered temperature differences ≤2.864908e-8 K). Diagnosed failures occur inside Newton before acceptance recovery. No tolerance relaxation or historical property change is approved.
- **Evidence retention:** `COUPLED_R_DIAGNOSTICS.json` and `COUPLED_R_FAILED_NEWTON.jsonl.gz` retain final residuals and complete failed iteration/derivative/line-search histories. The independent audit checks 2,552 histories, 1,669,542 derivative probes and 902,052 line-search probes. Archive SHA256: `c1ca2203fcf6026d2da70d5331c1bb5ac49ffe74a29997ce2cf8bdbcfe3a30fc`. Generation is not routine CI; preserve archive, summary and audit together.
- **Runtime/EOS support:** nominal pressure/offset ranges (~0.3–35 bar, 250 K superheat, 30 K subcooling) are not a complete table-availability domain. Missing below-200-K liquid rows depend on pressure brackets. CoolProp supports 0.32 bar / 200.05 K, but runtime PH and direct-EOS-inventory recovery reject it. Actual brackets are 0.3183890254–0.3247658591 bar with maximum subcooling 18.9999999 K. Existing qualified trajectories are unaffected. PH support, table-inventory/stage recovery and EOS-inventory recovery must be distinguished from physical exit. Sparse samples cannot certify whole intervals; no table extension or frozen-reference replacement is authorized.
- **Wet outlet and operating scope:** approved cold/warm fixtures end wet; no sustained dry-outlet guarantee, full shutdown/restart, hour-long coupled operation, hydraulic-reversal qualification or grazing/multiple-event qualification exists. Terminal-cell saturation events and imposed-pressure outlet diagnostics are different observables. No artificial vapor selection, forced superheat or invented suction trip is permitted.
- **Finite-air limits:** positive load without cooling cannot remain within 200–400 K indefinitely. Standalone connected +1 kW and coupled zero-exchange verification stop near 1566.702614 s for their declared Stage 1 temperatures; this is not a predicted stop time for the flowing cold/warm cases. Expected conserved domain stops can pass tests; unsupported continuation is excluded.
- **Spatial resolution:** five is provisional; no coupled nine-section implementation/qualification exists. Earlier prescribed-heat five-to-nine total-mass differences are 8.54–11.30%, liquid-mass differences 15.48–24.87%. Temporal errors are much smaller but spatial convergence is not established. Nine remains the maximum comparison mesh; a 45-bin accounting grid is not a 45-section simulation.
- **Physical validity:** constant conductances, geometry/materials, perfectly mixed fixed-mass air and homogeneous/upwind/quasi-steady refrigerant assumptions are uncalibrated. There is no film/entrainment/dryout/parallel-circuit model, validated two-phase multiplier, humidity/frost or complete connected equipment validation. Numerical conservation does not establish accuracy of these closures.
- **Performance:** headless blank-page Chromium/WebKit numerical portability is qualified, not real-device/iPad, interactive UI, worker/deadline or full-circuit performance. Local shared-runner reversal wall times vary materially (~31 s originally, ~59–72 s in candidate/corrected/instrumented diagnostics). Instrumented timing includes serialization/IO; no speed comparison is controlled and no integration decision follows.

## Hosted CI coverage and measured costs

The unchanged four-job structure in `.github/workflows/dx-fv-experiment.yml` runs on experimental pushes/manual dispatch:

| Job | Preserved and added coverage | Accepted run duration |
| --- | --- | ---: |
| `prototype` | 13 legacy numerical suites, build consistency, historical DX/time frozen/fresh references; standalone thermal frozen/fresh expm; coupled frozen/fresh direct-EOS comparisons, candidate fetch, domain, both independent audits and adaptive timestep controls/rollback | 23m 52s |
| `browser-performance` | Application Chromium/WebKit, historical DX/spatial comparisons, standalone thermal and coupled blank-page numerical verification | 8m 24s |
| `spatial-resolution` | Historical prescribed-heat three/five contracts and frozen/fresh qualification | 4m 53s |
| `nine-section-resolution` | Historical prescribed-heat three/five/nine spatial/temporal/extended tests, cost/warm-domain checks and fresh reference replay; **no coupled nine-section study** | 6m 19s |

Accepted run `38069836624` executed both complete coupled comparisons (five cases/ten additional checks plus existing expected-failure scenarios), fresh generation with zero EOS fallbacks, 27 boundary/ten solver-probe checks, two 150-record accounting audits, all five adaptive-control cases and both browsers. Hosted runtime was Node 22.23.3, Python 3.12.15, CoolProp 7.2.0, NumPy 2.5.3, SciPy 1.16.2, Playwright 1.62.1; local Stage 2A-R used Python 3.12.14. Declared support is Node 22/Python 3.12 with those pinned dependencies.

New coupled steps took 18m 46s aggregate runner time: frozen/fresh 404/403 s, direct-EOS regeneration 173 s, controls 54 s, browsers 85 s, plus domain/audit/uploads. All job durations total 43m 28s runner time; jobs run concurrently. These are observational CI costs, not equipment/main-thread benchmarks or fixed future runtime budgets.

New thermal/coupled logging blocks use `set -euo pipefail`; all scientific failures block successful CI, with no `continue-on-error` or relaxed criteria. Numerical/browser uploads use `if: always()` and retain JSON, references, runtime versions and failure logs/partial `.failure.json` files. Ten artifacts were uploaded and unexpired at qualification, including `coupled-five-section-numerical-verification` and `coupled-five-section-browser-verification`, plus all eight established artifacts. Retention is finite. Hosted logs were retrieved/inspected; artifact ZIP downloads from the development workspace returned `Forbidden`, so ZIP contents were not independently re-downloaded there. Full Newton-history generation is excluded from per-push CI; its committed audit remains reproducible separately.

`.github/workflows/verify.yml` remains separate application verification for main/PR/manual runs. No workflow change is part of this documentation handoff. Its push may trigger a new experimental CI run; delivery reports that run's actual current status without substituting the accepted implementation run for documentation-HEAD qualification.

## Complete reproduction commands

Run from a real repository root with **Node 22**, **Python 3.12** and working Git; do not silently substitute another runtime. Use temporary output paths so no frozen file is overwritten. Set up dependencies once:

```sh
node --version
python3.12 --version
npm ci
npx playwright install --with-deps chromium webkit
python3.12 -m venv /tmp/ammonia-dx-reference
/tmp/ammonia-dx-reference/bin/pip install CoolProp==7.2.0 numpy==2.5.3 scipy==1.16.2
source /tmp/ammonia-dx-reference/bin/activate
python --version
```

Shallow clones must explicitly obtain the immutable candidate object before domain regressions or candidate diagnostic comparisons. Use the same immutable fetch as hosted CI when the object is absent; skip it in a full clone that already has the candidate to preserve its complete ancestry graph. It does not switch/reset a branch or update refs/FETCH_HEAD:

```sh
if ! git cat-file -e aa9514b0338b6021d9afc4b9f47f88ebdde765da^{commit} 2>/dev/null; then
  git fetch --no-tags --depth=1 --no-write-fetch-head origin aa9514b0338b6021d9afc4b9f47f88ebdde765da
fi
git cat-file -e aa9514b0338b6021d9afc4b9f47f88ebdde765da^{commit}
git show aa9514b0338b6021d9afc4b9f47f88ebdde765da:experiments/dx-fv/coupled-model.cjs > /dev/null
git show aa9514b0338b6021d9afc4b9f47f88ebdde765da:experiments/dx-fv/coupled-implicit.cjs > /dev/null
```

Established application and historical prescribed-heat qualification:

```sh
npm test
npm run test:browser
npm run test:webkit
python tools/build.py /tmp/ammonia-dx-build
git diff --exit-code -- index.html validation.json integration-validation.json
node experiments/dx-fv/test.cjs /tmp/dx-fv-results.json
node experiments/dx-fv/time-test.cjs /tmp/dx-time-results.json
node experiments/dx-fv/spatial-test.cjs /tmp/dx-spatial-results.json
node experiments/dx-fv/resolution-test.cjs /tmp/dx-resolution-results.json
node experiments/dx-fv/warm-domain-test.cjs /tmp/dx-warm-results.json
node experiments/dx-fv/resolution-cost.cjs /tmp/dx-cost-results.json
node experiments/dx-fv/browser-benchmark.cjs /tmp/dx-browser-results.json
node experiments/dx-fv/spatial-browser.cjs /tmp/dx-spatial-browser.json
node experiments/dx-fv/resolution-browser.cjs /tmp/dx-resolution-browser.json
python experiments/dx-fv/generate_reference.py /tmp/dx-reference-stage3.json
DX_FV_REFERENCE_PATH=/tmp/dx-reference-stage3.json node experiments/dx-fv/test.cjs /tmp/dx-fv-fresh.json
python experiments/dx-fv/generate_time_reference.py /tmp/dx-reference-time.json
DX_FV_TIME_REFERENCE_PATH=/tmp/dx-reference-time.json node experiments/dx-fv/time-test.cjs /tmp/dx-time-fresh.json
python experiments/dx-fv/generate_spatial_reference.py /tmp/dx-reference-spatial.json
DX_FV_SPATIAL_REFERENCE_PATH=/tmp/dx-reference-spatial.json node experiments/dx-fv/spatial-test.cjs /tmp/dx-spatial-fresh.json
python experiments/dx-fv/generate_spatial_reference.py /tmp/dx-reference-resolution.json 3,5,9
node experiments/dx-fv/resolution-reference-check.cjs /tmp/dx-resolution-results.json /tmp/dx-warm-results.json /tmp/dx-reference-resolution.json /tmp/dx-resolution-fresh-check.json
```

Resolution replay checks saved qualified states/error bounds against fresh references; it does not rerun every trajectory with a replacement path. Preserve that distinction. Standalone thermal and hosted coupled qualification:

```sh
node experiments/dx-fv/thermal-test.cjs /tmp/dx-thermal-frozen.json
python experiments/dx-fv/generate_thermal_reference.py /tmp/dx-thermal-reference.json
DX_THERMAL_REFERENCE_PATH=/tmp/dx-thermal-reference.json node experiments/dx-fv/thermal-test.cjs /tmp/dx-thermal-fresh.json
node experiments/dx-fv/thermal-cost.cjs /tmp/dx-thermal-cost.json
node experiments/dx-fv/thermal-browser.cjs /tmp/dx-thermal-browser.json
node experiments/dx-fv/coupled-test.cjs /tmp/dx-coupled-frozen.json
python experiments/dx-fv/generate_coupled_reference.py /tmp/dx-coupled-reference.json
DX_COUPLED_REFERENCE_PATH=/tmp/dx-coupled-reference.json node experiments/dx-fv/coupled-test.cjs /tmp/dx-coupled-fresh.json
node experiments/dx-fv/coupled-domain-test.cjs /tmp/dx-coupled-domain.json
python experiments/dx-fv/audit_coupled_results.py /tmp/dx-coupled-frozen.json /tmp/dx-coupled-frozen-audit.json
python experiments/dx-fv/audit_coupled_results.py /tmp/dx-coupled-fresh.json /tmp/dx-coupled-fresh-audit.json
node experiments/dx-fv/coupled-controls.cjs /tmp/dx-coupled-controls.json
node experiments/dx-fv/coupled-browser.cjs /tmp/dx-coupled-browser.json
```

Optional preserved diagnostic/reference reproduction; this is not a new acceptance gate or a routine CI requirement:

```sh
python experiments/dx-fv/generate_coupled_domain_reference.py /tmp/dx-coupled-pressure-edge.json
python experiments/dx-fv/audit_coupled_diagnostics.py experiments/dx-fv/COUPLED_R_DIAGNOSTICS.json experiments/dx-fv/COUPLED_R_FAILED_NEWTON.jsonl.gz /tmp/dx-existing-newton-audit.json
node experiments/dx-fv/coupled-property-diagnostics.cjs experiments/dx-fv/COUPLED_R_DIAGNOSTICS.json /tmp/dx-property-resolution.json
python experiments/dx-fv/investigate_coupled_domain.py "$(command -v node)" /tmp/dx-runtime-domain.json
node experiments/dx-fv/coupled-diagnostics.cjs /tmp/dx-newton-diagnostics.json /tmp/dx-failed-newton.jsonl.gz
python experiments/dx-fv/audit_coupled_diagnostics.py /tmp/dx-newton-diagnostics.json /tmp/dx-failed-newton.jsonl.gz /tmp/dx-newton-audit.json
```

The fresh pressure-edge file is a separate directional diagnostic: the existing coupled suite still reads frozen `coupled-domain-reference.json`; do not replace it. `coupled-runtime-support.cjs` also accepts a JSON array of PH/EOS diagnostic points on stdin. It reports runtime availability and recovery separately, without declaring a physical trajectory exit. Full diagnostic generation is expensive and preserves large files; audit the existing committed archive when regeneration is unnecessary. Historical property grid SHA256: `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`.

## Proposed roadmap — separate approvals, no implementation authority

**A. Controlled nonlinear-solver efficiency research.** First propose a controlled Node 22 experiment with identical supported intervals, fixtures, physical closures and acceptance budgets. Compare work counts and repeated timings, preserving a baseline solver path and independent conservation/reference tests. Possible candidates are exact linear thermal-block derivatives/elimination within joint implicit stages, phase-sensitive table derivative/precision compatibility and nonlinear-failure-aware step growth. Determine causes rather than infer them solely from quantization. Tolerance relaxation, historical engine replacement or a new numerical method requires separate explicit approval; no remedy is selected or implemented by this handoff.

**B. Runtime/reference-domain qualification improvements.** Propose an independent representation of actual pressure brackets/missing-liquid masks, cross-checked against authoritative runtime PH and canonical-recovery probes. Retain independent direct-EOS integration and separate its physical support from runtime representability. Qualify continuous supported intervals using safeguarded dense-output/boundary bracketing; distinguish unsupported states, ill-conditioned inversion and solver failure. Do not treat sparse point checks or the nominal rectangular envelope as complete certification. Table extension, reference-generator modification, new frozen files or changed comparison intervals each need approval; preserve existing frozen references.

**C. Stage 2B nine-section coupled and extended operating studies.** After review of A/B readiness and computational cost, request approval for an isolated five/nine comparison with identical physical totals, energy-conserving nonuniform initialization and independent temporal/direct-EOS qualification per mesh. Report inventory/phase/common-port sensitivity without claiming convergence. Propose extended starts, load/feed changes, closed/shutdown/restart scenarios, heat/hydraulic reversal and difficult event/domain intervals explicitly; topology/transport changes remain separately gated. For a sustained dry-outlet case, submit energy/flow feasibility and proposed boundaries before adoption. No finer meshes, new correlations, protection logic or nine-section implementation is currently approved.

**D. Equipment calibration and eventual application integration.** Obtain measured geometry, capacities, flow/heat data and independent validation datasets before calibrating effective conductances or transport closures; document uncertainty and applicable operating ranges. Any expanded physics needs its own validation. Separately propose connected-circuit interfaces, initialization, controls, wet-suction/error semantics, profiles/UI migration and real-device/interactive performance tests. Only approved device/full-circuit qualification can support integration decisions. Production deployment, main/PR #3 changes and merges require explicit separate authorization; the old Live Plant failure remains unresolved there.

Recommended sequencing is design review of A and B before costlier C; D remains a separate equipment and integration program. The next approval gate is **user selection and approval of a narrowly scoped A or B investigation plan (or explicit alternative)**, including allowed files, unchanged budgets, experiments and delivery criteria. Acceptance of Stage 2A or this handoff does not authorize any of these lanes automatically.

## Restarting in a fresh Codex conversation

1. Supply repository `cdehek/Ammonia-sim`, branch `experimental/dx-fv-stage-3`, exact documentation handoff SHA from delivery, qualified implementation SHA `adbab1d5587471105a351f3467e0bb812effb148` and accepted CI URL `https://github.com/cdehek/Ammonia-sim/actions/runs/38069836624`.
2. Read this handoff, experimental README/restore points, the historical thermal proposal, Stage 1, Stage 2A and Stage 2A-R reports/evidence, current workflow and applicable `AGENTS.md`. Historical report approval statements are snapshots; the current user instruction controls. A downloaded mirror may not be a git checkout: verify identity before Git operations.
3. Verify branch, clean tree, exact HEAD/remote SHA and all restore ancestors. Review commits after the supplied handoff before treating later HEAD as accepted. Fetch missing immutable objects without moving/resetting refs; use disposable detached checkouts for restores. If shallow history prevents an ancestry proof, inspect a disposable full-history clone rather than interpreting a missing graph path as a rewritten milestone. Never force-reset or force-push main, PR #3 or the experimental branch.
4. Summarize understanding, numerical/physical limits, proposed scope and next gate before development. **At this handoff no next development stage is authorized.** Begin only read-only inspection/design discussion until the user approves a concrete A/B/C/D scope. The approved docs-only task ends at delivery.
5. On any later authorized change, preserve all existing tests/budgets/references, Stage 1, prescribed-heat physics and protected application files. Run applicable independent, conservation, temporal/control/rollback/domain/browser and historical regressions using the commands above and hosted workflow. Record runtime versions, actual CI SHA/step execution/artifacts, unsupported intervals, numerical failures and costs. Diagnose/report failures before unrelated edits; never weaken tests to pass.
6. Deliver a new isolated restore SHA after approved qualification and stop at that scope boundary. Do not automatically begin Stage 2B, calibrate Default, invent protections, extend property tables, force dry vapor, alter hydraulics or integrate/merge into the application.

Suggested opening prompt:

> Resume Ammonia Lab from documentation handoff `<exact handoff SHA from delivery>` on `cdehek/Ammonia-sim`, branch `experimental/dx-fv-stage-3`. Qualified Stage 2A source is `adbab1d5587471105a351f3467e0bb812effb148`; accepted CI is run `38069836624`. Read `experiments/dx-fv/DEVELOPMENT_HANDOFF.md`, README and restore points plus linked stage reports. Verify refs/CI and summarize current architecture, limitations and the next approval gate. No new implementation, optimization, reference change, Stage 2B or application integration is authorized yet.
