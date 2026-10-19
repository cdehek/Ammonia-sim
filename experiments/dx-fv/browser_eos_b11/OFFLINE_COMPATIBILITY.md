# Offline and native-file boundary

**NOT QUALIFIED.** No service worker/PWA or single-file scientific package was introduced. No scientific source was modified for offline compatibility.

| Mode | B11 observation |
|---|---|
| All local assets served, browser online, localhost | PASS independently in both browsers; no external scientific/application request |
| HTTPS with network disconnected | UNTESTED; no HTTPS deployment/host established |
| Existing fully loaded localhost worker, then browser offline | Three bounded advances pass; a new worker restart fails; no offline-startup qualification |
| Browser offline before lazy panel import | Panel unavailable, original ready |
| Browser offline after panel import, before worker | Scientific worker lost/unqualified, no accepted snapshot |
| Cached/service-worker offline mode | NOT IMPLEMENTED / NOT QUALIFIED |
| Native file on desktop | Actual observations below; NOT QUALIFIED |
| Native iPad Files/Safari | NOT TESTED / AWAITING USER |

- chromium native file: `{"originalReady":true,"loaded":false,"text":"A2 scientific panel unavailable \u00b7 Failed to fetch dynamically imported module: file:///tmp/b11-independent-zchabgp0/root/panel.mjs \u00b7 use local HTTP serving. Original workstation remains available."}`
- chromium offline-existing-session: `{"case":"offline-existing-session","existingWorkerThreeAdvances":[0.0001,0.0005,0.001],"offlineFreshRestart":{"status":"lost","snapshot":null,"error":{"message":"Worker error"}},"originalOperationContinues":"10.0 s simulated","qualification":"Existing loaded localhost worker only; not offline startup/cache/PWA or HTTPS-disconnected proof"}`
- chromium offline-before-worker: `{"case":"offline-before-worker","status":"lost","snapshot":null,"error":{"message":"Worker error"},"originalReady":true}`
- chromium offline-before-panel: `{"case":"offline-before-panel","loaded":false,"text":"A2 scientific panel unavailable \u00b7 Failed to fetch dynamically imported module: http://127.0.0.1:38113/panel.mjs \u00b7 use local HTTP serving. Original workstation remains available.","originalReady":true}`
- webkit native file: `{"originalReady":true,"loaded":false,"text":"A2 scientific panel unavailable \u00b7 Cross-origin script load denied by Cross-Origin Resource Sharing policy. \u00b7 use local HTTP serving. Original workstation remains available."}`
- webkit offline-existing-session: `{"case":"offline-existing-session","existingWorkerThreeAdvances":[0.0001,0.0005,0.001],"offlineFreshRestart":{"status":"lost","snapshot":null,"error":{"message":"Worker error"}},"originalOperationContinues":"10.0 s simulated","qualification":"Existing loaded localhost worker only; not offline startup/cache/PWA or HTTPS-disconnected proof"}`
- webkit offline-before-worker: `{"case":"offline-before-worker","status":"lost","snapshot":null,"error":{"message":"Worker error"},"originalReady":true}`
- webkit offline-before-panel: `{"case":"offline-before-panel","loaded":false,"text":"A2 scientific panel unavailable \u00b7 Importing a module script failed. \u00b7 use local HTTP serving. Original workstation remains available.","originalReady":true}`

Missing/corrupt scientific bundle tests also retain genuine unqualified/null-snapshot states. Original classic-script standalone/offline workflows pass separately in the original console suite; this is not scientific offline startup evidence. Local server availability is not equivalent to Safari browser offline mode, cached HTTPS, or Files opening. A separately authorized future offline package must test transport/security/cache lifecycle without changing model acceptance or introducing a fallback engine.
