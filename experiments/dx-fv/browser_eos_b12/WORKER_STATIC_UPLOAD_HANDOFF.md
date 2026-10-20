# Existing B12 Worker — owner upload handoff

**Packaging PASS; no upload performed.** Starting checkpoint:
`f66566af56bf14beb822b5b8951f74e488b01f1e`.
The owner reports an existing separate `ammonia-lab-research-b12` Worker, harmless
placeholder and owner-only Access policy for All traffic. These account settings,
hostnames and direct-asset protection have not been independently tested here.
No actual workstation URL or successful deployment is claimed.

Download [cloudflare-worker-static-upload.zip](https://github.com/cdehek/Ammonia-sim/raw/refs/heads/research/b12-private-https-ipad-preview-20261019/experiments/dx-fv/browser_eos_b12/cloudflare-worker-static-upload.zip)
and its separate [checksum](https://github.com/cdehek/Ammonia-sim/raw/refs/heads/research/b12-private-https-ipad-preview-20261019/experiments/dx-fv/browser_eos_b12/cloudflare-worker-static-upload.zip.sha256).
Repository path: `experiments/dx-fv/browser_eos_b12/cloudflare-worker-static-upload.zip`.

ZIP SHA-256:
`d7a766bc3c91c017dba3244a74d02472f23a35a6112ecc5105208e6c4c032956`.
ZIP size: 3,224,536 bytes. It contains exactly 14 asset files, no enclosing folder.
The scientific B11 package identity stays
`b7803a5bf93ddc102c7367b80e7dc4c620c21daec0dbad6ef1a988161e3a2914`.

1. Download the ZIP as a file, not the GitHub HTML preview page. Verify its SHA-256
   against the value above. On macOS use `shasum -a 256 cloudflare-worker-static-upload.zip`;
   on Linux use `sha256sum -c cloudflare-worker-static-upload.zip.sha256`; on Windows
   use `Get-FileHash .\cloudflare-worker-static-upload.zip -Algorithm SHA256`.
2. Extract into a NEW clean folder. Open it and confirm `index.html`, `404.html`
   and `asset-manifest.json` are immediately inside, alongside the other files and
   nested `science/` and `support/`. Do not edit files or flatten nested folders.
   Upload only this asset folder; keep the external checksum/instructions outside.
3. Before uploading science, independently verify owner-only Access on the actual
   Worker hostname, all preview/version aliases and direct asset paths, including
   `/worker.mjs`, `/panel.mjs`, `/science/candidate-bundle.mjs`, `/asset-manifest.json`
   and `/404.html`. Test fresh unauthenticated requests and authorized owner login.
   A policy label or ordinary missing-file 404 alone does not prove protection.
4. In the intended account open the EXISTING `ammonia-lab-research-b12` Worker and
   its reported **Upload static files to update your Worker** flow. Select the
   extracted asset folder. Check the upload preview maps index.html to `/` and
   preserves all 14 paths, including science/ and support/. Do not create another
   project, upload only index.html, select the repository, or upload the checksum.
   Treat the final upload/update/deploy control as publishing; the owner performs
   that step only after the access checks. This agent has not performed it.
5. Verify actual served bytes/MIME and authenticated missing root/nested module
   GET/HEAD responses afterward. Require real HTTP 404, not 200/index.html or the
   placeholder. Workers does NOT automatically activate the custom 404 body merely
   because 404.html exists: see [the Workers routing review](WORKERS_STATIC_ASSET_REVIEW.md).
   No HTTPS/browser/science/iPad qualification follows from successful file upload.

iPad Safari folder selection may be unsupported in this dashboard/browser version;
it has not been device-tested. If folder selection is unavailable or nested paths
cannot be preserved, use a desktop browser with folder upload. Do not compensate
by selecting only top-level files. An authenticated desktop Wrangler alternative,
including external routing configuration, is documented in the routing review.
No credentials/tokens/cookies should be sent in chat or committed.

After real HTTPS asset and browser qualification, use IPAD_OWNER_HANDOFF.md for the
bounded .0001/.0004/.0005 s review. Physical iPad stays AWAITING OWNER DEVICE REVIEW.
