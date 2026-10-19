# Static-hosting contract — approved one-file staging exception

The original artifact has 13 files, 3,222,883 bytes, root index.html and no server build.
No Wrangler configuration pointing at any account/project is committed. Desired
configuration is in `hosting-plan.json`, with null actual project/account fields.

**Approved resolution:** the owner follow-up from B12 checkpoint
`1ab61278159a51fb3f86bb817ea1f03b049443d8` permits exactly one minimal static
root `404.html` in a NEW B12 staging copy. It resolves the local packaging/design
concern. The B11 ZIP, original extraction and all 13 original files are unchanged.
The added HTML has only a title, heading and nonproduction missing-resource message;
no scripts, styles, links, external assets or runtime dependencies.

Run `stage.py --out NEW_B12_STAGING_PATH` to independently verify the committed
ZIP, canonical identity and every asset, extract into a fresh `.runtime/staging/`
directory, verify again, then add only `hosting/404.html`. Existing or symlinked
targets are refused. No manifests/test servers are placed in the served root.
The original-only, wrapper-only and combined manifests are staging-original-
manifest.json, hosting-wrapper-manifest.json and staged-deployment-manifest.json
in evidence/. staging-sha256.json seals them. The combined stage has 14 files;
the canonical B11 identity still describes only the 13 originals.

Actual loopback GET/HEAD checks return 404 for missing root/nested modules,
worker paths, CSS, JSON and extensionless resources. A labeled local Pages-rule
emulator serves the wrapper with 404; its unwrapped negative control serves
index.html with 200. An ordinary Python static server returns genuine 404s too.
These are local transport/handler observations, not Cloudflare implementation tests.
**Actual Cloudflare Pages response behavior remains UNVERIFIED until deployment.**
See [the official routing behavior](https://developers.cloudflare.com/pages/configuration/serving-pages/).
No Pages Functions, redirects, service workers, `_headers`, `_redirects`, Worker,
runtime dependency, extra asset or scientific change is introduced. No project
creation or upload occurs. All private-access/publication/HTTPS/device gates remain.

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
