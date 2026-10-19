# B12 isolated nonproduction HTTPS architecture

Design recorded before Cloudflare account actions. Start: B11
`909de1579051bfadca0e282adf93eaedc0e24b9c`. Only B12 files may change.

Use a NEW Cloudflare Pages Direct Upload project with an available name beginning
`ammonia-lab-research-b12`. No Git integration, build, CI, deployment hook, custom
domain, DNS edit, production configuration, or recurring deployment is required.
An empty project is the first account mutation, only after authentication and
intended account control are established. The actual project name is not reserved.
Label the project and Access applications **B12 NONPRODUCTION RESEARCH**. Preserve
the reviewed HTML exactly; do not inject a banner into the sealed artifact.

The only upload candidate is the extracted `preview/` inside the committed B11
ZIP, SHA-256 `a642fe22078e7637f9e5c12ce0efbc6f8b7de317da3853b6a52b03452a3ee078`.
Package identity is `b7803a5bf93ddc102c7367b80e7dc4c620c21daec0dbad6ef1a988161e3a2914`.
No scientific build, minification, rebundling or runtime external service.

Before uploading any workstation asset, establish owner-only Access on BOTH
`PROJECT.pages.dev` and `*.PROJECT.pages.dev`, covering the entire path space.
The owner must explicitly approve the sole allowed identity; Git author identity
and GitHub identity are not Access authorization. No public release is authorized.
Validate unauthenticated denial and owner login independently, including script,
worker, module and bundle paths and every discovered deployment/branch alias.
An empty-site 404 or dashboard checkbox is insufficient evidence of protection.
If a harmless probe is needed, use only a separately identified nonscientific
sentinel within this isolated project, retain no sentinel in the final package,
and keep its deployment aliases under Access too. Never use science as the probe.

Only then upload the exact extracted directory, record actual deployment IDs and
UTC time, verify all downloaded decoded bytes/MIME/404/security headers, and run
real HTTPS Chromium and WebKit qualification. Auth receipts must omit cookies,
tokens, email, account identifiers and session content. Physical iPad remains
AWAITING OWNER DEVICE REVIEW until the owner supplies observations.

Read current official documentation before commands; references and owner steps
are retained in OWNER_ACTION_CHECKLIST.md and CLOUDFLARE_DOCUMENTATION.md.
If auth, owner identity, Access coverage or compatibility is unavailable, stop
publishing and complete the local handoff. Production merge and plant coupling:
NO-GO. Removal must target only the recorded B12 project after engineering review.
