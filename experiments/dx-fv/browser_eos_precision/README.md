# Browser EOS flash-precision compatibility — experimental, unqualified

Started from `f17623f61592bd897200206692ec002088f0a605` on a separate research
branch. All 341 starting-commit files are SHA-256 protected by the checkpoint.
This study diagnoses official binaries; it does not replace or integrate properties.

- [Engineering report](ENGINEERING_REPORT.md)
- [Mechanic's Report](MECHANICS_REPORT.md)
- [Physical iPad package instructions](IPAD_TEST_INSTRUCTIONS.md)
- [Arithmetic/root-cause evidence](evidence/root-cause.json)
- [Summarized measurements](evidence/summary.json)

## Reproduce

Python 3.12 environments: CoolProp **8.0.0**, NumPy **2.3.5** for analysis; separate
CoolProp **7.2.0** for historical comparison. The prior study's pinned requirements,
Playwright **1.62.1** package/lockfile, binary provenance and setup remain unchanged.
Browser evidence here uses Chromium **151.0.7922.34** and Linux WPE WebKit **26.5**.
Physical iPad was unavailable. Toolchain and source commits are in evidence and
upstream provenance. No binary was rebuilt.

Run from the repository root, using `python8`/`python72` below to mean the matching
environment's Python executable (substitute real executable paths):

```
python experiments/dx-fv/browser_eos_precision/prepare.py
python8 experiments/dx-fv/browser_eos_precision/native.py native-8.0.0.json
python72 experiments/dx-fv/browser_eos_precision/native.py native-7.2.0.json
PXFLASH_DIRECT_EOS=0 python8 experiments/dx-fv/browser_eos_precision/native.py native-8.0.0-cached-path.json --primary
python8 experiments/dx-fv/browser_eos_precision/native.py native-8.0.0-no-super.json --no-super --primary
node experiments/dx-fv/browser_eos_precision/run_browser.cjs
python8 experiments/dx-fv/browser_eos_precision/native_contract.py
node experiments/dx-fv/browser_eos_precision/run_synthetic.cjs
python experiments/dx-fv/browser_eos_precision/package_ipad.py /tmp/ammonia-ipad-precision
node experiments/dx-fv/browser_eos_precision/smoke_ipad.cjs /tmp/ammonia-ipad-precision ipad-smoke-v2.json
python8 experiments/dx-fv/browser_eos_precision/analyze.py
python experiments/dx-fv/browser_eos_precision/audit.py
```

Completed evidence is immutable: native scripts refuse to overwrite it; browser
runners retain existing outputs. To collect independent new runs, use a separate
research checkout with this directory's evidence removed **only in that new copy**,
retaining the original repository and exported evidence. Use new artifact directories.
`analyze.py` compares existing summaries byte for byte rather than regenerating them.
Before capturing native defaults, ensure the two `PXFLASH_*` source environment
toggles are unset. `--no-super` changes a native diagnostic process configuration
only; no corresponding shipped WASM setter exists.

In the managed runtime used here:

```
PLAYWRIGHT_BROWSERS_PATH=/workspace/ammonia-browser-runtime/browsers \
EOS_WEBKIT_EXECUTABLE=/workspace/ammonia-browser-runtime/webkit-local.sh \
node experiments/dx-fv/browser_eos_precision/run_browser.cjs
```

That WebKit launcher supplies Linux WPE dependency paths; it is not an iPad emulator
qualification. Standard Playwright installations elsewhere can supply their own
WebKit executable via `EOS_WEBKIT_EXECUTABLE` (or omit it for the standard installation).
Native environments here are `/workspace/ammonia-browser-runtime/python8/bin/python`
and `/workspace/ammonia-two-patch-runtime/bin/python`.

The final package is reproducibly built from `ipad/`, the immutable previous loader,
official binary assets and pinned inputs. Neither package generation nor smoke tests
publish anything. V1's directory-URL offline defect and V2's fix are retained as
separate evidence. The new `audit.py` checks restrictions without rewriting the
previous study's completed audit or results.
