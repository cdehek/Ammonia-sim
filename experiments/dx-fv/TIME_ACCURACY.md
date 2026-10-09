# Isolated three-section numerical time-accuracy stage

Branch: `experimental/dx-fv-stage-3`. Stage 3 restore commit: **`f7b19adb67587d88195d53cee6081c8b014fb9ed`**. This stage changes only experimental numerical modules, verification and documentation. Production, PR #3, Live Plant, profiles, UI and the original thermodynamic table are unchanged. All experiments instantiate three sections; no five-section test is included.

## Selected method and usage

**Adaptive TR-BDF2 is recommended for the next isolated spatial-comparison stage.** Backward Euler and trapezoidal integration remain available for comparison. Calling the component without options still selects the original fixed-step backward Euler, preserving the Stage 3 regression path. Opt into the selected numerical configuration:

```js
const model = createEvaporator(engine, {adaptive: true});
```

The opt-in preset uses TR-BDF2, relative tolerance `1e-6`, absolute tolerances of `1e-11 kg`, `1e-8 kJ`, `1e-6 bar` and `1e-4 kJ/kg`, maximum trial interval `0.5 s`, minimum trial interval `1e-9 s`, and maximum detected-crossing bracket width `0.002 s`. Every accepted adaptive trial contains two half steps, so the maximum accepted substep is `0.25 s`. User overrides remain validated. A short remaining output interval can force a shorter final trial; the minimum interval limits retry reduction, not requested output-time alignment. It is not a proposal to run the entire plant at nanosecond steps.

Verification commands, from the repository root:

```sh
node experiments/dx-fv/test.cjs /tmp/stage3.json
node experiments/dx-fv/time-test.cjs /tmp/time-results.json
node experiments/dx-fv/browser-benchmark.cjs /tmp/browser-results.json
```

Independent continuous-time reference regeneration requires Python 3.12, CoolProp `7.2.0`, NumPy `2.5.3` and SciPy `1.16.2`:

```sh
python experiments/dx-fv/generate_time_reference.py /tmp/time-reference.json
DX_FV_TIME_REFERENCE_PATH=/tmp/time-reference.json node experiments/dx-fv/time-test.cjs /tmp/live-reference-results.json
```

The synthetic browser harness uses Playwright Chromium/WebKit and their installed dependencies (`npx playwright install --with-deps chromium webkit` on supported CI hosts). It loads the experimental modules into a blank page; it does not change or load the application UI. `DX_FV_BROWSERS=chromium` selects only that engine for local diagnostics. Hosted CI runs both. The benchmark's small CommonJS loader is test scaffolding, not a production browser packaging implementation.

## Conservative integration contract

Each section retains canonical mass `M`, total internal energy `U`, and fixed volume `V`. Pressure/enthalpy are constitutive solve coordinates. At each implicit stage the same signed face flux is used by both adjacent cells. External reservoirs and section heat remain the same uncalibrated screening fixture used in Stage 3.

Backward Euler uses end-of-step fluxes. Trapezoidal integration uses half the initial and half the final flux. TR-BDF2 uses `gamma = 2 - sqrt(2)`:

1. Solve a trapezoidal stage at `gamma * dt`.
2. Solve the final BDF stage, eliminating the intermediate inventory algebraically.

The final inventory change is `dt * [a*F_initial + a*F_stage + b*F_final]`, with `a = 1/[2*(2-gamma)] ≈ 0.353553` and `b = (1-gamma)/(2-gamma) ≈ 0.292893`. All weights are positive and sum to one. The **same weighted face fluxes** update section and global ledgers; prescribed heat is integrated over the actual accepted interval. No separate corrective mass/energy adjustment is made. `lastFluxes` reports instantaneous endpoint fluxes; cumulative face ledgers contain integrated quadrature, not endpoint-flow-times-elapsed approximations.

Every stage passes independent canonical mass/volume/energy recovery before acceptance. Saved pressure and inventory-derived enthalpy initialize the next constitutive solve; this avoids feeding the existing canonical-recovery tolerance back into the Newton starting coordinates. These are guesses consistent with accepted inventory, not prescribed operating pressures. Records still expose canonical recovery.

TR-BDF2 is self-starting and L-stable for the linear test equation. It needs no multistep-history migration at a heat/feed edit. This is why it is preferred over plain trapezoidal integration despite the extra stage. Linear L-stability is not a guarantee for every nonlinear property state.

## Adaptive error and event control

