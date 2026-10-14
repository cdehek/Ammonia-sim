# 🔧 Ammonia Lab — The Mechanic’s Report

**Release decision: BLOCKED for physical-iPad coworker qualification.** The unchanged candidate is available for rehearsal and review. Its scientific/model verification and three real operator scenarios are sound, but retained browser failures, native WebKit resize delays and unconfirmed physical Safari/offline/Files behavior prevent a dependable-device claim. No substantive fix has been introduced.

Branch: `release/demo-candidate-20261014`.
Approved checkpoint and parent: `99af25e3b68798919ede19a5c0805775d5828eab`.
Base: `feature/live-plant-focus-mode-20261013`, verified at that same SHA.
The exact release commit is supplied in the delivery receipt/final report; `git rev-parse origin/release/demo-candidate-20261014` retrieves it after fetching. No merge, deployment, Pages change, main/PR #3 modification or research branch work is included.

The engine, data, solvers, accounting, trips, equipment profiles, training objectives, history/exports, Operator Assist interpretation, Focus Mode and HMI are preserved. Production HTML is byte-identical to the approved checkpoint, including its existing version. The candidate name identifies packaging v0.1; it does not relabel the simulator's application version.

## Release-readiness matrix

| Area | Evidence / result | Qualification |
|---|---|---|
| Live Plant default / original workspaces | Focus checks exercise immediate startup and `?workspace=all` restoration; no rebuild/redesign | PASS in automated focus coverage |
| Approved HMI | Landscape/portrait screenshots retain charcoal/steel/green/amber, equipment illustrations and section navigation | PASS in Chromium; physical appearance/scrolling pending |
| Automatic circulating DX initialization | Actual UI initialization, repeated/reset initialization, four-vessel states and existing numerical initialization suite | PASS |
| Start/pause, playback speeds, compressor and valves | Existing browser and numerical coverage; native running/paused Assist; real 70→80% input response | Functional evidence passes; browser-clock failures are retained separately |
| Pressures, temperatures, superheat, receiver liquid volume, flows | Display/model agreement tests, history SI samples, numeric response reproduction; interval flow versus current demand distinction preserved | PASS; values are illustrative model outputs |
| Schematic / equipment inspection | All six equipment inspections; keyboard/touch, blocked/off/tripped paths and presentation purity | PASS in Chromium and native scenario actions; unchanged WebKit suite timeout recorded |
| Trends, retained history, exports | Trip/clear events retained, CSV/JSON downloaded, SI export unchanged by presentation | PASS for evidence/state; resize risk below |
| All five exercises | All five numerical recipes and Chromium training; correct/wrong/missing reflection, exact accepted-boundary completion | PASS numerical/Chromium; WebKit training suite timeout recorded |
| Operator Assist v0.1 | Existing lifecycle coverage: uninitialized, paused, running, off, trip, model stop, drafts, clear/reset; real hot-trip screenshot/export | PASS in completed lifecycle coverage |
| Reproducible production build | Two rebuilds match approved HTML; property grid and generated scientific reports unchanged | PASS |
| Complete browser suites | All 19 pinned Chromium suites PASS; all nine WebKit suites exercised across failed commands/continuation; isolated rerun fails training playback/pause assertion | WebKit remains FAIL; no assertions removed |
| Standalone offline bytes | Chromium actual `file://` with offline context; WebKit offline `setContent`, touch, DX +10 s, Assist and no HTTP requests | PASS for bundle independence; WebKit `file://` route failed with internal error |
| iPad landscape / portrait, keyboard, touch, Reduce Motion | Automated emulation and native-clock geometry probes | Automated evidence only; physical iPad pending |
| Profiles, units, exports | Existing profile/default-unit/model/history suites; frozen exercise JSON and byte-identical accepted SI CSV before/after presentation | PASS covered behavior; real Files workflow pending |
| Native WebKit chart rotation | Delayed/stale SVG width on candidate AND exact approved bytes under native timing; selecting another existing group redraws | Reproducible emulation defect/limitation; physical Safari risk unresolved |
| Internet-independent iPad cold startup | Self-contained bundle plus practical local LAN serving method documented | User must confirm actual device/access method |

## Three existing operator scenarios

[Structured summary](verification/scenario-summary.json) verifies actual downloaded evidence from Chromium and native WebKit at identical model endpoints. WebKit's native scenario uses supported 1× for its short playback check and manual exercise advancement; emulation is not a performance qualification for every playback speed. The earlier 10× audit probes were interrupted after several minutes and are not counted as passes.

