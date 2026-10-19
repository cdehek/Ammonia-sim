# Served browser boundary

B10 targets local HTTP-served research only. The existing workstation remains a pinned standalone HTML application; the added scientific module worker requires separately served assets with an appropriate origin and JavaScript MIME types. No service-worker cache, offline package, security bypass, external scientific service or illustrative fallback is introduced.

B9D's actual module startup failed under native file and browser-offline conditions. B10 must report its own observed checks without treating local asset serving as offline qualification. Desktop Chromium/WebKit and 1024×768 or 768×1024 viewport emulation are not physical iPadOS Safari evidence. Touch comfort, safe areas, onscreen keyboards, VoiceOver, actual file workflow, sustained device memory/performance and the inherited WebKit playback/chart findings require separate review.

Offline/local-file: NOT QUALIFIED. Physical iPad: NOT TESTED. Production merge and plant-wide backend: NO-GO. No deployment or feature-branch merge is authorized.

## Actual B10 observations

- chromium: browser-offline A2 status `lost`; native-file result `{"originalReady":true,"A2Loaded":false,"panelText":"A2 scientific panel unavailable \u00b7 Failed to fetch dynamically imported module: file:///experiments/dx-fv/browser_eos_b10/panel.mjs \u00b7 use local HTTP serving. Original workstation remains available."}`.
- webkit: browser-offline A2 status `lost`; native-file result `{"originalReady":true,"A2Loaded":false,"panelText":"A2 scientific panel unavailable \u00b7 Importing a module script failed. \u00b7 use local HTTP serving. Original workstation remains available."}`.

Missing scientific modules return an explicit unqualified backend and null snapshot in both browsers. Local HTTP passes. Original standalone workflows pass separately; this does not make the A2 sidecar package offline-ready.
