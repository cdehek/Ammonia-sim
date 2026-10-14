# Ammonia Lab — Demo Candidate v0.1 — 2026-10-14

This single HTML is the unchanged production build of approved checkpoint
`99af25e3b68798919ede19a5c0805775d5828eab`. Application version remains v0.5.0.
Release branch: `release/demo-candidate-20261014`. This is an unqualified candidate;
read the readiness report before presenting it on a physical device.

The HTML is self-contained: property data, models, HMI, schematic, charts and
scripts are embedded. No installation, login or Internet API is required by it.
SHA256: `2924babd0e2c6fb37c71a9473a83f68644a154c6354a1c834513c570386f5420`.

From GitHub, choose this release branch, open the HTML file, and use **Download
raw file**. A GitHub code preview is not the running simulator. Alternatively:

```sh
git clone --branch release/demo-candidate-20261014 https://github.com/cdehek/Ammonia-sim.git
cd Ammonia-sim/releases/demo-candidate-v0.1-20261014
python3 -m http.server 8000 --bind 0.0.0.0
```

Open the filename from that server in full Safari. For iPad Internet-independent
access, use the host's LAN IP on the same Wi-Fi and keep the host awake. Disconnect
the Internet uplink and repeat cold startup, but keep local Wi-Fi available.
Files/Quick Look is not qualified to execute HTML/JavaScript; this artifact does
not add a service worker/PWA or guarantee Safari-only file startup in airplane mode.

See [readiness evidence](../../docs/demo-candidate/REPORT.md),
[physical iPad checklist](../../docs/demo-candidate/IPAD_CHECKLIST.md) and
[2–3 minute runbook](../../docs/demo-candidate/DEMO_RUNBOOK.md).

The compact delivery ZIP is also prepared at
`/workspace/deliverables/ammonia-lab-demo-candidate-v0.1-20261014.zip` in the Codex
workspace. Open the workspace file explorer, locate that path, and download it
before the workspace expires. It contains the HTML, instructions, checksums,
screenshots and verification evidence. GitHub retains the committed HTML and
documentation on the isolated release branch; the workspace ZIP is not a hosted
application. No Pages, deployment, production branch or PR #3 change is authorized.