Each attempted interval solves one full step and two half steps. The estimated error of the two-half solution is their difference divided by `2^order - 1`. It is scaled separately by absolute-plus-relative tolerances for every section's mass, internal energy, pressure and enthalpy. The maximum normalized component must be at most one. Pressure/enthalpy checks supplement inventory checks because inventory differences can hide important intensive-state errors near saturation. The comparison fixtures retain an absolute pressure floor of `1e-6 bar`, including their tight reference runs; asking for unlimited relative pressure precision in nearly incompressible liquid would exceed the table/recovery/Newton resolution.

The accepted state is the **two-half-step solution**, without Richardson extrapolation. Extrapolating inventories could create unsupported phase states and would require a different flux quadrature. Rejected full/half candidates never consume physical time, change inventory, create events, or enter a conservation ledger. Step-size growth/shrinkage uses order-dependent scaling, safety factor `0.85`, growth cap `2`, and bounded rejection reductions. Convergence failures halve the trial interval. The next proposal persists between `advance` calls. A boundary edit resets the numerical proposal, while leaving physical state, time and ledgers unchanged.

Crossings use signed `h - hf(p)` and `h - hg(p)` for each section, including boiling/drying, condensation and emergence from subcooled liquid. If a crossing is detected across either half step, the interval is retried until its substep bracket is at most the requested event width. Event time is interpolated within that bracket. A bracket describes the computed trajectory; it is not a certified bound on the true continuous-time event. Comparisons against refined trajectories and an analytic sealed-boiling event quantify that additional error. Multiple crossings wholly inside a substep, grazing events, and pathological rapid switching are not formally guaranteed to be detected; these remain future event-analysis work.

The phase-aware Newton path uses smaller finite-difference perturbations, chooses derivative samples inside the current constitutive branch, and permits a much smaller line-search factor. This addresses the sharp compressibility change from subcooled liquid to mixture without modifying the EOS, clipping liquid fraction, or selecting vapor. The original fixed-step backward-Euler derivative settings remain available for the unchanged Stage 3 tests.

## Quantitative results

Machine-readable results are in [TIME_RESULTS.json](TIME_RESULTS.json). Timing is observational and hardware-dependent.

| Test | Result |
| --- | --- |
| Fixed-step startup refinement, steps 0.00625/0.003125/0.0015625/0.00078125 s | Backward Euler observed order 1.14–1.19; trapezoidal 1.91–1.96; TR-BDF2 1.95–2.00 |
| Direct-EOS continuous-time startup reference | At tight `1e-7` tolerance: maximum pressure difference `5.45e-8 bar`, enthalpy `0.00186 kJ/kg`, temperature `0.000162 K`, wet-event timing `4.72 microseconds` |
| Independent Radau reference's own refinement | `1e-8` versus `1e-10` relative tolerance agrees in outlet transition time to about `7e-11 s` and in terminal enthalpy to about `1.1e-8 kJ/kg` |
| Selected `1e-6` tolerance, seven scenarios | Maximum sampled pressure error below `1.11e-6 bar`; enthalpy error `0.0132 kJ/kg`; temperature error `0.00227 K`; event-time error below `0.000976 s` against tight same-table references |
| Tight-reference cross-check | Independently stepping trapezoidal and TR-BDF2 runs agree within `0.000173 kJ/kg` in sampled enthalpy and `0.000017 s` in event timing |
| Analytic sealed boiling event | Exact inventory/heat-derived time `0.381679305 s`; event bracket caps 8/2/0.5 ms reduce timing error to approximately 204/34/14 microseconds |
| One-hour adaptive dry operation | Global residual approximately `3.54e-10 kg`, `9.35e-8 kJ`; 14,598 accepted half steps |
| One-hour adaptive wet operation | Global residual approximately `2.39e-9 kg`, `7.66e-7 kJ`; 14,616 accepted half steps; wet outlet stays visible |

The seven scenarios cover stiff startup; cold wet startup; heat loss/restoration; feed-pressure increase/decrease; feed isolation; sealed boiling/condensation; and initially liquid-full transport. Relative-tolerance refinement (`1e-4`, `1e-5`, `1e-6`) reduces sampled enthalpy errors for each method whenever errors exceed the small comparison floor. Every accepted record passes per-section/global conservation checks: `1e-8 kg` and `1e-6 kJ`. The selected configuration passes sampled error acceptance thresholds of `0.05 kJ/kg`, `5e-5 bar`, `0.03 K` and `0.003 s` in event timing. These are numerical prototype criteria, not manufacturer calibration limits.

At equal requested startup tolerance `1e-6`, the comparison shows:

| Method | Maximum sampled enthalpy error | Outlet event-time error | Residual evaluations |
| --- | ---: | ---: | ---: |
| Backward Euler | 0.0879 kJ/kg | 0.256 ms | 48,987 |
| Trapezoidal | 0.00644 kJ/kg | 0.0312 ms | 8,367 |
| TR-BDF2 | 0.00591 kJ/kg | 0.0281 ms | 11,646 |

