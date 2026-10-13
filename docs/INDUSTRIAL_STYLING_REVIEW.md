# Live Plant industrial styling review

This pass starts from `1abbc39387232029b4f4f98f33241dbee80c51c6` on `ui/coworker-demo-polish-20261013`. It preserves the current page architecture, navigation, schematic placement, controls, and simulator behavior. Changes remain uncommitted for review.

## Visual refinements

- Graphite panel surfaces with steel-colored borders, subtle inset edges, and consistent button depth.
- Instrument-style operating readouts: local monospace numerals, tabular digits, compact uppercase labels, subdued units, and distinct pressure/feed accents. Accent colors identify readings; they do not assert alarms.
- Explicit uppercase playback and compressor states. Running uses muted green; paused/off remain neutral; equipment trips use red; model/numerical stops use amber. Status hooks only project existing simulator states.
- Cleaner control fields and selected equipment buttons, with clearly differentiated draft and applied notices. Touch targets and control groups retain their existing dimensions.
- A restrained schematic grid, brighter mechanical edges, and clearer primary/secondary reading contrast. Equipment geometry, readings, fill, arrows, animation, keyboard inspection, and reduced-motion behavior are unchanged.
- Matching chart surfaces, axes, legend values, and rounded curve rendering. Chart sizing, samples, interactions, history, and exports are unchanged.

Screenshot-led refinements removed input shadows from checkboxes and corrected the inherited red compressor styling during model-domain stops. A model stop now retains the normal equipment illustration with amber stop text; the equipment-trip presentation remains red.

## Before / after screenshots

All normal-view comparisons use the Default profile, automatic DX example, and a paused 10-second run. Viewports use a device scale factor of 1. These are browser viewport emulations, not physical iPad validation.

| View | Before | After |
| --- | --- | --- |
| Desktop landscape, 1440 × 1000 | [Before](ui-styling/before-desktop-landscape.png) | [After](ui-styling/after-desktop-landscape.png) |
| Desktop portrait, 900 × 1400 | [Before](ui-styling/before-desktop-portrait.png) | [After](ui-styling/after-desktop-portrait.png) |
| iPad landscape, 1024 × 768 | [Before](ui-styling/before-ipad-landscape.png) | [After](ui-styling/after-ipad-landscape.png) |
| iPad portrait, 768 × 1024 | [Before](ui-styling/before-ipad-portrait.png) | [After](ui-styling/after-ipad-portrait.png) |
| Full schematic | [Before](ui-styling/before-schematic.png) | [After](ui-styling/after-schematic.png) |
| iPad landscape pressure trends | [Before](ui-styling/before-trends-ipad-landscape.png) | [After](ui-styling/after-trends-ipad-landscape.png) |

[Portrait schematic panned right](ui-styling/after-ipad-portrait-right.png).

Additional Chromium and WebKit screenshots in `ui-styling/` show running, compressor off, draft controls, an actual high-discharge-pressure trip, and an actual full-liquid receiver model-domain stop.

| State | Chromium | WebKit |
| --- | --- | --- |
| Running | [View](ui-styling/after-chromium-running-ipad-landscape.png) | [View](ui-styling/after-webkit-running-ipad-landscape.png) |
| Compressor off | [View](ui-styling/after-chromium-off-ipad-landscape.png) | [View](ui-styling/after-webkit-off-ipad-landscape.png) |
| Draft controls | [View](ui-styling/after-chromium-draft-controls-ipad-landscape.png) | [View](ui-styling/after-webkit-draft-controls-ipad-landscape.png) |
| Equipment trip | [View](ui-styling/after-chromium-equipment-trip-ipad-landscape.png) | [View](ui-styling/after-webkit-equipment-trip-ipad-landscape.png) |
| Model-domain stop | [View](ui-styling/after-chromium-model-stop-ipad-landscape.png) | [View](ui-styling/after-webkit-model-stop-ipad-landscape.png) |

[WebKit normal paused view](ui-styling/after-webkit-paused-ipad-landscape.png). Faults are produced through supported profile/control inputs; no simulator state is injected.

## Layout and remaining limits

The normal iPad landscape SVG remains 982 pixels wide and fully visible above the bottom operator rail. Its top moves only from 305.97 to 304.78 pixels and bottom from 704.22 to 703.03 pixels. Portrait retains the existing intentional horizontal diagram scrolling and visible swipe instruction. No sections are reordered, hidden, or relocated.

