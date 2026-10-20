# B12 publication and final verification

The Worker ZIP handoff starts at `f66566af56bf14beb822b5b8951f74e488b01f1e` with
a clean tree. `worker-upload-before/after` ref and PR snapshots protect this
packaging change; run `verify-protected.py --worker-upload`. After the B12-only
push, capture `worker-upload-publication` under ignored .runtime and verify the
remote branch equals local HEAD and all other refs/PR #3 match. Download the ZIP
from the actual published GitHub commit and independently verify its external
SHA-256. GitHub artifact publication is authorized by this task; it is not a
Cloudflare upload or deployment. No Worker URL, privacy or device PASS is implied.

Only `research/b12-private-https-ipad-preview-20261019` may be pushed, without force,
tags, PR creation or merge. Its parent history starts at exact B11. The design
commit is `25da88e88d81b746b6c12665746981aa9cf38255`.

The local checks verify every starting tracked byte, exact ZIP/extracted assets,
pinned scientific/original source derivation, retained B11 receipts, all ten full
training exports and B12-only diff scope. validate.py checks all required documents
and the machine tracker's honest blocked/untested states. The HTTPS probe input
guard was exercised without network: it rejects non-HTTPS, production/unscoped,
credential-bearing, query/path and alternate-port origins. No remote probe ran.

Recorded after-snapshot refs and PR metadata match their before-snapshot values;
B12 did not exist remotely at those observations. At publication, capture another
read-only snapshot with `capture-remote.py --phase publication`, verify every
protected ref/tag and PR field unchanged and the sole new B12 head equals local
HEAD. Keep that final snapshot in ignored .runtime so it need not embed its own
future commit SHA. The final conversation records the observed publication outcome
and SHA. A source-control push never means a Cloudflare deployment occurred.

Final checks include `git diff --check`, B12-only committed path scope and clean
`git status --porcelain=v1`. No historical source, workflow, production branch,
production host, PR #3 or original-workstation branch is changed. The account-side
external integration settings remain unobserved; no account mutation was possible.

The owner-approved follow-up starts at `1ab61278159a51fb3f86bb817ea1f03b049443d8`.
Separate 404-before/after ref and PR receipts protect this existing B12 branch's
starting head; only B12 may advance. The final 404-publication observation is kept
under .runtime and checked against local HEAD after the push. Original snapshots
remain retained. Approved static 13+1 staging resolves only the local packaging
concern; actual Pages routing remains unverified until deployment.

All deployment/security gates remain blocked after publication.
No actual HTTPS or physical iPad qualification is inferred from this report.
