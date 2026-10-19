# Access review — PRIVATE ACCESS BLOCKED

Owner access: **NOT CONFIGURED**. There is no actual hostname, Access application,
approved email, authenticated session, account-control proof or denial receipt.
`evidence/cloudflare-auth-readiness.json` records absent environment bindings and
known Wrangler configuration, without reading credential values. No supported
Cloudflare connector or Wrangler executable is available. This establishes no
authenticated Cloudflare capability here; it does not assert the owner lacks an
account or could not log in on their own device. No account API call was attempted.

Required coverage is the full path space on `PROJECT.pages.dev` plus
`*.PROJECT.pages.dev`, including branch aliases and immutable deployment URLs.
No custom domain is planned. Verify the intended account owns each real hostname
using its authenticated project details. An obscure hostname is public by default.

Use separate main-hostname and preview Access applications per the linked official
procedure. The policy must allow only the owner identity explicitly approved by
the owner, with no Everyone, broad email-domain or account-membership allowance,
Bypass rule, public path exclusion, or service-token shortcut. Default denial must
remain effective. Account membership is not sufficient owner-only authorization.
Do not infer email from Git commits, repository settings or this session's profile.

Before science upload, test nonscientific content or the empty origin: fresh-client
GET of root and every scientific path must redirect to the intended Access login
or refuse access. A plain absent-page 404 does not establish Access. Owner login
must actually permit the protected probe. Repeat with a disallowed identity and
after session expiry. Inspect policy scope and independently check all aliases;
an uncreated future hostname requires checks as soon as it exists. Keep every
preexisting sentinel deployment protected until removal.

After upload repeat tests for HTML, CSS, JSON, scripts, nested modules, worker and
bundle, and verify owner-authorized bytes. Denial pages must never contain the
workstation or scientific asset bytes. Certificate validation stays enabled.
Retain sanitized UTC/status/path/decision receipts only, never full auth headers,
Location query strings, HARs, login screenshots, cookies, storage or JWTs.

No privacy PASS is claimed from configuration text. See evidence/access-tests.json
for explicit NOT TESTED entries and OWNER_ACTION_CHECKLIST.md for the next action.
