# Approved 404 hosting-only follow-up

Start: B12 `1ab61278159a51fb3f86bb817ea1f03b049443d8`, clean tree.
The owner explicitly authorizes one root static 404.html in a NEW B12-owned staging
copy and a B12-only commit/push. No Cloudflare project creation or upload is allowed.

`stage.py` uses only Python's standard library. It validates the original ZIP hash,
canonical B11 identity, manifest hash and all 13 files against both ZIP and committed
B11 Git blobs. It verifies the extracted copy, adds only hosting/404.html, then
checks the exact 14-file set and bytes again. Output is restricted to a new real
directory under B12 .runtime/staging; existing/symlinked outputs are rejected. No
B11 source, ZIP, canonical manifest or original extraction is modified.

The added page is static HTML with no scripts, styles, links or external requests.
No Pages Functions, redirects, service workers, workers, runtime dependencies,
physics, digest checks, failure contracts or scientific source generation is added.
The test-server emulation code lives outside the stage and is never deployed.

Evidence, all under evidence/:

- staging-original-manifest.json: 13 original files, sizes, MIME and SHA-256,
  original ZIP SHA-256, package identity and asset-manifest hash.
- hosting-wrapper-manifest.json: one added file and its SHA-256, original manifest
  linkage and independent wrapper identity. It never replaces the B11 identity.
- staged-deployment-manifest.json: all 14 candidate files and combined inventory.
- staging-sha256.json: hashes of all three manifests plus 404.html.
- staging-tests.json: two reproducible builds, targeted rejection checks and
  actual loopback HTTP status/MIME/hash observations.
- followup-preservation.json: historical byte checks, source pins and B12-only scope.

Tests make bounded GET/HEAD requests to loopback only. An ordinary Python static
server returns genuine HTTP 404 for missing root/nested modules, worker paths, CSS,
JSON and extensionless resources. A separate Pages-rule emulator returns 404 with
the exact wrapper body, while the unwrapped negative control returns 200 with the
application HTML. Existing assets return 200 with exact decoded hashes/MIME in all
local handlers. No output is called a Cloudflare test. Actual Pages routing,
Access, TLS, browser/science and physical iPad behavior remain unverified.

The existing A2 worker/service/client/scientific bytes preserve the original
fail-closed implementation. Deliberately corrupted staging science is rejected by
packaging validation; this does not claim a newly executed browser failure test.
No large completed browser or numerical campaign is rerun for a static extra file.

Run from repository root, choosing a new unused output path:

```sh
python3 experiments/dx-fv/browser_eos_b12/stage.py --out experiments/dx-fv/browser_eos_b12/.runtime/staging/review-copy
python3 experiments/dx-fv/browser_eos_b12/test-staging.py
python3 experiments/dx-fv/browser_eos_b12/verify.py --extract
python3 experiments/dx-fv/browser_eos_b12/verify-followup.py
python3 experiments/dx-fv/browser_eos_b12/validate.py
```

All private-access, deployment and publication gates stay as before. Authentication,
explicit owner Access identity and independently verified main/preview policies
remain outstanding. No real URL or device result exists. Stop for review.
