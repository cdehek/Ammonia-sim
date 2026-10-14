# Operator Workstation UX Overhaul v1

Review build based on `aa5612eb1caaeac38831fc0ae97cb94fe8048735`, the head of `release/demo-candidate-20261014`. Work is isolated on `feature/operator-workstation-bottom-panel-20261014`. No merge, deployment, publishing, hosting change or release-candidate modification is part of this milestone.

The live refrigerant schematic remains the workspace. The bottom Operator Console holds the existing tools, with a single set of DOM controls and the existing connected model and training adapter. The schematic equipment drawings and inspection controls are unchanged.

## Using the console

| State | Behavior | How to leave it |
|---|---|---|
| Collapsed | Compact launcher and horizontally scrollable tool links; a retained exercise shows its real status and objective count. | Open console or choose a tool. |
| Partial | Approximately 38% of viewport height, with internal scrolling. The plant, readings and playback remain above it. The schematic retains its existing scale and can be inspected by scrolling. | Expand, Collapse, Close or Escape. |
| Expanded | Detail space extends up to the playback header. The header's measured geometry limits panel height. | Partial height, Close or Escape. |

Guided Exercises, Plant Controls, Trends & History, Inventory, Equipment Profiles, Operator Assist and Independent Room Model share the console. The original Plant overview link returns focus and scroll to the live schematic. Each original section remains available. Switching tools does not initialize, apply, reset, pause or advance the model. Tool state is presentation state only; it is not saved as a competing simulator or training session.

The console is a nonmodal region. It does not trap Tab navigation. Open and tool selection move keyboard focus into the tool; Close returns focus to the launcher used to open it. Escape reduces expanded to partial and closes partial. Operator Assist preserves its original Close-button focus, Escape handling and return to its existing launcher. Buttons and fields retain touch sizing, inactive tools are hidden from navigation, and there is no required drag gesture. Safe-area padding and visual-viewport resize handling keep the panel usable with tablet browser chrome and keyboards. Physical keyboard and onscreen-keyboard behavior still require device review.

Focus Mode is preserved. `?workspace=all` restores the existing six workspaces and reference tools. Model information and limitations remain in the header, including the original validation route and keyboard return. The console is hidden when its Live Plant parent is hidden.

## Guided Exercises

The current attempt name and status, a short explanation and a **Suggested next action** appear first. **Go to control** focuses and scrolls to the existing control; it does not perform an operation. Expand or scroll within the console to see reflection choices, current measured objectives, recorded evidence, hints and exercise actions. Exercise selection, load/reset/end and evidence export remain in **Choose, load or manage an exercise**. Selecting a different lesson does not relabel or rewrite a retained attempt.

Suggestions follow the real attempt and accepted simulator state. They are explicitly separate from required grading. No extra button-order constraints were introduced. A disturbance before reflection remains supported. Each completion marker comes from the engine's existing `goal.met` and evidence. Accepted readings use their actual recorded sample timestamps and SI units even when the main instruments use Fahrenheit and psig. Completed or stopped attempts show frozen retained-attempt readings rather than drifting with subsequent free exploration.

For Hot Condenser Air, loading performs the existing automatic 30-second warmup. Guidance suggests reflection, the existing 104°F disturbance, simulated-time observation, inspection of the recorded high-discharge-temperature equipment trip, off-state restoration, clearing and accepted off-state continuation. It only describes a recorded trip after `expectedFault` exists, and only reports completion after the engine completes the attempt. All five exercises use their established recipes and thresholds.

Operator Assist v0.1 is the existing deterministic, read-only, offline projection. The console changes its presentation and focus integration only. It retains accepted observations, captured evidence, units, interpretations and the distinction between equipment trips and numerical/model stops.

## Review artifacts

- [The Mechanic's Report](MECHANICS_REPORT.md)
- [Test results and exact-baseline comparison](TEST_RESULTS.md)
- [Physical iPad review checklist](IPAD_REVIEW.md)
- [Exact changed-file manifest](CHANGED_FILES.txt)
- [Screenshots](SCREENSHOTS.md)
- [Protected-source byte comparisons](verification/protected-source-parity.json)

The built [index.html](../../index.html) is self-contained and offline-capable. `npm run build` also writes the standalone artifacts under ignored `dist/`; no assets or model libraries are loaded from a network service.

## Reproduce

```sh
npm ci
npx playwright install --with-deps chromium webkit
npm run build
npm test
npm run test:browser
npm run test:webkit
TEST_BROWSER=webkit node tests/run-complete.cjs . docs/operator-workstation/verification/local-webkit
npm run test:console
TEST_BROWSER=webkit npm run test:console
node tests/console-offline-file.cjs
TEST_BROWSER=webkit node tests/console-offline-file.cjs
```

`run-complete.cjs` executes every original suite and records failures instead of stopping at the first. The new console suite compares every exercise export with the approved commit using `git show`; `BASELINE_HTML` can supply an exact-baseline artifact instead. Ten of the original 19 browser suites are Chromium-only; setting `TEST_BROWSER=webkit` does not convert those into WebKit coverage. The existing nine WebKit-aware suites and the new console suite comprise WebKit coverage.

On this managed Linux host the pinned Chromium preload avoids the helper's optional system Chromium override. WebKit uses a workspace copy of the pinned browser launcher with downloaded shared libraries appended to its runtime path, plus `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` to bypass host-library discovery only. No application clock, numerical tolerance, objective, playback assertion or chart assertion was changed by this setup. Browser processes require the execution environment's permitted process/network context.
