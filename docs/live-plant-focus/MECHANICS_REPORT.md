# 🔧 Ammonia Lab — The Mechanic’s Report

Live Plant is the default workspace, with a compact **Ammonia Lab / Live Plant** header. The five older top-level sections, reference calculator and reference exports remain in the bundle and are hidden through presentation settings. Restore them using [`?workspace=all` or the build setting](README.md).

The approved charcoal/steel/green/amber palette, equipment illustrations, seven Live Plant section links, unit selectors, playback controls, animation, exercises, profiles and exports are preserved. Operator Assist v0.1 remains in the schematic header. Its paused/running, compressor-off, real equipment-trip and model-domain-stop behavior, keyboard/touch access, offline operation and identical SI export trajectories pass the preservation checks.

The header’s **Model information / limitations** entry explains the illustrative model, uncalibrated equipment assumptions, numerical-validation limits and unsuitability for actual plant safety decisions. It opens the original Model & Validation workspace with its existing tables and reports. Return preserves the connected run and restores keyboard focus to the entry. A portrait-size test caught a sticky-header overlap; closing the information panel and returning at the top of the workspace resolves it.

Approved checkpoint and base-branch head: `b3d0975453a142c1c7a49c2c979ba7fd62ad9274`.
Feature branch: `feature/live-plant-focus-mode-20261013`.

## Verification evidence

| Check | Result |
|---|---|
| Build | PASS; standalone bundle matches source; property-grid SHA256 unchanged |
| Numerical | PASS; all 11 existing suites, with scientific assertions and acceptance limits unchanged |
| Chromium | PASS; all 19 browser suites, including focus mode and retained workspace coverage |
| Final focus checks | PASS in Chromium and WebKit, including portrait validation return, retained live readings, URL/build restoration and offline startup |
| WebKit selection | 8/9 suites PASS; retained chart-resize assertion FAIL, reproduced against the approved checkpoint |

[Build output](verification/build.log), [numerical output](verification/numerical.log), [Chromium output](verification/chromium.log), [final Chromium focus check](verification/focus-chromium.log), [final WebKit focus check](verification/focus-webkit.log).

Numerical coverage includes 560 unseen single-phase states, 160 saturation states, 159 full-cycle comparisons, one expected out-of-domain rejection and 17 manufacturer-correlation points. Connected integration checks retain all 24 operating/fault/recovery cases. These quantify numerical agreement, not real-plant accuracy.

All 18 protected model, equipment, history, training, schematic, Operator Assist and scientific-data files match the checkpoint byte for byte: [hash evidence](verification/protected-files.json). No refrigeration physics, EOS, numerical algorithms/limits, accounting, equipment specifications, grading, fault/alarm rules, Operator Assist interpretation, history recording or export contents changed.

Offline tests load the standalone HTML bytes with network disabled/blocked and require no HTTP requests. This environment blocks Chromium `file://` navigation, so the check uses `setContent` as the existing offline suites do. No external assets or runtime dependencies were added.

The test environment lacks several WebKit libraries and root package-install privileges. Test-only libraries were extracted under `/tmp`, and a temporary copy of the downloaded launcher uses those libraries. Playwright’s host-cache check was bypassed because it does not recognize the temporary GLES library; the runtime loader resolves it. Browser assertions remain enabled and unchanged. The repository’s normal installation instructions and application runtime are unchanged.

## WebKit chart-resize comparison

`npm run test:webkit` exits 1 at the unchanged **Chart geometry expands at desktop width** assertion. Its five preceding suites pass. The three suites after that failure were run separately and pass, including Operator Assist. No assertion was weakened, skipped or given a longer acceptance deadline.

`tests/focus-webkit-resize.cjs` compares the approved checkpoint’s standalone HTML and the final Focus Mode artifact using Playwright 1.62.1 WebKit, the same navigation workflow, 1024×768 initial viewport, 1440×1000 resize and original chart assertions. A separate read-only probe records plot/SVG geometry and pinned-sample text; a native-clock probe observes ordinary resizing.

| Observation | Approved checkpoint | Focus Mode |
|---|---|---|
| First comparison, original assertion | PASS | FAIL |
| Second comparison, original assertion | FAIL | FAIL |
| Second probe, immediate mocked resize: plot / SVG width | 1157 / 1157 px | 1157 / 741 px |
| Second probe, settled mocked resize: plot / SVG width | 1157 / 1157 px | 1157 / 741 px |
| Native-clock resize after 350 ms: plot / SVG width | 1157 / 1157 px | 1157 / 1157 px |

The known mocked-clock instability reproduces at the approved baseline, while Focus Mode remains stale in both mocked probes. Pinned sample text remains identical. Native-clock geometry expands correctly in both artifacts. This is a retained browser-test limitation, not a green WebKit suite result or a guarantee for every resize. The chart-rendering module is unchanged and this milestone does not attempt a resize repair.

Evidence: [failed WebKit command](verification/webkit.log), [remaining suites](verification/webkit-remaining.log), [first comparison](verification/webkit-resize-first.json), [second comparison with native-clock observations](verification/webkit-resize.json), [comparison output](verification/webkit-comparison.log). Reproduce with `node tests/focus-webkit-resize.cjs approved-checkpoint.html index.html`; obtain `approved-checkpoint.html` with `git show b3d0975453a142c1c7a49c2c979ba7fd62ad9274:index.html`.

## Screenshots

Initialized plant, default units, paused after 10 simulated seconds:

- [Desktop · 1440×1000](screenshots/chromium-plant-desktop.png)
- [iPad landscape · 1024×768](screenshots/chromium-plant-ipad-landscape.png)
- [iPad portrait · 768×1024](screenshots/chromium-plant-ipad-portrait.png)

The [screenshot directory](screenshots) also contains startup and open-Operator-Assist views at all three sizes in Chromium and WebKit. These are browser-emulated desktop/iPad viewports, not physical iPad validation. Landscape retains the complete normal-state schematic above the bottom section rail; portrait retains the existing horizontal schematic and navigation scrolling. Original screenshot galleries are retained unchanged.

## Changed files and review boundary

[Exact changed-file manifest](changed-files.txt). Application changes are confined to `app.js`, `app.template.html` and the generated `index.html`. Existing browser-suite edits only adapt entry/navigation to the intentional presentation change; legacy functionality tests explicitly restore the old navigation. Package scripts register the focused browser coverage. Remaining files are documentation and review evidence.

Only the isolated feature branch is committed and pushed. No merge, main change, PR #3 merge, hosting change, deployment, experimental EOS work or coworker-demo milestone is included. Stop for review.
