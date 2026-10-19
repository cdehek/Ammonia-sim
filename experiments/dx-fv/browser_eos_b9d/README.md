# B9D — independent hardening and first shadow connection

Research branch: `research/browser-eos-b9d-hardening-hookup-readiness-20261018`, exact parent checkpoint `b67afb3215075b2ec82bef376d39e03953dc0da2`. All changes are confined here. Accepted A2, B9C, operator workstation, production, demo and historical research remain untouched.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md) for independent A–J decisions, [MECHANICS_REPORT.md](MECHANICS_REPORT.md) for the practical interpretation, and [FIELD_AND_UNITS_MAPPING.md](FIELD_AND_UNITS_MAPPING.md) before using any reading. This milestone permits only a separate five-section evaporator research display after prerequisite gates pass. It does not permit a merge, deployment, Live Plant connection, plant-backend replacement or equipment-safety claim.

Reproduce from repository root on a supported Linux browser host:

```sh
# Python Playwright 1.62.0 is used in the recorded environment.
# Install it in a separate workspace virtualenv if needed.
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers python3 experiments/dx-fv/browser_eos_b9/setup-browsers.py
python3 experiments/dx-fv/browser_eos_b9d/source-review.py
python3 experiments/dx-fv/browser_eos_b9d/run-review.py
python3 experiments/dx-fv/browser_eos_b9d/summarize-review.py
# Run the shadow browser validation only when evidence/gates-1-4.json authorizes it.
python3 experiments/dx-fv/browser_eos_b9d/run-shadow.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/experiments/dx-fv/browser_eos_b9d/` for the isolated prototype if present. It supports cold/warm initialization, three original requested intervals (.0001, .0004, .0005 s, total .001 s), latest accepted readings, basic diagnostics, stop and disposal/restart. It deliberately offers no continuous real-time claim, arbitrary edits or plant controls. Source assets remain in the verified historical directories and must be served with this folder. There are no external application services.

`audit.py` is a starting-checkpoint operation and asserts exact starting HEAD; do not run it on the completed commit and interpret that expected refusal as a scientific failure. `source-review.py`, browser review and shadow runs are reproducible on the completed branch and write their receipts only here. The byte-identical `isolated/coupled-model.cjs` copy supports B9C's source-extracted mechanical fetch test; the running scientific model is the original protected B9C candidate bundle, not that loose file.

Review evidence uses exact binary64 tags, complete accepted states/records/attempts and component hashes. Same-engine equality is required; cross-browser bit identity is not assumed. `review-path-failure*` preserves an initial B9D relative-source-fetch harness error, corrected without changing the solver. Browser launcher/dependency setup is workspace-local, preserves TLS/security settings and changes no historical tracked source. Offline/file and physical iPad limitations are in [OFFLINE_BROWSER_COMPATIBILITY.md](OFFLINE_BROWSER_COMPATIBILITY.md).

Stop for explicit engineering review after publication. The next-milestone recommendation is in [A2_TO_WORKSTATION_QUALIFICATION_GAPS.md](A2_TO_WORKSTATION_QUALIFICATION_GAPS.md).
