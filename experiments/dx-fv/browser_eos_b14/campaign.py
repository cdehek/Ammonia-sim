"""Replay into a new ignored B14 directory; sequential processes, no overwrites."""
import argparse,datetime,os,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--repeats',type=int,choices=[1,3],default=1);a=p.parse_args()
out=B/'.runtime'/('replay-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S'));out.mkdir(parents=True,exist_ok=False)
env={**os.environ,'B14_RECEIPTS':str(out)}
def command(args):subprocess.run(args,check=True,env=env,cwd=B)
def run(variant,fixture,schedule,name,horizon='.01'):
 command(['python3',str(B/'run.py'),variant,fixture,schedule,name,'--horizon',horizon,'--out-dir',str(out)])
for f in ['cold','warm']:
 for i in range(1,a.repeats+1):
  c=f'canonical-{f}-r{i}';o=f'observed-{f}-r{i}'+('-fixed'if f=='cold'and i==1 else '')
  run('canonical',f,'original',c);run('observed',f,'original',o);command(['node',str(B/'verify.mjs'),c,o])
 run('control',f,'original',f'control-{f}-baseline','.001')
 run('observed',f,'original',f'initialization-{f}','.000001')
for schedule in ['added','fine']:
 c=f'canonical-warm-{schedule}';o=f'observed-warm-{schedule}'
 run('canonical','warm',schedule,c);run('observed','warm',schedule,o);command(['node',str(B/'verify.mjs'),c,o])
command(['node',str(B/'verify-baseline.mjs')]);command(['node',str(B/'analyze.mjs')])
print('Replay complete:',out,'; deliberate budget-kill and domain contracts are separate commands.')
