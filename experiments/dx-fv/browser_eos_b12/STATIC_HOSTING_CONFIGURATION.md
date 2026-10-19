# Static-hosting contract — compatibility review required

The artifact has 13 files, 3,222,883 bytes, root index.html and no server build.
No Wrangler configuration pointing at any account/project is committed. Desired
configuration is in `hosting-plan.json`, with null actual project/account fields.

**BLOCKER: genuine missing-file 404.** The exact B11 package has no top-level
`404.html`. Cloudflare's documented Pages default then treats unmatched paths as
SPA routes and serves the root. An upload of the unchanged folder therefore cannot
currently be signed off against the required genuine 404 contract. This is a
documentation-based incompatibility finding, not a measured remote response.
See [the official routing behavior](https://developers.cloudflare.com/pages/configuration/serving-pages/).
No documented account-side override satisfying the unchanged file set was verified.
Engineering must approve a precise hosting-only exception, such as a separately
manifested 404 wrapper, or demonstrate an acceptable documented routing solution.
Such an exception is not implemented or authorized here. Keep the B11 ZIP/extracted
folder unchanged; do not silently add `404.html`, `_headers` or a Worker.

For any approved hosting plan require: HTML text/html; .mjs/.js JavaScript MIME;
CSS text/css; JSON application/json; same-origin modules, worker, digest fetch;
trusted TLS; no mixed content or external science service. HTTPS enables the
unchanged crypto.randomUUID and crypto.subtle.digest requirements. They must also
be tested in the actual page/worker; TLS alone proves no runtime initialization.

CSP must permit the original inline scripts/styles, same-origin module/worker/fetch
and data images. The exact B11 tested policy is retained in
`../browser_eos_b11/PREVIEW_HOSTING_HANDOFF.md`. Do not invent a deployed CSP;
actual headers and enforcement remain untested. SharedArrayBuffer/COOP/COEP are
not required. Do not add unsafe-eval or disable browser security.

Disable optional HTML/script injection, analytics, Rocket Loader, minification,
rewrites, content optimization and unapproved custom cache rules for the new
research project where applicable. No production setting may be changed. Standard
transport compression is acceptable only when decoded response bytes match the
manifest. Verify coherent assets on every hostname, including reload/revalidation.
