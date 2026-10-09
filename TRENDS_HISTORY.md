# Connected trends and event history · v0.5.0 stage 2

Open **Live plant → Initialize automatic DX example**, then Start storage or Advance 10 seconds. Below the inventory diagnostics, **Trends & event history** shows pressure, temperature, outlet superheat, valve opening/command, liquid volume fraction and compressor electrical demand. Use View to select a chart, Window to change the time range, and the curve checkboxes to show/hide series.

All charts use the same simulated-time axis and inspection cursor. Previous/Next, the sample slider or a chart tap pin an exact retained observation. Uncheck Follow newest to inspect without stopping playback; recheck it to return to the latest observation. Event inspection jumps to its associated observation, with recorded changes or fault evidence. The event filter selects applied changes, stops/clearing or playback actions.

## Observation timing and physical meaning

- History sampling runs inside the model at accepted outer-interval boundaries, nominally every **1 simulated second**, independent of browser refresh rate, playback speed and advance batching. Exact accepted timestamps are stored, not rounded or invented. Alternate numerical step sizes may cross a sampling deadline slightly later.
- Initialization, applied changes, stops, clearing and playback actions add exact-time observations. Before/after applied changes can have the same timestamp; sequence IDs preserve their order. Periodic sample spacing therefore does not imply every adjacent record is one second apart.
- Every plotted state is recovered from accepted stored mass/internal energy or computed by the existing controller/observation routines. Plotting does not change integration equations, equipment settings or physical state. Compressor discharge temperature and electrical demand are instantaneous model demand, not interval-average measurements.
- Isolated storage has no resolved outlet or valve/superheat trace. Unsupported/inhibited readings are null and shown as gaps, never filled with zero. Actual valve position remains separate from its command and sensor superheat remains separate from actual outlet superheat.
- Straight segments connect observations. For long plots, time buckets retain first/last values, extrema and gap boundaries; plots do not represent additional simulated states. The cursor, legends and CSV always use exact retained observations. Superheat target changes are drawn as steps.
- Event markers use exact recorded times. Applied changes are orange, stops red, and initialization/playback/clearing gray. Up to 100 markers per displayed time range are shown; the event table shows the latest 100 matching retained events.

## Events and retention

The event log records initialization, accepted control/boundary changes, start/pause, manual advance requests, playback speed changes, model/solver/equipment stops and stop clearing. No-op Apply and invalid changes produce no control-change event. A manual advance entry records the **request**, not a promise that the model reached the requested time. Backgrounding the browser records a pause when playback was running.

Stops capture their original full SI fault snapshot, including retained readings, configured limits and separate attempted trial evidence when present. Clearing adds a new entry and preserves the original event; it permits another attempt and does not establish physical recovery or correction. The existing storage CSV retains its independent per-advance history and format.

Each run retains at most **7,201 observations** and **2,000 events**, with removal counters and actual retained time range shown. Without extra action records, observations cover approximately two simulated hours; frequent actions shorten that span. Initialization/reset or applying different equipment starts a new history. Runs do not persist across reloads. Export before resetting or before older data is removed.

**History CSV · SI** exports schema 1, the exact applied equipment/initial room snapshots, retention counters, observations and events as chronological CSV records with explicitly labeled SI numerical columns and full quoted JSON details. Missing readings have blank cells, not zeros. Each observation includes the applied operations and room boundaries. IDs are independent sequences for observations and events; an event's sampleId links to its observation if still retained. This adds a portable history export without changing saved equipment/profile schemas.

## Verification

`tests/history.cjs` verifies fixed simulated-time sampling, batching invariance, accepted-state agreement, same-time control ordering, atomic invalid-input rejection, no-op suppression, exact fault/clear evidence, retention, SI conversion/export, absent-phase gaps and peak-preserving plot reduction. `tests/history-ui.cjs` exercises follow/pinned inspection, curve selection, chart/event controls, applied changes, fault clearing, units, keyboard/touch interaction, CSV, reset, tablet/mobile layout and offline operation. CI runs the browser suite in Chromium and WebKit with an iPad device configuration; this is not a physical iPad hardware test.

## v0.5.5 stage 3 capacity observations

Managed runs expose suction target/measured/sensed pressure and requested/actual speed as separate curves. Targets convert as absolute pressures; speed is a fraction converted to percent. The initial view is Suction control for managed histories and Pressures for legacy histories; All trends remains available. Capacity-setting edits appear in Applied changes and show converted before/after values. Raw SI settings/evidence remain in CSV. Automatic control ticks create no user action events.
