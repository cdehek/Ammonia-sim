# Official documentation checked 2026-10-19 UTC

These are documentation observations, not account or deployment receipts.

- [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/): prebuilt directory upload; Wrangler can create an empty project. Dashboard also accepts ZIPs, but the sealed ZIP wraps its files in `preview/`; choose the extracted folder to avoid a wrong static root. Do not use combined implicit create-and-deploy.
- [Pages commands](https://developers.cloudflare.com/workers/wrangler/commands/pages/): current command forms support `pages project create PROJECT --production-branch BRANCH`, `pages deploy DIRECTORY --project-name PROJECT --branch BRANCH --commit-hash SHA`, project/deployment lists, and project deletion. Check the installed CLI version and help before execution; no CLI version was installed or run in B12.
- [Preview access](https://developers.cloudflare.com/pages/configuration/preview-deployments/): previews are public by default; enabling preview Access does not secure the main hostname.
- [Main-hostname Access procedure](https://developers.cloudflare.com/pages/platform/known-issues/#enable-access-on-your-pagesdev-domain): remove the wildcard from the generated application's hostname to cover the main hostname; re-enable preview protection and confirm two applications exist. Scope both to the explicitly approved owner.
- [Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/): absence of a top-level `404.html` activates SPA fallback. B11 lacks this file, creating a blocking compatibility conflict. Never assume missing modules get 404.
- [Self-hosted Access application](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/): authenticated application/policy configuration is required; no policy is inferred from login readiness.

See STATIC_HOSTING_CONFIGURATION.md for the unresolved exact-file-set conflict.
