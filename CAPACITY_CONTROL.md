# Connected capacity control · v0.5.5 stage 1

## Scope and API

`capacity-controller.js` exports `AmmoniaCapacity` in the standalone browser bundle and a CommonJS module for tests. Stage 1 is an independent controller foundation. It is not called by storage-engine.js or storage-app.js, has no automatic-mode UI, and never assigns a plant pressure, temperature, flow, inventory or valve state. Connected compressor speed remains manual. The existing quasi-steady controller is a separate model.

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

Profiles currently provide compressor count and equipment pressure/temperature trip limits, not calibrated motor speed or response curves. Controller gains, speed-response limits and timing are separately labeled assumptions; this stage does not migrate profile schema or invent manufacturer specifications. Targets and their full deadband must be strictly above the profile low-pressure trip and below both its high-pressure limit and the supported 8 bar target ceiling. Stage 2 must retain independent plant protection checks.

Both modes share sensor, speed, delay and permission checks. Manual follows its speed request; automatic uses lagged suction pressure. With e = sensed pressure − target, the continuous deadband error removes the band's half-width outside the band. The raw automatic request is kp·e + I, bounded to min/max speed. Actual speed follows exponential actuator response with a per-step ramp bound. Integral change is dt·[ki·e + (actual speed − raw request)/trackingSeconds]. This prevents hidden integration growth when requested capacity cannot be delivered. These are numerical controller assumptions, not manufacturer-calibrated closed-loop tuning.

Entering automatic mode tracks actual speed on the first valid observation, avoiding a speed jump. Returning to manual without an explicit request uses actual speed as its request. Explicit requests still follow actuator/ramp response. Running limit edits that exclude actual speed reject; stop first to apply that range. No-op edits change neither timers nor pending time. Other accepted setting edits discard unapplied sub-cadence time and restart a pending start delay.

## Timing and stop priority

The controller uses fixed 0.1-second accepted control intervals; held observations produce the same trajectory across batching. Sub-cadence requests retain pending time. Valid observations/permissions cannot change while pending time is unresolved; a real setting edit can discard it at the accepted boundary. Urgent stop, disable, unavailable or invalid-signal inputs discard an incompatible pending interval and inhibit immediately. Stage 2 must schedule samples at accepted control boundaries, not rejected integration predictors or browser refreshes.

Ordinary `demand=false` honors minimum on time. Operator disable, equipment unavailability, missing pressure and any model stop override that hold immediately. Off telemetry is zero speed/request; a valid restart waits minimum off time plus fresh continuous start delay. A newly stopped controller starts its rest timer at the actual accepted stop time. A latched model stop discards requested/pending time and freezes the controller clock, matching a stopped plant. Clearing belongs to the external model; the controller retains the original supplied snapshot as `lastStop` after clearing and still enforces rest time.

Turning on enters the minimum modeled speed; turning off inhibits capacity immediately. The running ramp limit does not model rotor coast-down, motor acceleration through the unsupported 0–20% range, unloaders, oil interlocks or a measured start sequence. In stage 2, pass the running permission to the compressor and retain a valid 20–100% model speed setting while off; do not feed off telemetry zero into the existing speed validator.

Telemetry reports raw/requested/actual capacity, measured/sensed/target pressure, deadband error, integral, limit reasons, starts, delay/run/rest remaining time and original stop evidence. It is SI and detached from state. Display conversion and charts belong to stage 3; Fahrenheit/psig app defaults remain intact.

## Verification and next stages

The new numerical suite checks control direction/deadband, analytic sensor lag, bounded actuator/ramp response, extended high/low saturation and recovery, mode transitions, cancellation/restart of delays, run/rest timing, urgent-stop priority, invalid-input atomicity, no-op updates, batching, detached evidence, profile isolation and unsupported banks. A 30-second paired plant run proves that observing/calculating independent capacity does not change any connected state/history.

Chromium and WebKit browser suites check the bundled module with iPad emulation, older-browser compatibility, detached SI telemetry, offline execution and unchanged connected controls/readings. Existing physics, plant, history and training suites remain required. Coupled plant stability, timestep refinement with capacity feedback, trips during active automatic control and feed-controller interaction cannot be established until stage 2 connects the module.

1. Stage 1: independent controller contract and tests (implemented).
2. Stage 2: accepted-state integration with conservative plant accounting and independent protection; validate startup/load changes, controller sampling and feed-control interaction.
3. Stage 3: user controls, target/actual trends and limiting reasons. Assess banks separately before adding sequencing.
4. Stage 4: integrated operating/recovery checks, suitable training exercises, browser/offline release polish.

v0.6.0 remains manufacturer/measured equipment calibration. v0.5.0 remains the deployed stable baseline until the new release is approved and merged.
