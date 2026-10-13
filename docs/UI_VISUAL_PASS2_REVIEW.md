# Ammonia Lab — UI Visual Fidelity Pass 2

Starting commit: `22d2067dfb71e4055fd6488016adedabf42618c2`. Branch: `ui/coworker-demo-polish-20261013`. This is a review milestone; it includes no merge, publishing, production hosting change, PR #3 work or EOS research.

## What changed visually

The first pass established hierarchy and model separation, but its equipment remained rectangular cards and its square schematic began mostly below the iPad landscape fold. This pass changes the composition and the equipment renderer, while retaining that first pass's supported readings, draft/applied distinction, navigation, inspection, histories and five exercises.

### Illustrated, interactive equipment

The live circuit now has six custom SVG illustrations:

- **Compressor bank:** a ribbed motor/compressor housing, coupling, mounting feet, flanges and bolts, with current bank status and applied speed. It is one aggregate symbol; its displayed modeled count comes from the active profile. There are no invented individual compressor states.
- **Condenser:** a finned exchanger with a coil, end connections and supports. Its annotation distinguishes bulk refrigerant state from compressor discharge demand. No fan quantity, fan operation or additional condenser is implied.
- **Receiver:** a shaded cylinder with cap, supports and a dynamically updated model-volume indicator. The indicator's SVG height is proportional to the exact model liquid volume fraction. It is not a calibrated physical sight-glass height.
- **Evaporator core:** a distinct cooling coil and fin assembly, with actual pressure, temperature, phase and modeled liquid volume.
- **Resolved outlet/suction:** a dashed model-partition symbol, explicitly identified as a resolved model volume. It is not an added receiver or separator. Its isolated state is visibly inactive.
- **Liquid feed valve:** an actuator/stem and valve silhouette with actual opening, control mode and supported flow condition. The actual opening still lags its command.

All shapes are inline SVG. They remain sharp, clickable and offline; native equipment inspection buttons remain the keyboard alternative. The detail panel retains the real model values and explanations. The diagram expressly says its shapes are illustrative and have no physical scale.

The supported loop is now a wide, two-row composition: compressor → condenser → receiver across the top, followed by feed → evaporator → resolved outlet across the lower row. Rounded pipe connections terminate at those symbols. Discharge, drain/feed transfers and suction/outlet paths are visually distinct. Direction arrows require positive supported model transport; blocked, isolated and stopped paths have no live-flow arrows. Flow animation additionally requires active playback and respects the existing motion toggle and reduced-motion preference. There is no decorative equipment rotation or invented flow velocity.

### Dashboard composition and controls

The shared brand and existing application tabs now occupy one compact top rail where width permits. Simulator context, playback and simulated time share a compact status line. A short row of six supported readings and the fault/stop region lead directly into the diagram. A new restrained SVG brand mark and matching play/pause icons replace generic decoration; closed select fields now use consistent offline CSS styling across Chromium and WebKit.

At desktop widths, the primary compressor/feed controls sit beside the schematic. On the 1024 × 768 tablet layout, the diagram gets the full width and controls are immediately accessible through a persistent lower operator rail. The primary controls and advanced operating-condition/test-heat fields are grouped in the same working form; secondary settings occupy a separate full-width row rather than leaving a long empty column beside the diagram. The rail retains direct links to overview, controls, trends/history, exercises, inventory, profiles and the independent room model, including keyboard focus movement.

The dark panels use restrained borders, metallic SVG gradients and subtle depth. Important readings are separated from equipment artwork and pipe labels. Cyan/teal, blue and discharge orange identify readings/paths; they do not invent alarm conditions. Actual equipment trips and numerical/model-domain stops retain their distinct labeling and severity presentation.

Portrait and phone layouts preserve readable SVG text through an intentional horizontal circuit viewport. A visible swipe instruction appears above it. The portrait evidence includes a view panned to the receiver and valve. Primary touch controls remain at least 44 px high.

