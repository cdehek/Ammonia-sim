# Protected refs and PR #3 audit

PASS. All 2,791 tracked historical files match their starting SHA-256 hashes.
Every committed difference from exact B9B is an addition under browser_eos_b9c.
Fourteen accepted source bodies match A2 Git objects; original B9/B9A/B9B/C1/B6/B7
trees and scientific artifacts match their authoritative commits.

Full git ls-remote snapshots before work, pre-publication and after prototype
publication are in evidence/remote-{before,final,postpush}.tsv. Every original
HEAD/ref/tag identity remains unchanged. The only new ref is the authorized
research/browser-eos-b9c-boundary-ph-reuse-20261018 branch. No PR is created.

PR #3 remains open and unmerged with original title/body and identities:

| Identity | Exact SHA |
|---|---|
| Base main | 0473d32f62db992fde0f581d116e1bd0c8e7d8ed |
| Head | d4422425750a1d3c4e432cc103ac42ead40b7cc6 |
| Merge ref | f440560fccfa45421ec2bf679bac32df10df63ae |

The supplied C2 SHA is noncanonical. Original B8 audit, live ref and Git object
establish 7c75d9538d57080a01dffbf7e06128a27e2b9ccd. Both identities are retained
in gate0.json; no historical checkpoint or remote ref is altered.

Gate 1 design commit: 36b118b30e44613f1c7ac9ca615aa61c949a88c2.
Qualified prototype/evidence commit: 1e1248abbf249e56a5632ed8b1011f0f519b3c51.
The final receipt commit follows by ordinary fast-forward. Committed post-push
snapshots identify the prototype publication; a final read-only external check
verifies the receipt commit's remote HEAD and clean tree without self-reference.
No production main, accepted A2, demo, UI, Live Plant, hosting, merge or deployment
is changed. Operator integration remains NO-GO. Stop for engineering review.
