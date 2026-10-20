# Production isolation

Current 2026-10-20 scope: package/download handoff for the owner-reported existing
`ammonia-lab-research-b12` Worker. No account action or creation is performed.
The NEW Pages project design below is historical; do not create it for this handoff.
See WORKER_STATIC_UPLOAD_HANDOFF.md. All production exclusions remain unchanged.

Only a new Direct Upload research project is authorized. Existing production
Pages, public simulator URL, GitHub Pages, domains/DNS, secrets, environment
variables, hooks, main, demo, PR #3 and original workstation branch are excluded.
No existing Cloudflare project name or account mapping is assumed. No change to
an unknown project is safe merely because it resembles a simulator project.

Repository workflows at the B11 checkpoint have push filters for `main` and
`experimental/dx-fv-stage-3`. B12 adds no workflow and opens no PR. A B12-only push
does not match those push filters. Existing external Cloudflare integration
settings cannot be established from repository files; an account-side review
remains necessary to independently certify external integration behavior. The user
explicitly authorizes a B12-only branch push; no hosting upload is implied by it.
No authorization is inferred to edit production integration settings.

`evidence/remote-refs-before.txt` records all remote heads/tags. PR #3 head/base and
state are captured separately. Recheck all refs except the new B12 branch before
and after pushing. `verify.py` checks every B11 tracked file and source checkpoint.

Cloudflare control-plane isolation remains unobserved until authenticated account
review. Local preservation and absence of hosting mutations can be verified even
when account authentication is unavailable. No Cloudflare URL is claimed here.