### Trends

A single selected trend now fills the available panel instead of occupying one column of a two-column grid. On landscape/desktop layouts, its exact sample values and curve toggles occupy an adjacent legend. Chart geometry adapts to the available plot width; labels and traces remain readable rather than scaling a fixed small chart into a large empty panel. Resize handling preserves the inspection cursor and retained data. Chart clicks use the actual SVG coordinate system to select the nearest retained sample.

Sampling, extrema/gap preservation, histories, SI values and exports are unchanged. The chart palette and historic stop-marker styling are display projections of the existing series and recorded fault kinds.

## Before/after evidence

Matching screenshots use Default equipment, Initialize automatic DX example and Advance 10 seconds. Every viewport uses a fresh browser context. The before HTML is retrieved from the specified first-pass commit, not recreated from the redesigned source. These are Linux browser captures at desktop and iPad-sized viewports, **not physical iPad validation**.

| Viewport | First pass | Final pass 2 | Actual SVG canvas: before → after |
| --- | --- | --- | --- |
| Desktop landscape, 1440 × 1000 | [Before](ui-pass2/before-desktop-landscape.png) | [After](ui-pass2/after-desktop-landscape.png) | top 683 → 306 px; bottom 1301 → 755 px |
| Desktop portrait, 900 × 1400 | [Before](ui-pass2/before-desktop-portrait.png) | [After](ui-pass2/after-desktop-portrait.png) | top 797 → 514 px; bottom 1307 → 879 px |
| iPad-sized landscape, 1024 × 768 | [Before](ui-pass2/before-ipad-landscape.png) | [After](ui-pass2/after-ipad-landscape.png) | top 697 → 306 px; bottom 1282 → 704 px |
| iPad-sized portrait, 768 × 1024 | [Before](ui-pass2/before-ipad-portrait.png) | [After](ui-pass2/after-ipad-portrait.png) | top 797 → 514 px; bottom 1288 → 879 px |

These measurements refer to the **actual SVG canvas**, not the enclosing schematic panel. The first-pass report's 589 px landscape figure measured that panel; the artwork itself started around 697 px. The final normal-state landscape canvas fits entirely above the lower operator rail, including all six equipment silhouettes and their annotations. See [before measurements](ui-pass2/before-measurements.json) and [after measurements](ui-pass2/after-measurements.json).

Additional evidence:

- [Complete schematic before](ui-pass2/before-schematic.png) and [after](ui-pass2/after-schematic.png). Full-element captures omit the fixed operator rail so it does not overlay the standalone figure; viewport captures show the actual rail.
- [Pressure trends before](ui-pass2/before-trends-ipad-landscape.png) and [after](ui-pass2/after-trends-ipad-landscape.png).
- [Running connected circuit](ui-pass2/after-running-ipad-landscape.png), [primary controls](ui-pass2/after-controls-ipad-landscape.png) and [real modeled equipment trip](ui-pass2/after-trip-ipad-landscape.png). These capture their respective operator workflows rather than the matching 10-second benchmark.
- [Portrait panned right](ui-pass2/after-ipad-portrait-right.png) and [WebKit landscape](ui-pass2/after-webkit-ipad-landscape.png).

Reproduce the paired captures with `npm run build`, `node tests/capture-visual-pass2.cjs before`, then `node tests/capture-visual-pass2.cjs after`. The baseline commit must be present in Git history.

## Direct visual review against the reference

The final rendered result follows the reference's compact top status, high-contrast instrument row, large central circuit, dark panel depth and adjacent/readily accessible controls. It now has recognizable machinery, a receiver volume indication, mechanical details and purposeful pipework rather than generic equipment rectangles. The wide selected-trend panel also addresses the first pass's unused horizontal area.

