"""Sequential original WebKit baseline/candidate and console; literal assertions."""
import json,os,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
env=dict(os.environ,NODE_OPTIONS='--require='+str(B/'browser-preload.cjs'),PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS='1',TEST_BROWSER='webkit')
codes=[]
for mode in ['baseline','candidate']:
 with (E/(mode+'-webkit.log')).open('w') as f:p=subprocess.run(['node',str(B/'run-original.cjs'),mode],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 codes.append({'mode':mode,'code':p.returncode});print(mode,p.returncode,flush=True)
for test,log in [('operator-console-ui.cjs','candidate-console-webkit.log'),('console-retained-readings.cjs','retained-webkit.log')]:
 with (E/log).open('w') as f:p=subprocess.run(['node',str(B/'.runtime/candidate/tests'/test)],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 codes.append({'suite':test,'code':p.returncode});print(test,p.returncode,flush=True);assert p.returncode==0
(E/'webkit-sequential-codes.json').write_text(json.dumps(codes,indent=2)+'\n')
