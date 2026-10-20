# Owner desktop benchmark

NONPRODUCTION / EXPERIMENTAL. This runs named research fixtures in browser Web Workers on your own computer. No plant connection, public hosting, Cloudflare account, deployment, or workstation replacement is needed. Existing scientific qualification is 0.001 simulated seconds. The benchmark resets each fixture and explores through at most 0.01 s, which remains UNQUALIFIED RESEARCH.

## Small local package

Use `b16-owner-benchmark.zip` in this directory, or copy the B16 directory from this branch. Extract the ZIP into its own folder. The ZIP contains two frozen scientific bundles, the local harness, and a Python standard-library server. It requires no npm install, compiler, CoolProp, or scientific Python packages.

Prerequisites: an ordinary desktop browser that supports module Web Workers and Python 3 (`python --version`, `python3 --version`, or on Windows `py --version`). If Python is unavailable, have an engineer serve the extracted folder on localhost with correct `.mjs` JavaScript MIME types; opening `index.html` via `file://` is insufficient. Do not install browser extensions or alter browser security flags for this test.

From the extracted folder:

```sh
python3 serve.py
```

Windows commonly uses `py serve.py` or `python serve.py`. Open <http://127.0.0.1:8765/index.html> in the browser being tested. The server binds only localhost. Stop it with Ctrl-C when finished. If port 8765 is occupied, use `serve.py --port 8766` and adjust the URL.

## Collect genuine device data

Record OS and version, exact browser name/version, processor model and installed RAM in the machine field. Windows: Settings → System → About, plus `edge://version` / `chrome://version`. macOS: About This Mac, plus browser About/version page. Browser-reported logical cores and deviceMemory are hints and do not replace processor/RAM details. Record power/battery mode, other heavy applications and whether the tab stayed foreground. Actual Edge results require running Microsoft Edge; Chrome/Chromium results cannot be renamed Edge.

Press **Run bounded desktop benchmark** once. Keep the tab foreground and avoid other expensive workloads. The run uses six counterbalanced pairs for each cold/warm fixture, one bounded untimed warmup per fresh Worker, then a fresh measured model. All runs end at ≤0.01 s and terminate their Worker. It may take several minutes on slower machines. The output includes worker-ready latency, asset verification/import/table creation, initialization/first snapshot, computation, service/round-trip timings, ping and compact snapshot echo, 10 ms heartbeat delays, synthetic input/tool-click acknowledgements, disposal and errors. Warmup time is separately reported and is not warm initialization of an existing model. The browser asset cache may be warm; this is not an empty-disk-cache cold-start test.

Press **Download genuine JSON results**. Preserve the file unchanged. If there is a browser error, copy the displayed error and browser console output; do not replace it with a successful example. Record whether all 24 samples completed. Optional: screenshot the page and browser version. Repeat in another browser as a separate file, with the exact runtime recorded. A screenshot alone does not establish parity or performance.

The JSON includes binary64 scientific digests outside timed compute windows and per-pair workload checks. An engineer should compare each candidate/control digest and scientific counters before using timing evidence. Run the full automated scientific suite on the target runtime when practical; this small owner package is a performance handoff, not a substitute for all diagnostic/refusal regressions. No integration or accepted-engine promotion follows automatically from submitting results.

No genuine owner-device result is included in B16 cloud measurements. Windows/macOS performance remains NOT TESTED until actual results are supplied. The UI is a small research harness; its responsiveness does not qualify the full workstation. Synthetic DOM clicks are explicitly labeled and do not measure physical mouse/touch-to-display latency. Short reset sessions do not prove hours-long memory stability. No unsupported property states or extended physics operation are requested.

## Rebuild the package from the B16 checkout

```sh
python3 experiments/dx-fv/browser_eos_b16/package-desktop.py --output .runtime/rebuilt-owner.zip
```

Use a new output name if one already exists. All generated output stays within B16. Check the corresponding package manifest and frozen asset SHA-256 values before distributing. Keep the exact B9C original available as the `control` mode; never replace it with the candidate or make a production default from these measurements.