The first illustrated iteration still had an avoidably tall canvas: its lower equipment row was below the landscape fold. The [first iteration](ui-pass2/refinement-1-ipad-landscape.png) and [schematic](ui-pass2/refinement-1-schematic.png) show that problem. A [second iteration](ui-pass2/refinement-2-ipad-landscape.png) moved readings into shared rows and shortened the layout, but lower readings still approached the tool rail. The final refinement removed duplicate annotations and excess spacing, giving the diagram a 1080 × 438 viewBox without reducing touch-target sizes or the primary reading type. Intermediate [first](ui-pass2/refinement-1-measurements.json) and [second](ui-pass2/refinement-2-measurements.json) measurements are retained.

The new WebKit visibility assertion then detected about 1.2 px of canvas overlap with the rail. A small spacing reserve fixed the actual layout; the assertion was not relaxed. WebKit screenshots also exposed inconsistent native select surfaces, which now use a shared CSS treatment.

### Remaining differences and reasons

| Reference feature | Actual implementation and reason |
| --- | --- |
| Many individually depicted compressors, condensers and room circuits | One aggregate compressor-bank symbol and the actual small modeled circuit. The active profile count is shown honestly; individual machine statuses, extra banks, headers and rooms are unsupported. |
| Detailed photographic equipment and plant-specific pipe geometry | Stylized vector machinery with restrained metallic depth. There is no supplied manufacturer geometry, and the model has no piping holdup. Shapes illustrate component roles rather than asserting physical dimensions, compressor type or a surveyed plant layout. |
| Multiple receiver systems and measured levels | Only the supported receiver and modeled volume states. The resolved outlet is a model partition, and liquid indicators display model volume fractions rather than sight-glass readings. |
| Oil pressure, extra sensors, operating modes and alarm actions | Omitted because the simulator does not support them. Real controls, modeled trips and numerical/domain stops remain available with their existing behavior. |
| A small trend strip always beneath the overview | The exact-sample trend/history workspace is one rail action away and uses the full panel efficiently. This preserves curve toggles, synchronized cursor, event inspection and exports; an additional preview chart would duplicate those controls in the limited tablet overview. |
| All controls and all supporting panels visible simultaneously | Desktop primary controls are adjacent; tablet controls use the persistent rail and normal scrolling. Portrait/phone circuits intentionally scroll horizontally. Active fault evidence can expand the status region and take priority over fitting the whole picture. |

Physical iPad Safari, finger interaction, the on-screen keyboard and assistive-technology behavior still require human review. The screenshots and Chromium/WebKit tests establish browser-emulated coverage, not physical-device certification.

## Tests and boundaries

- **Build: PASS.** The unchanged build generates the standalone `index.html` as usual. Final artifact: 1,666,260 bytes; repeated builds produce SHA256 `e31efb34e0d34d2f44efe6db37daedacc873521e4bf4f8e6bc1545fcfbd4338a`. Property-grid SHA256 remains `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`. [Build output](ui-pass2/build.txt).
- **`npm test`: PASS**, all ten numerical/model suites. All 24 integrated cases retain maximum mass residual `2e-13 kg` and combined energy residual `2.6e-9 kJ`. [Numerical log](ui-pass2/numerical-tests.txt).
- **`npm run test:browser`: PASS**, all 15 Chromium suites, including every existing assertion and the added `visual-pass2-ui.cjs`. [Chromium log](ui-pass2/chromium-tests.txt). A concurrent full-page screenshot attempt timed out; the unchanged suite passed on the serial rerun.
- **`npm run test:webkit`: PASS**, all five suites: release, schematic, history, training and the new visual regression. [WebKit log](ui-pass2/webkit-tests.txt). The managed environment uses the previously downloaded WebKit 26.5 browser and dependencies extracted in `/tmp`; its temporary launcher retains `LD_LIBRARY_PATH`. The system-library-location preflight is skipped because it does not recognize that temporary setup. Browser execution and all test assertions run normally.
- **Syntax checks and `git diff --check`: PASS.** No diff in physics/property data, solvers/tolerances, equipment specifications, conservation accounting, history storage/sampling/export, training objectives/grading, experimental baselines, or `tools/build.py`. No dependency, remote font, framework, CDN or runtime raster image was added.

