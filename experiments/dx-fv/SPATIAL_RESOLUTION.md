# Controlled three-versus-five-section comparison

## Decision and scope

Five sections are recommended as the **provisional investigative mesh**, not a production section count. Three sections are useful for fast steady-state screening but are not established as adequate for inventory or phase-transition timing. Two meshes do not establish spatial convergence. A finer reference requires explicit approval before it is run.

This work is confined to `experimental/dx-fv-stage-3`. Temporal restore point `3e2cdbf1c8e1c9c42268a72bda5b0d05cf54f0f5` remains its unchanged ancestor. No numerical component, Live Plant, equipment profile, UI, PR #3, production file or production ref was changed. New comparison fixtures, diagnostics, independent references and tests exercise the existing configurable component. Raw trajectories and regenerated references are uploaded by the isolated CI workflow; [SPATIAL_RESULTS.json](SPATIAL_RESULTS.json) is the local quantitative snapshot.

## Holding the physical system fixed

Both meshes use 0.003 m³ total refrigerant volume, 0.020 m diameter and 9.5492966 m total length, Darcy friction factor 0.02 and viscosity 1e-5 Pa·s. The boundary restrictions remain K=1000 inlet and K=2 outlet. Each boundary connection spans half a cell and each internal connection a full cell; total connection length and both linear/quadratic homogeneous-fluid resistances are identical. Internal interfaces gain no extra local restriction on refinement. Equal cell volumes are 0.001 and 0.0006 m³. Dimensions and resistance invariants are regression-tested.

Reservoirs initially impose 4 bar / 500 kJ/kg upstream and 3.5 bar / 1700 kJ/kg downstream. Cold initial conditions are uniformly 3.5 bar / 500 kJ/kg; warm conditions uniformly 3.65 bar / 1650 kJ/kg. Initial total mass and internal energy therefore match exactly between meshes. Uniform heat is distributed by cell volume; graded heat integrates the same continuous profile q(x)=Q(0.5+x), for normalized x in [0,1]. Both meshes receive exactly the same total heat.

The cases cover warm startup at 12 kW, cold startup at 18 kW, load 18→12→18 kW at 15/30 s, feed pressure 4→4.3→4 bar at 15/30 s, graded 18 kW startup, and one-hour operation at uniform 12/18 kW and graded 18 kW. They are deliberately isolated prescribed-boundary fixtures, not calibrated Default equipment or the old connected circuit.

The reported terminal state is the last cell's bulk state. Its center is x=5/6 on three cells and x=9/10 on five: terminal-center pressures and first-to-last center pressure drops cover different positions. The boundary port pressure is imposed at 3.5 bar on both meshes; total imposed pressure drop is 0.5 bar (0.8 during increased feed pressure). Whole-tube friction-only pressure drop is also reported to provide a comparable loss measure. Fifteen overlap bins conservatively compare piecewise-constant inventory fields; they are a diagnostic accounting grid, **not a fifteen-section simulation**.

## Independent temporal qualification

Each mesh and case independently uses adaptive conservative TR-BDF2 at relative tolerances 1e-6, 1e-7 and 1e-8, maximum steps 0.5/0.25/0.125 s and phase-event brackets 0.002/0.0005/0.0001 s. An additional same-tolerance maximum-step refinement isolates the step-cap effect. Spatial differences use the tight 1e-8 trajectories, not the nominal trajectories.

Across the initial qualification runs, nominal versus tight errors were at most approximately 8.3e-6 bar, 0.0166 kJ/kg, 0.0064 K, 89 microseconds in phase events and 2.4e-7 kg in the inventory-profile L1 norm. The final snapshot contains the exact values after adding output times inside differing transition windows. Smaller-step checks and tighter-tolerance improvements passed independently on both meshes.

Independent CoolProp 7.2.0 steady shooting validates six discrete operating points. A separate conserved-M/U SciPy Radau solve with direct EOS validates warm startup on each mesh; Radau itself is refined from 1e-8 to 1e-10. JavaScript bypasses neither conservation nor phase recovery to match it. Maximum startup differences are about 1.2e-5 bar, 0.0044 kJ/kg and 0.0021 K; phase/domain timing differences are about 1.4 microseconds. Steady enthalpy agreement is within 0.0048 kJ/kg. This is independent numerical implementation using the same underlying EOS, not independent experimental evidence or a continuum reference.

## Spatial differences

Five-minus-three differences at one hour:

| Heat fixture | Total mass | Liquid mass | Terminal temperature | Terminal enthalpy | Whole-tube friction drop |
| --- | ---: | ---: | ---: | ---: | ---: |
| Uniform 18 kW, dry terminal | +15.29% | +39.95% | −0.1181 K | −0.2581 kJ/kg | −0.0002086 bar |
| Uniform 12 kW, wet terminal | +11.77% | +23.60% | −0.0148 K | +0.0612 kJ/kg | +0.0000704 bar |
| Graded 18 kW, dry terminal | +17.01% | +34.82% | −0.2295 K | −0.5187 kJ/kg | −0.0004144 bar |

Uniform dry mass is 0.0124675 versus 0.0143743 kg; wet mass is 0.0171369 versus 0.0191536 kg; graded dry mass is 0.0149559 versus 0.0174994 kg. Uniform dry superheat is 41.5406 versus 41.4450 K. Wet superheat is zero on both; wet outlet quality is approximately 0.75953 versus 0.75960. These are fixture results, not realistic design superheat targets.

