"""Run the WebKit suites after npm test:webkit's fail-fast release-suite check.
All original suites/assertions remain unchanged; failures remain failures.
"""
import json, os, pathlib, subprocess
out=pathlib.Path('docs/demo-candidate/verification')
tests=['schematic-ui.cjs','history-ui.cjs','training-ui.cjs','visual-pass2-ui.cjs','industrial-styling-ui.cjs','hmi-uplift-ui.cjs','operator-assist-ui.cjs']
results=[]
for test in tests:
 with (out/('webkit-'+test+'.log')).open('w') as log:
  p=subprocess.run(['node','tests/run-browser.cjs',test],env={**os.environ,'TEST_BROWSER':'webkit'},stdout=log,stderr=subprocess.STDOUT)
 results.append({'suite':test,'exitCode':p.returncode});print(test,p.returncode,flush=True)
 (out/'webkit-remaining-results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(int(any(r['exitCode'] for r in results)))
