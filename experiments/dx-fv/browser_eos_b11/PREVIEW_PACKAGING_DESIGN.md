# B11 preview packaging design — committed before functional packaging

Build identity: B11-portable-static-v1. Base: B10 a49c5c4ade306fe02117139cf81c30a59727a7b1. Branch: research/b11-portable-ipad-preview-20261019. Gate 0 receipts hash every tracked B10-start file, record local/remote refs/tags and PR #3, and verify the fourteen-file accepted A2 closure. Protected scientific/workstation identities remain unchanged.

## Artifact and trust boundary

`preview/` alone is a conventional static HTTP root. `index.html` is the literal B10 integrated workstation with only its absolute lazy panel import replaced by a document-relative URL. B10 mount, console registration, original embedded scripts, property data, training, history, Assist and illustrative Live Plant remain literal. Reverse both the URL adaptation and B10's documented reversible insertions to verify the exact original 262b6092 HTML. Do not rebuild or redesign the application.

Place B10 panel/transport/style modules at the preview root. Copy the minimal B9D snapshot projection and B9 exact-value utility into `support/`; copy the exact B9C `candidate-bundle.mjs` into `science/`. Rewrite only static module/asset specifier strings in B10 adapters. Keep the scientific bundle byte-exact (SHA-256 f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919). Its literal registry already contains all table/property/model dependencies; no external thermodynamic API, WASM backend, CDN or runtime download is needed. The bundle creates the same owned, recursively frozen table engine per worker.

Keep B10's `crypto.subtle` bundle verification and `crypto.randomUUID` session/request identities intact. These APIs require a secure context: localhost HTTP is potentially trustworthy; a typical private-LAN HTTP address is not. B11 must investigate and document this distinction, not replace verification or weaken browser security to force LAN compatibility. Recommend trusted HTTPS for subsequent physical-device review if nonsecure LAN HTTP cannot initialize. Same-origin module worker, correct JavaScript MIME, relative asset URLs, no cross-origin redirects. No service worker, PWA, caching semantics, solver, state or failure-rule change.

## Reproducibility and audit

`build.py` reads exact Git blobs at the pinned B10/B9C/B9D commits, applies asserted one-occurrence URL substitutions, records source blob SHA, source/output SHA-256, transform description, output path, bytes and MIME. Fail closed on an unknown source or scientific identity. Emit a machine-readable `preview/asset-manifest.json` and a human-readable complete ASSET_MANIFEST.md. Manifest excludes its own hash to avoid recursion; the external delivery seal hashes every output including it. Package identity is a deterministic hash of source pins and generated asset records. No timestamp or absolute checkout path enters the package. Produce a sorted ZIP with fixed member timestamps/permissions and an external checksum. Rebuild in a second output directory and compare every byte and ZIP checksum.

The preview runtime may access only files inside its own folder. Verify this by serving a copied folder outside the checkout as root, then as `/review/b11/`; record every request and prohibit external/historical paths. No developer checkout is needed after building. Build/test dependencies stay in ignored B11 `.runtime/`, never committed. Test harnesses and source comparators stay outside preview.

## Verification sequence

1. Exact-source closure and reverse derivation; original B10 saved same-browser hashes/states/records at 0/.0001/.0005/.001, cold/warm. Reuse unchanged bounded B10 scientific/render/lifecycle assertions with a B11 test adapter; retain all refusals, rollback, Newton/signed FD/TR-BDF2 and property-domain contracts. Never extend the normal horizon.
2. Sequential Chromium then desktop WebKit original pinned suites, independent state/history/Assist checks and all five complete exercise export byte comparisons against pinned baseline evidence. Retain historical chart and variable training pause failures with raw logs. No assertion repairs.
3. Actual standalone-root/nested path startup, scientific module failure, worker loss, disposal/restart, native file and browser-offline probes. Private-LAN origin policy is tested separately from physical reachability; no iPad claim follows from desktop tests.
4. Matched B10/B11 bounded startup/panel/worker/table/model/advance/render/switch/frame/heartbeat/trusted-input/dispose/restart and coarse RSS observations, sequentially. Report outliers and sampling limits; startup is distinct from numerical compute.
5. Desktop/tablet-viewport screenshots, physical iPad owner checklist and future HTTPS/local-server instructions. Physical status AWAITING USER DEVICE REVIEW. Offline NOT QUALIFIED unless separately demonstrated. No deployment or production authorization.

## Acceptance and stop

Report the requested gates independently and choose exactly one final B11 classification based on retained evidence. Inherited WebKit findings remain explicit even if one flaky sample passes. LAN reachability/HTTPS feasibility is not physical-device qualification. Missing assets must yield B10's genuine unavailable/lost/unqualified state and preserve the original simulator. Public/remote deployment, PR #3 edits, production merge and Live Plant coupling remain NO-GO. Commit/push only B11, verify historical bytes/refs and a clean tree, then stop for engineering review.
