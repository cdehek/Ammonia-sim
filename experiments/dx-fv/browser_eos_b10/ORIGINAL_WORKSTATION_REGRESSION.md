# Original workstation regression preservation

PASS for preservation. Exact source at 262b6092 is the comparator, not the different root application on the research branch. Rebuilt HTML is byte-identical before the reversible presentation insertion. Eleven original numerical suites pass. Chromium is 19/19 in baseline and B10; original console and retained-reading suites also pass. Desktop WebKit is 7/9 in both the sealed pre-implementation baseline and the final sequential pinned baseline; the final sequential B10 candidate is 8/9. No assertion is weakened and no new original-suite regression is observed.

| Browser | Original suite | Baseline | B10 | Assertion |
|---|---|---|---|---|
| chromium | focus-mode-ui | PASS | PASS | unchanged original assertions |
| chromium | default-units | PASS | PASS | unchanged original assertions |
| chromium | tab-errors | PASS | PASS | unchanged original assertions |
| chromium | browser | PASS | PASS | unchanged original assertions |
| chromium | live-ui | PASS | PASS | unchanged original assertions |
| chromium | profiles-ui | PASS | PASS | unchanged original assertions |
| chromium | fault-ui | PASS | PASS | unchanged original assertions |
| chromium | initialization-ui | PASS | PASS | unchanged original assertions |
| chromium | storage-ui | PASS | PASS | unchanged original assertions |
| chromium | valves-ui | PASS | PASS | unchanged original assertions |
| chromium | release-ui | PASS | PASS | unchanged original assertions |
| chromium | schematic-ui | PASS | PASS | unchanged original assertions |
| chromium | history-ui | PASS | PASS | unchanged original assertions |
| chromium | training-ui | PASS | PASS | unchanged original assertions |
| chromium | dashboard-ui | PASS | PASS | unchanged original assertions |
| chromium | visual-pass2-ui | PASS | PASS | unchanged original assertions |
| chromium | industrial-styling-ui | PASS | PASS | unchanged original assertions |
| chromium | hmi-uplift-ui | PASS | PASS | unchanged original assertions |
| chromium | operator-assist-ui | PASS | PASS | unchanged original assertions |
| webkit | focus-mode-ui | PASS | PASS | unchanged original assertions |
| webkit | release-ui | PASS | PASS | unchanged original assertions |
| webkit | schematic-ui | PASS | PASS | unchanged original assertions |
| webkit | history-ui | PASS | PASS | unchanged original assertions |
| webkit | training-ui | FAIL | PASS | Baseline storage-pause.isDisabled at training-ui:34; candidate PASS (variable, no fix claimed) |
| webkit | visual-pass2-ui | FAIL | FAIL | Chart geometry expands at desktop width |
| webkit | industrial-styling-ui | PASS | PASS | unchanged original assertions |
| webkit | hmi-uplift-ui | PASS | PASS | unchanged original assertions |
| webkit | operator-assist-ui | PASS | PASS | unchanged original assertions |

Startup, Live Plant initialization/playback/start-stop, equipment controls/profiles, schematic inspection, original units, inventory, trends/history, guided exercises/scoring/exports, retained attempts, Assist conclusions, seven original console tools, focus/keyboard/Escape and collapsed/partial/expanded behavior retain original assertions. Existing standalone/offline-original workflows remain intact because A2 modules load only on selecting the new tool. This does not qualify offline A2 startup.

`regression-comparison.json` explicitly records same/different assertions, new regressions and disappeared prior failures. The inherited chart-width assertion at visual-pass2-ui:22 fails identically in baseline and candidate. The training pause assertion at training-ui:34 fails in both pinned baseline samples but passes in the final sequential candidate sample: its prior failure disappeared in that sample. This variable result is not a claimed fix; original training functions and assertions are unchanged. B10 is not fully green on WebKit. Original console step-based completion/export checks and all five full export comparisons pass.

`isolation-*.json.gz` contains full original state/history hashes, independent clocks, exact storage/history CSV hashes, retained Assist text and all fourteen required workflows. A2-only initialization leaves original state null; advancing either model leaves the other's snapshot/history exact. Tool changes, faults and disposal do not mutate the original plant. Trusted original Start input is acknowledged during an actual pending A2 advance. Worker startup loss is caught locally while original playback remains running. Training never dispatches A2 work.
