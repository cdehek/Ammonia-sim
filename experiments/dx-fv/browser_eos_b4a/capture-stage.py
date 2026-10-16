"""Record an external source stage and exact build settings without secrets."""
import os
import argparse,hashlib,json,platform,shutil,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'));S=Path('/workspace/coolprop-b4a')
ap=argparse.ArgumentParser();ap.add_argument('stage');args=ap.parse_args()
def command(*a):return subprocess.check_output(a).decode().strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=command('git','-C',str(S),'ls-files').splitlines();sources={p:sha(S/p)for p in names if(S/p).is_file()}
out=dict(stage=args.stage,commit=command('git','-C',str(S),'rev-parse','HEAD'),tree=command('git','-C',str(S),'rev-parse','HEAD^{tree}'),status=command('git','-C',str(S),'status','--porcelain'),trackedSourceSHA256=sources,platform=platform.platform(),compiler=command('g++','--version'),python=command('python3','--version'))
target=E/f'source-stage-{args.stage}.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
if args.stage=='control44':
 for label,root in [('native',Path('/workspace/b4a-native-build')),('wasm',Path('/workspace/b4a-wasm-build'))]:
  for name in ['compile_commands.json','CMakeCache.txt']:
   p=E/f'{label}-{name}';assert not p.exists();shutil.copyfile(root/name,p)
 shutil.copyfile('/workspace/b4a-configure.log',E/'configure-native-initial.log')
 shutil.copyfile('/workspace/b4a-webkit.sh',E/'webkit-launcher.sh')
 shutil.copyfile(S/'cmake/dependencies.cmake',E/'upstream-dependencies.cmake')
