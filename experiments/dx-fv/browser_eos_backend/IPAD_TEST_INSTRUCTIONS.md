# Physical iPad test — experimental, unqualified

No physical iPad result was collected in B1. Desktop Chromium and Linux WPE
WebKit are different platforms. They establish neither Safari/iPadOS memory
limits nor thermal, battery, touch-latency or long-duration performance.

Build a new standalone artifact from the repository root:

```bash
python3 experiments/dx-fv/browser_eos_backend/package_ipad.py /tmp/ammonia-b1-ipad-new ipad-replay-package.json
```

The adjacent ZIP bundles four separately identified backends, exact inputs,
worker, hash manifest, service worker and licenses. It contains no application
engine or Live Plant. Its page is `experiments/dx-fv/browser_eos_backend/`.
The final tested package's SHA256 and size are in `evidence/ipad-package.json`.
Repackaging the same files uses fixed ZIP timestamps for a stable archive.

Serve the extracted folder over an isolated, owner-managed HTTPS LAN origin with
a certificate trusted by that iPad. Use `application/wasm` and JavaScript MIME
types. An iPad connecting to a laptop's ordinary LAN HTTP IP cannot perform the
service-worker offline test. Do not use `file://`. Nothing here publishes a site
or configures hosting, Cloudflare, production DNS or certificates. The device
owner manages any temporary HTTPS/certificate setup and removes it afterward.

1. Record iPad model, iPadOS/Safari version, tab versus Home Screen mode, origin,
   package SHA, battery/charging, Low Power Mode, free storage and other active
   tabs. Unknown hardware details remain unknown. Keep the page in the foreground.
2. Enter those labels on the page. Run each backend separately: `official8`,
   `build30`, `build44`, `official72`. Type in the responsiveness field during
   work. Export every JSON, including failures. Record stalls, reloads and memory
   warnings. Do not change input literals, pressure/enthalpy probes or step scheme.
3. Repeat three fresh-page runs per backend. Label the first uncached network
   load separately from warm loads; fresh pages can still share compiled-code/OS
   caches. Initialization timestamps start inside the worker and omit first-page
   download. Use Web Inspector for complete network/navigation timing if available.
4. The saved pressure probe is exactly 0.01 Pa at
   `30298.937123458254 Pa`, `94523.34612321304 J/kg`; accepted enthalpy step is
   `0.0009452334612321304 J/kg`. Desktop ratios are about 20.1904555 for both
   30-bit controls, 0.999959589 for build44 and 0.999993952 for official72.
   Device results are measurements to preserve, not values to force or hardcode.
5. Press **Prepare offline assets** online. This verifies every runtime asset's
   SHA256 and waits for service-worker control. Record its success/failure.
6. Disconnect actual networking, stop the origin server, close/reopen Safari,
   and reopen the **exact same page URL**. Run each backend and export evidence.
   Record any navigation error, cache eviction, worker failure or OS termination.
   `navigator.onLine` alone is not proof of a disconnected origin.
7. Remove only this isolated origin's data/service worker and any temporary
   device-owner trust settings. Preserve all exported evidence and its package SHA.

The V1 package had duplicate precache URLs and failed installation in both
desktop engines. V2 deduplicates canonical URLs. Desktop WebKit's automation
`context.offline=true` navigation failed even after cache preparation; the
separate origin-disabled test must be read independently. Physical Safari
disconnect/relaunch behavior still requires this real-device sequence.

WASM linear-memory bytes exclude compiled code, JavaScript buffers, browser/OS
overhead and other tabs. Timer gaps are worker/page scheduling observations, not
touch latency. A short successful test is not proof against later iPad memory
termination. All results remain research evidence requiring engineering review.
