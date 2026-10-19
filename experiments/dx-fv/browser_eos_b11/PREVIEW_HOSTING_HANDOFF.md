# Static preview hosting handoff

**Deployment authorization: NO-GO / AWAITING APPROVAL.** B11 creates no remote host, public URL, Pages change, Cloudflare change, deployment workflow or production merge. Serve locally for engineering review. A future remote deployment requires the owner to approve the concrete host, research URL, access policy and exact reviewed package identity/checksum.

## Use the ready-built folder

Copy `preview/` alone, or extract `preview.zip` (verify `preview.zip.sha256` first). No Git checkout, Node, Python packages, CoolProp installation or runtime dependency download is needed by the browser. A static HTTP server is sufficient; Python below is one server option:

```sh
cd /path/to/copied/preview
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/` on that computer. Under a nested path, place the complete folder at the static server's `review/b11/` and open `http://127.0.0.1:8000/review/b11/` with its trailing slash. Disable no browser security features. Ensure the server maps directories to index.html; return real 404s for missing modules instead of an SPA HTML fallback.

Local-network serving may bind to a private interface with `--bind 0.0.0.0`, subject to owner firewall/Wi-Fi policy, but this is **not a working iPad A2 recipe over ordinary LAN HTTP**. The unchanged B10 crypto APIs require a secure context. Use an owner-approved trusted HTTPS server/reverse proxy reachable from the iPad, with a valid device-trusted certificate and complete local assets. Certificate warnings or insecure-content exceptions do not qualify an origin. Loopback on the iPad is not loopback on the desktop. Confirm the devices can route to each other, the server is listening, firewall allows the chosen port, and Wi-Fi client isolation is off where appropriate. No peer-device reachability was established in this cloud environment.

## Requirements for a separately approved HTTPS preview

- Isolated research path/site with explicit B11/nonproduction labeling in the hosting description; do not replace the existing simulator. Preserve the delivered B10 application source.
- Same HTTPS origin for index, styles, modules, worker and scientific bundle. Serve `.mjs` and `.js` as `text/javascript` (or another supported JavaScript MIME), `.css` as `text/css`, HTML as `text/html`, JSON as `application/json`. `X-Content-Type-Options: nosniff` is suitable with correct MIME.
- HTTPS with a certificate chain trusted by the actual iPad; no mixed-content imports, external model/API/CDN requests or CORS redirects. Standard same-origin module worker support. COOP/COEP/SharedArrayBuffer are not required.
- CSP must permit original inline scripts/styles, same-origin module imports, worker and fetch; original data images need `data:`. The B11 portability runner tests `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; worker-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'`. No `unsafe-eval` or blob worker is needed. If a host mandates a stricter policy, qualify it separately with the unchanged application.
- Serve a coherent version of all assets. Prefer no-cache/revalidation for the preview until an explicit immutable-version strategy is reviewed. No service worker is supplied. The scientific bundle's runtime digest is checked by the original worker; do not rewrite/minify it or inject hosting scripts.
- Verify all SHA-256 entries before transfer and after downloading from the approved URL; do not mistake transfer compression for a changed source. Open cold/warm, three advances, stop/dispose/restart and original simulator controls on the actual device. Record worker errors and independent clocks.

Approval should name: intended host/account, exact isolated path, public/private access, certificate/DNS ownership, package identity and ZIP hash, retention/removal plan, and explicit permission to publish that artifact. This document is an implementation-ready handoff, **not deployment approval**. No request to merge production or PR #3 is implied.
