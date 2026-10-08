# v0.5.0 release acceptance

## Automated coverage

| Area | Evidence |
|---|---|
| Physics and accounting | Property/cycle references, profile/initialization/storage/valve suites and 24 integrated operating/fault/recovery cases; conservative charge and combined room/refrigerant energy, domain/solver limits and timestep refinement. |
| Display consistency | Schematic/current compressor telemetry and history match accepted model states, retain flow intervals, distinguish unavailable/off-state readings and convert SI without mutating it. |
| Guided exercises | All five Default recipes; sustained superheat objectives, correct/incorrect reflections, real disturbances, expected and unexpected trips, restore/clear continuation, incompatible controls and profile guards. |
| Completion timing | Browser 1×, 10× and 60× playback; numerical fractional and 15/60/75/300 s requests. Feed restriction stops at 40 s when complete; no extra pending time leaks into later exploration. Without the reflection, its modeled temperature trip still stops the attempt. |
| Observation purity | A non-stopping accepted-boundary observer yields identical states, controller, counters, history and energy to ordinary advancement. Integration equations remain unchanged. |
| Evidence lifecycle | Exact completion time matches final exported state; selected preview does not relabel the retained attempt; reset clears answers; later free exploration and a trip do not mutate the completed JSON report. |
| Retention and exports | Two hours plus five seconds of actual sealed storage advances through the default 7,201-observation bound, with five dropped samples, retained range and conservative state. SI history/storage CSV and training JSON retain controls, profiles, boundary conditions and original faults. |
| Browser operation | Thirteen Chromium suites; four WebKit suites with iPad configuration. Tabs, keyboard/touch controls, units, older-browser compatibility, background pause, tablet/mobile widths and network-blocked standalone HTML. |
| Build | Rebuild from checked-in source; CI rejects drift in index.html and both existing validation reports. No external browser assets or runtime APIs required. |

Run `npm test`, `npm run build`, `npm run test:browser` and `npm run test:webkit`. Playwright browser installation instructions are in README.md. The training completion hook is optional; ordinary free exploration uses the unchanged advancement path. Training grading remains read-only, and pausing alters only scheduling/pending playback time.

## Demonstration checklist

1. Open the final standalone HTML or, after merge/deployment, the GitHub Pages site in a full browser. Confirm the header says v0.5.0 and the startup notice disappears. Defaults should be Fahrenheit/psig.
2. Open Live plant with Default active. Load DX startup, submit the reflection and advance/play until its measured objectives complete. Inspect the schematic and trends.
3. Select Room load increase without loading. Confirm Selected lesson previews the new brief while Retained attempt still identifies DX startup. Export its JSON before loading the next setup.
4. Load Restricted liquid feed, answer its reflection, apply the disturbance and play at 60×. Completion should pause at 40.0 s with no trip. Reset it without answering and repeat; the temperature trip should remain a stop, not a successful lesson.
5. Load Hot condenser air; observe and inspect the computed discharge-temperature trip, restore off-state inputs, clear and advance ten seconds. Confirm the original fault survives in exported evidence.
6. Try a custom active profile, return to Default, switch display units and inspect charts with touch/keyboard. On a physical iPad, check Firefox/Safari controls, scrolling and the Files/share download workflow. Browser emulation does not replace this physical-device check.

## Release boundaries

Default compressor curves, valve coefficients and heat-transfer assumptions are illustrative. Numerical conservation/property agreement do not establish measured plant accuracy. Connected compressor speed remains manual; automatic suction capacity control is planned for v0.5.5. Oil, entrainment, defrost, multistage behavior and manufacturer/measured calibration remain outside this release; calibration is reserved for v0.6.0.

Attempt state is not persisted across reload. Export it before leaving. History is bounded with explicit removal counters. Custom equipment is available for free exploration, while guided recipes require Default. The reference cycle and quasi-steady room model remain separate from the connected circuit.

GitHub Pages changes only after the release PR is merged and its deployment completes. This checklist documents release acceptance and known scope; it does not claim physical iPad or manufacturer validation.

## v0.5.5 stage 3 acceptance

`tests/capacity-controls-ui.cjs` covers the actual managed UI against SI history exports, pressure/capacity charts, meaningful applied-change events, pressure target/deadband conversion, atomic invalid/no-op edits, mode tracking, rest timers vs playback, explicit legacy reset, training isolation, tablet/phone widths, 44px buttons/selectors and offline/older-browser operation. Both Chromium and WebKit run it. `tests/capacity-plant.cjs` additionally validates combined plant/controller edit transactions and manual-mode request synchronization. Existing regression suites now open the actual settings/training disclosures before interacting with their controls.
