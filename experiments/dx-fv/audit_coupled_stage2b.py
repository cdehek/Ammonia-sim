"""Independent Stage 2B accounting/column audit. No JavaScript solver imports."""
import ast
import copy
import hashlib
import json
import math
import subprocess
import statistics
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
evidence=Path(sys.argv[1]); target=Path(sys.argv[2])
assert not target.resolve().is_relative_to(root)
length=.003/(math.pi*.020**2/4)
tube=math.pi/4*(.024**2-.020**2)*length*7850*.470
fin=1910*math.pi/4*(.080**2-.024**2)*.0002*2700*.900
air=6*.718
at=math.pi*.024*(length-1910*.0002)*50/1000
af=1910*(2*math.pi/4*(.080**2-.024**2)+math.pi*.080*.0002)*50/1000
result=dict(passed=False,rows=0,columnEntries=0,worst=dict(massKg=0.,fluidEnergyKJ=0.,nodeEnergyKJ=0.,combinedEnergyKJ=0.,matrix=0.,exchangeKW=0.),files={})
def near(a,b,budget):
    assert abs(a-b)<budget,(a,b,budget)
def accounting(initial,row,n):
    caps=[tube/n,fin/n]*n+[air]; ledger=row['ledger']; faces=ledger['faces']; heat=ledger['tubeRefrigerantKJ']
    if 'settings' in row:
        assert row['settings']['nonlinearTolerance']==1e-11 and row['settings']['thermalResidualK']==1e-12
        assert row['lastResidual'] is None or row['lastResidual']<=1e-11
    assert len(row['sections'])==n and len(faces)==n+1 and len(heat)==n
    temps=row.get('temperaturesK',[v['temperatureK'] for v in row.get('nodes',[])])
    starttemps=initial.get('temperaturesK',[v['temperatureK'] for v in initial.get('nodes',[])])
    expected=[0.]*(2*n)+[ledger['airLoadKJ']];combined=0.
    for i,(a,b) in enumerate(zip(initial['sections'],row['sections'])):
        dm=b['massKg']-a['massKg']-faces[i]['massKg']+faces[i+1]['massKg']
        du=b['internalEnergyKJ']-a['internalEnergyKJ']-faces[i]['energyKJ']+faces[i+1]['energyKJ']-heat[i]
        near(dm,0,1e-8);near(du,0,1e-6)
        result['worst']['massKg']=max(result['worst']['massKg'],abs(dm));result['worst']['fluidEnergyKJ']=max(result['worst']['fluidEnergyKJ'],abs(du))
        qa,qf,qc=ledger['thermalLinksKJ'][3*i:3*i+3]
        expected[-1]-=qa+qf;expected[2*i]+=qa+qc-heat[i];expected[2*i+1]+=qf-qc
        combined+=b['internalEnergyKJ']-a['internalEnergyKJ']
        if 'fluxes' in row:
            q=.60/n*(temps[2*i]-(b['T']+273.15))
            # Zero-exchange records carry their actual total conductance.
            if sum(row.get('conductancesKWK',[.60/n]*n))==0:q=0
            err=abs(q-row['fluxes']['tubeRefrigerant'][i]);near(err,0,1e-6)
            result['worst']['exchangeKW']=max(result['worst']['exchangeKW'],err)
    for c,a,b,budget in zip(caps,starttemps,temps,expected):
        de=c*(b-a);residual=de-budget;near(residual,0,1e-6)
        result['worst']['nodeEnergyKJ']=max(result['worst']['nodeEnergyKJ'],abs(residual));combined+=de
    combined-=faces[0]['energyKJ']-faces[-1]['energyKJ']+ledger['airLoadKJ'];near(combined,0,1e-6)
    result['worst']['combinedEnergyKJ']=max(result['worst']['combinedEnergyKJ'],abs(combined));result['rows']+=1
