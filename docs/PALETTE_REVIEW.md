# Live Plant palette refinement

A targeted color-only refinement of the approved HMI working UI on `ui/coworker-demo-polish-20261013`. Baseline standalone HTML SHA256: `5a7ae1ffab5792ad45e629d7c58d2ca0c117c3e7d764626c85ba95060fbb7efc`.

## Changes

- Blue-tinted surfaces become charcoal/graphite with quiet steel-gray borders and highlights.
- Instrument values, sparklines, selected controls and liquid indicators use restrained teal-green.
- Warm amber/orange remains the high-side/process emphasis. Running remains green; paused/off remains neutral slate; equipment trips remain red; model stops and caution remain amber.
- Equipment retains its dimensional illustrations and mechanical detail, with neutral steel rather than blue paint/glow. Feed/drain paths use muted green; suction paths use pale sage/slate; discharge retains muted orange.
- Trend colors move to jade, amber and distinct neutral tones. Numerical values, samples, scaling, cursor interactions and exports are unchanged.

No font, spacing, sizing, structure, navigation, control, illustration geometry or simulator behavior changes were made. A source comparison against the approved standalone HTML confirms that `live-schematic.js` and `storage-trends.js` differ only in color literals. Existing assertions remain unchanged.

## Screenshots

Same Default profile and paused automatic-DX run at 10 simulated seconds. All viewports are browser emulations, not physical iPad validation.

| View | Approved palette | Revised palette |
| --- | --- | --- |
| Desktop landscape · 1440 × 1000 | [Before](ui-palette/before-desktop-landscape.png) | [After](ui-palette/after-desktop-landscape.png) |
| Desktop portrait · 900 × 1400 | [Before](ui-palette/before-desktop-portrait.png) | [After](ui-palette/after-desktop-portrait.png) |
| iPad landscape · 1024 × 768 | [Before](ui-palette/before-ipad-landscape.png) | [After](ui-palette/after-ipad-landscape.png) |
| iPad portrait · 768 × 1024 | [Before](ui-palette/before-ipad-portrait.png) | [After](ui-palette/after-ipad-portrait.png) |
| Full schematic | [Before](ui-palette/before-schematic.png) | [After](ui-palette/after-schematic.png) |
| Pressure trends | [Before](ui-palette/before-trends-ipad-landscape.png) | [After](ui-palette/after-trends-ipad-landscape.png) |

The rendered review prompted one palette adjustment: retain green liquid/feed/coil cues so active process information remains distinct from neutral steel equipment. Normal-state schematic bounds remain identical at all four viewports, including the complete iPad landscape circuit above the bottom navigation.

Additional state screenshots show actual running/off, equipment-trip, model-stop and draft-control states in Chromium and WebKit. Their filenames are in the evidence manifest below. Faults were produced through the existing supported controls/profile inputs.

## Validation

- Build: passed through the unchanged standalone build pipeline.
- Numerical: all 10 suites passed, including all five exercises and conservation checks.
- Chromium: all 17 suites passed, including exact readouts/samples, responsive geometry, flow states, offline use, history/exports and training.
- WebKit: 6 of 7 suites passed — release, schematic, history, training, status and HMI sample/spacing coverage. The unchanged `visual-pass2-ui.cjs:22` assertion, “Chart geometry expands at desktop width,” failed in the complete run and isolated retry. The exact same test also failed against the approved pre-palette HTML snapshot. This existing resize/redraw timing limitation is preserved rather than changing behavior in a palette-only task. No assertions were removed, weakened or skipped.
- Before/after history exports are byte-identical for the same 10-second DX workflow.
- Before/after layout measurement JSON is identical at all four viewports.
- JavaScript syntax and `git diff --check`: passed.
- WebKit used the existing temporary browser/shared libraries; only the host library-location preflight was skipped, with every assertion active.

## Mechanic’s Report

The same dashboard now looks more like a steel control panel. The blue cast has been reduced, the equipment looks like graphite and metal, and the readings use calmer green accents. The status indicators retain green for running, gray for paused/off, red for equipment trips, and amber for model stops or caution. The controls and simulator work exactly as before.

## Exact files changed in this refinement

- `app.template.html` — color tokens, surfaces, gradients, borders, highlights and active accents.
- `live-schematic.js` — SVG color literals only.
- `storage-trends.js` — chart palette only.
- `index.html` — generated through the unchanged build pipeline.
- `tests/capture-palette.cjs` — matching before/after screenshots and history-export comparison.
- `docs/PALETTE_REVIEW.md` — this review.

New evidence files:

- `docs/ui-palette/after-chromium-draft-controls-ipad-landscape.png`
- `docs/ui-palette/after-chromium-equipment-trip-ipad-landscape.png`
- `docs/ui-palette/after-chromium-model-stop-ipad-landscape.png`
- `docs/ui-palette/after-chromium-off-ipad-landscape.png`
- `docs/ui-palette/after-chromium-running-ipad-landscape.png`
- `docs/ui-palette/after-desktop-landscape.png`
- `docs/ui-palette/after-desktop-portrait.png`
- `docs/ui-palette/after-history-si.csv`
- `docs/ui-palette/after-ipad-landscape.png`
- `docs/ui-palette/after-ipad-portrait-right.png`
- `docs/ui-palette/after-ipad-portrait.png`
- `docs/ui-palette/after-measurements.json`
- `docs/ui-palette/after-schematic.png`
- `docs/ui-palette/after-trends-ipad-landscape.png`
- `docs/ui-palette/after-webkit-draft-controls-ipad-landscape.png`
- `docs/ui-palette/after-webkit-equipment-trip-ipad-landscape.png`
- `docs/ui-palette/after-webkit-model-stop-ipad-landscape.png`
- `docs/ui-palette/after-webkit-off-ipad-landscape.png`
- `docs/ui-palette/after-webkit-running-ipad-landscape.png`
- `docs/ui-palette/before-desktop-landscape.png`
- `docs/ui-palette/before-desktop-portrait.png`
- `docs/ui-palette/before-history-si.csv`
- `docs/ui-palette/before-ipad-landscape.png`
- `docs/ui-palette/before-ipad-portrait.png`
- `docs/ui-palette/before-measurements.json`
- `docs/ui-palette/before-schematic.png`
- `docs/ui-palette/before-trends-ipad-landscape.png`

 Earlier HMI work and evidence are preserved. Changes remain uncommitted; nothing is merged or published.