Representative tight terminal phase timings:

| Event | Three cells (s) | Five cells (s) | Five minus three (s) |
| --- | ---: | ---: | ---: |
| Cold startup becomes dry | 1.983952 | 1.798686 | −0.185267 |
| Graded startup becomes dry | 2.224739 | 2.014857 | −0.209882 |
| Load reduction becomes wet | 15.382958 | 15.470447 | +0.087489 |
| Restored load becomes dry | 31.096484 | 31.124951 | +0.028467 |
| Increased feed becomes wet | 15.355830 | 15.428301 | +0.072471 |
| Restored feed becomes dry | 30.929367 | 30.979843 | +0.050476 |

Phase timings and inventory differences are substantially larger than temporal error. Shared samples within these transition windows explicitly record wet/dry disagreement. Outlet steady intensives are comparatively close, but this does not validate distributed charge or transient accuracy. More cells reduce coarse upwind mixing; the direction and size of error relative to a converged solution remain unknown.

## Stability, conservation and a model-domain limitation

Cold startup, disturbances and all six one-hour runs meet global and per-cell ledger limits of 1e-8 kg mass and 1e-6 kJ energy. Worst hour-long global residuals are approximately 2.7e-9 kg and 8.5e-7 kJ. No refrigerant is removed or clamped, and wet terminals remain observable without an attached compressor or fictitious equipment trip.

The warm five-cell case reaches the existing 250 K-superheat property boundary at approximately **0.272581 s**. Three cells instead reach a wet terminal at approximately 1.138327 s and continue. The independent direct-EOS Radau solution reaches the same five-cell domain boundary at 0.272579576 s; time refinement changes the prototype stop by only a few microseconds. This verifies a genuine limitation of the fixture/model, not proof of a hardware event. At shared time 0.2 s, five cells predict about 63.22 kJ/kg greater terminal enthalpy and 26.55 K greater temperature/superheat.

Less numerical mixing can expose a hot, low-inventory terminal under prescribed heating before cold feed arrives. Heat has no wall/air storage or temperature feedback in this model. Homogeneous equilibrium transport also omits slip, void-fraction correlations and momentum inertia. Those assumptions need separate physical review; refinement alone cannot repair them. The domain stop retains the last accepted state, conserves its ledger and remains frozen on further advance. No thermal-boundary extension, forced vapor selection, dry-suction enforcement or protective shutdown was added.

## Computational cost and browser implications

State dimension rises from six to ten unknowns. Across matched cold startup/load/feed/graded nominal runs, five cells require approximately 1.46–1.59 times as many residual calls; Newton iteration counts are close. Node wall time is approximately 1.5–1.8 times longer in those local measurements. Exact counters and elapsed times are recorded in the snapshot. Warm-start wall time is not a matched-duration comparison because the five-cell run stops early.

Local Chromium, three alternating repeats over five simulated startup seconds, measured median 619 ms (three cells) versus 822 ms (five), about 1.33 times longer. Longest individual 0.1-s advance calls reached about 84 versus 135 ms. This benchmark ran alongside numerical tests; it is observational, not an iPad measurement. The browser harness measures both Chromium and WebKit in hosted CI without loading or changing the application UI. Read the CI `three-five-section-dx-spatial-browser` artifact for host-specific results.

Five cells are not universally slower over an hour: different near-steady nonlinear iteration counts can offset larger per-iteration cost. Local browser one-hour calls took roughly 1.9–4.2 seconds across meshes/loads. A single long synchronous advance is unsuitable for interactive use on the main thread; bounded work or a worker should be evaluated only during approved future integration. Desktop WebKit does not establish responsiveness on an actual iPad.

## Recommended next approval

Approve a **nine-section isolated reference comparison**, preserving geometry, initialization and source integrals and independently qualifying temporal error again. Three/five/nine can test whether inventory and event differences diminish and estimate convergence per observable; even that may not demonstrate an asymptotic regime. Do not assume an order from two meshes.

Nine cells would mean 18 unknowns. Against five, dense finite-difference Jacobian work scales roughly 3.24 times and dense linear algebra roughly 5.83 times per iteration. A planning range of roughly 2–6 times the five-cell run cost is an unmeasured estimate, strongly dependent on nonlinear iterations and adaptive events, not a runtime guarantee. Browser measurements must accompany it. No finer integrated model has been run in this stage.

Keep both meshes available: three as the historical fast baseline, five as the provisional diagnostic choice. Do not select a final production count, integrate the circuit, calibrate equipment or merge on the strength of this comparison alone.

## Reproduction

```sh
node experiments/dx-fv/spatial-test.cjs /tmp/dx-spatial-results.json
python experiments/dx-fv/generate_spatial_reference.py /tmp/dx-spatial-reference.json
DX_FV_SPATIAL_REFERENCE_PATH=/tmp/dx-spatial-reference.json node experiments/dx-fv/spatial-test.cjs /tmp/dx-spatial-live-results.json
node experiments/dx-fv/spatial-browser.cjs /tmp/dx-spatial-browser.json
```

Reference dependencies are pinned to CoolProp 7.2.0, NumPy 2.5.3 and SciPy 1.16.2. Browser execution requires Playwright Chromium/WebKit and their system dependencies. Existing Stage 3, temporal, legacy numerical and source/build checks remain enabled in the workflow.
