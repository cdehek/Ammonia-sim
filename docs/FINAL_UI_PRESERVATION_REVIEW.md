# Approved HMI milestone — preservation review

2026-10-13 · branch `ui/coworker-demo-polish-20261013` · reviewed against committed baseline `1abbc39387232029b4f4f98f33241dbee80c51c6`.

This review covers **all accumulated uncommitted work**, including industrial styling, instrumentation/illustration uplift and the approved charcoal/steel/teal-green/amber palette. No additional styling pass or screen rearrangement was performed during final verification.

## Scope and preservation

- Template markup outside `<style>` is byte-identical to the committed baseline. Layout foundation, navigation destinations, supported controls and schematic placement are retained.
- Appended CSS provides industrial surfaces, instrument/readout hierarchy, applied/draft and actual-state differentiation, touch/readability refinements and the approved palette. The major responsive arrangements are retained.
- `storage-app.js` adds read-only sparklines from retained real samples, display-only state attributes and operational tooltip context. Unavailable readings remain unavailable; traces identify their window, range and independent scaling. Control handlers and model progression are unchanged.
- `live-schematic.js` improves the existing six equipment illustrations with steel surfaces, highlights, shadows and mechanical details. Component quantities, SVG layout, selection, actual readings, exact receiver fill, supported-flow logic and reduced-motion behavior remain intact. Outlet/suction remains explicitly a resolved model partition, not another vessel.
- `storage-trends.js` changes chart colors and display-only resize scheduling/observation. Series definitions, historical observations, envelope reduction, cursor mapping and exports are unchanged. The resize scheduling has an unresolved WebKit timing limitation documented below.
- Existing numerical commands and original browser assertions are unchanged. Browser runners add two focused UI suites; new capture scripts record genuine simulated workflows.
- Physics, properties, profiles, solver/fault logic, conservation accounting, training objectives/grading, historical evidence/export logic and build pipeline are unchanged. `app.js`, `engine.js`, `storage-engine.js`, `equipment-profiles.js`, `properties.json`, `training-app.js`, `training-engine.js`, `storage-history.js` and `tools/build.py` were directly compared with HEAD.
- `index.html` was regenerated using the project build. SHA256 remains **`15bc108cebe4c3346490c0db9433aabd6e19190d96397933d7867c4afe2dd5c4`**, identical to the approved palette before this verification. Property grid SHA256 remains `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`.

## Visual evidence

The historical galleries are preserved as captured, rather than overwritten with screenshots from a later design. Reports written during those stages describe their then-uncommitted state; this final review supersedes those historical delivery notes.

- [Approved desktop](ui-palette/after-desktop-landscape.png)
- [Approved iPad landscape](ui-palette/after-ipad-landscape.png)
- [Approved iPad portrait](ui-palette/after-ipad-portrait.png)
- [Portrait panned to receiver/feed](ui-palette/after-ipad-portrait-right.png)
- [Full before/after palette gallery and state evidence](PALETTE_REVIEW.md)
- [Earlier instrumentation/illustration evidence](HMI_UPLIFT_REVIEW.md)
- [Earlier panel/status evidence](INDUSTRIAL_STYLING_REVIEW.md)

Rendered iPad views were inspected again during preservation. Landscape shows the full supported circuit above the operator rail; portrait preserves communicated horizontal schematic scrolling. Matched before/after palette bounds and 10-second DX history CSVs are identical. All tablet evidence is **browser emulation**, not physical iPad validation. The schematic is illustrative, not physical geometry or a certified safety HMI. Independently scaled sparklines are observation cues, not calibrated axes.

## Narrow WebKit investigation

Reproduction: `tests/verify-webkit-resize.cjs` runs the **original `visual-pass2-ui.cjs` unchanged** against three HTML versions, sequentially, with the same Playwright 1.62.1 WebKit engine, 1024×768 initial viewport, installed mock clock, workflow and 1440×1000 resize. It also runs a separate read-only geometry probe. See [raw results](ui-verification/webkit-resize.json).

