# Complete test results — Demo Candidate v0.1

Source: exact approved `99af25e3b68798919ede19a5c0805775d5828eab`.
No application or original test/assertion changes. Packaging and verification scripts only.

| Command / check | Result | Evidence |
|---|---|---|
| `npm ci` using package-lock | PASS | Playwright 1.62.1 installed; no lock changes |
| `npm run build`, repeated production build, compare approved bytes | PASS | [build](verification/build.log), [repeat](verification/build-repeat.log), [hash](verification/build-sha256.txt) |
| `npm test` | PASS, all 11 numerical suites | [full output](verification/numerical.log) |
| Complete Chromium, pinned Playwright Chromium 151.0.7922.34 | PASS, 19/19; command exits 0 | [full output](verification/pinned-chromium-complete.log), [exit code](verification/pinned-chromium-complete.exit) |
| Complete Chromium on host Chromium 154.0.8037.57 | FAIL; 17/19 eventually pass, industrial/HMI playback assertions fail | [original fail-fast](verification/chromium.log), [HMI remainder](verification/chromium-remaining.log), [Assist remainder](verification/chromium-operator-assist.log), [industrial repeat](verification/chromium-industrial-repeat.log) |
| Default WebKit command, initial run | FAIL at release-suite click timeout; focus passes | [full output](verification/webkit.log) |
| Remaining seven WebKit suites after fail-fast, all executed | 4 PASS / 3 FAIL; combined with initial command, 5/9 pass | [completion summary](verification/webkit-completion.log), [individual results](verification/webkit-remaining-results.json) |
| Default WebKit command, isolated repeat | FAIL, exit 1; first four PASS, training playback/pause assertion FAIL; remaining suites already exercised separately | [full output](verification/webkit-isolated-complete.log), [exit](verification/webkit-isolated-complete.exit) |
| Original resize assertions, exact baseline versus candidate | PASS/PASS in completed comparison, original assertion code unchanged | [nested results and geometry](verification/webkit-resize-comparison.json), [output](verification/webkit-resize-comparison-repeat.log) |
| Native WebKit resize, both identical artifacts, ordinary and reduced motion | FAIL geometry agreement in several 350/1,350 ms observations; group selection redraws correctly | [native geometry](verification/native-webkit-resize.json) |
| Scenarios A/B/C, actual UI/export evidence | PASS in Chromium and native WebKit; global WebKit audit still exits 1 for its `file://` route | [scenario summary](verification/scenario-summary.json), [Chromium audit](verification/scenarios-chromium.log), [WebKit audit](verification/scenarios-webkit-1x.log) |
| Independent same-endpoint speed model versus UI export | PASS; no input-only screenshot inference | [model evidence](verification/normal-speed-model-response.json) |
| Presentation purity | PASS; accepted SI CSV bytes identical before/after units/inspection/rotation; Assist observer invariance also in original tests | [scenario summary](verification/scenario-summary.json), before/after CSVs |
| Standalone offline Chromium file startup | PASS in offline browser context | [native audit](verification/scenarios-chromium.log) |
| Standalone offline WebKit bytes | PASS; offline `setContent`, touch init/+10 s/Assist, zero HTTP requests | [output](verification/webkit-offline-bytes.log), [exit](verification/webkit-offline-bytes.exit) |
| WebKit `file://` startup | FAIL, internal navigation error in this environment | [output](verification/scenarios-webkit-1x.log); do not infer iPad Files support |
| Physical iPad | NOT RUN; user confirmation required | [manual checklist](IPAD_CHECKLIST.md) |

## Every original suite

The repository defines 19 Chromium suites and nine WebKit-aware suites. Ten other suites are hard-coded to Chromium; merely setting TEST_BROWSER=webkit does not turn them into WebKit tests. Extra environment-flag runs of those Chromium-only suites are retained in `webkit-remaining.log` but **are not counted as WebKit coverage**.

