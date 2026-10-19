# HTTPS and served assets — NOT TESTED

Actual URL: **none**. No TLS handshake, Access challenge, asset download or remote
404 result is claimed. Local bytes are verified in EXACT_B11_ARTIFACT_AUDIT.md.

After owner actions and compatibility review, list all actual project/deployment/
branch hostnames from authenticated project details. Verify normal TLS trust on
each, with no certificate bypass. Run `https-probe.py` against every actual origin
for independent unauthenticated denial checks. The probe is prepared tooling,
not a completed access receipt; owner-login/denied-identity checks remain manual.

After successful owner login use browser network requests on the same origin to
retrieve all 13 manifest paths and compare decoded response byte length/SHA-256
against `evidence/deployment-package-manifest.json`. Use GET, not only HEAD; a
200 login page must fail the expected MIME/hash checks. Request `/` for index.html
because Pages may canonicalize `/index.html`. Any redirect for scientific assets
must be reviewed; cross-origin asset redirection is disallowed. Record MIME,
SHA-256, length, content encoding, cache/CSP/nosniff/worker-src outcome and UTC,
excluding session material. Require a real 404 for invented root and nested .mjs
paths after owner login. A 302 Access challenge is expected only before login.

In actual Chromium and WebKit confirm secureContext, crypto.randomUUID, module
worker creation and successful original science digest verification. Inspect
requests for same-origin resolution and absence of mixed/external model requests.
Test reload, module failure without stale successful replacement, worker disposal
and restart, and denied access to direct script/worker/bundle paths. Recheck all
aliases; an alias omitted from the inventory prevents privacy qualification.

Do not simulate these checks through localhost or request interception and call
them remote HTTPS tests. See BROWSER_HTTPS_RESULTS.md for the pending run matrix.
