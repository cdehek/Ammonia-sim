# Live Plant — HMI visual uplift

This pass builds on the current pending work on `ui/coworker-demo-polish-20261013`, whose committed base is `1abbc39387232029b4f4f98f33241dbee80c51c6`. The before screenshots use the actual working UI at the start of this request, not an earlier Git commit. Baseline standalone HTML SHA256: `fcee1ae40d8d01b82fc944a8093f19e7fd77b038184ad35d9a62be08482f1ec6`.

## What changed and why

| Area | Change | Operator benefit |
| --- | --- | --- |
| Console framing | Near-black background, blue-steel panel faces, section-edge strips, compact uppercase headings, stronger borders and inset instrument surfaces | Separates instrumentation, process overview, controls and supporting information without moving them |
| Operating readings | Larger desktop numerals, distinct units, cyan low-side/feed emphasis, amber high-side emphasis | Makes primary readings easier to scan; section colors do not imply faults |
| Micro-trends | Five small SVG traces from retained pressure, room-temperature, actual-superheat and actual-valve-opening history | Shows recent direction beside the current values, using only actual recorded data |
| State handling | Neutral paused/off states, green running, red equipment trips, amber model/numerical stops; matching header, state mark, schematic text and persistent Live Plant tab indicator | Separates playback, compressor state and genuine stop severity |
| Equipment | Richer steel gradients, beveled housings, dimensional fins/coils, mechanical trim, glass-indicator highlight and restrained equipment shadows | Makes the existing circuit the visual centerpiece without adding machines or changing geometry |
| Pipework | Dark backing, thin surface highlight, clearer active/inactive contrast | Improves line continuity and depth; existing flow directions and animation rules remain intact |
| Controls | Recessed numeric/select fields, segmented fieldsets, stronger Start/Pause/Apply hierarchy, neutral uninitialized notice, green applied and amber draft notices | Makes controls look like an operator panel while retaining native inputs and the same actions |
| Trends/history | Matching dark chart surfaces, stronger traces, consistent heading and legend treatment | Keeps the supporting views visually cohesive; chart samples and interactions are unchanged; direct plot-width observation keeps coordinates sharp after resizing |

Micro-trends show the last 60 retained simulated seconds, or all available samples when the run is shorter. Each trace scales independently. Straight segments connect retained observations; null readings break the line. The existing extrema/gap-preserving plotting helper reduces dense history for display. No history is created, modified or discarded by these traces. An unavailable measurement has no invented line. SVG accessible names describe the time window, units, range, independent scaling and gaps.

The equipment finishes are illustrations, not calibrated physical geometry. The compressor bank remains one aggregate symbol with the actual modeled count. The receiver indicator remains modeled liquid volume fraction, not a measured sight glass. The dashed outlet/suction volume remains a model partition, not an added vessel. No equipment, sensor, control mode or process value was added.

## Screenshot review

All normal comparisons use the Default profile, automatic DX example, and a paused 10-second run. Browser viewports use a device scale factor of 1. These are browser emulations, not physical iPad validation.

| View | Before | After |
| --- | --- | --- |
| Desktop landscape · 1440 × 1000 | [Before](ui-hmi-uplift/before-desktop-landscape.png) | [After](ui-hmi-uplift/after-desktop-landscape.png) |
| Desktop portrait · 900 × 1400 | [Before](ui-hmi-uplift/before-desktop-portrait.png) | [After](ui-hmi-uplift/after-desktop-portrait.png) |
| iPad landscape · 1024 × 768 | [Before](ui-hmi-uplift/before-ipad-landscape.png) | [After](ui-hmi-uplift/after-ipad-landscape.png) |
| iPad portrait · 768 × 1024 | [Before](ui-hmi-uplift/before-ipad-portrait.png) | [After](ui-hmi-uplift/after-ipad-portrait.png) |
| Full schematic | [Before](ui-hmi-uplift/before-schematic.png) | [After](ui-hmi-uplift/after-schematic.png) |
| iPad landscape pressure trends | [Before](ui-hmi-uplift/before-trends-ipad-landscape.png) | [After](ui-hmi-uplift/after-trends-ipad-landscape.png) |

