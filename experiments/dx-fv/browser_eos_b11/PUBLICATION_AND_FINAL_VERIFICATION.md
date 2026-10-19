# Publication and final verification

The B11 delivery was pushed only to `research/b11-portable-ipad-preview-20261019` and independently read back at `8293e90722d86adc9102f7a571c580f9332bf952`. `evidence/publication-receipt.json` records that exact delivery, its clean-tree observation, deterministic package/ZIP identities, protected source/ref checks and fresh PR #3 identity/status. No PR was created or edited, no production branch merged, and no remote host/public preview deployed.

The following audit commit adds only publication receipts/documentation and reseals the delivery. Its final SHA is deliberately verified read-only after its push, because a commit cannot contain its own SHA. The saved remote snapshot records the verified delivery commit; live verification requires current remote B11 to equal current local HEAD while every other remote head/tag remains exact. No runtime artifact, scientific source, original application or browser result changes in this audit commit.

Read-only final checks (from repository root):

```sh
python3 experiments/dx-fv/browser_eos_b11/verify-source.py
python3 experiments/dx-fv/browser_eos_b11/audit.py
python3 experiments/dx-fv/browser_eos_b11/verify-protected.py --live
python3 experiments/dx-fv/browser_eos_b11/validate-delivery.py
python3 experiments/dx-fv/browser_eos_b11/seal-delivery.py --check
git status --porcelain
```

Source/audit commands regenerate byte-identical deterministic receipts and do not run physics. A fresh connector/API read of PR #3 additionally verifies its live head/base/status. Browser evidence is complete and does not need to be rerun for publication metadata. All 3,221 historical tracked files and protected refs remain unchanged. Working tree must be clean and only B11 changes committed.

**B11 PORTABLE SERVED-PREVIEW PASS**, scoped to the declared desktop served targets. Desktop WebKit PARTIAL; file/offline NOT QUALIFIED; direct private-network transport BLOCKED, owner-network reachability UNTESTED; physical iPad AWAITING USER DEVICE REVIEW; research hosting AWAITING APPROVAL. Production merge and full Live Plant coupling NO-GO. Stop for engineering review.
