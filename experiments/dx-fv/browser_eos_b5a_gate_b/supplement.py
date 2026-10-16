"""Fresh EOS checks of refused algebraic mixtures, provenance and deterministic replay."""
import hashlib,json,sys
from pathlib import Path
import CoolProp
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));import binary64 as f
m=f.ref;m.precision(90);mp=m.mp;E=m.E
def run():
    original=json.loads((E/'four-case-reproduction-and-controls.json').read_text())['rows'];rows=[]
    for r in original:
        if 'refusedAlgebraicMixtureAudit'not in r:continue
        a=r['refusedAlgebraicMixtureAudit'];l,v=[m.hp.eos(mp.mpf(z['rho']),mp.mpf(a['T']))for z in a['endpoints']]
        q=mp.mpf(a['Q']);d,u=m.exact(dict(input=r['originalInput']));vol=(1-q)/l['rho']+q/v['rho'];um=(1-q)*l['u']+q*v['u']
        rows.append(dict(key=r['key'],label='Fresh 90-digit EOS at separately reconstructed QT endpoint coordinates and traced invalid Q, not failed-backend cache; QT pressure getter equality alone is not EOS equality',
            pResidual=l['p']-v['p'],muResidual=l['g']-v['g'],volumeResidual=vol-1/mp.mpf(d),uResidual=um-mp.mpf(u),physicalQuality=bool(0<=q<=1)))
    repeated=[]
    for r in json.loads((E/'binary64-results.json').read_text())['rows']:
        if r['case']['label']!='exact saved inventory':continue
        for a in r['attempts']:
            x=f.solve(r['case']['rho'],r['case']['u'],a['initial'],a['result']['stopPolicy']);y=dict(a['result']);x.pop('seconds');y.pop('seconds')
            repeated.append(dict(key=r['case']['key'],seed=a['seedShiftK'],policy=a['result']['stopPolicy'],identical=x==y))
    assert all(r['identical']for r in repeated)
    wheels={str(p.relative_to(Path(CoolProp.__file__).parent)):hashlib.sha256(p.read_bytes()).hexdigest()for p in Path(CoolProp.__file__).parent.rglob('*.so')}
    m.write('supplement.json',dict(refusedMixtureIndependentEOS=rows,binary64SeparateProcessRepeat=repeated,wheelVersion=CoolProp.__version__,wheelGit=CoolProp.__gitrevision__,wheelBinariesSHA256=wheels,
        setupNotes=['Initial sandbox clone failed to reach configured proxy; succeeded with tool network access enabled; no proxy/policy change.',
        'Read-only GitHub connector file lookup at an incomplete repository path returned 404; local clone provided required files.',
        'Pip warned about unwritable cache and used uncached downloads; installed only in /workspace/b5-tools.',
        'Initial coordinate-grid normalized and de-normalized state coordinates, potentially collapsing adjacent samples. Retained as coordinate-grid-initial-scaled-roundtrip.json; corrected coordinate-grid.json evaluates exact adjacent coordinates directly. Equilibrium solver data unchanged.'],
        policy='No new numerical acceptance tolerance; all original unresolved phase classifications retained'))
if __name__=='__main__':run()
