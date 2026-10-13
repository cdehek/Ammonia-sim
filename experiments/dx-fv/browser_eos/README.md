# Local browser EOS feasibility research

**Experimental and unqualified. No simulator integration.**
Read [Engineering Report](ENGINEERING_REPORT.md) and
[Mechanic's Report](MECHANICS_REPORT.md).

The preferred researched option is official CoolProp 8.0.0 HEOS::Ammonia in a
worker with exact caching. Desktop operation is demonstrated. A low-pressure
PH flash precision issue and actual-iPad validation remain migration gates.

## Open the isolated prototype

From the repository root, use an HTTP server with `.wasm` served as
`application/wasm`, for example Python 3.12:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/experiments/dx-fv/browser_eos/`. The buttons run a
historical inventory in a worker and prepare only this research directory for
offline use. This does not load the production simulator. Assets are local and
pinned; no thermodynamic request leaves the browser. `file://` is unsupported.
The prototype prints research data in SI, including raw nonphysical Q sentinels.

## Reproduce in a disposable checkout

Keep delivered evidence unchanged. The harness **skips completed output files**;
use a disposable checkout or move its new browser evidence to an external
baseline folder for a deliberate fresh replay. Do not delete original protected
files or old research evidence.

Node 24.19.0 and Playwright 1.62.1 were used. The experimental package/lockfile
are separate from the root application package. Install here, not at the root:

```bash
cd experiments/dx-fv/browser_eos
npm ci
npx playwright install chromium webkit
```

Linux WebKit also needs its usual system libraries. This environment extracted
needed Debian libraries under `/workspace/ammonia-browser-runtime/sysroot` and
used the retained `upstream/desktop-webkit-launcher.sh`; paths in that file are
specific to this execution workspace. On a normally configured machine use the
standard Playwright launcher. Local test runtime files are not shipped as app
assets. This is Linux desktop WebKit, not iPad Safari.

From the repository root:

```bash
node experiments/dx-fv/browser_eos/benchmark.cjs accuracy initialization performance worker
node experiments/dx-fv/browser_eos/benchmark.cjs offline-server-disabled scientific-supplement probe-sweep interior-patterns legacy-high-level
python experiments/dx-fv/browser_eos/analyze.py
python experiments/dx-fv/browser_eos/audit.py
```

For the recorded environment set `PLAYWRIGHT_BROWSERS_PATH` to
`/workspace/ammonia-browser-runtime/browsers` and `EOS_WEBKIT_EXECUTABLE` to
`/workspace/ammonia-browser-runtime/webkit-local.sh`. The harness starts a local
HTTP server under a GitHub-Pages-like project prefix. It does not publish a site.
The offline server-disabled step intentionally rejects HTTP requests during
reload and fresh EOS initialization. It does not depend on `navigator.onLine`.

The original `deployment` step's Chromium result and WebKit network-emulation
failure are retained. Use `offline-server-disabled` for the conclusive completed
offline test. The default harness steps include the original `deployment`
experiment for historical replay; its artifacts and failures are not hidden.

Python 3.12.14 reference environments were separately pinned by
`requirements-7.2.txt` and `requirements-8.0.txt`. Their existing 612-request
results were preserved on resume. To deliberately reproduce those experiments
in a disposable checkout, **reuse** `inputs.json` rather than reseeding:

```bash
/path/to/python7/bin/python experiments/dx-fv/browser_eos/reference.py
/path/to/python8/bin/python experiments/dx-fv/browser_eos/reference.py
/path/to/python7/bin/python experiments/dx-fv/browser_eos/flash_probe.py
/path/to/python8/bin/python experiments/dx-fv/browser_eos/flash_probe.py
/path/to/python7/bin/python experiments/dx-fv/browser_eos/flash_probe.py saved
/path/to/python8/bin/python experiments/dx-fv/browser_eos/flash_probe.py saved
```

These commands write only new-study evidence in that disposable checkout.
`reference.py seed` is for original input construction, not a necessary replay.
No library reference-state setter is used. Browser/native version differences
and failed states must remain visible.

## Evidence and source map

- `eos.mjs`, `worker.mjs`, `index.html`, `sw.js`: isolated loader, raw SI state
  evaluation, exact bounded cache, worker and experiment-scoped offline page.
- `benchmark.cjs`: static comparisons, both browser engines, memory/costs,
  representative solver call patterns, accounting and finite-difference probes.
  It never imports or runs a coupled solver.
- `reference.py`: independent pinned Python reference entry paths.
- `flash_probe.py`: separate native flash precision investigation.
- `analyze.py`, `audit.py`: standard-library evidence summary and preservation
  audit. A passing evidence audit does not qualify a backend.
- `vendor/`: unmodified official builds and notices; hashes in `assets.json`.
- `upstream/`: exact binding/build/dependency source snapshots and local setup.
- `inputs.json`: original saved requests and physical seed states, never refitted.

`evidence/` contains the interruption manifest and initial loader; preservation
hashes for all 250 old files; both Python runs; per-version and aggregate browser
accuracy; three initialization rounds; interleaved property timings; sustained
runs; worker heartbeat evidence; MIME/missing-asset/offline tests; near-boundary
and interior call patterns; exact-cache comparisons; 189 accounting roundtrips;
browser/native flash sweeps; licensing/build metadata; summary and final audit.
Early harness and network-emulation failures are retained under their explicit
failure filenames. Native step sweeps are diagnostics, never adopted solver
parameters. Reference results and original binaries remain byte-identical to
the interruption checkpoint.

Benchmark timings vary with host and browser caches. Reproduction means replay
of the pinned implementation and scientific checks, not bit-identical timings.
No actual iPad, full coupled trajectory or physical-EOS experimental validation
is claimed. Stop for review before migration or further stages.
