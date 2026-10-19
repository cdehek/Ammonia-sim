"""Final delivery identities; no recursive self-hash claim."""
import hashlib,json,platform,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
required=['README','ENGINEERING_REPORT','MECHANICS_REPORT','INDEPENDENT_B9C_REVIEW','BOUNDARY_AND_PHASE_REGRESSIONS','SCIENTIFIC_PARITY_MATRIX','FAILURE_AND_ROLLBACK','OPERATOR_WORKSTATION_INTEGRATION_CONTRACT','FIELD_AND_UNITS_MAPPING','WORKER_TO_OPERATOR_PROTOCOL','OFFLINE_BROWSER_COMPATIBILITY','A2_TO_WORKSTATION_QUALIFICATION_GAPS']
assert all((B/(n+'.md')).is_file() for n in required)
assert json.loads((E/'preservation-final.json').read_text())['passed']
for n in ['chromium','webkit']:assert json.loads((E/f'performance-{n}.json').read_text())['passed']
core={str(p.relative_to(R)):sha(p) for p in B.iterdir() if p.is_file() and p.suffix in ['.mjs','.html','.cjs','.py','.md','.json','.csv']}
binary=list(Path('/workspace/b9-runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))+list(Path('/workspace/b9-runtime/browsers/webkit-2336/minibrowser-wpe/bin').glob('*'))
runtime={'python':platform.python_version(),'node':subprocess.check_output(['node','--version'],text=True).strip(),'binaries':{str(p):sha(p) for p in binary if p.is_file()},'launcher':{str(Path('/workspace/b9-runtime/webkit.sh')):sha(Path('/workspace/b9-runtime/webkit.sh'))},'B9DDeliveryFiles':core,'originalSources':'accepted-source-manifest.json','optimizedSources':'optimized-source-manifest.json','prerequisiteGateCommit':'6d9bb14cf708630d9f48dce085179a77172efd99','selfHashExcluded':True}
(E/'runtime-manifest.json').write_text(json.dumps(runtime,indent=2)+'\n')
print('Delivery sealed:',len(core),'B9D sources/reports; required reports present; real browser binary hashes recorded')