| Browser suite | Pinned Chromium | WebKit initial + completion |
|---|---|---|
| focus-mode-ui.cjs | PASS | PASS |
| default-units.cjs | PASS | Chromium-only |
| tab-errors.cjs | PASS | Chromium-only |
| browser.cjs | PASS | Chromium-only |
| live-ui.cjs | PASS | Chromium-only |
| profiles-ui.cjs | PASS | Chromium-only |
| fault-ui.cjs | PASS | Chromium-only |
| initialization-ui.cjs | PASS | Chromium-only |
| storage-ui.cjs | PASS | Chromium-only |
| valves-ui.cjs | PASS | Chromium-only |
| release-ui.cjs | PASS | FAIL, tab-validation click timeout; same failure on exact approved baseline |
| schematic-ui.cjs | PASS | FAIL, storage-example click timeout |
| history-ui.cjs | PASS | PASS |
| training-ui.cjs | PASS | FAIL, training-load click timeout |
| dashboard-ui.cjs | PASS | Chromium-only |
| visual-pass2-ui.cjs | PASS | FAIL, storage-example click timeout; isolated exact-byte comparison later PASS |
| industrial-styling-ui.cjs | PASS | PASS on completion run; earlier environment-flag run failed playback assertion |
| hmi-uplift-ui.cjs | PASS | PASS on completion run; earlier environment-flag run failed playback assertion |
| operator-assist-ui.cjs | PASS | PASS on completion run; earlier environment-flag run timed out |

Numerical suite names, all PASS: physics, dynamic, profiles, initialization, storage, valves, integration, schematic, history, training, operator-assist. Integration covers 24 real operating/fault/recovery cases. Training covers all five exercises, conservation, correct/incorrect/missing reflections, sustained bands, accepted-boundary stopping and read-only grading. Existing reference tolerances, conservation assertions, trip conditions and histories are unchanged. See the complete numerical output for measured errors and limitations.

The isolated repeat passes focus, release, schematic and history, then fails `training-ui.cjs:34` at `assert(await page.locator('#storage-pause').isDisabled())` following the existing DX-startup exercise Run/Pause interaction. It has no equipment/physics edit and no weakened assertion. This is additional browser playback-state evidence beyond the known chart check; a test-clock/state synchronization explanation is plausible but not proven for this assertion. The earlier native short playback/scenario evidence passes, so do not label this a reproducible physical iPad failure or dismiss it as harmless. Exact baseline release timeout and host Chromium industrial failure were reproduced separately; this newer training assertion was not independently rerun on the baseline. All nine WebKit suites have actual execution evidence across the initial command, seven-suite continuation and comparison, but **no completed all-nine command is green**.

## Reproduce

Normal dependency/runtime setup on a supported host:

```sh
npm ci
npx playwright install --with-deps chromium webkit
npm run build
npm test
NODE_OPTIONS="--require $(pwd)/docs/demo-candidate/pinned-chromium.cjs" npm run test:browser
npm run test:webkit
TEST_BROWSER=webkit python3 docs/demo-candidate/run-webkit-remaining.py
git show 99af25e3b68798919ede19a5c0805775d5828eab:index.html > /tmp/ammonia-approved.html
node tests/focus-webkit-resize.cjs /tmp/ammonia-approved.html index.html
node docs/demo-candidate/verify-native-resize.cjs /tmp/ammonia-approved.html index.html
node docs/demo-candidate/verify-demo.cjs
TEST_BROWSER=webkit node docs/demo-candidate/verify-demo.cjs
```

On this managed host, browser paths are under `/workspace/playwright-browsers` and WebKit libraries are extracted in `/workspace/browser-libs`; the downloaded launcher includes that library path and PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 bypasses only host-library discovery. Scientific/browser assertions remain active. The `pinned-chromium.cjs` preload only removes the helper's `/usr/bin/chromium` selection and uses Playwright's matching downloaded browser. It does not adjust clocks, assertions or application behavior.

Early parallel probes and interrupted native 10× runs are not passes. Their logs/screenshots/exports are preserved separately. Some browser invocations left orphan WebKit content processes; these test-only processes were terminated before finishing isolated checks. Environment timing/load and Linux rendering must be considered before attributing delays to actual iPad Safari. The report still retains native geometry mismatches and device acceptance gates.
