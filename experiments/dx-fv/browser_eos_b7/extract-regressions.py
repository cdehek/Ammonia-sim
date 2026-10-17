"""Retain original harness schemas for the unchanged focused scientific auditor."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
for engine in ['chromium','webkit']:
 d=json.loads((E/f'regressions-{engine}.json').read_text());assert 'harnessError' not in d
 for r in d['result']['rows']:
  label='controlA' if r['id']=='rebuiltB4C' else 'candidateB'
  p=E/(f'{engine}-{label}-focused'+('-full-vle' if r['fullVLE'] else '')+'.json');assert not p.exists();p.write_text(json.dumps(r['result'],indent=2)+'\n')
print('Original focused result schemas extracted without modifying scientific fields')