[Portrait diagram panned right](ui-hmi-uplift/after-ipad-portrait-right.png). [WebKit normal landscape](ui-hmi-uplift/after-webkit-paused-ipad-landscape.png).

| Operational view | Chromium | WebKit |
| --- | --- | --- |
| Running | [View](ui-hmi-uplift/after-chromium-running-ipad-landscape.png) | [View](ui-hmi-uplift/after-webkit-running-ipad-landscape.png) |
| Compressor off | [View](ui-hmi-uplift/after-chromium-off-ipad-landscape.png) | [View](ui-hmi-uplift/after-webkit-off-ipad-landscape.png) |
| Draft controls | [View](ui-hmi-uplift/after-chromium-draft-controls-ipad-landscape.png) | [View](ui-hmi-uplift/after-webkit-draft-controls-ipad-landscape.png) |
| Actual equipment trip | [View](ui-hmi-uplift/after-chromium-equipment-trip-ipad-landscape.png) | [View](ui-hmi-uplift/after-webkit-equipment-trip-ipad-landscape.png) |
| Actual model-domain stop | [View](ui-hmi-uplift/after-chromium-model-stop-ipad-landscape.png) | [View](ui-hmi-uplift/after-webkit-model-stop-ipad-landscape.png) |

State screenshots use supported controls/profile inputs to produce the real behavior. No sensor values, faults or simulator states are injected for appearance.

The full normal 1024 × 768 circuit retains its exact prior bounds: top `304.78 px`, bottom `703.03 px`, width `982 px`. It remains above the bottom operator rail. The desktop readout row grows only 6 pixels for larger digits. Portrait keeps the established three-card grouping, controls placement and intentional horizontal schematic scrolling. No navigation destinations, sections, essential controls or inspection paths were relocated or hidden.

The rendered review prompted a refinement to use neutral text for paused/off compressor states in the schematic, green only for running, and a neutral uninitialized settings notice. A small state indicator and an actual-state tooltip on the existing sticky Live Plant tab keep operating context visible while scrolling to controls or trends. Genuine equipment trips remain red; model stops remain amber. This improves state clarity without inferring additional fault conditions. WebKit validation also exposed a stale SVG coordinate width after resizing; observing the actual plot widths fixed it while retaining the original resize and pinned-sample assertions.

## Remaining differences from the concept

The reference depicts a much larger plant with multiple suction headers, compressor selections and vessels. The supported simulator is a small circuit, so its honest depiction has fewer machines and readings. Equipment remains stylized SVG rather than photorealistic. The top traces are compact contextual plots; the full trends/history view retains exact inspection, units and exports. Portrait still requires horizontal diagram scrolling, and long genuine fault messages expand the alarm panel. Tablet controls retain their existing position below the schematic. Performance and touch behavior on a physical iPad have not been validated.

## Validation

- Build: passed through the unchanged `tools/build.py` pipeline. Generated standalone HTML is 1,692,897 bytes.
- `npm test`: all 10 suites passed, including physics, dynamic/storage/valve models, initialization/profiles, conservation integration, read-only schematic telemetry, history and all five training exercises. The 24 integration cases retain maximum mass residual `2e-13 kg` and energy residual `2.6e-9 kJ`.
- Export parity: before/after 10-second DX histories are byte-identical. Both SHA256 checksums are `9f2916c5282ddc1b9408c40852133ad543c232f6daf09a99c38541f118e19182`.
- Property grid SHA256 remains `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`.
- Chromium: all 17 suites passed on the final redraw implementation. This includes the existing schematic, trends/history, training, profile/export, responsive/offline and runtime-error assertions, plus the new retained-sample HMI checks.
- WebKit: all 7 suites passed on the final implementation, including release, schematic, history, training, visual-fit, original status coverage and new microtrend/spacing checks. The session's temporary browser/shared libraries were used; only host library-location preflight was skipped. Every test assertion remained active.
- JavaScript syntax and `git diff --check`: passed.
- Standalone output SHA256: `5a7ae1ffab5792ad45e629d7c58d2ca0c117c3e7d764626c85ba95060fbb7efc`.

