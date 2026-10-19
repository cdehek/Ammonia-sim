"""Check recorded remote ref/PR snapshots, without network or remote mutations."""
import argparse
import json
from pathlib import Path
import subprocess

B = Path(__file__).resolve().parent
R = B.parents[2]
E = B / 'evidence'
OWN = 'refs/heads/research/b12-private-https-ipad-preview-20261019'

def refs(path):
    return dict(row.split()[::-1] for row in path.read_text().splitlines() if row.strip())

ap = argparse.ArgumentParser()
ap.add_argument('--published', action='store_true', help='Also require recorded remote B12 == current HEAD')
ap.add_argument('--followup', action='store_true', help='Use the 404 follow-up snapshots; B12 already exists')
args = ap.parse_args()
prefix = '404-' if args.followup else ''
before, after = [refs(E / f'remote-refs-{prefix}{p}.txt') for p in ['before', 'after']]
if args.followup:
    assert before[OWN] == '1ab61278159a51fb3f86bb817ea1f03b049443d8'
else:
    assert OWN not in before, 'B12 was not a new remote branch'
assert {k: v for k, v in after.items() if k != OWN} == {k: v for k, v in before.items() if k != OWN}, 'Protected remote ref/tag changed'
keys = ['number', 'state', 'merged', 'base', 'base_sha', 'head', 'head_sha', 'head_repo_full_name', 'draft']
a, b = [json.loads((E / f'pr3-{prefix}{phase}.json').read_text()) for phase in ('before', 'after')]
assert {k: a[k] for k in keys} == {k: b[k] for k in keys}, 'PR #3 changed'
if args.published:
    assert after[OWN] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R).decode().strip()
print('PASS: all recorded protected remote heads/tags and PR #3 unchanged' + ('; published B12 == HEAD' if args.published else ''))