Compared with the concept image, this remains an illustrative single-stage simulator circuit rather than a multi-header, multi-vessel plant. No equipment or readings were added. Long genuine fault messages still expand the alarm panel and require scrolling to see the complete circuit. Tablet controls retain their existing position below the schematic. No physical iPad testing has been performed.

## Validation

- `npm run build`: passed. Standalone HTML is generated through the unchanged build pipeline.
- `npm test`: all 10 numerical/model/history/training suites passed. Integration covered 24 scenarios, with maximum mass residual `2e-13 kg` and energy residual `2.6e-9 kJ`. All five guided exercises passed their existing grading tests.
- `npm run test:browser`: all 16 Chromium suites passed on the final implementation, including schematic, trends/history, training, offline behavior, touchscreen target dimensions, and the new status-presentation regression.
- `npm run test:webkit`: all 6 WebKit suites passed, including release, schematic, history, training, visual-fit, and new status-presentation coverage. The engine used the session's temporary browser/shared libraries; only the host library-location preflight was skipped. All test assertions ran unchanged.
- Final screenshot review: normal desktop landscape/portrait, iPad landscape/portrait, portrait panning, schematic, pressure trends, controls, running/off, equipment trip, and model stop reviewed. The final normal landscape diagram remains completely above the bottom rail.
- JavaScript syntax checks and `git diff --check`: passed.

No existing assertions were removed or weakened. The property grid checksum remains `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`. Physics, property data, solver thresholds, model states, fault logic, grading, and history/export modules have no source changes.

The final application changes are CSS and two display-only data attributes in the dashboard renderer. No simulator state writes, operating handlers, or navigation handlers changed.

## Exact changed files

Application/build output:

- `app.template.html` — scoped presentation CSS; no markup reordering.
- `storage-app.js` — two display-only status styling hooks.
- `index.html` — generated standalone application.

Validation/capture:

- `package.json` — includes the new presentation regression in WebKit checks.
- `tests/run-browser.cjs` — includes the new regression in the Chromium suite.
- `tests/industrial-styling-ui.cjs` — real state/severity transitions, draft/applied checks, screenshots.
- `tests/capture-industrial-styling.cjs` — reproducible baseline/current screenshots and layout measurements.

Documentation:

- `docs/INDUSTRIAL_STYLING_REVIEW.md` — this report.

Screenshot and measurement files (prior milestone screenshots are retained unchanged):

- `docs/ui-styling/after-chromium-draft-controls-ipad-landscape.png`
- `docs/ui-styling/after-chromium-equipment-trip-ipad-landscape.png`
- `docs/ui-styling/after-chromium-model-stop-ipad-landscape.png`
- `docs/ui-styling/after-chromium-off-ipad-landscape.png`
- `docs/ui-styling/after-chromium-running-ipad-landscape.png`
- `docs/ui-styling/after-desktop-landscape.png`
- `docs/ui-styling/after-desktop-portrait.png`
- `docs/ui-styling/after-ipad-landscape.png`
- `docs/ui-styling/after-ipad-portrait-right.png`
- `docs/ui-styling/after-ipad-portrait.png`
- `docs/ui-styling/after-measurements.json`
- `docs/ui-styling/after-schematic.png`
- `docs/ui-styling/after-trends-ipad-landscape.png`
- `docs/ui-styling/after-webkit-draft-controls-ipad-landscape.png`
- `docs/ui-styling/after-webkit-equipment-trip-ipad-landscape.png`
- `docs/ui-styling/after-webkit-model-stop-ipad-landscape.png`
- `docs/ui-styling/after-webkit-off-ipad-landscape.png`
- `docs/ui-styling/after-webkit-paused-ipad-landscape.png`
- `docs/ui-styling/after-webkit-running-ipad-landscape.png`
- `docs/ui-styling/before-desktop-landscape.png`
- `docs/ui-styling/before-desktop-portrait.png`
- `docs/ui-styling/before-ipad-landscape.png`
- `docs/ui-styling/before-ipad-portrait.png`
- `docs/ui-styling/before-measurements.json`
- `docs/ui-styling/before-schematic.png`
- `docs/ui-styling/before-trends-ipad-landscape.png`
