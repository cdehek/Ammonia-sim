import re,json,hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
original=(root/'v0.1.0.html').read_text()
svg=re.search(r'<svg viewBox="0 0 1060 615".*?</svg>',original,re.S).group(0)
for a,b in [('①','1 ·'),('②','2 ·'),('③','3 ·'),('④','4 ·')]:svg=svg.replace(a,b)
# Ideal separator is drawn on the suction path only in flooded mode.
svg=svg.replace('</svg>','<g id="separator-symbol" style="display:none"><rect x="199" y="315" width="26" height="55" rx="9" fill="#fff" stroke="#3389ac" stroke-width="2"/><path d="M201 349H223" stroke="#3389ac"/><text x="242" y="358" font-size="10" fill="#3389ac">Ideal separator</text></g></svg>')
text=(root/'app.template.html').read_text()
for token,value in {'__CYCLE_SVG__':svg,'__PROPERTY_DATA__':(root/'properties.json').read_text(),'__VALIDATION_DATA__':(root/'validation.json').read_text(),'__ENGINE_CODE__':(root/'engine.js').read_text(),'__APP_CODE__':(root/'app.js').read_text(),'__DYNAMIC_ENGINE__':(root/'dynamic-engine.js').read_text(),'__DYNAMIC_APP__':(root/'dynamic-app.js').read_text(),'__EQUIPMENT_PROFILES__':(root/'equipment-profiles.js').read_text()}.items():
 text=text.replace(token,value)
remaining=re.findall(r'__[A-Z_]+__',text)
if remaining:raise RuntimeError('Unexpanded build placeholders: '+', '.join(sorted(set(remaining))))
output=Path(sys.argv[1]) if len(sys.argv)>1 else root/'dist'
output.mkdir(parents=True,exist_ok=True)
for name in ['index.html','ammonia-lab-v0.4.1.html','ammonia-lab-v0.4.0.html','ammonia-lab-v0.3.0.html','ammonia-lab-v0.2.0.html','ammonia-refrigeration-simulator.html','ammonia-refrigeration.html']:
 p=output/name;p.write_text(text)
(root/'index.html').write_text(text)
print('Built standalone HTML:',len(text.encode()),'bytes')
print('Property grid SHA256:',hashlib.sha256((root/'properties.json').read_bytes()).hexdigest())