for p in sorted(evidence.glob('*.json')):
    if p==target or '.failure.' in p.name or '.partial.' in p.name:continue
    r=json.loads(p.read_text());result['files'][p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    if p.name=='smoke.json':
        for c in r:
            for row in c['rows'][1:]:accounting(c['rows'][0],row,9)
    if isinstance(r,dict) and r.get('mode') in ('compare','extra'):
        assert r['passed']
        for run in r['runs']:
            for row in run['rows']:accounting(run['initial'],row,r['sectionCount'])
    if isinstance(r,dict) and r.get('stage')=='2A' and 'runs' in (r.get('cases') or [{}])[0]:
        assert r['passed']
        for c in r['cases']:
            for run in c['runs']:
                for row in run['rows']:accounting(run['initial'],row,r['sectionCount'])
    if isinstance(r,dict) and r.get('mode') in ('columns','geometry'):
        assert r['passed']
        for g in r['geometry']:
            for name,value in [('tube',tube),('fin',fin),('air',air)]:near(g['capacityTotals'][name],value,1e-12)
        a,b=r['nonuniform'];
        for key in ('massKg','internalEnergyKJ'):near(a['record']['totals'][key],b['record']['totals'][key],1e-10)
        near(sum(a['energies']),sum(b['energies']),1e-10)
        for capture in r.get('columns',[]):
            n=capture['sectionCount'];caps=[tube*((i+1)/n-i/n) if k==0 else fin*((i+1)/n-i/n) for i in range(n) for k in (0,1)]+[air]
            context={};gtr=sum(capture['spec']['conductancesKWK'])
            for event in capture['work']['diagnostics']:
                if event['type']=='iteration' and event['iteration']==0:context=event['context']
                if event['type']!='exact-thermal-column':continue
                assert len(context['labels'])==len(context['physicalScales'])==4*n+1
                for c,scale in zip(caps,context['physicalScales'][2*n:]):near(scale,.1*c,1e-13)
                gamma=2-math.sqrt(2);weight=context['stageWeight'];seconds=context['stageSeconds']
                if capture['method']=='backward-euler':near(weight,1.,1e-15);near(seconds,capture['dt'],1e-15)
                elif weight==.5:near(seconds,gamma*capture['dt'],1e-15)
                else:near(weight,(1-gamma)/(2-gamma),1e-15);near(seconds,capture['dt'],1e-15)
                col=event['column']-2*n; dE=[0.]*(2*n+1);dE[col]=1.;dt=[v/c for v,c in zip(dE,caps)];rates=[0.]*(2*n+1);fluid=[0.]*n
                # Apply signed thermal incidence to a unit energy perturbation.
                for i in range(n):
                    fraction=(i+1)/n-i/n
                    for f,t,g in [(2*n,2*i,at*fraction),(2*n,2*i+1,af*fraction),(2*i+1,2*i,2*fraction)]:
                        q=g*(dt[f]-dt[t]);rates[f]-=q;rates[t]+=q
                    q=gtr/n*dt[2*i];rates[2*i]-=q;fluid[i]+=q
                tau=context['stageSeconds']*context['stageWeight'];unscaled=[v for q in fluid for v in (0.,-tau*q)]+[v-tau*f for v,f in zip(dE,rates)]
                expected=[v/s for v,s in zip(unscaled,context['physicalScales'])]
                assert len(expected)==4*n+1
                for a,b in zip(expected,event['values']):
                    err=abs(a-b);near(err,0,1e-13);result['worst']['matrix']=max(result['worst']['matrix'],err);result['columnEntries']+=1
                near(sum(unscaled[1:2*n:2])+sum(unscaled[2*n:]),1.,1e-13)
# Reuse only the established independently written Python growth-law verifier.
# It has no section-count dependence and imports no JavaScript implementation.
result['regrowth']=[]
observed=evidence/'nine-observed.json';matrix=evidence/'nine-compare.json'
if observed.exists() and matrix.exists():
    observations=json.loads(observed.read_text());comparison=json.loads(matrix.read_text());assert observations['passed'] and comparison['passed']
    original=root/'experiments/dx-fv/audit_roadmap_a2.py';tree=ast.parse(original.read_text())
    selected=[v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name in ('close','attempts','replay')];assert len(selected)==3
    namespace={'math':math};exec(compile(ast.Module(body=selected,type_ignores=[]),str(original),'exec'),namespace)
    for item in observations['runs']:
        run=next(v for v in comparison['runs'] if v['choice']==item['choice'] and v['name']==item['name'] and v['tolerance']==1e-6)
        for key in ('stateHash','recordHash','propertyCalls','work'):assert run[key]==item[key]
        assert item['stats']['otherFailedSolves']==0
        assert item['acceptedHistory']==item['work']['acceptedTrials'] and item['rejectedHistory']==item['work']['rejectedTrials']
        state=copy.deepcopy(run['state']);state['trace']=[];state['rejectionTrace']=[]
        for a in item['stats']['attempts']:
            failure=a['failure'];kind=failure['kind'] if failure else a['reason']
            if kind:state['rejectionTrace'].append(dict(seconds=a['seconds'],trialSeconds=a['dt'],kind=kind,error=a['error']))
            else:state['trace'].append(dict(startSeconds=a['seconds'],endSeconds=a['seconds']+a['dt'],trialSeconds=a['dt'],error=a['error']))
        assert len(state['trace'])==run['work']['acceptedTrials'];assert len(state['rejectionTrace'])==run['work']['rejectedTrials']
        # These are diagnostic comparators assembled from real observed decisions;
        # no trace is inserted into the integration state or used to select a step.
        stats=namespace['replay']({'name':item['name']},item['choice'],{'state':state,'rows':run['rows']})
        result['regrowth'].append(dict(name=item['name'],choice=item['choice'],**stats))
# Same-mesh EOS comparisons are separate from cross-mesh spatial differences.
def reference_budget(sample,n):
    # Triangle bounds independently enforce global as well as per-cell/node
    # budgets from the reference's independently integrated signed ledgers.
    for key,factor,budget in [('maximumMassResidualKg',n,1e-8),('maximumFluidEnergyResidualKJ',n,1e-6),('maximumThermalResidualKJ',2*n+1,1e-6),('combinedEnergyResidualKJ',1,1e-6)]:
        assert factor*abs(sample[key])<budget,(n,key,sample[key])
    for cell in sample['sections']:
        assert all(math.isfinite(cell[k]) for k in ('p','h','T','rho','u')) and cell['rho']>0
        assert cell['quality'] is None or 0<=cell['quality']<=1
    assert all(math.isfinite(v) for v in sample['temperaturesK'])
result['directEOS']=[]
for n in (5,9):
    source=evidence/f'{"five" if n==5 else "nine"}-compare.json'
    if not source.exists():continue
    matrix=json.loads(source.read_text());assert matrix['passed']
    reference=json.loads((root/'experiments/dx-fv/coupled-stage2b-reference.json').read_text()) if n==9 else json.loads((root/'experiments/dx-fv/coupled-reference.json').read_text())
    references=[('frozen',reference)]
    fresh=evidence/f'{"five" if n==5 else "nine"}-fresh-reference.json'
    if fresh.exists():references.append(('fresh',json.loads(fresh.read_text())))
    for source_kind,reference in references:
        for run in matrix['runs']:
            if run['tolerance']!=1e-8:continue
            case=next(c for c in reference['cases'] if c['name']==run['name']);lo,hi=case['runs'];error=dict(p=0.,h=0.,T=0.,thermalK=0.,eventSeconds=0.)
            own=dict(p=0.,h=0.,T=0.,thermalK=0.,eventSeconds=0.)
            assert not lo['domainEventsSeconds'] and not hi['domainEventsSeconds'] and len(run['rows'])==len(lo['samples'])==len(hi['samples'])
            for row,a,b in zip(run['rows'],lo['samples'],hi['samples']):
                assert row['seconds']==a['seconds']==b['seconds']
                reference_budget(a,n);reference_budget(b,n)
                for u,v,w in zip(row['sections'],a['sections'],b['sections']):
                    for key in ('p','h','T'):
                        error[key]=max(error[key],abs(u[key]-w[key]));own[key]=max(own[key],abs(v[key]-w[key]))
                error['thermalK']=max(error['thermalK'],*(abs(u['temperatureK']-v) for u,v in zip(row['nodes'],b['temperaturesK'])))
                own['thermalK']=max(own['thermalK'],*(abs(u-v) for u,v in zip(a['temperaturesK'],b['temperaturesK'])))
            events=[e['seconds'] for e in run['state']['events'] if e['section']==n-1 and e['boundary']=='vapor']
            assert len(events)==len(lo['terminalSaturationEventsSeconds'])==len(hi['terminalSaturationEventsSeconds'])
            error['eventSeconds']=max([0.]+[abs(a-b) for a,b in zip(events,hi['terminalSaturationEventsSeconds'])])
            own['eventSeconds']=max([0.]+[abs(a-b) for a,b in zip(lo['terminalSaturationEventsSeconds'],hi['terminalSaturationEventsSeconds'])])
            for key,budget in [('p',1e-4),('h',.05),('T',.01),('thermalK',.01),('eventSeconds',.001)]:assert error[key]<budget,(n,run['choice'],run['name'],error)
            for key,budget in [('p',1e-7),('h',1e-4),('T',1e-4),('thermalK',1e-5),('eventSeconds',1e-6)]:assert own[key]<budget,(n,run['name'],own)
            result['directEOS'].append(dict(sectionCount=n,reference=source_kind,choice=run['choice'],name=run['name'],errors=error,referenceRefinement=own))
result['freshReferenceReproduction']=[]
for n in (5,9):
    original=root/'experiments/dx-fv/coupled-reference.json' if n==5 else root/'experiments/dx-fv/coupled-stage2b-reference.json'
    fresh=evidence/f'{"five" if n==5 else "nine"}-fresh-reference.json'
    if fresh.exists():
        a,b=json.loads(original.read_text()),json.loads(fresh.read_text());assert len(a['cases'])==len(b['cases'])==5
        if n==9:assert a['cases']==json.loads((evidence/'nine-reference.json').read_text())['cases']==b['cases']
        if n==5:assert original.read_bytes()==fresh.read_bytes()
        result['freshReferenceReproduction'].append(dict(sectionCount=n,physicalCasesExactlyEqual=a['cases']==b['cases'],emittedWarnings=b.get('emittedWarnings',[])))
result['EOSSpatial']=[]
if (evidence/'nine-reference.json').exists():
    five=json.loads((root/'experiments/dx-fv/coupled-reference.json').read_text());nine=json.loads((evidence/'nine-reference.json').read_text())
    for a,b in zip(five['cases'],nine['cases']):
        assert a['name']==b['name'];pairs=[]
        for x,y in zip(a['runs'][1]['samples'],b['runs'][1]['samples']):
            assert x['seconds']==y['seconds']
            def totals(row,n):
                # Original cases never enter subcooled liquid; EOS Q=None denotes
                # vapor in these stored samples. Density/U are direct EOS values.
                return dict(massKg=sum(v['rho']*.003/n for v in row['sections']),internalEnergyKJ=sum(v['rho']*.003/n*v['u'] for v in row['sections']),liquidMassKg=sum(v['rho']*.003/n*(1-v['quality']) for v in row['sections'] if v['quality'] is not None))
            pairs.append(dict(seconds=x['seconds'],five=totals(x,5),nine=totals(y,9)))
        result['EOSSpatial'].append(dict(name=a['name'],rows=pairs))
# New operating cases retain the same numerical and EOS budgets.
result['extraQualification']=[]
for n in (5,9):
    source=evidence/f'{"five" if n==5 else "nine"}-extra.json'
    if not source.exists():continue
    matrix=json.loads(source.read_text());assert matrix['passed']
    for name in sorted(set(v['name'] for v in matrix['runs'])):
        runs=sorted([v for v in matrix['runs'] if v['name']==name],key=lambda v:-v['tolerance']);assert [v['tolerance'] for v in runs]==[1e-6,1e-7,1e-8]
        errors=[]
        for run in runs[:2]:
            err=dict(p=0.,h=0.,T=0.,thermalK=0.,eventSeconds=0.)
            for row,ref in zip(run['rows'],runs[2]['rows']):
                assert row['seconds']==ref['seconds']
                for a,b in zip(row['sections'],ref['sections']):
                    for key in ('p','h','T'):err[key]=max(err[key],abs(a[key]-b[key]))
                err['thermalK']=max(err['thermalK'],*(abs(a['temperatureK']-b['temperatureK']) for a,b in zip(row['nodes'],ref['nodes'])))
            a,b=run['state']['events'],runs[2]['state']['events'];assert len(a)==len(b)
            for x,y in zip(a,b):
                assert all(x[k]==y[k] for k in ('section','boundary','direction'));err['eventSeconds']=max(err['eventSeconds'],abs(x['seconds']-y['seconds']))
            temp=.01 if run['tolerance']==1e-6 else .001
            for key,budget in [('p',5e-5),('h',.05),('T',temp),('thermalK',temp),('eventSeconds',.001)]:assert err[key]<budget,(n,name,run['tolerance'],err)
            errors.append(err)
        label='nonuniform' if name=='nonuniform' else 'extended';refpath=evidence/f'{label}-{"five" if n==5 else "nine"}-reference.json'
        if refpath.exists():
            reference=json.loads(refpath.read_text())['cases'][0];lo,hi=reference['runs'];assert not lo['domainEventsSeconds'] and not hi['domainEventsSeconds'];assert len(hi['samples'])==len(runs[2]['rows'])
            error=dict(p=0.,h=0.,T=0.,thermalK=0.,eventSeconds=0.);own=dict(error)
            for row,a,b in zip(runs[2]['rows'],lo['samples'],hi['samples']):
                assert row['seconds']==a['seconds']==b['seconds']
                reference_budget(a,n);reference_budget(b,n)
                for u,v,w in zip(row['sections'],a['sections'],b['sections']):
                    for key in ('p','h','T'):error[key]=max(error[key],abs(u[key]-w[key]));own[key]=max(own[key],abs(v[key]-w[key]))
                error['thermalK']=max(error['thermalK'],*(abs(u['temperatureK']-v) for u,v in zip(row['nodes'],b['temperaturesK'])))
                own['thermalK']=max(own['thermalK'],*(abs(u-v) for u,v in zip(a['temperaturesK'],b['temperaturesK'])))
                for k,budget in [('maximumMassResidualKg',1e-8),('maximumFluidEnergyResidualKJ',1e-6),('maximumThermalResidualKJ',1e-6),('combinedEnergyResidualKJ',1e-6)]:assert abs(b[k])<budget
            events=[v['seconds'] for v in runs[2]['state']['events'] if v['section']==n-1 and v['boundary']=='vapor'];assert len(events)==len(lo['terminalSaturationEventsSeconds'])==len(hi['terminalSaturationEventsSeconds'])
            error['eventSeconds']=max([0.]+[abs(a-b) for a,b in zip(events,hi['terminalSaturationEventsSeconds'])]);own['eventSeconds']=max([0.]+[abs(a-b) for a,b in zip(lo['terminalSaturationEventsSeconds'],hi['terminalSaturationEventsSeconds'])])
            for k,budget in [('p',1e-4),('h',.05),('T',.01),('thermalK',.01),('eventSeconds',.001)]:assert error[k]<budget,(n,name,error)
            for k,budget in [('p',1e-7),('h',1e-4),('T',1e-4),('thermalK',1e-5),('eventSeconds',1e-6)]:assert own[k]<budget,(n,name,own)
            result['extraQualification'].append(dict(sectionCount=n,name=name,temporal=errors,directEOS=error,referenceRefinement=own))
result['performance']=None
performance=evidence/'performance.json'
if performance.exists():
    perf=json.loads(performance.read_text());assert perf['passed'] and len(perf['blocks'])>=5
    def distribution(values):
        return dict(samples=values,median=statistics.median(values),mean=statistics.mean(values),minimum=min(values),maximum=max(values),standardDeviation=statistics.stdev(values),coefficientOfVariation=statistics.stdev(values)/statistics.mean(values))
    records={};totals={}
    for warm in perf['warmup']:
        key=(warm['sectionCount'],warm['choice'],warm['name']);assert key not in records
        samples=[]
        for block in perf['blocks']:
            item=next(v for v in block if (v['sectionCount'],v['choice'],v['name'])==key)
            for k in ('stateHash','recordHash','work','propertyCalls'):assert item[k]==warm[k]
            samples.append(item['elapsedMS'])
        matrix=json.loads((evidence/f'{"five" if key[0]==5 else "nine"}-compare.json').read_text());qualified=next(v for v in matrix['runs'] if v['name']==key[2] and v['choice']==key[1] and v['tolerance']==1e-6)
        for k in ('stateHash','recordHash','work','propertyCalls'):assert qualified[k]==warm[k]
        records[key]=dict(sectionCount=key[0],choice=key[1],name=key[2],milliseconds=distribution(samples),work=warm['work'],propertyCalls=warm['propertyCalls'])
    for n in (5,9):
        for choice in ('baseline','exact','fd-aware','exact-aware'):
            samples=[sum(v['elapsedMS'] for v in block if v['sectionCount']==n and v['choice']==choice) for block in perf['blocks']]
            rows=[v for key,v in records.items() if key[:2]==(n,choice)]
            totals[(n,choice)]=dict(sectionCount=n,choice=choice,milliseconds=distribution(samples),work={k:sum(v['work'][k] for v in rows) for k in rows[0]['work']},propertyCalls={k:sum(v['propertyCalls'][k] for v in rows) for k in rows[0]['propertyCalls']})
    comparisons=[]
    for n in (5,9):
        for choice in ('exact','fd-aware','exact-aware'):
            a,b=totals[(n,choice)],totals[(n,'baseline')];ratios=[u/v for u,v in zip(a['milliseconds']['samples'],b['milliseconds']['samples'])]
            comparisons.append(dict(sectionCount=n,choice=choice,relativeTo='baseline',pairedRatio=distribution(ratios)))
    for choice in ('baseline','exact','fd-aware','exact-aware'):
        ratios=[u/v for u,v in zip(totals[(9,choice)]['milliseconds']['samples'],totals[(5,choice)]['milliseconds']['samples'])]
        comparisons.append(dict(choice=choice,sectionCount=9,relativeTo='five sections',pairedRatio=distribution(ratios)))
    result['performance']=dict(hardware=perf['hardware'],fixtures=list(records.values()),totals=list(totals.values()),comparisons=comparisons)
# Every pre-existing tracked file except the two authorized coupled files is immutable.
base='be9eb35a4ddf5098e685182f8104685127c6a6ee';allowed={'experiments/dx-fv/coupled-model.cjs','experiments/dx-fv/coupled-implicit.cjs'}
files=subprocess.check_output(['git','ls-tree','-r','--name-only',base],cwd=root,text=True).splitlines()
for f in files:
    if f in allowed:continue
    old=subprocess.check_output(['git','show',base+':'+f],cwd=root)
    current=(root/f).read_bytes()
    if f=='experiments/dx-fv/coupled-test.cjs':
        assert current==old.replace(b'.create({sectionCount:9})',b'.create({sectionCount:17})'),'Only the approved mesh assertion may change'
    else: assert current==old,'Protected file changed: '+f
result['protectedFilesVerified']=len(files)-len(allowed)-1
result['approvedMeshAssertionVerified']=True
if '--complete' in sys.argv:
    required=['baseline-history.json','geometry.json','columns.json','baseline.json','five-frozen.json','nine-frozen.json','five-fresh.json','five-compare.json','nine-compare.json','five-extra.json','nine-extra.json','nine-observed.json','nine-rules.json','nine-orders.json','nine-domain.json','performance.json','spatial.json']
    for n in (5,9):
        for choice in ('baseline','exact','fd-aware','exact-aware'):
            required += [f'controls-{n}-{choice}.json',f'browser-{n}-{choice}.json',f'memory-{n}-{choice}.json']
    required += [f'nine-domain-{c}.json' for c in ('exact','fd-aware','exact-aware')]
    for name in required:
        item=json.loads((evidence/name).read_text());assert item['passed'],name
    assert len(json.loads((evidence/'baseline.json').read_text())['comparisons'])==20
    histories=json.loads((evidence/'baseline-history.json').read_text())['comparisons'];assert len(histories)==5
    assert all(v['acceptedHistory']==v['work']['acceptedTrials'] and v['rejectedHistory']==v['work']['rejectedTrials'] for v in histories)
    for n in ('five','nine'):assert len(json.loads((evidence/f'{n}-compare.json').read_text())['runs'])==60
    assert len(result['directEOS'])==80 and len(result['extraQualification'])==4 and len(result['regrowth'])==20
    assert len(json.loads((evidence/'spatial.json').read_text())['spatial'])==7
    for name,count in [('regression-queue.json',21),('compatibility-queue.json',12),('reference-queue.json',8),('browser-queue.json',14),('post-numerical-queue.json',13),('fresh-regression-queue.json',6)]:
        queue=json.loads((evidence/name).read_text());assert len(queue)==count,(name,len(queue));assert all(v['returncode']==0 for v in queue)
    perf=json.loads((evidence/'performance.json').read_text());assert len(perf['blocks'])>=5 and len(perf['warmup'])==40
    assert all(len(block)==40 for block in perf['blocks'])
    result['completeQualification']=True
result['passed']=True;target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
