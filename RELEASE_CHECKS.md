# v0.5.5 release acceptance

## Automated coverage

| Area | Evidence |
|---|---|
| Physics and accounting | Existing property/cycle, initialization/storage/valve and 24 integrated operating/fault/recovery cases remain required. Managed tests retain charge and combined room/refrigerant energy checks; conservation does not establish measured plant accuracy. |
| Capacity dynamics | Controller direction/deadband, sensor/actuator/ramp limits, high/low saturation recovery, tracking anti-windup and manual/automatic transitions. Coupled .1/.05/.025 s refinement, accepted-only updates, ten-minute simultaneous suction/feed PI with load changes and mode switches. |
| Demand and timers | Managed ordinary demand is separate from immediate master inhibition. Fractional 7.525 s demand-stop boundary is tested at three timesteps; start/rest, cancellation/fresh delay, no-demand initialization, independent trip priority and frozen clocks/evidence. Legacy/bank behavior is preserved. |
| Atomic edits and display | Combined room/feed/capacity edits reject without partial changes. Excluding actual speed requires a stop-first edit; no-op and SI-preserving unit conversion do not create setting events. Actual compressor state is separate from playback; readings/trends/exports match accepted snapshots. |
| Guided exercises | Five preserved legacy recipes plus three managed recipes: sequential rest/start delay, minimum-run demand hold, and suction-target response. Exact controller settings, master/demand controls and model basis are guarded. Incorrect reflections, incompatible edits, unexpected trips and missing observations cannot earn completion. |
| Completion and evidence | Numerical .25/2.5/15/75/300 s managed requests and browser 1×/10×/60× playback complete at accepted boundaries with no leaked pending time. Capacity starts/stops have exact linked history observations. Frozen JSON contains initial settings, applied actions, final controller and original trips. Later exploration cannot alter finished reports. |
| Retention and exports | Existing two-hour-plus-five-second sealed run covers the 7,201-observation production bound. History/storage CSV retain SI snapshots; managed storage adds run demand. Column alignment, original fault evidence and frozen JSON are checked. |
| Browser operation | Required: 16 Chromium suites and 7 WebKit suites. Includes iPad viewport/touch emulation, all tabs, units, keyboard, background pause, desktop/tablet/phone layout, older-browser compatibility and network-blocked standalone operation. |
| Build | Required: 13 numerical suites and a deterministic source rebuild. CI rejects drift in index.html and the two existing validation reports. The standalone HTML requires no runtime assets or APIs. |

Run `npm test`, `npm run build`, `npm run test:browser` and `npm run test:webkit`. Browser installation instructions are in README.md. The new focused suites are `tests/capacity-release.cjs` and `tests/capacity-release-ui.cjs`; the existing controller, coupled model, training and release suites remain enabled.

Training grading is read-only. A non-stopping accepted-boundary observer yields identical physical/controller state, counters, histories and energy to unobserved advancement. Lesson completion changes only scheduling and discards unused requested time.

## Demonstration checklist

1. Open the final standalone HTML, or Pages after merge/deployment, in a full browser. Confirm v0.5.5, Fahrenheit/psig defaults and disappearance of the startup notice.
2. In Live plant, initialize the DX automatic-feed/manual-compressor example. Select automatic suction PI, reset explicitly, edit the suction target and Apply. Compare target/measured/sensed pressure and requested/actual speed; playback pause is separate from compressor state.
3. Load **Managed compressor startup**, answer its reflection and apply its Enable action before advancing. Observe 3 s rest, 2 s start delay, exact start at 5 s and completion at 10 s. These are shortened lesson assumptions.
4. Load **Minimum-run demand hold**, answer and remove demand. Master permission stays enabled; actual compression continues until 7.5 s, then drops to zero. Completion pauses at 10 s. Inspect Capacity transitions and export the exact-time evidence.
5. Load **Automatic suction target response**, answer and raise the target. The actual 120 s warmup is retained; completion pauses at 150 s when the measured short response is met. This does not claim steady tracking or calibrated tuning.
6. Reset a managed lesson, alter its target/gain/mode and Apply. Confirm interruption. Unit changes alone should keep the lesson active. Select another lesson after completion and confirm the retained attempt/export stays labeled correctly.
7. Demonstrate a modeled trip, restore off-state controls, Apply and clear. Inspect original trip evidence and remaining rest time; clearing alone does not correct operating inputs or establish a real restart procedure.
8. Verify legacy lessons and manual bank profiles still work. On a physical iPad, check Firefox/Safari touch controls, scrolling and the Files/share download workflow. Browser emulation does not replace this device check.

## Release boundaries

This release adds a managed single-compressor speed controller using illustrative response and tuning assumptions. It uses resolved suction pressure to request compressor capacity; it never assigns refrigerant pressure or inventory. Ordinary demand is an explicit external input, not a newly modeled room thermostat. Initial enabled/demanded equipment is a running snapshot with zero run age; initial off equipment has zero rest age. Rotor acceleration through 0–20%, coast-down, unloaders and oil interlocks are not modeled.

Default compressor curves, valve coefficients and heat-transfer assumptions are illustrative. Manufacturer/measured calibration remains v0.6.0. Managed banks/sequencing, oil, entrainment, defrost, multistage behavior and real interlocks remain outside this release. Independent model trips remain active, but completion/recovery is supported-model behavior, not measured equipment qualification.

Attempts are not persisted across reload; export before leaving. Histories are bounded with removal counters. Custom equipment is supported for free exploration; guided recipes require Default. The reference cycle and quasi-steady room model remain separate from the connected circuit. Profile schemas and browser storage keys are unchanged.

The candidate is prepared on PR #3. GitHub Pages changes only after approval, merge and successful deployment. Automated browser coverage does not claim physical iPad or manufacturer validation.
