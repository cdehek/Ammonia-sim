# Owner action checklist — stop before publishing science

**Current Worker handoff, 2026-10-20:** use WORKER_STATIC_UPLOAD_HANDOFF.md for the
owner-reported existing `ammonia-lab-research-b12` Worker. The owner reports its
placeholder and owner-only Access All traffic policy. Independently verify direct
asset protection before owner publishing. Do not create a Pages project or use
the historical Pages CLI steps below for this Worker. This packaging task runs
no Cloudflare/Access/Wrangler/upload operation. The older Pages plan is retained
as historical context, not the current action checklist.

The smallest immediate action is to authenticate on the intended Cloudflare
account and explicitly approve the identity allowed to access this private preview.
No credentials, API tokens, cookies or login links with session parameters should
be sent in chat. The developer may assist with documented authenticated dashboard
actions. No package upload is authorized until protection is independently checked.
The one-file staging exception below is explicitly approved. This follow-up does
not authorize Cloudflare project creation or uploads; private-access gates remain.

1. Open [Cloudflare dashboard](https://dash.cloudflare.com/) yourself, log in and
   select the intended account. Confirm permission to create a separate Pages
   Direct Upload project and manage Access. Confirm available features do not
   require a purchase or paid enablement. If permission/plan is missing, stop.
2. Explicitly approve the owner-only identity for Access; do not infer it from Git.
   Keep the identity itself in owner-private configuration. Supply a nonsecret
   confirmation that owner approval occurred for the review record.
3. Review STATIC_HOSTING_CONFIGURATION.md and the approved 13+1 manifests. All B11
   files stay unchanged; exactly one root static 404.html is added only in a NEW
   B12 stage. Local checks pass; actual Pages behavior still needs deployed
   authenticated missing-path GET/HEAD checks. No further files/runtime changes
   are approved. Login alone does not establish private access.
4. In Workers & Pages review existing projects without editing them. Create only
   a NEW empty Direct Upload project, using an available `ammonia-lab-research-b12`
   prefix. Use a research-only production branch name such as `b12-sealed`.
   The Pages word “production” here refers only to this isolated project's main
   hostname. Do not select repository integration or an existing application.
   Prefer Wrangler's documented empty-project step; dashboard create-and-upload
   is unsafe for actual workstation assets before Access is verified.
5. Enable preview Access. Following the official [main-hostname procedure](https://developers.cloudflare.com/pages/platform/known-issues/#enable-access-on-your-pagesdev-domain),
   edit the generated application to remove its wildcard, securing the main host;
   re-enable preview Access and confirm separate main and wildcard applications.
   Name both B12 NONPRODUCTION RESEARCH and constrain both to the approved owner.
   Do not accept a default policy allowing every account member. No Bypass rules.
6. Confirm actual account ownership and all hostnames/aliases privately. Test a
   harmless nonscientific probe or empty origin independently: Access challenge
   before login, owner access after login, disallowed identity refusal, root and
   direct module/worker/bundle-path protection. A 404 alone is insufficient.
   Never upload science as an access experiment. Keep any probe aliases protected.
7. After access and local staging checks pass, use only the approved 14-file B12
   staging directory for any separately permitted upload. Record returned IDs/URL/UTC and
   approved hosting configuration; review sensitive identifiers before committing.
8. Complete served-byte, MIME, genuine 404, browser/science/five-export and
   authentication tests on every actual origin. Only then place the working URL
   in IPAD_OWNER_HANDOFF.md and perform the physical review. Stop for engineering
   review afterward; no merge, plant coupling or automatic deployment.

Optional CLI path on the owner's trusted workstation (not run in B12): install
Wrangler per [official setup](https://developers.cloudflare.com/workers/wrangler/install-and-update/),
record its version and use that reviewed installation. Run `wrangler login` and
complete browser authentication yourself; then `wrangler whoami` privately to
confirm intended account. Do not paste its account/email output into reports.
Check `wrangler pages project create --help` and `wrangler pages deploy --help`.

```sh
# Empty-project step only, after account/identity review.
# Set B12_PROJECT to the actual available isolated project name.
wrangler pages project create "$B12_PROJECT" --production-branch b12-sealed
```

Do not proceed from empty creation to upload until steps 3, 5 and 6 have passed.
After revalidating the exact B11 checkout plus B12 branch:

```sh
python3 experiments/dx-fv/browser_eos_b12/verify.py --extract
# Use a NEW staging path each run; existing output is never overwritten.
python3 experiments/dx-fv/browser_eos_b12/stage.py --out experiments/dx-fv/browser_eos_b12/.runtime/staging/approved-preview
python3 experiments/dx-fv/browser_eos_b12/test-staging.py
```

Conditional future upload, **BLOCKED in this delivery**: from an otherwise empty
local staging directory with no functions/, .env, .dev.vars or inherited Wrangler
configuration, explicitly select the new account/project. Replace B12_STATIC_ROOT
with the absolute verified `.runtime/staging/approved-preview` path, never the
original extraction, ZIP or parent. Retain both original and wrapper manifests
with the future deployment receipt:

```sh
wrangler pages deploy "$B12_STATIC_ROOT" --project-name "$B12_PROJECT" --branch b12-sealed --commit-hash 909de1579051bfadca0e282adf93eaedc0e24b9c
wrangler pages deployment list --project-name "$B12_PROJECT"
```

The source hash attached to a deployment is metadata; it does not prove served
asset equality or privacy. Review deployment hooks/integration assumptions without
editing any existing project. No actual project name or URL is invented here.
