# Protected checkpoint and preservation audit

The checkout was clean at exact B9A
`355db28d853817e1931295d6ec2f007876d53f90`, then the isolated branch
`research/browser-eos-b9b-solver-property-profiling-20261017` was created.
The first additive commit `5fae85a` independently sealed PROFILING_DESIGN.md
before instrumentation. No previous research commit was amended or replaced.

`starting-files-sha256.json` hashes all 2,675 historical tracked files.
Gate 0 compared every one against its original starting Git object. Fourteen A2
source identities are separately verified against `be9eb35...`; root later
coupled-solver research files are not substituted. Complete B9, C1, B6 and B7
directories are checked against their original protected commits, including
browser bundle, error/rollback sources, loader and scientific artifacts. B9A
compact worker and all saved performance/scientific evidence remain byte-identical.

`remote-before.tsv` records all 37 original remote refs, including production,
accepted A2, prior research, UI, release and PR #3 head/merge refs. There were no
remote tags at the start. The complete original PR #3 API record is retained.
Pre-push `remote-final.tsv` / `pr3-final.json` compare exactly for protected
identities. The only allowed new remote ref is the named B9B branch.

After the authorized research push, GitHub's raw PR API embeds a changed
repository-global `pushed_at` in `head.repo` and `base.repo`. The raw responses
are preserved. Post-push comparison normalizes only those two timestamp fields
and asserts every other API field unchanged, including all PR identities,
content, own timestamps, head/base SHAs and state. These repository timestamps
are not a PR #3 edit. The initial unpushed receipt command continued after its
overstrict raw-response comparison failed; the receipt was corrected and all
checks rerun before publishing that receipt commit.

`preservation.py` rechecks historical bytes, branch/ancestry, additive-only Git
scope, protected refs and complete PR #3 data. It permits no changed or deleted
historical tracked path, even if the resulting scientific output would agree.
The exact original numerical/property/thermal/phase/acceptance code is untouched.

`observational.patch`, `diagnostic-source-manifest.json` and the independent
`observational-removal-audit.json` audit the profiling-only copies. Removing all
declared insertions restores every original source byte. Full saved B9A science,
original decisions and property sequences independently validate observation.
`measurement-source-manifest.json` identifies the final harness/copy implementation;
`deliverables-manifest.json` seals review artifacts, excluding itself and later
post-push receipts explicitly.

Push only the additive B9B branch; collect separate post-push receipts and verify
the exact remote head and a clean final worktree. A receipt cannot hash or contain
its own final commit identity without recursion, so final HEAD/remote/cleanliness
are also checked after the receipt commit. No force push, merge, deployment,
operator/Live Plant/Cloudflare change or optimization implementation is performed.
