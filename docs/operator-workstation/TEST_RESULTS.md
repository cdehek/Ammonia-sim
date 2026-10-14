# Verification results

Starting checkpoint: `aa5612eb1caaeac38831fc0ae97cb94fe8048735`. The baseline was checked out in a detached worktree. Both versions use Playwright 1.62.1, pinned Chromium 151.0.7922.34 and WebKit 26.5/build 2336 on the same managed Linux host. These are browser-emulation results, not physical iPad validation.

## Outcomes

| Check | Exact checkpoint | Console candidate |
|---|---|---|
| Production build | Approved standalone artifact used directly | PASS; self-contained build, [log](verification/build-final.log), [hash and runtime metadata](verification/build-metadata.json) |
| Numerical/model suites | Protected sources byte-compared with checkpoint | PASS: all 11 suites, [output](verification/numerical-final.log) |
| Complete original Chromium coverage | 19/19 PASS, [results](verification/baseline-chromium/results.json) | 19/19 PASS; standard command also runs the new console suite, **20/20 PASS**, [output](verification/chromium-command-final.log) |
| Complete original WebKit coverage | 7/9 PASS, [results](verification/baseline-webkit/results.json) | 7/9 PASS, [final results](verification/candidate-webkit-final/results.json), [completion output](verification/webkit-complete-final.log) |
| Focused console checks | Used as exact exercise/evidence comparator | PASS in [Chromium](verification/chromium-console-final.log) and [WebKit](verification/webkit-console-final.log) |
| Frozen retained-attempt readings and timestamps | Existing export behavior preserved | PASS in [Chromium](verification/chromium-retained-readings.log) and [WebKit](verification/webkit-retained-readings.log) |
| Native offline `file://` startup | Chromium PASS; WebKit internal navigation error | Same result; [Chromium comparison](verification/chromium-offline-file.json), [WebKit comparison](verification/webkit-offline-file.json) |
| Offline standalone bytes, no HTTP requests | Existing behavior preserved | PASS in both focused console suites: initialize, advance and Assist |
| Physical iPad | Not performed | Not performed; [review gate](IPAD_REVIEW.md) |

The 11 numerical suites cover physics, dynamic response, profiles, inventory initialization, storage, valves, integration, schematic projection, history, training and Operator Assist. Integration includes 24 operating/fault/recovery cases. No numerical test, reference tolerance or conservation assertion changed.

## Every original WebKit suite

| Suite | Baseline | Final candidate |
|---|---|---|
| focus-mode-ui | PASS | PASS |
| release-ui | PASS | PASS |
| schematic-ui | PASS | PASS |
| history-ui | PASS | PASS |
| training-ui | FAIL | FAIL |
| visual-pass2-ui | FAIL | FAIL |
| industrial-styling-ui | PASS | PASS |
| hmi-uplift-ui | PASS | PASS |
| operator-assist-ui | PASS | PASS |

The training failure is the existing `storage-pause.isDisabled()` assertion after DX-startup Run/Pause at `training-ui.cjs:34`. It fails on the exact checkpoint and the final candidate: [baseline](verification/baseline-webkit/training-ui.log), [candidate](verification/candidate-webkit-final/training-ui.log). It remains unresolved. Step-based exercise completion and identical exported evidence do not resolve this playback finding.

The chart failure is the original **Chart geometry expands at desktop width** assertion at `visual-pass2-ui.cjs:22`. It fails on both: [baseline](verification/baseline-webkit/visual-pass2-ui.log), [candidate](verification/candidate-webkit-final/visual-pass2-ui.log). No chart implementation, resize assertion or history semantics were changed.

The standard `npm run test:webkit` command was also executed and exits 1 at training, preserving fail-fast behavior. Its concurrent repeat failed one assertion earlier in the same playback interaction, at the `/Pause/` label expectation: [output](verification/webkit-command-final.log). That exact label variation is recorded separately from the matched full-run `isDisabled()` failure; its cause has not been established. Sequential isolated training reruns **pass on both baseline and candidate**: [results](verification/webkit-isolated-training.json), [baseline output](verification/webkit-isolated-baseline-training.log), [candidate output](verification/webkit-isolated-candidate-training.log). Thus full-run failures and the concurrent label variation remain variable, not explained or dismissed. The exact label variation was not reproduced on the checkpoint in these runs. The complete runner ensures the remaining WebKit suites are still exercised after a failure. **There is no green all-WebKit release claim.**

## Newly introduced regression found and fixed

An initial candidate WebKit run found that opening Assist moved focus away from its original Close button. The new console heading took focus after Assist had set it. The console now preserves Assist's original opening focus. The original keyboard assertion passes in the [targeted rerun](verification/webkit-assist-focus-fix.log) and the final complete WebKit run. The initial failure remains in [this log](verification/candidate-webkit/operator-assist-ui.log). This was a new regression, not a baseline finding.

Early Chromium iteration logs include incomplete test-navigation migration (loop scope and hidden-control navigation) and a console focus-return issue. They were corrected, and every original assertion passes in the standard Chromium command. Iteration logs are retained under `verification/candidate-chromium/` and `verification/candidate-chromium-final/`; they are not reported as final passes. Legacy workflows now navigate through the actual console links before acting or inspecting a tool. The helper does not force clicks, adjust clocks, pause playback, mutate the simulator or relax assertions. Playback and chart assertions remain present.

## Evidence and model preservation

The new focused suite completes all five recipes in both versions, exports each attempt, and compares the entire JSON **byte for byte**. This includes SI histories, objective evidence, accepted completion boundaries, quiz attempts, disturbances, stop events, final state and training exports. All five comparisons pass in both browsers. The [Chromium summary](verification/chromium-console-summary.json) and [WebKit summary](verification/webkit-console-summary.json) link to the full evidence files stored beside them.

Hot Condenser Air observes the actual modeled high-discharge-temperature equipment trip, checks Assist's original recorded evidence across tool changes, restores the established off-state controls, clears the stop and accepts the required continuation before completion. No synthetic trip or completion flag is used. A disturbance-before-reflection workflow also completes without an added ordering constraint.

Console navigation, inspection, rotation and Assist viewing leave exported SI storage CSV bytes unchanged. The focused checks verify one copy of each DOM control, all tool categories, all three console states, schematic visibility, expanded playback-header clearance, touch targets, keyboard activation, Escape/focus return, 1440×1000 desktop, 1024×768 landscape and 768×1024 portrait. Offline byte startup has zero HTTP requests and no page errors. Retained reading values and timestamps stay frozen when free exploration advances the connected plant after completion.

[Seventeen protected source/artifact comparisons](verification/protected-source-parity.json) show byte-identical engines, properties, profiles, accepted history, grading, Assist interpretation, schematic implementation and the released demo-candidate HTML. Only UI presentation, build inclusion, browser navigation/tests and review documentation changed. The CI checkout now fetches history so the new exact-checkpoint evidence comparison also works outside a full local clone.

## Limits and review status

The Linux WebKit `file://` internal error occurs on both artifacts before application startup. Offline `setContent` succeeds and exercises the self-contained application in both browsers, but does not prove the intended physical iPad Files/Safari workflow. The reported playback and chart findings need device investigation. Safe areas, onscreen keyboards, VoiceOver and touch comfort need the [physical iPad checklist](IPAD_REVIEW.md).

The branch stops for review. No main/release branch, protected release artifact, research branch, Cloudflare preview or hosting configuration was changed, merged or deployed.
