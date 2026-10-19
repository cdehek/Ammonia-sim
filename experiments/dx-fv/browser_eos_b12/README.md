# B12 — isolated private HTTPS iPad preview

**B12 PARTIAL / BLOCKED.** No Cloudflare project or deployment URL exists.
Exact B11 artifact integrity: PASS. Private Access: NOT CONFIGURED.
Physical iPad: **AWAITING OWNER DEVICE REVIEW**.

The environment lacks Cloudflare authentication and an approved owner Access
identity. A separate compatibility review is also required: the sealed B11 folder
has no 404.html and Pages documents SPA fallback without it, conflicting with the
required genuine 404s. No workstation assets were uploaded or modified.

Start with [owner actions](OWNER_ACTION_CHECKLIST.md), [engineering decisions](ENGINEERING_REPORT.md),
[private-access review](ACCESS_CONTROL_REVIEW.md) and [hosting blocker](STATIC_HOSTING_CONFIGURATION.md).
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
```

The original workstation commit is outside B11 ancestry. A fresh clone may need
`git fetch --no-tags --no-write-fetch-head origin 262b6092b2ed694073ad9ffd41265f44dd0b6ca0`
before checks. This reads an object without moving protected refs. Extraction stays
under ignored `.runtime/`; do not upload that parent folder or rebuild B11.

Reports, manifests, source checks and machine-readable milestone status are all
confined to this directory. Production merge and full Live Plant coupling: NO-GO.
