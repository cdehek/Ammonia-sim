# Safe research removal and rollback — future procedure only

No B12 Cloudflare project currently exists, so no remote removal is needed.
Never delete or roll back an existing production or unrelated project for B12.

If a B12 deployment is later made, first check the private record of actual account,
project ID/name, domains, Access applications and all deployment IDs. Confirm it
is the new Direct Upload research project with no production custom domains or Git
integration. Keep Access enabled while handling any incident or failed qualification.

For a bad research deployment, use only that project's dashboard rollback to a
previously verified B12 deployment, then recheck Access and exact asset identity.
If none is verified, withdraw the research site rather than promote an unknown
artifact. Rollback does not delete immutable old deployment URLs; inventory them.

For full retirement, after owner/engineering retention review, delete only the
identified B12 project via its dashboard or the documented `wrangler pages project
delete PROJECT` command. Review the target interactively; do not force, enumerate
and delete unrelated deployments, or copy a broad cleanup script. Keep its Access
applications until every alias is confirmed unavailable. Remove only those B12
applications afterward if no other resource depends on them. Do not touch DNS,
production domains, GitHub Pages, PR #3 or protected branches. No deletion is run now.

Retain sanitized project/deployment receipts, package identity and removal UTC.
Recheck main, branch and immutable URLs for unavailability and no exposed assets.
Do not purge an account-wide or production cache. Repository evidence and sealed
B11 bytes should remain available for engineering review.
