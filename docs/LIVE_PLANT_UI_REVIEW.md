# Live Plant UI review — 13 October 2026

Built from production `main` at `0473d32f62db992fde0f581d116e1bd0c8e7d8ed` on `ui/coworker-demo-polish-20261013`. This milestone stops at branch review; no merge or hosting change is included.

## UI audit

- **Plant hierarchy:** Equipment profile editing, the complete training panel, and a large control form preceded the connected schematic. In the initialized baseline it began 2,614 px below the top on a 1024 × 768 viewport and 3,063 px below the top at 768 × 1024.
- **Competing contexts:** The reference calculator sidebar occupied tablet width alongside Live Plant, despite controlling an independent calculation. Connected inventory dynamics and the independent quasi-steady room model shared a long page with similar playback controls.
- **Readings:** Connected suction/discharge pressure, outlet superheat and actual feed opening required diagram/table inspection. The compact metric row emphasized charge and accumulated electricity over immediate equipment conditions.
- **Controls:** Compressor, geometry, test heat, room boundaries and valve tuning were spread across an undifferentiated form. The form did not clearly show whether an edit was applied.
- **Stops:** Equipment trips and numerical/domain stops had explanatory text but little visual prominence. A generic status paragraph carried too much information.
- **Inspection, trends and training:** Equipment inspection and retained history already worked well, including keyboard alternatives and unavailable-value gaps, but were difficult to reach. All five exercises were present; their placement pushed the process view down.
- **Tablet use:** Small labels/buttons, the independent sidebar and long preceding content reduced schematic readability. Plot/table horizontal scrolling existed and should remain contained.

## Implemented changes

Connected Live Plant now leads with model context, playback state, simulated time, six supported readouts, playback controls, and a dedicated fault/stop region. The summary uses the same storage record and compressor observation as the existing schematic. It distinguishes condenser bulk pressure, actual valve opening, speed setting, and accepted-interval superheat; unavailable readings remain dashes with explanations.

The large schematic is first in the process area. It retains actual model readings, equipment selection, keyboard inspection buttons, flow animation, animation opt-out, and reduced-motion behavior. Dark vessel panels, larger SVG labels, brighter stream colors and a readable inspection panel replace the light presentation. Tablet layouts give the schematic the full width; desktop layouts place grouped controls alongside it.

Controls are grouped into compressor, feed valve, operating conditions, and test heat/PI tuning. Draft status and an applied-settings summary clarify the difference between typed controls and the running model. Existing semantics remain: connected Start/Advance also apply controls; circuit geometry requires reset. The independent room model has its own draft notice, including its different Advance behavior.

Persistent section links reach Plant overview, Plant controls, Trends & history, Guided exercises, Inventory, Equipment profiles and Independent room model. They scroll and move keyboard focus to the destination. Secondary tools remain available below the plant; none are removed or silently mixed into the connected readings.

The fault region remains neutral without a modeled stop. Equipment trips are labeled **EQUIPMENT TRIP** in red; numerical/model-domain stops use explicit labels and a separate caution treatment, stating that no equipment trip is asserted. Existing captured evidence, fault clearing and histories remain intact.

The shared shell uses graphite/slate panels, cyan/teal accents, high-contrast readouts, local system typography, global unit selectors and 44 px minimum primary controls. Independent reference exports moved to the footer, preserving their functions while removing them from the operator header. The reference calculator follows Live Plant instead of consuming its width, and reference diagrams also receive readable dark styling.

## Screenshots and rendered review

All matching screenshots use Default equipment, Initialize automatic DX example, then Advance 10 seconds and pause. The baseline is read directly from the specified production commit. These are Chromium viewport captures, **not physical iPad validation**.

| Viewport | Before | After | Schematic top: before → after |
| --- | --- | --- | --- |
| Desktop landscape, 1440 × 1000 | [Before](ui-evidence/before-desktop-landscape.png) | [After](ui-evidence/after-desktop-landscape.png) | 2,314 → 571 px |
| Desktop portrait, 900 × 1400 | [Before](ui-evidence/before-desktop-portrait.png) | [After](ui-evidence/after-desktop-portrait.png) | 2,809 → 685 px |
| iPad-sized landscape, 1024 × 768 | [Before](ui-evidence/before-ipad-landscape.png) | [After](ui-evidence/after-ipad-landscape.png) | 2,614 → 589 px |
| iPad-sized portrait, 768 × 1024 | [Before](ui-evidence/before-ipad-portrait.png) | [After](ui-evidence/after-ipad-portrait.png) | 3,063 → 685 px |

Additional rendered evidence: [schematic before](ui-evidence/before-schematic.png), [schematic after](ui-evidence/after-schematic.png), [controls](ui-evidence/after-controls-ipad-landscape.png), [pressure trends](ui-evidence/after-trends-ipad-landscape.png), and [real modeled pressure trip](ui-evidence/after-trip-ipad-landscape.png). Exact viewport measurements are retained in [before](ui-evidence/before-viewports.json) and [after](ui-evidence/after-viewports.json) JSON.

Screenshot review caught an initially oversized header and a clipped tablet circuit. The final layout shortens the header and gives the tablet schematic its own full-width row. The circuit, flow annotations and equipment details are readable without a narrow sidebar competing for space. The six key readouts and neutral fault region appear before the schematic. Primary settings are one section-link away.

