# Operator Assist v0.1 verification

Approved base: `6ab134dfe31f71cbab72c3a4f0ac4c5f3a46a29f`.
Feature branch: `feature/operator-assist-v0-1-20261013`.

| Check | Result | Evidence |
|---|---|---|
| `npm run build` | Passed; standalone bundle 1,709,014 bytes; 14,455-byte increase, no dependency added | [Build log](build.log) |
| `npm test` | All 11 suites passed, including Operator Assist | [Numerical log](numerical.log) |
| `npm run test:browser` | All 18 Chromium suites passed | [Chromium log](chromium.log) |
| Focused WebKit Operator Assist | Passed with all focused assertions active | [Focused WebKit log](assist-webkit.log) |
| `npm run test:webkit` | All 8 WebKit suites passed in the final complete run | [WebKit log](webkit.log) |
| Exact protected-file comparison | 15 scientific/application/history/chart sources and validation reports byte-identical to approved base | [Hashes](source-preservation.txt) |
| JavaScript syntax / source whitespace | Passed for all changed JS and both new tests | `node --check`, `git diff --check` |

The integrated scientific suites retain all existing assertions, including the 24 operating/fault cases with conservative maxima of **2e-13 kg** mass residual and **2.6e-9 kJ** combined energy residual. The focused observer test compares entire states after each advancement, including history, controller, counters and pending playback. Browser coverage compares actual SI exports from equal UI advances, with and without Operator Assist and with different display units.

## Matched WebKit chart-resize comparison

The existing `tests/verify-webkit-resize.cjs` diagnostic was reused through a temporary copy that changes only output location, version labels and module path. It invokes the original `tests/visual-pass2-ui.cjs` unchanged on both HTML snapshots, sequentially, under identical WebKit, viewport and clock conditions. No assertion, deadline or chart code was changed.

| Snapshot | HTML SHA256 | Original assertion run |
|---|---|---|
| Exact approved baseline | `15bc108cebe4c3346490c0db9433aabd6e19190d96397933d7867c4afe2dd5c4` | **Failed**: “Chart geometry expands at desktop width”, `visual-pass2-ui.cjs:22` |
| Operator Assist build | `37d90ed8ba0800ee5a8ccb2b814abde278bf11eb7218674a2f157f085254c444` | **Passed** |

[Full matched results and geometry](webkit-resize.json) · [Raw diagnostic output](baseline-comparison.log).

Separate geometry probes measured 741-unit plots/viewBoxes at 1024px, and 1157-unit plots/viewBoxes after the 1440px resize, both immediately and after settling, with the same pinned 0.0000 s sample retained. These later probes do not turn the original baseline failure into a pass. The approved baseline already documents this timing-sensitive failure. A passing feature comparison does not establish a fix; `storage-trends.js` is unchanged. The known WebKit redraw timing risk remains explicit.

## Environment and limits

Playwright remains the pinned **1.62.1**, with system Chromium and downloaded **WebKit v2336 / 26.5**. WebKit's system installer could not obtain root access. Missing Debian runtime libraries were downloaded/extracted under `/tmp`, verified with `ctypes.CDLL`, and made available to the temporary browser bundle. Only Playwright's library-location preflight was bypassed with `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`; test assertions were preserved. Final WebKit verification ran outside the shell sandbox after sandboxed browser processes had unusually long runtimes.

Representative command for that temporary environment:

```sh
PLAYWRIGHT_BROWSERS_PATH=/tmp/ammonia-playwright \
LD_LIBRARY_PATH=/tmp/ammonia-webkit-libs/usr/lib/x86_64-linux-gnu \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 npm run test:webkit
```

The focused test uses a paused test clock and explicit advancement so screenshots cannot accrue additional simulation time while being captured. The existing browser suites and their scientific/browser assertions remain unchanged. Superseded diagnostic runs are excluded from final pass counts; their failures prompted the entry-button layout correction and deterministic capture-clock setup. Historical checked-in screenshot galleries are restored after browser suites generate their incidental captures.

Standalone offline startup, keyboard, emulated touch and reduced motion are automated checks in both Chromium and WebKit. Screenshots are desktop/iPad viewport emulation, not physical-device acceptance. No real-plant validation or recovery certification is claimed.

The exact commit file manifest is in [changed-files.txt](changed-files.txt). The feature is prepared only for review on its isolated branch; no merge, hosting change or navigation-mode work is included.