The new browser regression checks five traces against exported retained SI samples in both unit systems, validates the one-minute scope and exact observation IDs, verifies unavailable values have no invented trace, checks the six existing equipment symbols, and checks value/trace separation and touch targets at desktop, landscape/portrait tablet and mobile widths.

No existing assertion was removed or weakened. No physics, properties, model state definitions, solvers, tolerances, fault logic, grading or historical evidence/export source was changed.

## Ammonia Lab — The Mechanic’s Report

The same simulator now looks more like an operator station. The readings have instrument faces and small real-history traces, the machines have more convincing metal and mechanical detail, and the control panels have clearer boundaries. Running, paused, switched-off, equipment-trip and model-stop states are easier to tell apart. The machinery, controls, physics, exercises and exported evidence still work the same way.

## Exact files changed in this pass

Application sources and generated output:

- `app.template.html` — visual system, instrument layout and state styling.
- `storage-app.js` — read-only history traces and initialized/applied display hook.
- `live-schematic.js` — vector material/detail/shadow treatment and pipe highlights.
- `storage-trends.js` — observes actual plot widths to redraw chart geometry reliably without altering samples or pinned inspection.
- `index.html` — generated by the existing build.

Validation and capture:

- `package.json` — adds HMI regression to WebKit checks.
- `tests/run-browser.cjs` — adds HMI regression to Chromium checks.
- `tests/hmi-uplift-ui.cjs` — retained-sample/unit agreement, unavailable traces, symbol count, spacing and real state screenshots.
- `tests/capture-hmi-uplift.cjs` — before/after capture, measurements and actual history exports.

Documentation:

- `docs/HMI_UPLIFT_REVIEW.md` — this review.

The earlier pending styling work and its evidence are retained. New screenshots, measurements and comparison exports:

- `docs/ui-hmi-uplift/after-chromium-draft-controls-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-chromium-equipment-trip-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-chromium-model-stop-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-chromium-off-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-chromium-running-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-desktop-landscape.png`
- `docs/ui-hmi-uplift/after-desktop-portrait.png`
- `docs/ui-hmi-uplift/after-history-si.csv`
- `docs/ui-hmi-uplift/after-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-ipad-portrait-right.png`
- `docs/ui-hmi-uplift/after-ipad-portrait.png`
- `docs/ui-hmi-uplift/after-measurements.json`
- `docs/ui-hmi-uplift/after-schematic.png`
- `docs/ui-hmi-uplift/after-trends-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-webkit-draft-controls-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-webkit-equipment-trip-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-webkit-model-stop-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-webkit-off-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-webkit-paused-ipad-landscape.png`
- `docs/ui-hmi-uplift/after-webkit-running-ipad-landscape.png`
- `docs/ui-hmi-uplift/before-desktop-landscape.png`
- `docs/ui-hmi-uplift/before-desktop-portrait.png`
- `docs/ui-hmi-uplift/before-history-si.csv`
- `docs/ui-hmi-uplift/before-ipad-landscape.png`
- `docs/ui-hmi-uplift/before-ipad-portrait.png`
- `docs/ui-hmi-uplift/before-measurements.json`
- `docs/ui-hmi-uplift/before-schematic.png`
- `docs/ui-hmi-uplift/before-trends-ipad-landscape.png`
- `docs/ui-hmi-uplift/checked-history-chromium.csv`
- `docs/ui-hmi-uplift/checked-history-webkit.csv`

This pass remains uncommitted for review; nothing is merged, published or pushed.
