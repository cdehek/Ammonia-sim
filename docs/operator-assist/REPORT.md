# 🔧 Ammonia Lab — The Mechanic’s Report

Operator Assist v0.1 is an offline diagnostic console for the connected Live Plant model. Open **Operator Assist** beside **Flow animation** in the schematic header. The console shows what the simulator is doing, the readings behind that statement, and a training observation. Close it with **Close ×** or Escape while focus is in the console; focus returns to the entry button.

Based on approved commit `6ab134dfe31f71cbab72c3a4f0ac4c5f3a46a29f`, which exactly matched `ui/coworker-demo-polish-20261013`. Work is isolated on `feature/operator-assist-v0-1-20261013`. No merge or hosting change is part of this milestone.

## Exact simulator inputs

The existing `storage-app.js` renderer passes its already-produced `model.record(state)` and `model.observeCompressor(state)` observations to a pure `AmmoniaOperatorAssist.analyze` function. The console receives only that resulting display projection. It has no engine, state, controls, playback commands, training adapter or write capability.

| Existing input | Interpretation |
|---|---|
| `record.seconds` | Accepted simulated time; separate from wall time and playback speed. |
| `record.operations.circuit` and `vessels.outlet` | Connected DX versus isolated storage; unavailable connected measurements remain unavailable. |
| `record.vessels.outlet.p`, falling back to `evaporator.p` | Current suction boundary pressure; identifies the source volume. |
| `record.vessels.condenser.p` | Current condenser bulk pressure, labeled discharge / condenser pressure. |
| `record.operations.compressorOn` and `.speed` | Applied enablement and speed setting; not evidence of actively advancing equipment by themselves. |
| Existing application `running` flag | Playback advancing versus paused; does not imply every item of equipment is running. |
| `observeCompressor.inhibited`, `.error`, `.massFlow` | Current-state modeled demand availability, positive demand, or explicitly zero demand. No trial compressor calculation is added. |
| `record.flows.superheat`, only for supported connected flows without `flows.error` | Actual current outlet superheat, not the lagged sensor or target. Although port flow rates may represent an accepted interval, this superheat is computed at the current outlet state. |
| `record.controller.opening` | Actual accepted valve actuator position in the connected circuit. |
| `record.flows.command` and `record.operations.valveMode` | Current applied valve command and mode, separate from actual opening. The console never substitutes a draft manual setting for this observation. |
| `record.fault.kind`, `.message`, `.seconds` | Active latched equipment trip, solver stop or domain stop; original reason and detection time take precedence over ordinary commentary. |
| `fault.readings.pressure`, `.condensing`, `.discharge`, `.speed` | Captured stop evidence, shown separately from current ordinary readings. Missing captured values are labeled **Unavailable**. |
| `fault.limits.highTrip`, `.lowTrip`, `.dischargeTrip` | The recorded equipment profile threshold, selected only for the existing exact high-pressure, low-pressure or discharge-temperature trip reason. The captured comparison is shown without guessing a root cause. |
| `fault.attemptedReadings` presence | Notes that rejected-trial evidence is retained separately in history; never substitutes it for accepted captured readings. |
| Existing selected display units | SI values remain unchanged. Absolute bar → gauge subtracts 1.01325 bar; psi conversion uses the existing factor 14.503773773. Celsius → Fahrenheit absolute adds 32; superheat differences multiply by 1.8 only. |
| Existing `renderDraft()` dirty result | Warns when draft controls differ from applied settings or are invalid; analysis continues using accepted observations. |

Retained history is available through the existing Trends & history interface. This version does not infer historical changes, trends or causes from it. After clearing a latch, old retained faults remain in history but no longer appear as the active diagnosis. Reset or profile change removes the connected snapshot, preventing stale stop evidence.

## Interpretation boundaries

The rules distinguish initialization, paused playback, advancing playback, disabled compressor settings, supported compressor demand and recorded stops. They explain actual valve position versus command, outlet superheat and recorded trip comparisons. Isolated-storage operation points learners to inventory and thermal boundaries.

