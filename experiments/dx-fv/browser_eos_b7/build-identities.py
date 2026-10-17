"""Seal separately named generated artifacts and actual compiler/linker provenance."""
import hashlib,json,subprocess,sys,platform,importlib.metadata
from pathlib import Path
B=Path(__file__).resolve().parent;W=Path('/workspace/b7-work');E=B/'evidence'
ids={'control':'rebuiltB4C','candidate':'gateA','control-diagnostic':'diagnosticB4C','candidate-diagnostic':'diagnosticGateA'}
out={}
for label,id in ids.items():
 p=B/'vendor'/label
 if not p.exists():continue
 js,wasm=p/'coolprop.js',p/'coolprop.wasm'
 out[id]=dict(id=id,label=label,jsPath=str(js.relative_to(B)),wasmPath=str(wasm.relative_to(B)),jsSHA256=hashlib.sha256(js.read_bytes()).hexdigest(),wasmSHA256=hashlib.sha256(wasm.read_bytes()).hexdigest(),jsBytes=js.stat().st_size,wasmBytes=wasm.stat().st_size)
target=E/('artifacts-with-diagnostics.json' if 'diagnosticGateA' in out else 'artifacts.json')
if '--versions-only' in sys.argv:
 assert json.loads(target.read_text())==out
else:
 assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
if not (E/'build-versions.json').exists():
 commands={}
 for name,cmd in [('emcc',[str(W/'emsdk/upstream/emscripten/emcc'),'--version']),('clang',[str(W/'emsdk/upstream/bin/clang'),'--version']),('wasm-ld',[str(W/'emsdk/upstream/bin/wasm-ld'),'--version']),('cmake',['/workspace/b7-tools/bin/cmake','--version']),('ninja',['/workspace/b7-tools/bin/ninja','--version'])]:
  commands[name]=subprocess.check_output(cmd,text=True)
 emsdk=subprocess.check_output(['git','-C',str(W/'emsdk'),'rev-parse','HEAD'],text=True).strip();assert emsdk=='389a68bc35dcff7ebae4614e1615099dafda00d1'
 assert '4.0.12 (6f625bd62ee64f4f8cd11476774741b961e4a2d5)' in commands['emcc']
 for label in ['control','candidate']:
  cmds=json.loads((E/f'{label}-compile_commands.json').read_text())
  assert all('-ffast-math' not in r['command'] and '-Ofast' not in r['command'] and '-O3' in r['command'] and '-sDISABLE_EXCEPTION_CATCHING=0' in r['command'] for r in cmds)
  commands[label+'-link']=subprocess.check_output(['/workspace/b7-tools/bin/ninja','-C',str(W/'wasm-control'),'-t','commands','coolprop.js'],text=True).splitlines()[-1]
 versions=dict(emsdk=emsdk,commands=commands,platform=platform.platform(),python=platform.python_version(),packages={n:importlib.metadata.version(n) for n in ['cmake','ninja','CoolProp','numpy','playwright']},cpuQuota=Path('/sys/fs/cgroup/cpu.max').read_text().strip(),memoryLimit=Path('/sys/fs/cgroup/memory.max').read_text().strip())
 (E/'build-versions.json').write_text(json.dumps(versions,indent=2)+'\n')
print(json.dumps(out,indent=2))
