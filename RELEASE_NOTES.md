# Ammonia Lab v0.5.5 · stage 4 release candidate

- Completed managed single-compressor manual/automatic suction capacity control while preserving legacy manual/bank behavior and Fahrenheit/psig defaults.
- Connected ordinary run demand separately from master permission. Demand withdrawal honors minimum run; master disable and independent stops inhibit immediately. Fractional demand-stop deadlines are accepted plant boundaries with exact history evidence.
- Added initialization and pending-mode guidance, visible stop-first instructions for excluding speed limits, a Capacity transitions filter, and demand/controller snapshots in SI exports.
- Added three measured Default lessons: delayed managed startup, minimum-run demand hold, and automatic suction target response. Fixed controller/input guards prevent incompatible edits from earning completion. Timing lessons label shortened assumptions; reports freeze on completion.
- Release checks cover sustained coupled operation, high/low saturation recovery, demand cancellation/restart, trips/clear evidence, mode switching, timestep refinement, batching, conservation, grading and frozen exports. Required regression: 13 numerical suites, 16 Chromium suites, 7 WebKit suites, source/bundle consistency and offline/older-browser operation.
- Manufacturer/measured calibration remains v0.6.0. Managed capacity still requires one compressor; connected bank sequencing, oil, defrost and rotor start/coast-down physics remain outside scope.
- Prepared on PR #3; the deployed v0.5.0 baseline changes only after approval, merge and Pages deployment.

# Ammonia Lab v0.5.5 stage 3

- Added connected legacy/managed manual/automatic capacity selection, suction targets, running-speed bounds and illustrative response/timing settings. Legacy remains default; managed control requires one compressor and explicit initialization.
- Added applied target/requested/actual capacity readings, true compressor state separate from playback, limiting reasons and remaining timers. Managed mode switching tracks actual speed.
- Added suction target/measured/sensed and requested/actual capacity trends, converted capacity-edit details/filtering and SI snapshots in both CSV routes. Combined form edits validate atomically.
- Incorporated all six UI review fixes: full-width tablet workspace with collapsible reference calculator; schematic/controls first with folded training/settings/diagnostics; distinct capacity/feed/model wording; actual compressor status/speed; enlarged touch targets/text; capacity trend/event presentation.
- Preserved Fahrenheit/psig defaults, legacy banks, fixed training recipes, offline bundling and older-browser compatibility. Pressure draft formatting retains SI precision across unit changes.
- Added a managed-controls Chromium/WebKit suite and transactional numerical checks. Required regression is twelve numerical suites, fifteen Chromium suites and six WebKit suites. Stage 4 remains training/integrated release polish; v0.6.0 remains equipment calibration.

# Ammonia Lab v0.5.5 stage 2 · opt-in plant capacity feedback

- Coupled suction PI and delivered compressor speed to conservative circulating physics; accepted adaptive steps alone advance controller time.
- Exact fractional stop/rest timestamps and start deadlines; independent equipment, domain and solver stops retain original evidence and inhibit output.
- Preserved legacy manual/default/bank/training behavior. Managed single-compressor capacity is explicit at initialization; full UI arrives in stage 3.
- Separate user settings, requested/actual speed and measured/sensed/target pressure in detached history and managed CSV. Smooth controller updates create no user-action events.
- Added coupled conservation, load/feed interaction, switching, fault/recovery, batching/refinement and bundled iPad browser checks. Generic equipment/control assumptions remain uncalibrated.

# Ammonia Lab v0.5.5 stage 1

Adds a standalone, single-compressor capacity-controller foundation: manual/automatic suction PI, absolute-pressure targets and deadband, speed bounds, sensor/actuator/ramp response, start/minimum run/rest timing, mode tracking and anti-windup against delivered capacity. Operator disable, missing signals, unavailable equipment and original model stops inhibit output with priority over ordinary demand holds. Validation is atomic, no-op edits preserve timing, and accepted cadence prevents batching-dependent results.

The module is bundled but not connected to storage integration or user controls yet. No refrigerant equations, valve controls, saved profile schemas or existing manual bank behavior change. Controller response assumptions remain illustrative; targets respect profile pressure limits. Stage 2 must validate the actual coupled loop and preserve independent protection. See [CAPACITY_CONTROL.md](CAPACITY_CONTROL.md).

New numerical and Chromium/WebKit foundation suites cover response, limits, saturation recovery, switching, timers, stops, invalid/no-op inputs, batching, detached SI evidence, single-compressor scope, offline/older-browser execution and unchanged plant trajectories/readings. Required regression now comprises eleven numerical suites, fourteen Chromium suites and five WebKit suites with iPad emulation.

# Ammonia Lab v0.5.0

Live plant now combines an accepted-state equipment schematic, synchronized trends/event history and five guided Default exercises with measured objectives, reflections, hints and exportable debrief evidence.

