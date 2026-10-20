# Deployment execution — BLOCKED

2026-10-20 owner report: a separate Worker `ammonia-lab-research-b12` already has
a harmless placeholder and owner-only Access All traffic policy. The new ZIP is a
packaging handoff to that existing Worker only. No account/Access/Wrangler/upload
operation was executed here and no workstation deployment is claimed. Earlier
Pages planning/execution history below is not the current Worker procedure.

Design commit: `25da88e88d81b746b6c12665746981aa9cf38255`.
No Cloudflare remote account operation, project creation, login, Access mutation,
hostname reservation or asset upload was performed. No deployment ID, deployment
time or returned URL exists. `evidence/deployment.json` has null actual fields.

Read-only repository bootstrap was necessary because this environment started
without a checkout. The exact B11 branch was cloned; starting SHA and cleanliness
were verified; B12 was created locally. The separate original-workstation commit
was fetched by SHA without changing refs/FETCH_HEAD. The first preservation run
correctly stopped when that nonancestor object was absent; it passed after fetch.
No science was regenerated and no historical script that writes evidence was run.

Gate 0 and artifact checks passed. Cloudflare readiness found no credential
bindings, supported connector or Wrangler session configuration. No owner email
has been approved. PRIVATE ACCESS BLOCKED: account operations stopped there.
Documentation review originally found the exact package's missing-404 conflict.
The owner follow-up approves precisely one static root 404.html in a NEW B12 stage.
The new 14-file candidate preserves all 13 B11 bytes and canonical identity; local
packaging/HTTP checks pass. Actual Pages behavior remains unverified. This follow-up
creates no Cloudflare project and uploads no files.

Next execution requires review of the implemented exception and the authenticated
owner checklist. Only after private protection is verified may the separately
manifested 13+1 stage be selected for a permitted Direct Upload. Actual routing
and all served-byte/browser checks must pass afterward.
The two-phase create/protect/deploy procedure avoids publishing science to
discover whether access control works. Do not use implicit project creation by
the deploy command, inherited Wrangler cache, or a production-linked Git project.

Before executing, use current CLI help; record the chosen CLI version, exact
redacted command, intended account ownership attestation, new project ID/name,
production branch, actual returned URL/aliases, deployment ID, UTC, Access coverage
and artifact manifest. Keep sensitive identifiers in owner-private records.
Afterward complete all asset and browser gates before handing over a verified URL.
There is no runnable publish script in B12 that could bypass these gates.
