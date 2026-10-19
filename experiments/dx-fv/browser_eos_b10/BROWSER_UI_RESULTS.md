# Served-browser UI results

B10 scientific/display/lifecycle/isolation checks PASS in actual Chromium 151.0.7922.34 and desktop WPE WebKit 26.5/build 2336. Original Chromium remains 19/19 plus console; pinned WebKit baseline is 7/9 and final sequential B10 candidate is 8/9, plus passing console. The inherited chart assertion still fails identically. The training pause assertion passes in that candidate sample, a variable result without a claimed fix. See ORIGINAL_WORKSTATION_REGRESSION.md. No physical iPad was tested.

| Browser | Viewport | Focus/touch/overflow/control access | Section table client / scroll px |
|---|---|---|---|
| chromium | desktop 1440×1000 | PASS | 1404 / 1404 |
| chromium | landscape 1024×768 | PASS | 988 / 1075 |
| chromium | portrait 768×1024 | PASS | 732 / 1075 |
| webkit | desktop 1440×1000 | PASS | 1404 / 1404 |
| webkit | landscape 1024×768 | PASS | 988 / 1082 |
| webkit | portrait 768×1024 | PASS | 732 / 1082 |

The new region is inside the real console-content; it is not an iframe or second workstation. Real accepted cold/warm instruments appear beneath the original schematic workspace. Desktop, landscape and portrait reviews check 44-pixel controls, no page overflow/duplicate parent IDs, correct resizing and horizontal table confinement. Expanded/partial/collapsed behavior, keyboard activation, Escape and focus return retain existing console ownership. Expanded screenshots show source/qualification labels and genuine values; instrument screenshots review scrolling. Existing playback controls remain above the expanded console. Expansion intentionally occupies the detail workspace; collapse/Plant overview returns to the original schematic.

Actual pagehide cleanup and five restart/disposal cycles per browser pass. B10 uses one isolated root and bounded metrics; no panel ResizeObserver is created. No listener/observer growth is introduced by tool switching in this bounded design; this is not a sustained leak campaign. Interaction/status/clock logs and screenshots are evidence/integration-*, isolation-* and candidate-*. Original schematic/training/Assist interactions are independently covered by the unmodified suites.
