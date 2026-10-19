# Source and build audit

Starting branch/HEAD were verified at exact B10 `a49c5c4ade306fe02117139cf81c30a59727a7b1` with a clean tracked/untracked tree before B11 additions. New isolated B11 branch was created there. Gate 0 hashed all 3221 starting tracked files and their Git blobs, recorded refs/tags/remote heads and PR #3, and verified all fourteen accepted A2 closure files. Architecture and source audit were committed at `9b7827c7204b72bba96ec6092ac9cb4f6d9a8e91` before functional packaging.

| Protected source | Exact SHA |
|---|---|
| A2 | be9eb35a4ddf5098e685182f8104685127c6a6ee |
| B9C | b67afb3215075b2ec82bef376d39e03953dc0da2 |
| B9D | 20ddac46423a7a742af19ac415ef8796cf3a429f |
| B10 | a49c5c4ade306fe02117139cf81c30a59727a7b1 |
| original | 262b6092b2ed694073ad9ffd41265f44dd0b6ca0 |

`build.py` reads immutable Git blobs; twelve generated runtime assets plus the JSON manifest total 3,222,883 bytes. Seven literal specifier replacements across index/service/snapshot/view are recorded individually in the manifest (counts included). All other bytes are preserved. `verify-source.py` reverses every relocation and B10 insertion to exact original HTML SHA-256 `0485cdf94b22101f976e365d6e5099bb3f8e15669914d5c12038e3eb37147945`. It verifies the complete local static import graph and forbids unmanifested package files. The complete original 574-file input manifest is freshly verified against the original Git blobs and SHA-256s by verify-source.py; B10's original build receipt also remains protected by starting hashes. No original script/model/training source is rebuilt or edited.

B9C bundle SHA-256 `f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919`; it contains the required literal property tables, engine, accepted A2 mechanics/fixtures and exact B9C boundary-PH optimization. No EOS downloads or thermodynamic service is involved. B10's hash verification and owned worker remain unchanged. Source/build identity and each Git blob, SHA-256, source/target path, bytes, MIME and relocation are in `preview/asset-manifest.json`; ASSET_MANIFEST.md additionally hashes the JSON manifest. No timestamp or checkout path enters the runtime artifact.

Two builds to different output directories produced identical complete file maps and identical ZIP bytes (`evidence/reproducibility.json`). ZIP is sorted, has fixed timestamps/modes and uses stored entries to avoid compressor-version dependence. Check `preview.zip.sha256`. `seal-delivery.py` hashes all nonignored B11 delivery files excluding its own seal; Git seals that inventory. No node_modules, browser downloads, caches or environments are committed.

## Optional full verification setup

Run from repository root, with Internet access only for test tooling installation. Use the same Playwright versions and isolated libraries for matched historical browser receipts:

```sh
python3 -m venv experiments/dx-fv/browser_eos_b11/.runtime/venv
experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/pip install playwright==1.62.0
python3 experiments/dx-fv/browser_eos_b11/prepare-tests.py --install-node
PLAYWRIGHT_BROWSERS_PATH="$PWD/experiments/dx-fv/browser_eos_b11/.runtime/browsers" experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python -m playwright install chromium webkit
experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python experiments/dx-fv/browser_eos_b11/setup-runtime.py
python3 experiments/dx-fv/browser_eos_b11/prepare-verification.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python experiments/dx-fv/browser_eos_b11/run-integration.py
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 experiments/dx-fv/browser_eos_b11/.runtime/venv/bin/python experiments/dx-fv/browser_eos_b11/run-scientific-review.py
bash experiments/dx-fv/browser_eos_b11/run-verification.sh
python3 experiments/dx-fv/browser_eos_b11/write-reports.py
```

The host-requirement skip selects the actual WPE binary with the exact B10-pinned extracted libraries, without modifying browser security. Runtime executable hashes/versions and host resource limits are in runtime-manifest.json. Chromium 151.0.7922.34; desktop WPE WebKit 26.5; Python Playwright 1.62.0, Node Playwright 1.62.1. Original assertions are literal pinned suites in disposable Git archives. B11 test adapters change only URLs, output roots, runtime selection and additional exact B10 comparisons; `test-adapter-derivation.json` records their diffs. Scientific review reuses unchanged B9C/B9D harnesses and compact B10 evidence retention to bound memory. No physical equations/limits or original assertions are weakened. All large browser campaigns ran sequentially on a 8-GiB cgroup host.

An initial sandbox lacked local socket permission; the failure log remains. Enabling ordinary network access for the server/browser process resolved that environment issue. The first packaging run exposed a missing B9D view dependency; its failed receipt is retained and the final build closes that exact import without source edits. A later CSP probe exposed Playwright string-wait eval, resolved by test-only direct polling with no CSP/security change; its original failure and final follow-up remain separate. Direct private-address transport also returned 503 before the application loaded; that failure is separately retained, and nonsecure API behavior is qualified only by a labeled local-interception origin-policy test, not peer-device reachability.