| Version | Standalone SHA256 | Original resize assertion |
| --- | --- | --- |
| Committed `1abbc39` | `e31efb34e0d34d2f44efe6db37daedacc873521e4bf4f8e6bc1545fcfbd4338a` | Passed |
| Approved HMI before palette | `5a7ae1ffab5792ad45e629d7c58d2ca0c117c3e7d764626c85ba95060fbb7efc` | Failed |
| Approved current palette | `15bc108cebe4c3346490c0db9433aabd6e19190d96397933d7867c4afe2dd5c4` | Failed |

The exact failure is `tests/visual-pass2-ui.cjs:22`: **“Chart geometry expands at desktop width”**, requiring SVG viewBox width >900 after 30 mock milliseconds. Earlier probes saw a 1157px plot with a stale 741-unit SVG viewBox. In the separate final probes all three versions reached plot/viewBox width 1157 and retained the pinned sample at 0.0000 seconds, both immediately and after settling. That does **not** turn the failing original assertions into passes.

The original assertion subsequently passed in the complete final WebKit run, without source or assertion changes. Both outcomes are retained: this is an intermittent failure, not a consistently failing assertion.

Conclusion: the failure predates the palette revision, but this comparison does **not** establish that it predates the accumulated HMI changes. It is a timing-sensitive WebKit chart redraw regression risk in the earlier pending UI work, involving display-only scheduling/layout delivery under the installed clock. An engine-only cause has not been proven. The committed baseline passing and revised versions failing must remain explicit. No numerical/data failure was found. The exact root cause remains unresolved within this narrow preservation task; no simulator changes, timing/assertion relaxation, skipped assertions or unrelated development were used to conceal it.

To reproduce, supply committed/pre-palette/current HTML snapshots as the three command arguments. The committed snapshot is obtainable with `git show 1abbc39387232029b4f4f98f33241dbee80c51c6:index.html`; pre-palette evidence uses the recorded session snapshot hash above. WebKit here uses temporary downloaded browser libraries and skips only host library-location preflight (`PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`), with assertions active.

## Final validation

No merge, production hosting change, main update or force push is part of this milestone.

- `npm run build`: passed; generated HTML is byte-identical to the approved palette.
- `npm test`: all 10 numerical suites passed. All five guided exercises passed; integrated conservation maxima were 2e-13 kg mass and 2.6e-9 kJ energy over 24 scenarios.
- `npm run test:browser`: all 17 Chromium suites passed. [Full output](ui-verification/chromium.log).
- JavaScript syntax checks passed for all modified display modules and the new resize diagnostic.
- Palette before/after layout measurements and SI CSV exports are byte-identical.
- Source diff whitespace checks passed. Staged evidence checks use `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check` to recognize the CSV exporter's original CRLF line endings without rewriting exported evidence.


- `npm run test:webkit`: all 7 suites passed in the final complete run. The controlled baseline comparison still records the intermittent resize failure described above. [Full output](ui-verification/webkit.log).
- Original screenshot galleries were restored byte for byte after test captures. Fresh final-run [WebKit landscape](ui-verification/final-webkit-ipad-landscape.png) and [Chromium running landscape](ui-verification/final-chromium-running-ipad-landscape.png) are retained separately.

## Exact changed files

[Complete milestone manifest](ui-verification/changed-files.txt) lists every source, test, documentation and evidence file in this commit. Only the diagnostic, final review, final logs and final-run captures were added during preservation; the approved application source was unchanged.

## Mechanic’s Report

The approved dashboard is preserved: steel equipment, calm green instruments, amber process cues and clear red trips. The machine underneath runs the same calculations and exercises. One WebKit chart-resize check remains a known display timing problem: the revised dashboard does not reliably redraw within that test's short deadline, even though the final full run passed and later geometry and pinned readings are correct. It is documented openly for review.