They cannot establish real-plant safety, diagnose an unmodeled fault, infer root causes, predict recovery, prescribe field procedures or certify a repair. A changing value alone is not diagnosed as a fault. Clearing a latch is explicitly distinguished from repairing its underlying issue. Generic equipment models remain illustrative, with no added calibration claim.

There is no unrestricted chat, external inference, voice input/output, artificial loading or typing sequence, network request, remote asset or new dependency. The subtle operating indicator honors reduced motion. Status changes use a polite live region; accepted readings update automatically without repeatedly announcing every sample. The contained console does not overlay the schematic. The entry button leaves the existing plant-title and playback controls in their approved layout.

## Demonstration evidence

All nine images come from actual browser-operated simulation states, with a fixed test clock. Desktop is 1440×1000, iPad landscape 1024×768, and iPad portrait 768×1024.

| State | Desktop | iPad landscape | iPad portrait |
|---|---|---|---|
| Paused, enabled at 70% | [Image](screenshots/paused-desktop.png) | [Image](screenshots/paused-ipad-landscape.png) | [Image](screenshots/paused-ipad-portrait.png) |
| Playback advancing | [Image](screenshots/running-desktop.png) | [Image](screenshots/running-ipad-landscape.png) | [Image](screenshots/running-ipad-portrait.png) |
| Actual equipment trip | [Image](screenshots/trip-desktop.png) | [Image](screenshots/trip-ipad-landscape.png) | [Image](screenshots/trip-ipad-portrait.png) |

The trip images use the existing **Hot condenser air** exercise with the Default equipment profile and its real disturbance, advanced until the model records **High discharge temperature**. No fault is injected and no threshold is lowered for these screenshots. The captured discharge temperature is approximately 338.29 °F against the recorded 338.00 °F modeled threshold, at 65.125 simulated seconds. A real model-domain stop is also exercised in browser coverage using an all-liquid receiver and prescribed test heat. A real solver stop is exercised numerically with the existing strict integration-tolerance configuration; solver settings in the shipped simulator are unchanged.

## Verification

`tests/operator-assist.cjs` covers uninitialized and unsupported records; paused/enabled; advancing; compressor off, zero demand and unavailable demand; real equipment, solver and domain stops; clear/reset; missing data; four pressure units; absolute temperatures versus superheat differences; drafts; deeply frozen inputs; and exact equality of the entire evolving simulator state with and without repeated analysis. Equality includes controller, pending time, counters, rows and retained history.

`tests/operator-assist-ui.cjs` covers lifecycle updates, accepted reading agreement, draft/applied separation, real Default thermal trip, actual domain stop, stale evidence removal after clear/reset/profile changes, focus return, Enter/Space/Escape, touch targets, tablet/mobile widths, reduced motion and standalone startup with HTTP requests blocked. It also compares full exported SI trajectories after the same model operations with the panel open versus closed and different display units.

Final test results and any matched baseline browser failure are recorded in `verification.md`. Browser emulation verifies iPad-sized layout and touch interaction; it is not a physical iPad test.

## Changed files

- `operator-assist.js`: deterministic, read-only interpretation and display-unit projection.
- `operator-assist-app.js`: accessible contained console, rendering and open/close behavior.
- `storage-app.js`: four display-integration additions using existing records and dirty-state detection.
- `live-schematic.js`: entry button beside the existing animation control; no schematic model logic changed.
- `app.template.html`: console container, matching industrial styles, responsive layout and reduced motion.
- `tools/build.py`: inline the two new scripts in standalone HTML.
- `index.html`: regenerated standalone build.
- `package.json`, `tests/run-browser.cjs`: register focused deterministic and Chromium/WebKit tests.
- `tests/operator-assist.cjs`, `tests/operator-assist-ui.cjs`: focused verification.
- `docs/operator-assist/REPORT.md`, `verification.md`, logs, source hashes, matched WebKit resize evidence, manifest and nine screenshots: review evidence. [Exact manifest](changed-files.txt).

No physics, properties, numerical methods, limits, control algorithms, conservation accounting, training grading or playback scheduling were changed. The new feature neither advances nor pauses the model. Existing browser and scientific assertions are preserved.