Stage 4 fixes fast-playback overshoot: exercise grading observes committed outer integration boundaries within a request, stops at completion and discards unused time. A short restriction lesson therefore completes at 40 s instead of continuing into a later starvation trip. Missing reflections still allow the modeled trip to occur. A non-stopping observer produces identical physical states and history to a run without it; the integration equations are unchanged.

The selected lesson preview and current/retained attempt now have separate labels. Selecting another lesson preserves the original objectives, reflection, debrief and report under the retained-attempt heading. Reset/export buttons identify the retained attempt. Loading another lesson explicitly replaces it. Exported completion evidence remains unchanged after subsequent free exploration and stops.

Final release checks cover all five recipes; 1×/10×/60× browser playback; large/fractional advancement; exact completion/fault timing; discarded pending time; original trip evidence; wrong controls/reflections; report freezing; selected/retained content; Default/custom profile guards; units; two hours of actual sealed-storage advancement through the production history-retention limit; mobile layouts; offline operation and source/bundle consistency. The suite comprises ten numerical suites, thirteen Chromium suites and four WebKit suites. WebKit uses iPad emulation, not physical hardware. See [RELEASE_CHECKS.md](RELEASE_CHECKS.md).

Connected automatic suction capacity control remains v0.5.5; manufacturer/measured calibration remains v0.6.0. Default equipment and training outcomes remain illustrative supported-model behavior.

# Ammonia Lab v0.5.0 stage 3

Five guided exercises now load repeatable Default connected-circuit setups: startup, increased room load, hot condenser air, short feed restriction and superheat target response. Disturbances use the existing model controls and boundaries. Objectives grade accepted observations, sustained superheat bands and original fault evidence; a correct reflection is also required. Hints, reset/end controls, debrief and full SI JSON evidence are available offline.

Exercises pause on completion or interruption. Unplanned changes, custom equipment, unexpected stops and missing retained observations cannot silently earn completion. The hot-air exercise requires restored off-state inputs and ten simulated seconds after clearing; clearing alone does not qualify. Exported finished evidence stays frozen during subsequent exploration. Loading replaces the connected run without editing saved profiles.

No integration equations changed. History observations additionally retain accepted feed/drain flow and its interval for grading/export. Verification covers ten numerical suites, thirteen Chromium suites and four WebKit suites in CI, including all five outcomes, negative paths, conservation, read-only grading, batching, units, keyboard/touch controls, responsive layouts and offline HTML. WebKit uses an iPad configuration, not physical hardware. See [TRAINING_SCENARIOS.md](TRAINING_SCENARIOS.md); stage 4 release polish is next, with calibration still reserved for v0.6.0.

# Ammonia Lab v0.5.0 stage 2

Connected trends now share simulated time, an exact observation cursor and selectable time windows. Pressure, temperature, actual/sensed/target superheat, command/actual valve opening, liquid volume fraction and compressor electrical demand can be inspected independently or together. Curve visibility controls, follow/pinned inspection, touch and keyboard navigation work offline on tablet/mobile layouts.

Nominal one-second observation sampling runs at accepted model boundaries, independent of playback/batching. Exact-time before/after applied changes, stop/clear snapshots and playback actions preserve causal order. Invalid/no-op updates do not create control-change events, and clearing retains original stop evidence. Long plots preserve bucket extrema/gap boundaries while inspection/export retains exact observations.

History is bounded to 7,201 observations and 2,000 events, with visible retained ranges/removal counts. Reset/equipment changes start a new run. A separate SI history CSV includes applied profile, initial room, per-observation controls/boundaries and original fault snapshots; existing storage CSV/profile schemas remain unchanged. See [TRENDS_HISTORY.md](TRENDS_HISTORY.md) for interpretation and retention.

The new numerical history suite verifies batching invariance, model agreement, rejected-update atomicity, fault evidence and retention. Chromium/WebKit history suites cover controls, units, event inspection, CSV, reset, tablet/mobile and offline behavior. Training scenarios remain stage 3; v0.6.0 equipment calibration remains on [ROADMAP.md](ROADMAP.md).

# Ammonia Lab v0.5.0 stage 1

Live plant now shows the connected refrigerant circuit as a live schematic. Vessel fills, pressure, temperature, phase, valve opening and supported flow direction follow the storage model's accepted state. Equipment inspection works through touch and keyboard controls. Compressor current-state demand supplies discharge temperature and electrical demand independently of condenser bulk temperature. Off/latched-stop demand is suppressed; animation pauses with playback and respects reduced motion.

The display labels accepted port-flow intervals and distinguishes them from current-state compressor demand. Isolated storage uses its actual evaporator suction path; profile changes clear stale readings. Tablet/mobile scrolling and offline standalone operation are covered by the new schematic browser suite in Chromium and WebKit CI. A numerical telemetry suite verifies energy consistency, observational purity and identical trajectories with/without display sampling. No integration equations, equipment profile schemas or saved profile keys changed.

