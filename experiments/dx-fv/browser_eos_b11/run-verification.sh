#!/bin/bash
# Sequential campaigns only. Failures remain in their own raw logs and receipt.
set -u
B11_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$B11_DIR/../../.."
export NODE_OPTIONS="--require=$B11_DIR/browser-preload.cjs"
export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1
: > "$B11_DIR/evidence/campaign-exits.tsv"
run_case() {
 local label="$1"
 shift
 "$@" > "$B11_DIR/evidence/$label.log" 2>&1
 local status=$?
 printf '%s\t%s\n' "$label" "$status" >> "$B11_DIR/evidence/campaign-exits.tsv"
 printf '%s exit %s\n' "$label" "$status"
}
run_case original-numerical npm --prefix "$B11_DIR/.runtime/pinned" test
for browser in chromium webkit; do
 export TEST_BROWSER="$browser"
 for mode in baseline candidate; do
  run_case "$mode-$browser" node "$B11_DIR/run-original.cjs" "$mode"
 done
 for suite in operator-console-ui console-retained-readings; do
  run_case "candidate-$browser-$suite" node "$B11_DIR/.runtime/candidate/tests/$suite.cjs"
 done
done
unset TEST_BROWSER
for suite in isolation portability render performance; do
 run_case "$suite-run" "$B11_DIR/.runtime/venv/bin/python" "$B11_DIR/run-$suite.py"
done
