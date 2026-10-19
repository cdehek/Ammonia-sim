"""Capture public GitHub ref/PR metadata read-only; never overwrites a receipt.

Run with --phase after before final commit. A later live publication snapshot can
be kept under ignored .runtime to avoid a self-referential commit SHA receipt.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import urllib.request

B = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--phase', required=True, choices=['before', 'after', 'publication'])
args = ap.parse_args()
out = B / ('.runtime' if args.phase == 'publication' else 'evidence')
out.mkdir(exist_ok=True)
dest = out / f'remote-refs-{args.phase}.txt'
prdest = out / f'pr3-{args.phase}.json'
stamp = out / f'remote-observation-{args.phase}.json'
assert not any(p.exists() for p in [dest, prdest, stamp]), 'Receipt already exists; use a new reviewed observation'
refs = subprocess.check_output(['git', 'ls-remote', '--heads', '--tags', 'origin'], cwd=B.parents[2])
request = urllib.request.Request('https://api.github.com/repos/cdehek/Ammonia-sim/pulls/3',
                                 headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'B12-read-only-audit'})
with urllib.request.urlopen(request, timeout=30) as response:
    pr = json.load(response)
obj = {'number': pr['number'], 'state': pr['state'], 'merged': pr['merged'],
       'base': pr['base']['ref'], 'base_sha': pr['base']['sha'],
       'head': pr['head']['ref'], 'head_sha': pr['head']['sha'],
       'head_repo_full_name': pr['head']['repo']['full_name'], 'draft': pr['draft']}
dest.write_bytes(refs)
prdest.write_text(json.dumps(obj, indent=2) + '\n')
stamp.write_text(json.dumps({'observedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                             'source': 'git ls-remote and public GitHub PR GET; no remote writes'}, indent=2) + '\n')
print('Captured sanitized ref and PR identity snapshot:', args.phase)
