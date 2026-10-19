# Protected history, refs and PR #3

PASS for the recorded verification snapshots. `audit.py` verifies all 3,221 starting tracked file bytes against exact B10 and the complete starting SHA-256 inventory, all fourteen accepted A2 closure files, the pinned commits and unchanged historical local refs. Every committed addition/change is confined to `experiments/dx-fv/browser_eos_b11/`. `verify-source.py` freshly checks all 574 original-workstation source identities plus reverse derivation and the exact B9C scientific bundle.

`evidence/remote-refs-before.txt` and `remote-refs-after.txt` record all remote heads/tags. `verify-protected.py` requires complete equality except the newly authorized B11 branch. No tags existed in the starting remote snapshot; none may be introduced. The protected A2/B9C/B9D/B10/original branches retain the exact user-specified SHAs. No protected branch is checked out for implementation, merged or pushed.

PR #3 remains **OPEN, unmerged, not draft**:

| Identity | Preserved value |
|---|---|
| Head | `v0.5.5-stage-1` at `d4422425750a1d3c4e432cc103ac42ead40b7cc6` |
| Base | `main` at `0473d32f62db992fde0f581d116e1bd0c8e7d8ed` |
| URL | https://github.com/cdehek/Ammonia-sim/pull/3 |

The before/after connector snapshots and checked identity/status fields are saved in `evidence/pr3-before.json`, `pr3-after.json` and `protected-refs-pr3.json`. No PR mutation, comment, review, merge or replacement was performed.

Existing repository push workflows target `main` and `experimental/dx-fv-stage-3`; B11 changes no workflow/Pages/Cloudflare/hosting configuration. Only the B11 research branch may be pushed. No deployment action or public preview URL creation was performed. Research deployment awaits separate approval; production merge and full Live Plant coupling remain NO-GO.

After publication, run the read-only checks below against final HEAD (a new connector read of PR #3 separately confirms live status):

```sh
python3 experiments/dx-fv/browser_eos_b11/audit.py
python3 experiments/dx-fv/browser_eos_b11/verify-protected.py --live
python3 experiments/dx-fv/browser_eos_b11/seal-delivery.py --check
git status --porcelain
```

The live check requires the B11 remote to equal local HEAD and all other remote refs/tags to equal the starting snapshot. Publication receipts identify their verified delivery commit; the final audit commit is verified read-only after its own push to avoid a self-referential commit hash. Stop for engineering review.
