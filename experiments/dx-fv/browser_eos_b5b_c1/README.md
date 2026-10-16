# C1 reproduction and evidence index

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md),
[GATE1_DESIGN.md](GATE1_DESIGN.md), [MATRIX.md](MATRIX.md),
[PERFORMANCE.md](PERFORMANCE.md), [EXECUTION_NOTES.md](EXECUTION_NOTES.md) and
[MECHANICS_REPORT.md](MECHANICS_REPORT.md). Final assessment:
**FOCUSED CONTRACT IMPLEMENTATION PASS**, with two independent gates passed and
all inherited exact-boundary qualification blockers retained.

Parent: `26df10c1f486b60978646e9c8819fc0054cb9465`.
Branch: `research/browser-eos-b5b-c1-failclosed-propagation-20261016`.
Pre-edit contract-review commit: `95f7881`.
Final delivery SHA: `git rev-parse HEAD` and the delivery response. No commit
can include its own hash. No integration, merge, deployment or further milestone.

## Reproduce

Use a disposable checkout/output copy to avoid overwriting preserved delivery
evidence. Python 3.12, Node 24, Playwright 1.62, Chromium and desktop WebKit are
used. Native tests require only Python's standard-library ctypes/lzma, the system
C++ runtime and preserved archives. No CoolProp wheel, source tree, build or
new mathematical root solve is needed. Native libraries are decompressed into
`/workspace/c1-native` and verified against archive and uncompressed digests.

From repository root:

```
timeout 90 python experiments/dx-fv/browser_eos_b5b_c1/native.py
timeout 120 node experiments/dx-fv/browser_eos_b5b_c1/native-wrapper.mjs
timeout 220 python experiments/dx-fv/browser_eos_b5b_c1/replay.py
timeout 90 python experiments/dx-fv/browser_eos_b5b_c1/guard-replay.py
python experiments/dx-fv/browser_eos_b5b_c1/audit_evidence.py
```

`native-wrapper.mjs --properties-only` runs the fifteen property-interface cases
without repeating the native A2 set. Main browser replay accepts `C1_ENGINES`,
`CHROMIUM_PATH` and `WEBKIT_PATH`. Defaults are `/usr/bin/chromium` and
`/workspace/c1-browsers/webkit-2336/pw_run.sh`. Browser launch is bounded to 30 s;
workers have a 30 s deadline. The outer timeout also bounds synchronous browser
evaluation. Use the managed execution tool's additional network permission for
loopback browser/child-process access when required by its sandbox.

Install the compatible WebKit with:

```
PLAYWRIGHT_BROWSERS_PATH=/workspace/c1-browsers python -m playwright install webkit
```

This host also needed the exact six Debian archives in
`../browser_eos_b5/evidence/browser-libraries.json`. Download through the
configured proxy, verify every listed SHA256, extract into a disposable directory
using `dpkg-deb -x`, and copy its `usr/lib/x86_64-linux-gnu/*.so*` files into this
WebKit installation's `minibrowser-wpe/sys/lib`. Do not change repository assets
or loaders. `evidence/webkit-setup.log` preserves installation diagnostics.
This is WPE desktop WebKit, not physical Safari/iPadOS.

## Source intervention and preservation

All changes are additions under this directory. `adapter.mjs` imports the
historical adapter and uses the unchanged B4C loader/WASM. `a2/` contains the
12 copied dependencies (nine unchanged, three modified) and the new diagnostic
helper. To reproduce those exact isolated A2 changes independently:

```
cp -r experiments/dx-fv/browser_eos_backend/accepted /tmp/c1-a2-replay
patch -p1 -d /tmp/c1-a2-replay < experiments/dx-fv/browser_eos_b5b_c1/a2-error-propagation.patch
```

Do not apply the patch to protected sources. `audit_evidence.py` emits the
patch and verifies preserved thermal proof and detached commit bytes. The source
manifest identifies the complete wrapper, helper, harnesses, copies and evidence.
The pre-edit receipt `a2-before-edit.json` binds all twelve copies before editing.

The start audit is historical evidence; do not rerun `audit.py --start` on a later
commit. `audit.py` verifies all starting file bytes, historical artifacts,
accepted dependencies and protected local/remote refs using `refs-before.txt`
and a fresh `refs-after.txt`. Stage only this directory before the final audit so
Git's additive diff also covers new files. Post-push validation compares the final
target SHA and every protected ref outside the self-referential commit evidence.

## Machine-readable deliverables

- `checkpoint.json`, `starting-file-hashes.json`, `start-audit.json`,
  `refs-before.txt`: exact start, clean observation, all historical identities.
- `a2-before-edit.json`, `scientific-audit.json`, `source-manifest.json`:
  original budgets, original reference comparisons, unchanged versus modified
  dependency hashes, source/audit evidence and the two gate decisions.
- `classification-matrix.json`: seven original cases per browser, exact input
  and output bits, canonical/nonlinear checks, runtime C versus independently
  attributed two/five mechanism and immutable reference hash.
- `chromium-replay.json`, `webkit-replay.json`: actual historical control and
  candidate, original PH, raw DU, strict refusal, 24-case pressure/phase matrix,
  both saved inward controls, async/worker/lifecycle, focused properties and A2.
- `native-replay.json`: 250 archived outcomes and Gate A native-only controls.
  `native-wrapper.json`: fifteen paired actual native property cases, including
  three numerical QT exceptions. `native-A2.json`: 24 completed actual native
  A2 scenarios with the same scientific settings as the browser harness.
- `*-guards.json`: candidate/control lower/upper support, temperature guard
  isolation and actual loader refusal. Synthetic cases are explicitly labeled.
- `*-initial-pass.json`, `*-extended-pass.json`,
  `*-detached-harness-failure.json`: retained earlier executions and harness
  failure, without overwriting final scientific conclusions.
- `final-preservation.json`, `refs-after.txt`: before-push preservation receipt.
  The externally retained post-push receipt verifies the final target and clean
  tree; its final SHA is in the delivery response.

All raw properties inside error records are diagnostic-only. No C/B/E failure
returns an accepted state. The two historically returned inward controls remain
qualification blockers and are never labeled repaired or independently certified.
