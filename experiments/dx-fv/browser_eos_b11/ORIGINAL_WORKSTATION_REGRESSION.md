# Original workstation regression

PASS for preservation; desktop WebKit remains PARTIAL as a release target. Comparator is exact 262b6092, not the different repository-root application. The original embedded model/control/Assist/training/history and UI function bodies are byte-preserved. Eleven original numerical suites pass. All original assertions remain unchanged.

| Browser | Suite | Original pinned | B11 package |
|---|---|---|---|
| chromium | focus-mode-ui | PASS | PASS |
| chromium | default-units | PASS | PASS |
| chromium | tab-errors | PASS | PASS |
| chromium | browser | PASS | PASS |
| chromium | live-ui | PASS | PASS |
| chromium | profiles-ui | PASS | PASS |
| chromium | fault-ui | PASS | PASS |
| chromium | initialization-ui | PASS | PASS |
| chromium | storage-ui | PASS | PASS |
| chromium | valves-ui | PASS | PASS |
| chromium | release-ui | PASS | PASS |
| chromium | schematic-ui | PASS | PASS |
| chromium | history-ui | PASS | PASS |
| chromium | training-ui | PASS | PASS |
| chromium | dashboard-ui | PASS | PASS |
| chromium | visual-pass2-ui | PASS | PASS |
| chromium | industrial-styling-ui | PASS | PASS |
| chromium | hmi-uplift-ui | PASS | PASS |
| chromium | operator-assist-ui | PASS | PASS |
| webkit | focus-mode-ui | PASS | PASS |
| webkit | release-ui | PASS | PASS |
| webkit | schematic-ui | PASS | PASS |
| webkit | history-ui | PASS | PASS |
| webkit | training-ui | FAIL | PASS |
| webkit | visual-pass2-ui | FAIL | FAIL |
| webkit | industrial-styling-ui | PASS | PASS |
| webkit | hmi-uplift-ui | PASS | PASS |
| webkit | operator-assist-ui | PASS | PASS |

Chromium: baseline 19/19, package 19/19. Desktop WebKit: baseline 7/9, package 8/9. Raw logs and assertion context are retained in baseline/candidate directories and regression-comparison.json; no new required-suite regression.

B10 previously recorded Chromium 19/19, WebKit baseline 7/9 and integrated 8/9: chart width failed historically and the training-pause assertion was variable. B11 reproduces the current sequential samples above. A passing training sample is not a repair or proof that flakiness is resolved; the chart/playback source/assertions are unchanged. No unrelated repair is made.

Additional original operator-console and retained-reading suites pass in both browsers. They exercise collapsed/partial/expanded states, seven original tools, touch/keyboard/focus/Escape, original schematic and settings/units, all five lessons, hot-trip/recovery, retained Assist, full training and SI exports and standalone original offline bytes. Original offline setContent evidence does not qualify the scientific worker.

isolation-{browser}.json.gz retains fourteen original state/history/clock workflows, exact original storage/history CSV checks, Assist and full exercise exports. A2-only initialization leaves original state null; advancing either model leaves the other state/history exact. Idle, initializing, running, stopped, disposed and lost/refusal paths preserve original controls. Real worker startup loss leaves original playback running. No A2 history enters Live Plant history and no A2 fault becomes an equipment alarm.
