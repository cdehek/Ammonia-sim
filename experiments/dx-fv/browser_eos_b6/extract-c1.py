import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent
src=(X/'browser_eos_b5b_c1/a2-tests.cjs').read_text()
# Retain exact existing blocks and assertions, select one existing fault kind.
prefix=src[:src.index(' try{\n let lineSearchFailure;')]
start=src.index(' // Supported success with real properties')
end=src.index(' // Preserve errors thrown while preparing')
body=src[start:end].replace("['numerical','boundary','real-browser-boundary','unsupported','legacy-domain-text','untyped-domain','line-search-wrapped']","['real-browser-boundary']")
thermal=src[src.index(' // Genuine independently rechecked'):src.index(' // Independently recheck a false thermal proof')]
subset=prefix+' try{\n let lineSearchFailure;\n'+body+thermal+" return {passed:true,rows,fullA2Qualification:false};\n }catch(error){error.a2Partial={rows};throw error;}\n}\nmodule.exports={runA2};\n"
(B/'a2-subset.cjs').write_text(subset)
receipt=dict(source='browser_eos_b5b_c1/a2-tests.cjs',sourceSHA256=hashlib.sha256(src.encode()).hexdigest(),subsetSHA256=hashlib.sha256(subset.encode()).hexdigest(),selection='Exact supported pair, real-browser-boundary transient/persistent loop, and two thermal boundary blocks. Fault-kind list filtered only. Run once with original boundary failure and once with actual PT failure under labeled dispatch injection. No classification/solver semantics changed.',candidateFiles=sorted(p.name for p in (X/'browser_eos_b5b_c1/a2').glob('*.cjs')),controlFiles=sorted(p.name for p in (X/'browser_eos_backend/accepted').glob('*.cjs')))
(B/'evidence/c1-harness-provenance.json').write_text(json.dumps(receipt,indent=2)+'\n')
for engine in ['chromium','webkit']:
 p=X/f'browser_eos_b5b_c1/evidence/{engine}-replay.json';d=json.loads(p.read_text())
 subset=dict(source=str(p.relative_to(X)),sourceSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),rows=[dict(key=r['key'],error=r['error']) for r in d['rows']],extraction='Verbatim seven errors only; unused legacy evidence has Python -Infinity tokens that strict browser JSON rejects. No numerical source values replaced.')
 (B/f'evidence/c1-original-{engine}-subset.json').write_text(json.dumps(subset,indent=2,allow_nan=False)+'\n')