The added regression checks the supported illustrated-component set; exact receiver fraction and SVG fill geometry; the complete landscape canvas above the rail; keyboard inspection; actual flow animation; adaptive full-width charts and stable pinned samples; blocked/isolated/stopped arrows; actual bank count; reduced motion; portrait/mobile scrolling instructions; touch targets; and offline SVG startup. Existing tests continue to cover initialization, start/pause, feed changes, equipment inspection, real trips, exact fault histories, exports/profiles, trends, all five lessons and completed exercise evidence.

## Ammonia Lab — The Mechanic's Report

The first pass put the gauges and controls in the right order. This pass replaced the plain equipment boxes with machinery you can recognize and brought the whole modeled loop onto the iPad landscape screen.

You can see the compressor bank, condenser, receiver, feed valve, evaporator and resolved suction volume together. Tap a component to inspect it. The receiver indicator follows the simulator's actual liquid volume; the bank count comes from the profile. The pictures are explanatory symbols, not new plant hardware or measured geometry.

Start and Pause remain beside the clock. The control panel still tells you which settings are drafts and which are applied. Flow moves only when playback and the model support it; blocked, isolated and stopped routes do not pretend to be flowing.

The lower rail takes you straight to controls, trends, histories and lessons. A selected trend now uses the available width, and its cursor still inspects exact retained samples.

The refrigeration engine, trips, conservation checks, exports and five exercises stayed intact. The remaining job is review on an actual iPad. This branch is ready for review and has not been merged or published.

## Exact changed files

Application changes are display/layout code. `index.html` is generated by the unchanged build. Test changes add coverage and redirect new captures into this pass’s evidence folder; existing assertions remain intact. All first-pass evidence remains unchanged.

```text
app.template.html
docs/UI_VISUAL_PASS2_REVIEW.md
docs/ui-pass2/after-controls-ipad-landscape.png
docs/ui-pass2/after-desktop-landscape.png
docs/ui-pass2/after-desktop-portrait.png
docs/ui-pass2/after-ipad-landscape.png
docs/ui-pass2/after-ipad-portrait-right.png
docs/ui-pass2/after-ipad-portrait.png
docs/ui-pass2/after-measurements.json
docs/ui-pass2/after-running-ipad-landscape.png
docs/ui-pass2/after-schematic.png
docs/ui-pass2/after-trends-ipad-landscape.png
docs/ui-pass2/after-trip-ipad-landscape.png
docs/ui-pass2/after-webkit-ipad-landscape.png
docs/ui-pass2/before-desktop-landscape.png
docs/ui-pass2/before-desktop-portrait.png
docs/ui-pass2/before-ipad-landscape.png
docs/ui-pass2/before-ipad-portrait.png
docs/ui-pass2/before-measurements.json
docs/ui-pass2/before-schematic.png
docs/ui-pass2/before-trends-ipad-landscape.png
docs/ui-pass2/build.txt
docs/ui-pass2/chromium-tests.txt
docs/ui-pass2/numerical-tests.txt
docs/ui-pass2/refinement-1-ipad-landscape.png
docs/ui-pass2/refinement-1-measurements.json
docs/ui-pass2/refinement-1-schematic.png
docs/ui-pass2/refinement-2-ipad-landscape.png
docs/ui-pass2/refinement-2-measurements.json
docs/ui-pass2/refinement-2-schematic.png
docs/ui-pass2/webkit-tests.txt
index.html
live-schematic.js
package.json
storage-app.js
storage-trends.js
tests/capture-visual-pass2.cjs
tests/dashboard-ui.cjs
tests/run-browser.cjs
tests/visual-pass2-ui.cjs
```
