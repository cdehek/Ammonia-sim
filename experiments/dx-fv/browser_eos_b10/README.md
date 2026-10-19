# B10 — Operator Workstation Shadow Hook-Up

An opt-in **A2 — Five-Section Evaporator Research** tool inside an exactly derived copy of the real operator workstation. Read ENGINEERING_REPORT.md for the final scoped decision and evidence. The original schematic, illustrative Live Plant, training, history and Operator Assist retain their pinned model and source.

## Open the research workstation

From repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/experiments/dx-fv/browser_eos_b10/`. Select **A2 Evaporator Research** in the existing bottom console rail (scroll the rail horizontally if needed). Expand the console for instrumentation. Initialize cold or warm, then request exactly .0001, .0004 and .0005 seconds. The accepted clock ends at .001 s. Readings and the small history come from the actual accepted numerical model, not animation. Use original console tools or Plant overview to return; both models retain independent state.

Opening the page/panel initializes neither model. Original **Initialize auto DX**, Start, Pause, +10 s and training controls continue to operate only the original illustrative plant. A2 has its own session, clock, worker, accepted history, stop/dispose and restart. A2 numerical/domain stops never become equipment alarms. Previous accepted readings remain explicitly stale after a refusal. Valid partial accepted progress can precede refusal; worker time and displayed successful time are separate.

Five evaporator sections only. No qualified compressor, condenser, receiver, actuator or plant coupling. Bulk wet is not compressor suction safety evidence. Effective conductance is uncalibrated. Table-backed served research only; no continuous operation, offline packaging, physical iPad certification, production merge or deployment.

## Reproduce the exact artifact and checks

All generated/committed material stays here. Runtime files are ignored under `.runtime`. Do not run root build tools on the historical checkout.

```sh
python3 experiments/dx-fv/browser_eos_b10/build.py
```

This archives the exact pinned workstation Git objects, checks all 574 source identities and all 2,958 historical hashes, runs the original build only in `.runtime/build-source`, verifies pinned HTML, applies reversible presentation insertions, and writes this directory's index.html and bridge adapters. `artifacts/pinned-workstation.html` is the byte-exact original comparator. `evidence/build-manifest.json` and `bridge-adapter-diff.json` describe every derivation change. No original function body or scientific algorithm is edited.

Browser setup: Python Playwright 1.62.0, Node Playwright 1.62.1, Chromium 151.0.7922.34, desktop WPE WebKit 26.5/build 2336. Install node dependencies using the pinned package-lock in an isolated Git archive, with npm's cache inside `.runtime`. Install browsers into `.runtime/browsers`; `setup-runtime.py` extracts the original hash-pinned Debian shared libraries and creates the WPE launcher without host package edits. No security preference or file/CORS bypass is used. See `evidence/runtime-manifest.json` for executable hashes.

```sh
python3 experiments/dx-fv/browser_eos_b10/prepare-tests.py --install-node
PLAYWRIGHT_BROWSERS_PATH="$PWD/experiments/dx-fv/browser_eos_b10/.runtime/browsers" python3 -m playwright install chromium webkit
python3 experiments/dx-fv/browser_eos_b10/setup-runtime.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 python3 experiments/dx-fv/browser_eos_b10/run-scientific-review.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 python3 experiments/dx-fv/browser_eos_b10/run-integration.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 python3 experiments/dx-fv/browser_eos_b10/run-isolation.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 python3 experiments/dx-fv/browser_eos_b10/run-render.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 python3 experiments/dx-fv/browser_eos_b10/run-performance.py
```

Run exhaustive suites sequentially on this two-core environment. Host-requirement discovery is skipped only because the pinned workspace WPE launcher supplies its actual libraries; browser security stays enabled. The scientific review runs the unchanged exhaustive B9C/B9D harness and retains complete scientific/component hashes, avoiding duplicate raw diagnostic retention. Original raw scientific receipts remain protected in B9C/B9D; B10 retains its own accepted states/records and exact attempt hashes. Test-only C1 injection stays separate from the optimized table worker.

`run-original.cjs candidate` runs literal pinned suites from `.runtime/candidate` with the derived index.html and correct static module MIME serving. Use `NODE_OPTIONS=--require=<absolute B10>/browser-preload.cjs`, `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`, and `TEST_BROWSER=webkit` for WebKit. The preload changes runtime selection only. Prepare candidate by copying the isolated pinned archive and replacing only its index.html. Original tests/assertions remain byte-identical. `tests/operator-console-ui.cjs` and `console-retained-readings.cjs` run additionally from that archive. New isolation tests compare all five complete exports against actual pinned baseline files, including SI histories, objectives, timing and stop evidence.

The nine WebKit-aware suites are 7/9 in the pinned baseline and 8/9 in the final sequential B10 candidate. The inherited chart assertion fails identically. Training passes in that candidate sample despite a failing baseline pause assertion; this variable result is not a claimed fix. WebKit is not fully green. Compare each candidate assertion with the exact baseline. No physical-device, offline, production or plant-wide claim follows from the served tests. Run `preservation.py` with freshly recorded remote refs/PR identity before publication. Only the B10 branch may be pushed. Stop for engineering review after the final audit.

Completed results are already saved. To verify the delivery without repeating browser or numerical suites:

```sh
python3 experiments/dx-fv/browser_eos_b10/seal-delivery.py --check-only
python3 experiments/dx-fv/browser_eos_b10/preservation.py --check-only
```

`evidence/delivery-sha256.json` hashes every nonignored B10 file except itself; Git seals that manifest. The packaging check also verifies all ten complete training exports and the preserved pre-implementation WebKit receipts directly. `preservation.py` checks the saved remote/PR snapshots; a fresh live remote/connector comparison is required for publication. `write-reports.py` regenerates reports and tracker from completed receipts, and `seal-delivery.py` refreshes the manifest after authorized B10 delivery changes. These commands do not advance either physical model.

After publication, `preservation.py --check-only --live` additionally reads the current remote refs and requires the B10 remote head to equal local HEAD. It does not write receipts. See PUBLICATION_AND_FINAL_VERIFICATION.md for the sealed publication identity and final read-only procedure.