**A — Normal automatic DX.** Initialize, start/pause, reinitialize for an exact starting point, advance 10 s, apply compressor 70→80%, advance another 10 s. At 10 s the HMI shows approximately 50.94 psig suction, 157.13 psig discharge, 58.90 °F room, 10.47 °F superheat difference and 18.16% actual feed opening. At 20 s with changed speed: 47.62/159.94 psig, 58.81 °F, 11.29 °F difference and 20.83% opening. These are transient responses, not a promised steady state. Draft controls do not change applied readings until Apply.

[Independent model reproduction](verification/normal-speed-model-response.json) uses identical approved initialization and identical simulated endpoints, changing only supported speed after 10 s. At 20 s: unchanged 70% gives 4.5349948/11.8906438 bar(a) suction/discharge and 5.7459406 K superheat; changed 80% gives 4.2962460/12.0407806 bar(a) and 6.2703637 K. Changed feed is 0.0207586 versus 0.0168964 kg/s. The actual UI SI export matches the independent changed-run model within 1e-8 for checked pressures/superheat; existing conservation limits remain active. Assist follows applied speed and accepted state.

**B — Restricted liquid feed.** Load the existing 30 s warmup recipe, submit correct reflection, apply its 2% manual command and advance. Completion stops at **40.000 s**, without a trip; it includes measured lag/reduced feed and the reflection. Reset and omit reflection: physical progression continues and the actual high-discharge-temperature trip stops the attempt at **56.7375 s**, not successful completion. Superheat, feed, objective evidence and frozen reports are retained in both browser exports. Existing wrong-reflection and 1×/10×/60× completion assertions remain active.

**C — Hot condenser air.** Load existing 30 s warmup, correct reflection, prescribed ambient 25→40 °C and manual exercise advancements. The recorded equipment trip occurs at **65.125 s**: discharge **170.1596974 °C ≥ 170 °C**, condenser **17.6326461 bar(a)**, suction **3.3648504 bar(a)**, speed **0.7**, one compressor. Pressure remains below the unchanged 24 bar(a) high-pressure limit. No synthetic fault, physics edit or threshold reduction is used. Assist displays **338.29 °F ≥ 338.00 °F**, **241.04/34.11 psig** and **70%** with the actual reason. Restore off-state controls, clear the latch, continue 10 s: objectives complete at **75.125 s**, no active fault, while original expected fault and stop/clear events remain in JSON/history CSV.

Presentation-only unit conversion, equipment selection, resizing and opening/closing Assist preserve accepted SI state/export evidence. Existing playback-history events can legitimately differ when playback controls themselves are used; those controls are not mere presentation operations.

## WebKit resize investigation and baseline comparison

The candidate HTML and exact approved `99af25e…` HTML share SHA256
`2924babd0e2c6fb37c71a9473a83f68644a154c6354a1c834513c570386f5420`.
The comparison uses the same Playwright 1.62.1 WebKit 26.5/revision 2336 and unchanged original assertions. Initial unchanged suites/probes sometimes timed out waiting for element stability before reaching the chart assertion; this is reported as failure, not a chart pass. In the completed [narrow comparison](verification/webkit-resize-comparison.json), the specific original chart assertion **passed for both identical artifacts**; its documented assertion failure was not reproduced in that completed comparison. A separate mocked probe stayed at 741 px versus a 1,157 px plot on the baseline; native 350 ms probes stayed at 741 px versus 1,157 px on both. The narrow comparison repeat and native geometry outputs are retained verbatim. A comparator exit of zero means the diagnostic completed; inspect its nested original-test results before calling an assertion passed.

[Native-clock comparison](verification/native-webkit-resize.json) initializes/advances the real model, selects pressure, rotates 1024→768→1024→1440 px, observes after 350 and 1,350 ms, and checks ordinary/Reduce Motion. Both artifacts show native delays or stale geometry:

| Example | Actual plot width | SVG viewBox width | Native observation |
|---|---:|---:|---|
| Approved baseline, ordinary motion, desktop | 1,157 | 682 | Still stale at 1,350 ms |
| Candidate, ordinary motion, portrait | 682 | 741 | Still stale at 1,350 ms |
| Candidate, Reduce Motion, return to landscape | 741 | 682 | Still stale at 1,350 ms |
| Both, after selecting another existing trend group | 1,157 | 1,157 | Existing redraw restores matching geometry |

