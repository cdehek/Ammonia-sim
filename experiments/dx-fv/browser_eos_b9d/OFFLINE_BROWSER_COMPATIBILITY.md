# Offline/browser compatibility boundary

The pinned workstation's `tools/build.py` embeds its classic-script engine, properties, UI, profiles and validation into one HTML. That existing artifact needs no dynamic imports or scientific sidecar fetch. Its documented Chromium native file startup passed; desktop WebKit native file navigation failed before application startup, while setContent of standalone bytes passed. Neither establishes physical iPad Files/Safari support. Existing WebKit training playback and chart resize failures remain unresolved.

B9C uses module registries and a large table bundled as literal scientific source. An ESM main page, dedicated module worker and static/dynamic imports need a compatible origin and JavaScript MIME types. Opening a multi-file research harness through file:// may fail module CORS/origin checks even when the existing single-file classic-script workstation starts. A successful localhost run establishes that served transport only. No --disable-web-security, file-access override, security preference change, network backend or fallback plant model is permitted.

Supported B9D execution target: a local HTTP server serving the unchanged repository assets with no external application requests, Chromium and desktop WPE WebKit. Scientific registry carries properties; no EOS/WASM fetch is used. Serving already-local assets without Internet can work; this is distinct from browser offline mode, which may prevent uncached local HTTP requests. Explicit asset interception/missing bundle and browser offline failures must retain unavailable/lost status. There is no service-worker cache or installable offline package in this milestone.

A future offline workstation hook-up must choose and test packaging deliberately: for example a separately reviewed single-file classic bootstrap with owned worker bundle and embedded assets may be investigable, but has not been built or qualified here. Blob module workers, dynamic import resolution, CSP, Safari worker support, memory and disposal all need evidence for the chosen artifact. No compatibility follows merely from those APIs existing in a desktop browser.

Actual B9D HTTP/file/missing-asset/offline outcomes are recorded in `evidence/shadow-*.json.gz` when Gate 5 is authorized. A native file or offline failure is a reported deployment limitation, not hidden by substituting an illustrative backend. Physical iPadOS Safari performance, local file workflow and workstation full WebKit release readiness remain **OPEN**. Actual workstation integration and offline packaging remain **NO-GO** pending explicit engineering review.

## B9D actual outcomes

- chromium 151.0.7922.34: local HTTP PASS; missing bundle `unqualified-backend` with null snapshot; browser-offline `lost` with no snapshot; native file returned, application module loaded=False. Exact error/status is retained in the browser receipt.
- webkit 26.5: local HTTP PASS; missing bundle `unqualified-backend` with null snapshot; browser-offline `lost` with no snapshot; native file returned, application module loaded=False. Exact error/status is retained in the browser receipt.
