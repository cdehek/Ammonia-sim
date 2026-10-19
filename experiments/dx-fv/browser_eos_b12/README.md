# B12 — isolated private HTTPS iPad preview

**B12 PARTIAL / BLOCKED.** No Cloudflare project or deployment URL exists.
Exact B11 artifact integrity: PASS. Private Access: NOT CONFIGURED.
Physical iPad: **AWAITING OWNER DEVICE REVIEW**.

The environment lacks Cloudflare authentication and an approved owner Access
identity. The owner has approved exactly one static root `404.html` in a NEW B12
staging copy. Reproducible 13+1 staging resolves the local packaging concern while
preserving every original byte and the canonical B11 identity. Actual Pages 404
behavior is **UNVERIFIED until deployment**. No workstation assets were uploaded.

Start with [owner actions](OWNER_ACTION_CHECKLIST.md), [engineering decisions](ENGINEERING_REPORT.md),
[private-access review](ACCESS_CONTROL_REVIEW.md) and [approved hosting wrapper](STATIC_HOSTING_CONFIGURATION.md).
The [iPad handoff](IPAD_OWNER_HANDOFF.md) is conditional on a real verified URL.
There is no fabricated URL, login, HTTPS result or device result.

Source: B11 `909de1579051bfadca0e282adf93eaedc0e24b9c`.
Branch: `research/b12-private-https-ipad-preview-20261019`.
Package: `b7803a5bf93ddc102c7367b80e7dc4c620c21daec0dbad6ef1a988161e3a2914`.
ZIP SHA-256: `a642fe22078e7637f9e5c12ce0efbc6f8b7de317da3853b6a52b03452a3ee078`.

From repository root, local verification (no credentials/network needed):

```sh
python3 experiments/dx-fv/browser_eos_b12/verify.py --extract
python3 experiments/dx-fv/browser_eos_b12/verify-protected.py
# Choose a NEW output path; existing staging directories are never replaced.
python3 experiments/dx-fv/browser_eos_b12/stage.py --out experiments/dx-fv/browser_eos_b12/.runtime/staging/approved-preview
python3 experiments/dx-fv/browser_eos_b12/test-staging.py
```

The original workstation commit is outside B11 ancestry. A fresh clone may need
`git fetch --no-tags --no-write-fetch-head origin 262b6092b2ed694073ad9ffd41265f44dd0b6ca0`
before checks. This reads an object without moving protected refs. Extraction stays
under ignored `.runtime/`. The original extraction stays separate from the approved
`.runtime/staging/approved-preview` candidate. Never upload either parent or rebuild
B11. Local HTTP tests need loopback socket permission, not Internet access.

Reports, manifests, source checks and machine-readable milestone status are all
confined to this directory. Production merge and full Live Plant coupling: NO-GO.
