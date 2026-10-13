# Physical iPad Safari research test — unqualified

This package measures a pinned backend, not the accepted simulator. It deliberately
retains the saved failing PH inputs and 0.01 Pa pressure probe. No production files,
hosting, workflows, property defaults or numerical contracts are changed.

## Build and serve without publishing

From the repository root, with Python 3.12:

```
python experiments/dx-fv/browser_eos_precision/package_ipad.py /tmp/ammonia-ipad-precision
```

The destination must be new. It contains the page, both unmodified official binaries,
input cases, worker, service worker, SHA-256 manifest and license notices. The adjacent
ZIP is self-contained. Preserve its metadata file alongside exported test evidence.

Serve that directory with a static server. Use `application/wasm` for `.wasm`, JavaScript
MIME for `.js`/`.mjs`, and HTTPS for physical-device offline restart. The loader also
has an ArrayBuffer compilation fallback if streaming MIME is unavailable. Do not
open `file://` URLs. No CDN, remote property service, API key or cross-origin isolation
is required. A worker runs synchronous EOS calls away from the page thread.

A laptop's `http://localhost` works for desktop tests. An iPad's connection to the
laptop's LAN IP over ordinary HTTP is **not** a secure origin for service workers.
For physical testing use an isolated LAN HTTPS static server with a certificate
trusted on that iPad, managed by the device owner; remove any temporary trust after
the study. Apple Safari Web Inspector on a connected Mac can record console and
network failures. If that setup is unavailable, seek separate approval for hosting.
Nothing in this study publishes a page or installs a certificate on a user's device.

## Reproducible sequence

1. Record physical iPad model, RAM if reliably known, iPadOS/Safari versions, Safari
   tab versus Home Screen mode, battery/charging, Low Power Mode, free storage,
   other active tabs, origin, connection and package SHA. Record unknowns as unknown.
   Keep Safari in the foreground. Desktop WebKit results are not an iPad baseline.
2. Load the page from HTTPS. Record first network transfer/loading time using Web
   Inspector where available. The exported EOS initialization time starts inside
   the worker and does not include first-page navigation or real WAN download.
3. Enter device/version labels. Select 8.0.0 and run. During work, type in the
   responsiveness field. Export JSON to Files and record any visible stall, tab
   reload, worker failure, or OS memory warning. The export includes exact input
   bits, PH residuals, derivative ratios, startup, linear memory, three 500 ms PH
   and DU rounds, three 1 s mixed epochs, repeated flashes and error recovery.
   Supported liquid, saturated vapor and two-phase requests are used for throughput.
4. Repeat three times in freshly reloaded pages for 8.0.0, then for 7.2.0. There is
   no property cache. Browser compiler/OS caches may remain: label these warm loads.
   Record an initial uncached load separately rather than calling all runs cold.
   Preserve failures; do not average properties, round inputs or alter perturbations.
5. Press **Prepare offline assets** while online. It verifies every runtime asset's
   SHA-256 after the worker has stopped, registers a service worker scoped to the
   isolated package, and waits for control. Export this preparation record.
6. Disconnect the network (Airplane Mode and Wi-Fi off), stop the laptop server,
   and completely close/reopen Safari. Reopen the exact bookmarked HTTPS URL.
   Run each backend again and export. Record the new page/run timestamps, cache
   status, any browser trust/network error and whether initialization succeeds.
   Cached assets can be evicted by Safari; failure is evidence, not permission to
   supply fallback thermodynamic values. The page's `navigator.onLine` flag alone
   does not prove offline operation. A stopped origin plus actual disconnect does.
7. Reconnect, export any remaining evidence, and remove the isolated site's stored
   data/service worker when finished. Do not clear production application data.

## Interpretation and observable limits

- Expected desktop 8.0.0 saved-case forward ratio: about **20.19046**, with perturbed
  underlying enthalpy residual about **−0.000474579 J/kg**. Seeing this on iPad would
  reproduce a blocker, not pass a precision gate. 7.2.0 desktop ratio is about 0.999994.
- WASM linear memory is measured directly. It excludes JavaScript buffers, compiled
  code, browser overhead and OS memory. `performance.memory` is normally absent in
  Safari; absence is recorded as null. A successful short run cannot prove freedom
  from memory termination during long sessions.
- Timer gaps measure main-thread availability during a worker test; manual typing
  observations supplement them. Hidden/background ticks are flagged. They are not
  measured touch latency. JSON download/share behavior itself must be checked on
  the physical device.
- Flash testing is deterministic, bounded and static. No multihour trajectories,
  Stage 2B matrix, empirical ammonia validation or migration approval are implied.

## Optional deployment proposal requiring separate approval

If trusted LAN HTTPS is impractical, the smallest proposal is a **separate temporary
HTTPS static research origin/repository**, containing only this ZIP's extracted
contents, no analytics or external requests, with service-worker scope limited to
that origin/path. Upload both pinned versions and notices, retain the SHA manifest,
verify MIME and offline restart, then remove hosting after collection. Seek explicit
approval for that publication first. Do not publish through the production Ammonia
Pages site or modify its workflow. No publication was performed by this study.