Trend/event improvements and training scenarios are subsequent v0.5.0 stages. Connected automatic suction capacity control is planned for v0.5.5; manufacturer/measured equipment calibration is reserved for v0.6.0. See [LIVE_SCHEMATIC.md](LIVE_SCHEMATIC.md) and [ROADMAP.md](ROADMAP.md).

# Ammonia Lab v0.4.5

This release integrates equipment inventory, conservative storage dynamics, pressure-driven valve flow and outlet superheat control. It keeps the existing reference-cycle calculator and quasi-steady room/control model separate from the connected refrigerant model.

## Demonstrate it

1. Open the deployed site or standalone HTML in a full browser.
2. Select Live plant and use Default equipment, or a custom profile with configured inventory/connections.
3. Click **Initialize automatic DX example**, then **Start storage** or **Advance 10 seconds**.
4. Change ambient air, heat gain, feed mode, drain availability or compressor speed and Apply. Observe pressure, actual/sensed superheat, valve response and conservation metrics. Pause and export SI CSV for the exact profile, controls and fault evidence.

The example initializes an automatic feed at a 9 °F difference (5 K) target and manual 70% compressor speed. It resets the circuit and loads illustrative boundaries. Initial room temperature/heat capacity come from applied room conditions; changing either requires reinitialization. Custom profiles may reach a modeled limit with these example controls. No live run is restored on reload.

## Stage-4 fixes

- Domain/solver stops report the retained accepted state, timestamp and exact limits. Predictor readings are separate attempted evidence.
- A paired liquid-phase transport limiter handles dry receiver/condenser transitions without repairing mass or energy. Phase exhaustion is checked at three step sizes.
- Runtime ambient, room gain and leakage changes validate atomically and appear in history even when exported immediately after Apply.
- CSV includes initial/current room snapshots, per-row boundaries and full fault snapshots. Sampled port flow intervals distinguish accepted flow from instantaneous demand.
- The Model & validation view includes the deterministic integrated release report. The quasi-steady room model is labeled separately, and outdated inventory-scope statements are corrected.

## Verification

`npm test` runs seven suites: property/cycle references, quasi-steady dynamics, equipment profiles, initialization, storage, valve control and integration. `npm run build` embeds both validation reports and all code/data in one HTML file. GitHub CI regenerates the reports/build and checks for source drift. Browser verification runs ten Chromium suites and a WebKit release suite with an iPad device configuration; this emulates browser behavior and viewport, not a physical iPad hardware test.

The published report rounds operating readings to 0.001 SI, case residuals to 1e-9 kg / 1e-7 kJ, and maximum residual/refinement bounds upward to two significant digits. This makes evidence reproducible across supported runtimes; all physical/accounting assertions use full precision.

The integrated report contains 24 operating/fault/recovery cases: startup, load changes, full-speed/manual operation, blocked drain, off-state retained pressure, wet restart/recovery, high/low/discharge trips and recovery, feed starvation, unavailable liquid, custom efficiencies, property/tolerance stops, hot-condenser phase exhaustion and live boundaries. It also checks invalid-update rollback, fault/playback batching and geometry feasibility.

Observed maximum integrated residuals are approximately 2.0e-13 kg charge and 2.6e-9 kJ combined energy. Refining a 30-second Default run from 0.1 to 0.05-second outer steps with half tolerance changes outlet pressure by approximately 1.57e-5 bar, room temperature by 2.14e-10 K and electrical energy by 4.21e-9 relative. The 40 °C condenser-air case produces consistent temperature trips near 64.525 s at 0.1/0.05/0.025-second steps, with condenser-pressure differences below 0.0001 bar. Assertions use broader numerical tolerances; these observed values are not universal error bounds.

The earlier 600-second Default automatic test remains enabled and settles near 5.0165 K outlet superheat. Existing 560 single-phase/160 saturation property checks, 159 full-cycle comparisons, 17 manufacturer saturation-fit checks and 90 direct density/internal-energy storage references remain enabled.

## Scope

The EOS grid is bounded and no state or valve vapor-pressure request is extrapolated. Valve areas/recovery factors, compressor curves and lumped UAs are generic example assumptions. Ideal phase selection excludes entrainment; wet suction stops the supported compression model and is not a modeled real safety device. Gravity head is an external work boundary. Conservation verifies accounting, not measured plant accuracy.

Compressor bank speed in the connected model remains manual. Automatic suction capacity control and compressor sequencing belong to the separate quasi-steady model. Metal/pipe/compressor/valve holdup, oil, noncondensables, defrost, latent loads, manufacturer-calibrated valve/heat-transfer behavior and two-stage intercooling remain outside this release. Live schematic and training scenarios remain planned for v0.5.0.
