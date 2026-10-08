# Connected capacity control · v0.5.5 stage 3

## User controls and workspace

Stage 3 connects the explicit managed-capacity API to Live plant. Initialize the automatic-feed DX example, select managed manual or automatic suction PI, then initialize/reset the circuit. Apply edits to the active managed mode through the operating controls. The UI defaults to legacy manual and retains training/bank behavior. Managed modes require one compressor and circulation. Legacy/managed basis changes require explicit reset; manual/automatic managed transitions track actual speed.

Targets use the selected pressure display units; deadband is a difference with no atmospheric offset. Pressure inputs display six decimal places at most while retaining unchanged SI drafts across conversion. Gains keep their labeled SI basis. Compressor speed is a manual request, not automatic delivered output. Mode, applied pressure target, requested/actual speed, compressor ON/OFF, playback state, limits and remaining delays are shown separately.

The reference calculator is collapsible in Live plant and its shared unit selectors remain available. The schematic and primary capacity controls precede configuration. Room/feed settings, test heat/tuning, diagnostics and guided training use disclosures; faults reveal diagnostic evidence. Routine buttons/selects and checkbox labels/history cursor have 44px touch targets. Tablets show the full schematic; narrow phones retain horizontal diagram scrolling. Navigation links jump to schematic, trends, equipment and exercises.

Managed histories add suction target/measured/sensed pressure and requested/actual speed series. Capacity setting events appear under Applied changes with meaningful converted descriptions. Legacy defaults to the pressure view; managed runs default to suction control; All trends remains available. Both CSV routes retain separate SI capacity snapshots and signals.

`storage.update(state, operations, roomBoundary, capacityPatch)` validates combined form edits before changing state/history. A rejected capacity target cannot partially apply a room load, feed setting or manual request. A live transition to managed manual without a changed manual request tracks actual speed and synchronizes the applied operation speed. No-op settings and unit conversions preserve controller timing and add no setting events.

## Scope and API

`capacity-controller.js` exports `AmmoniaCapacity` in the standalone browser bundle and CommonJS tests. Stage 2 explicitly couples it to the conservative circulating plant. The controller never assigns a pressure, temperature, inventory, valve flow or heat balance. Compressor work and mass flow use delivered speed. The quasi-steady controller remains a separate model.

`storage.create(profile, room, operations, capacitySettings)` opts in with a fourth argument; omitted/null retains the existing manual plant, including bank profiles and training behavior. Managed capacity supports exactly one compressor and requires a circulating circuit. An initially enabled compressor starts from the supplied valid running speed with zero elapsed run age; initially disabled equipment starts with zero rest age and must wait its configured rest/start delay. `operations.compressorOn` remains the operator permission and `operations.speed` remains the user setting. Neither is overwritten by automatic output.

`storage.updateCapacity(state, patch)` changes managed settings atomically and records one settings event with before/after samples. Existing `storage.update` edits master permission/manual speed and room/feed controls. No-op settings edits preserve timing and generate no event. A mode change to manual without a speed request tracks actual speed; a later speed-setting edit supplies a new request. Controller settings and the legacy slider value are distinct records.

`storage.record(state).capacity` and history sample `.capacity` hold detached SI settings, requested/actual speed, measured/sensed/target suction pressure, timing and limits. Automatic ticks do not produce user control events. Managed CSV exports add labeled capacity columns and retain complete JSON evidence; legacy CSV layout and history are unchanged. The opt-in API and user controls are exercised by numerical/browser tests.
`create(profile, settings, initial)` normalizes an equipment snapshot and accepts exactly one compressor. Initial state supports `running` and `speed`; elapsed run/rest age starts at zero, never an invented history. `advance(state, seconds, input)` consumes a held accepted pressure observation and permissions. `update(state, patch)` validates setting edits atomically. `record(state)` returns a detached SI telemetry snapshot. Unsupported banks are rejected by this new module; existing manual bank profiles continue working unchanged in the plant.

Inputs are `pressureBarAbsolute`, `enabled`, `demand`, `available` and `stop`. Pressure must be a number or null. Null, nonfinite or out-of-grid (0.3–35 bar absolute) readings inhibit operation in either mode. Incorrect types/settings reject without changing state. `enabled` is the operator master permission; `demand` is ordinary run demand, and `available` is an external equipment permission. A supplied stop must be an existing equipment/domain/solver snapshot with message and detection time. The controller does not detect new equipment trips, clear a model stop, infer discharge protection from suction pressure, or decide whether real equipment is safe to restart.

## Illustrative settings

| Setting | Default | Meaning |
|---|---:|---|
| Mode / manual speed | manual / 70% | Manual requested capacity while running. |
| Suction target | 2.5 bar absolute | Approximately 21.6 psig at the app's 1.01325 bar reference atmosphere. |
| Minimum / maximum speed | 20% / 100% | Supported connected-model speed envelope; narrower user ranges are allowed. |
| Proportional / integral gain | 0.45 fraction/bar / 0.003 fraction/(bar s) | Positive suction-pressure error requests greater compressor capacity. |
| Deadband | ±0.05 bar | Error is zero inside the band, continuous outside it. |
| Pressure sensor / actuator response | 2 s / 30 s | First-order lag assumptions. |
| Ramp limit | 0.02 fraction/s | At most two percentage points per second while running. |
| Integral tracking response | 10 s | Back calculation tracks delivered capacity under saturation, actuator and ramp limits. |
| Continuous start delay | 3 s | Applied after minimum rest expires, while valid demand persists. |
| Minimum run / rest time | 90 s / 90 s | Ordinary demand-stop hold and restart hold. |

