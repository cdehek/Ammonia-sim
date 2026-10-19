# B11 — Portable workstation research preview

**B11 PORTABLE SERVED-PREVIEW PASS** for the declared desktop HTTP-served scope. Desktop WebKit remains PARTIAL for inherited application assertions. Physical iPad: **AWAITING USER DEVICE REVIEW**. Offline NOT QUALIFIED. Deployment AWAITING APPROVAL; production merge and full Live Plant coupling NO-GO.

Copy `preview/` alone to another directory/computer, or extract `preview.zip` after checking `preview.zip.sha256`. No checkout is needed to serve the result:

```sh
cd /path/to/copied/preview
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`. Select **A2 Evaporator Research** in the original bottom console (scroll the tool rail if needed), expand, and initialize cold or warm. Request only .0001, .0004 and .0005 s; accepted times are 0/.0001/.0005/.001 s. Original Initialize auto DX/Start/Pause/+10 s and training use the independent original illustrative plant, never A2. The delivered interface intentionally remains B10's actual workstation.

Ordinary private-LAN HTTP does not supply B10's secure crypto APIs in the tested browsers. For an iPad use a separately approved, reachable trusted HTTPS origin, then execute PHYSICAL_IPAD_REVIEW.md. A localhost test does not establish device reachability. See PREVIEW_HOSTING_HANDOFF.md for exact server/MIME/CSP/approval requirements. No host or public URL has been created.

Package identity: `b7803a5bf93ddc102c7367b80e7dc4c620c21daec0dbad6ef1a988161e3a2914`. Scientific bundle remains exact B9C. Rebuild from these Git identities:

```sh
python3 experiments/dx-fv/browser_eos_b11/build.py
python3 experiments/dx-fv/browser_eos_b11/verify-source.py
python3 experiments/dx-fv/browser_eos_b11/audit.py
python3 experiments/dx-fv/browser_eos_b11/seal-delivery.py --check
```

Build requires only Python standard library and Git objects; all browser dependencies stay ignored in B11/.runtime. Full rerun setup and campaign commands are in SOURCE_AND_BUILD_AUDIT.md. Reports/receipts include complete exact accepted-state comparisons, ten full exercise exports, original baseline/candidate logs, viewport screenshots, independent root/nested serving and matched B10/B11 performance. Read ENGINEERING_REPORT.md before interpreting this scoped pass.
