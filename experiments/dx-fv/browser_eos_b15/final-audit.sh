#!/bin/sh
# Read-only live delivery check from repository root; no pushes or deployments.
set -eu
b=experiments/dx-fv/browser_eos_b15
python3 "$b/seal.py" --verify
python3 "$b/verify-protected.py" --published
test -z "$(git status --porcelain=v1)"
local_sha=$(git rev-parse HEAD)
remote_sha=$(git ls-remote origin refs/heads/research/b15-vapor-ph-bracket-reuse-20261020 | cut -f1)
test "$local_sha" = "$remote_sha"
printf 'Clean B15 local/remote HEAD: %s\n' "$local_sha"