The error estimate is local, so equal requested tolerance does not imply equal global accuracy across orders. Trapezoidal is cheaper here, and remains useful for cross-checking. However, a coarse 0.05 s trapezoidal startup produces spurious wet/dry crossings; adaptive trapezoidal and adaptive TR-BDF2 match the reference crossing sequence. TR-BDF2's damping gives a more defensible general-purpose choice for the stiff reduced model. It is not the cheapest method for a sealed cell with constant heat, where the energy equation is linear.

## Failure behavior and limitations

Regression tests distinguish:

- **Accuracy stop:** the error/event tolerance cannot be met above the minimum retry interval. No failed candidate is accepted. Tests cover rejection at initialization and after previously accepted time/ledgers.
- **Solver stop:** deliberately inadequate Newton iterations; no accepted physical advancement or invented property-domain diagnosis.
- **Domain stop:** the concentrated 2/4/12 kW low-inventory startup reaches the existing 250 K-superheat table boundary near `0.160728 s` under the selected temporal method. It retains the last valid state. The original coarse backward-Euler example reached that boundary much later; it was not an accurate continuous-time failure timestamp.

A failed Newton line search is not automatically called a domain stop. If domain trials were encountered and a very small retry interval (at most `1e-6 s`) is exhausted, independent canonical recovery checks the local conservative M/U transport direction. Only a confirmed out-of-domain recovery changes the classification; the original numerical cause and diagnostic evidence are retained. That predictor is diagnostic only and never becomes physical state or ledger flow. Stops freeze subsequent advancement. No wet-outlet or evaporator-level equipment trip is added.

The independent startup reference uses direct CoolProp D/U flashes and SciPy Radau in conserved M/U coordinates, without the embedded table or JavaScript solver. CoolProp occasionally fails its D/U flash exactly at vapor saturation during event location. The reference generator then solves the same density/internal-energy state using a direct D/T energy root, checks the recovered energy residual, and reports the fallback count. It does not clamp phase or inventory. This is an independent computational path, but shares the table's EOS source and is not independent plant measurement.

The liquid-full fixture contains an initial pressure/phase transient on the scale of tens of microseconds; the selected adaptive run uses an accepted substep near `0.2 microseconds` before growing again. That is a consequence of the existing incompressible-liquid/quasi-steady resistance model, not a validated pressure-wave timescale in a real coil. Momentum/inertance, slip, entrainment, wall/air storage, flashing-valve physics, geometry calibration and full-circuit coupling remain outside this authorization. Temporal convergence makes those limitations more visible; it does not resolve them.

## Browser cost and next decision

The [synthetic desktop Chromium run](BROWSER_RESULTS.json) measured approximately **0.70 s** for one stiff startup second, **7.37 s** for a simulated dry hour, and **5.66 s** for a simulated wet hour. These were measured during other verification work; they are not controlled device benchmarks. A cold startup advanced in 0.1 s simulation batches took about 1.19 s total CPU/wall time across five simulated seconds, with a **143 ms** longest synchronous call. Node measurements without browser instrumentation were about 3–4 s per simulated hour. Raw counts are retained because they are more portable than host milliseconds. `attemptedResidualEvaluations` and `attemptedIterations` include coarse, fine, rejected and failed Newton work; accepted counters exclude discarded candidates.

Hosted CI repeats isolated numerical execution/conservation and performance in **Chromium and WebKit** and uploads the measurements. Linux WebKit does not reproduce iPad CPU, memory, thermal throttling, touch interaction or operating-system behavior. No physical-iPad performance claim is made.

The longer synchronous cold-start chunk shows that eventual UI integration should use a bounded work budget and/or a worker rather than running arbitrary catch-up intervals on the UI thread. This is a recommendation, not an implementation in this stage. Playback batching can affect the accepted step sequence; arbitrary batching invariance is not claimed. Dense finite-difference Newton solves and step doubling have a real cost, and a larger section count will increase it. Sparse/analytic derivatives, error-estimator reuse and browser scheduling should be evaluated if needed, without relaxing physical conservation or temporal acceptance criteria.

**Temporal convergence is adequate to propose the next isolated five-section comparison, subject to approval.** For the tested three-section trajectories, temporal errors are quantified and comfortably below the chosen prototype thresholds, with first/second-order refinement demonstrated and independent continuous-time startup agreement. For spatial comparisons, hold geometry, thermal boundaries and temporal tolerances fixed, repeat temporal refinement on every approved mesh, and distinguish mesh effects from event/table/solver resolution. This is not release acceptance for the complete circuit. No five-section run, equipment calibration, UI/Live Plant integration, PR #3 change or merge is performed here.
