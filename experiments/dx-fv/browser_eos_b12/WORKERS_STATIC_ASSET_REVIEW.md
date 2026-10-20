# Workers static assets versus Pages — documentation review 2026-10-20

The owner-selected host is an existing Worker, not the earlier proposed Pages
project. No account/API/CLI verification or configuration change was made here.
The owner's dashboard upload flow is reported, not independently exercised.

The [Workers asset overview](https://developers.cloudflare.com/workers/static-assets/)
documents asset-first routing by default. Matching files are served as assets.
An unmatched request may invoke an existing Worker script; without one, the
default result is HTTP 404. Therefore the placeholder could affect missing-path
responses if its script remains. This package adds no server-side Worker script;
`worker.mjs` is the unchanged B11 browser module worker, not a Cloudflare entrypoint.

For a custom body, the [SSG/custom 404 documentation](https://developers.cloudflare.com/workers/static-assets/routing/static-site-generation/)
requires `assets.not_found_handling = "404-page"`; when asset serving handles an
unmatched request, that mode uses the nearest 404.html with status 404. Presence
of root 404.html alone does not select this
mode in Workers. `single-page-application` instead falls back to index.html with
status 200 and is unsuitable for the required missing-science failure contract.
The previous Pages-rule local emulator is no evidence of Workers behavior.
The ZIP carries the approved 404 page as an asset, not deployment configuration.

The [configuration/bindings reference](https://developers.cloudflare.com/workers/static-assets/binding/)
also describes `run_worker_first`: its default is false, but an existing true or
selective setting can route requests through the placeholder first. Inspect the
existing configuration; do not infer static-only behavior from an upload label.
Use externally enforced Access across all traffic, not a hypothetical script
guard that asset-first serving could bypass. No new guard/Worker code is supplied.

[HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/)
can canonicalize HTML URLs; navigate to `/` and record redirects. Require exact
same-origin JavaScript/module/worker, CSS and JSON responses. Verify authenticated
missing .mjs/.js/CSS/JSON paths with GET and HEAD, alongside all 14 served hashes.
A 200 login/placeholder/HTML response is not a valid module or missing-resource
result. Actual Workers status, custom 404 body, MIME, digest, Access and TLS remain
UNVERIFIED. If the existing script/configuration prevents genuine 404s, stop for
review rather than adding a Worker script or weakening application failure handling.

## Optional desktop Wrangler handoff — owner only, not executed

Use [supported Workers deploy commands](https://developers.cloudflare.com/workers/wrangler/commands/workers/),
not `wrangler pages deploy`. On the owner's trusted desktop install a reviewed
Wrangler version, run `wrangler login` and `wrangler whoami` privately to confirm
the intended account. Review the existing research Worker's settings and access
coverage. Keep local deployment configuration OUTSIDE the 14-file asset folder.
An asset-only configuration can omit `main` and use the following shape:

```jsonc
{
  "name": "ammonia-lab-research-b12",
  "compatibility_date": "2026-10-20",
  "assets": {
    "directory": "./extracted-assets",
    "not_found_handling": "404-page",
    "html_handling": "auto-trailing-slash"
  }
}
```

This is an inert example, not an account configuration receipt. Resolve the path
to the exact extracted folder and review/preserve the existing compatibility date,
routes, bindings and other settings. Review how a script-free deployment replaces
the harmless research placeholder; do not introduce a new script or point `main`
at browser worker.mjs. Do not use repository auto-detection or create another Worker.
Once the owner has verified Access and approved the concrete update:

```sh
wrangler deploy --config /absolute/path/to/owner-reviewed-worker.jsonc
```

This publishes and is NOT run by this task. No login, Wrangler, upload API, temporary
account or deployment operation was performed. Dashboard and CLI outcomes both
require the same real post-upload HTTP, hash and browser checks.
