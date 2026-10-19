# Exact artifact integrity — PASS

Committed B11 checkpoint: `909de1579051bfadca0e282adf93eaedc0e24b9c`.
ZIP: `../browser_eos_b11/preview.zip`.
SHA-256: `a642fe22078e7637f9e5c12ce0efbc6f8b7de317da3853b6a52b03452a3ee078`.
Package: `b7803a5bf93ddc102c7367b80e7dc4c620c21daec0dbad6ef1a988161e3a2914`.

`verify.py --extract` independently recomputes ZIP and canonical package identity,
checks the manifest itself against its recorded SHA-256, compares all 13 ZIP
members with committed preview files and per-file hashes/lengths, and checks the
exact file set. Extracted static root is `.runtime/extracted/preview/`, with root
`index.html`. Extraction does not rebuild any source. The ZIP itself is unchanged.
Extracted files are local ignored copies; the authoritative artifact remains B11.

All twelve runtime asset relocations reverse to exact pinned Git blobs. The B9C
scientific bundle matches `f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919`.
The original HTML reverses exactly to
`0485cdf94b22101f976e365d6e5099bb3f8e15669914d5c12038e3eb37147945`;
all 574 original source inputs verify. Fourteen accepted A2 closure files verify.
The local module dependency graph resolves inside the package; the unchanged B11
portability receipts also establish no historical runtime asset requests.

`evidence/deployment-package-manifest.json` lists every original B11 byte,
MIME and SHA-256, including the JSON manifest; asset-manifest.json preserves source
commit/blob mappings. `evidence/artifact-audit.json` is the local verification
receipt. No served-byte or HTTPS scientific parity result exists.

The original retains no `404.html`, `_headers`, `_redirects` or server functions.
The owner approved one root static `404.html` in a NEW B12 stage. `stage.py`
independently checks the committed ZIP, identity and original files before/after
adding it. staging-original-manifest.json describes the 13 originals;
hosting-wrapper-manifest.json describes the sole addition and separate wrapper
identity; staged-deployment-manifest.json inventories all 14. staging-sha256.json
seals them. No wrapper identity replaces B11's canonical identity. Actual Pages
404/served-byte behavior remains unverified until deployment.