Profiles currently provide compressor count and equipment pressure/temperature trip limits, not calibrated motor speed or response curves. Controller gains, speed-response limits and timing are separately labeled assumptions; this stage does not migrate profile schema or invent manufacturer specifications. Targets and their full deadband must be strictly above the profile low-pressure trip and below both its high-pressure limit and the supported 8 bar target ceiling. Independent plant protection checks remain active in both capacity modes.

Both modes share sensor, speed, delay and permission checks. Manual follows its speed request; automatic uses lagged suction pressure. With e = sensed pressure − target, the continuous deadband error removes the band's half-width outside the band. The raw automatic request is kp·e + I, bounded to min/max speed. Actual speed follows exponential actuator response with a per-step ramp bound. Integral change is dt·[ki·e + (actual speed − raw request)/trackingSeconds]. This prevents hidden integration growth when requested capacity cannot be delivered. These are numerical controller assumptions, not manufacturer-calibrated closed-loop tuning.

Entering automatic mode tracks actual speed on the first valid observation, avoiding a speed jump. Returning to manual without an explicit request uses actual speed as its request. Explicit requests still follow actuator/ramp response. Running limit edits that exclude actual speed reject; stop first to apply that range. No-op edits change neither timers nor pending time. Other accepted setting edits discard unapplied sub-cadence time and restart a pending start delay.

## Timing and stop priority

The controller uses fixed 0.1-second accepted control intervals; held observations produce the same trajectory across batching. Sub-cadence requests retain pending time. Valid observations/permissions cannot change while pending time is unresolved; a real setting edit can discard it at the accepted boundary. Urgent stop, disable, unavailable or invalid-signal inputs discard an incompatible pending interval and inhibit immediately. The plant adapter uses `advanceAccepted` at every accepted adaptive endpoint, with an interval no larger than 0.1 s. It holds delivered speed across each physical substep, then updates sensor/actuator/PI from the accepted endpoint pressure for the next interval. This causal split is first-order in the coupling interval; .1/.05/.025 s refinement is tested. Rejected trials never mutate controller state. Start/rest deadlines split physical intervals so startup is not shifted to the next outer step. No work is assigned to an endpoint-only start. Controller and plant clocks consume the same accepted dt, including fractional stops, and no unused playback is consumed.

`advanceAccepted(state, dt, input)` supports 0–0.1 s with no standalone pending time. A stop input must match its exact accepted clock. Zero-time inhibition/clearing observes permissions without inventing elapsed time. Standalone `advance` can reconcile a fractional stop inside previously requested pending time using the original held observation; it rejects stop timestamps outside that requested interval.

Ordinary `demand=false` honors minimum on time. Operator disable, equipment unavailability, missing pressure and any model stop override that hold immediately. Off telemetry is zero speed/request; a valid restart waits minimum off time plus fresh continuous start delay. A newly stopped controller starts its rest timer at the actual accepted stop time. A latched model stop discards requested/pending time and freezes the controller clock, matching a stopped plant. Clearing belongs to the external model; the controller retains the original supplied snapshot as `lastStop` after clearing and still enforces rest time.

Turning on enters the minimum modeled speed; turning off inhibits capacity immediately. The running ramp limit does not model rotor coast-down, motor acceleration through the unsupported 0–20% range, unloaders, oil interlocks or a measured start sequence. The adapter passes actual running/speed to compressor calculations while retaining a valid user speed setting when off. Clearing a plant stop retains original evidence and starts no automatic bypass of the rest/start delay.

Telemetry reports raw/requested/actual capacity, measured/sensed/target pressure, deadband error, integral, limit reasons, starts, delay/run/rest remaining time and original stop evidence. It is SI and detached from state. Display conversion and charts are implemented in stage 3; Fahrenheit/psig app defaults remain intact.

## Verification and next stages

The new numerical suite checks control direction/deadband, analytic sensor lag, bounded actuator/ramp response, extended high/low saturation and recovery, mode transitions, cancellation/restart of delays, run/rest timing, urgent-stop priority, invalid-input atomicity, no-op updates, batching, detached evidence, profile isolation and unsupported banks. A 30-second paired plant run proves that observing/calculating independent capacity does not change any connected state/history.

Chromium and WebKit browser suites check the bundled module with iPad emulation, older-browser compatibility, detached SI telemetry, offline execution and unchanged connected controls/readings. Existing physics, plant, history and training suites remain required. The coupled numerical suite checks conservative balances, simultaneous feed PI, load changes, mode/manual transitions, accepted-only timing, exact fractional stops and start deadlines, equipment/domain/solver inhibition and recovery, detached history without tick events, legacy/bank compatibility, batching and .1/.05/.025 s refinement. Browser checks run the opt-in plant API inside the standalone bundle. Setpoints can be unattainable at a speed limit; generic PI assumptions do not guarantee every profile/load is stable or establish measured plant accuracy.

1. Stage 1: independent controller contract and tests (implemented).
2. Stage 2: accepted-state integration, accounting/protection and coupled verification (implemented).
3. Stage 3: user controls, target/actual trends, limiting reasons and six workspace/UI improvements (implemented). Bank sequencing remains outside this release.
4. Stage 4: integrated operating/recovery checks, suitable training exercises, browser/offline release polish.

v0.6.0 remains manufacturer/measured equipment calibration. v0.5.0 remains the deployed stable baseline until the new release is approved and merged.

Stage 3 verification adds a Chromium/WebKit user-path suite for model/export agreement, automatic startup, mode tracking/rest status, signal charts, capacity events, atomic invalid/no-op edits, SI-preserving target/deadband conversion, legacy reset, training isolation, tablet/phone layout, touch sizes and offline/older-browser execution. Existing controller, plant and training suites remain required.