To reproduce: `npm run build`, then `node tests/capture-dashboard.cjs before` and `node tests/capture-dashboard.cjs after`. The before command requires the production commit in Git history. The focused dashboard test refreshes the controls/trends/trip evidence.

## Verification

- `npm run build` — PASS. Standalone generated HTML: 1,644,689 bytes. Two consecutive builds produced identical output. The property grid SHA256 remains `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`. [Build output](ui-evidence/build.txt).
- `npm test` — PASS, all ten numerical/model suites: physics, dynamic room, profiles, initialization, storage, valves, integration, schematic telemetry, history and training. The 24 integrated cases retain maximum mass residual `2e-13 kg` and combined energy residual `2.6e-9 kJ`. [Full output](ui-evidence/numerical-tests.txt).
- `npm run test:browser` — PASS, all 14 Chromium suites, including existing schematic, trends/history and training UI checks plus `dashboard-ui.cjs`. [Full output](ui-evidence/chromium-tests.txt).
- `npm run test:webkit` — PASS: release, schematic, trends/history and training, all on WebKit 26.5 with emulated iPad viewports. [Full output](ui-evidence/webkit-tests.txt). The managed machine lacked WebKit libraries and root installation access, so dependencies were extracted in `/tmp` and a temporary browser launcher was adjusted to retain `LD_LIBRARY_PATH`. `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` bypassed only the system-library-location preflight; the browser and all four test suites actually ran. No app code or assertions were changed for WebKit.
- `git diff --check` and JavaScript syntax checks — PASS. Physics, solvers, property data, numerical thresholds, equipment assumptions, accounting, history processing, training grading and `tools/build.py` have no diff.

The new regression compares summary readings against independently advanced model records; checks unapplied drafts and actual valve lag; starts/pauses playback; verifies independent-room isolation; inspects section focus; triggers existing equipment-trip and model-domain cases; verifies unavailable isolated readings, touch targets, reduced motion, and contained overflow at desktop/tablet/phone widths.

Existing browser checks also inspect equipment, exports, history cursors, accepted fault snapshots, all playback speeds, profile persistence, all five exercises, and completion/debrief/export of the startup exercise. Standalone HTML runs with HTTP requests blocked. No remote fonts, CSS frameworks, CDN runtime assets or dependencies were added.

## Remaining UI limitations

- This is browser emulation on Linux; physical iPad Safari, native touch feel, on-screen keyboard behavior and assistive technology still need human review.
- A whole circuit and every control cannot fit on a small tablet at once. Vertical scrolling remains, and portrait/phone diagrams and dense tables/plots intentionally scroll horizontally inside their own regions.
- Detailed trends, inventory and exercises remain substantial sections. Persistent links shorten access; this phase does not replace them with another application or change their capabilities.
- The operator header describes the connected model. The independent room model retains its own readings, playback and faults below, explicitly labeled as a separate model.
- No unsupported sensors, oil readings, alarm acknowledgments, additional compressor banks or safety controls were invented. Current model restrictions remain visible in context and in Model & validation.

## Ammonia Lab — The Mechanic’s Report

The engine stayed under the bonnet. This work rearranged the dashboard, labels and switches so you can see what the simulator is doing before digging into its paperwork.

Open Live Plant and initialize the automatic DX example. Suction, discharge, room temperature, superheat and actual feed opening are now at the front. Start and Pause sit together. Tap equipment to inspect it, or use the inspection buttons below the circuit.

Plant controls separate the compressor, feed valve and room conditions. A draft notice tells you when typed settings have not reached the run. The valve’s actual opening still takes time to follow its command; the screen shows that lag rather than pretending the valve moves instantly.

When the model trips, the fault region names the trip and preserves its evidence. If the mathematics or property domain stops the run, the screen says that separately. Clearing a stop still does not prove the cause has been fixed.

Trends, event history and all five lessons are easy to reach from the section bar. Profiles and exports still work. The independent room model and reference calculator remain independent. Nothing in this pass changed refrigeration behavior, grading, or the app’s offline operation.

The next job is review on an actual iPad. This branch is ready for that review, not merged or published.

## Exact changed files

`index.html` is generated by the unchanged project build. The other application changes are display/layout code. Evidence files are committed for review.

```text
app.js
app.template.html
docs/LIVE_PLANT_UI_REVIEW.md
docs/ui-evidence/after-controls-ipad-landscape.png
docs/ui-evidence/after-desktop-landscape.png
docs/ui-evidence/after-desktop-portrait.png
docs/ui-evidence/after-ipad-landscape.png
docs/ui-evidence/after-ipad-portrait.png
docs/ui-evidence/after-schematic.png
docs/ui-evidence/after-trends-ipad-landscape.png
docs/ui-evidence/after-trip-ipad-landscape.png
docs/ui-evidence/after-viewports.json
docs/ui-evidence/before-desktop-landscape.png
docs/ui-evidence/before-desktop-portrait.png
docs/ui-evidence/before-ipad-landscape.png
docs/ui-evidence/before-ipad-portrait.png
docs/ui-evidence/before-schematic.png
docs/ui-evidence/before-viewports.json
docs/ui-evidence/build.txt
docs/ui-evidence/chromium-tests.txt
docs/ui-evidence/numerical-tests.txt
docs/ui-evidence/webkit-tests.txt
dynamic-app.js
index.html
live-schematic.js
storage-app.js
tests/capture-dashboard.cjs
tests/dashboard-ui.cjs
tests/run-browser.cjs
```