This evidence **does not support calling the issue only a mocked-clock synchronization failure**. Mocked-clock/redraw timing is implicated in the old assertion, and separate native SVG redraw delays also reproduce on approved bytes. The chart can remain scaled using an earlier viewBox; curves still show retained data, but chart sizing/labels and touch positioning need physical rotation review. The screenshot is emulated evidence, not proof of a physical iPad defect. Ordinary resizing eventually works in several probes, but not reliably within every observed native interval. No scientific states or exported values change.

Recommendation: request a separate narrowly scoped chart-resize/redraw investigation, with native Safari/rotation and mocked-clock coverage, before introducing a substantive fix. Keep model/data/trips and all assertions unchanged. No chart-engine rewrite belongs in this milestone. The existing group-selection redraw is a rehearsal workaround to test on the iPad, not a repaired acceptance result.

## Test environment and remaining risks

Debian 13; Node 24.19.0; npm 11.9.0; Python 3.12.14; pinned Playwright 1.62.1. The helper automatically chooses host Chromium **154.0.8037.57**, while Playwright ships **151.0.7922.34 / revision 1234**. Host-browser industrial/HMI tests produced paused-versus-running failures. A read-only diagnostic captured the paused state and `Advance storage by greater than zero and at most 3600 seconds` after a mocked-clock transition; the exact approved baseline reproduces the industrial failure. Selecting pinned Chromium through the release-only preload makes those two unchanged suites pass. Full pinned results are recorded separately; host failures remain evidence.

WebKit host libraries were downloaded/extracted into `/workspace/browser-libs`, and the downloaded test launcher includes that local library directory. Playwright host validation was skipped because it does not recognize the workspace GLES library; runtime library resolution and a minimal native rAF/click probe were checked. No application/test assertion is skipped and no system/application source is changed. Font/cache warnings and slow concurrent browser probes are recorded. Linux WebKit is not shipped iPad Safari; test/environment instability must not be converted into a physical-device pass or assumed away as harmless.

An isolated full WebKit rerun passed focus/release/schematic/history, then failed the training UI's existing pause-disabled assertion after a Run/Pause interaction (`training-ui.cjs:34`). This is a separate unresolved playback-state verification risk, not a scientific acceptance failure. Native scenario actions and numerical objectives pass, but its exact cause has not been isolated; the failure must remain visible. Recommend a narrowly scoped baseline/device playback/clock investigation, with this assertion preserved, before changing application code. The complete test matrix records which tests failed initially, passed on retry or failed with a different assertion.

Other existing limitations: illustrative compressor/UA/valve profiles, interpolated properties within validated domains, lumped inventory/room models, bounded history, no manufacturer/measured plant calibration, no oil/entrainment/defrost/multistage physics, manual compressor speed, no persisted exercise/run across reload. Model-domain/solver stops remain distinct from equipment trips. Download reports before leaving or resetting. Clear retains history; reinitialization starts a new run. Guided exercises require Default. Scientific validation concerns numerical agreement, not real-plant operating accuracy or safety approval.

Physical-device gates: controls and touch scrolling, playback responsiveness, actual Safari rotation/plot redraw, JSON/CSV Save to Files/open/share, repeatable reset, and cold startup through a tested Internet-independent access method. The bundle adds no PWA/service worker or Safari file loader. For reliable offline Internet access use a local host on the same Wi-Fi; a standalone iPad-only route must be independently confirmed. See the checklist; do not rely on Files Quick Look or a previously loaded page.

## Deliverables and review boundary

- [Candidate HTML](../../releases/demo-candidate-v0.1-20261014/ammonia-lab-demo-candidate-v0.1-20261014.html) and [retrieval instructions](../../releases/demo-candidate-v0.1-20261014/README.md).
- [Physical iPad checklist](IPAD_CHECKLIST.md) and [2–3 minute runbook](DEMO_RUNBOOK.md).
- [Full test matrix](TEST_RESULTS.md), [scenario evidence](verification/scenario-summary.json), screenshots and exact source/packaging hash manifest.
- Screenshots: [Chromium landscape](screenshots/chromium-normal-landscape.png), [portrait](screenshots/chromium-normal-portrait.png), [real trip with Assist](screenshots/chromium-hot-trip-assist.png), [native WebKit trip](screenshots/webkit-native-1x-hot-trip-assist.png), [native WebKit portrait resize](screenshots/webkit-native-1x-resize-768.png). All are automated screenshots, not physical-device photos.

Only verification scripts, evidence, documentation and the identical HTML packaging are committed to the isolated release branch. Stop for review and user physical-device acceptance. The refrigeration machinery has been checked without tuning its protections; the remaining work is browser/device qualification, not a new simulator milestone.
