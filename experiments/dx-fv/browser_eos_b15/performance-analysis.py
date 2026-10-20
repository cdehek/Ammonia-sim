"""All samples retained. Statistics are descriptive for this host/workload only."""
from pathlib import Path
import json,statistics,itertools,math
B=Path(__file__).resolve().parent;E=B/'evidence';rows=json.loads((E/'timing-samples.json').read_text())
def stats(a):return {'n':len(a),'median':statistics.median(a),'min':min(a),'max':max(a)}
summary={}
for kind,scope in [('ph','vapor'),('ph','mixed'),('cold','advance'),('warm','advance')]:
 group=[r for r in rows if r['kind']==kind and r['pair']>0];pairs=[]
 for i in range(1,7):
  p={r['variant']:r for r in group if r['pair']==i};a,b=p['control'],p['candidate'];assert a['result']==b['result']or kind!='ph' # solver init timings naturally differ
  if kind!='ph':
   for k in ['seconds','attempts','accepted','rejected','residuals','newtonCorrections','recordResiduals','physicalChecksum']:assert a['result'][k]==b['result'][k],k
  aw,bw=a['scopes'][scope]['wallMS'],b['scopes'][scope]['wallMS'];ac,bc=a['scopes'][scope]['cpuMS'],b['scopes'][scope]['cpuMS'];pairs.append({'pair':i,'order':a['order'],'controlWallMS':aw,'candidateWallMS':bw,'savedWallMS':aw-bw,'improvementPercent':100*(1-bw/aw),'controlCpuMS':ac,'candidateCpuMS':bc,'savedCpuMS':ac-bc,'cpuImprovementPercent':100*(1-bc/ac)})
 percentages=[p['improvementPercent']for p in pairs];bootstrap=sorted(statistics.median(p)for p in itertools.product(percentages,repeat=6));ci=[bootstrap[int(.025*(len(bootstrap)-1))],bootstrap[int(.975*(len(bootstrap)-1))]]
 metrics={v:{'wallMS':stats([r['scopes'][scope]['wallMS']for r in group if r['variant']==v]),'cpuMS':stats([r['scopes'][scope]['cpuMS']for r in group if r['variant']==v]),'rssKiB':stats([r['resources']['maxRSS']for r in group if r['variant']==v]),'heapUsedBytes':stats([r['memoryAfter']['heapUsed']for r in group if r['variant']==v]),'engineConstructionMS':stats([r['engineConstructionMS']for r in group if r['variant']==v]),'modelInitializationMS':stats([r['result'].get('initializationMS',0)for r in group if r['variant']==v])}for v in ['control','candidate']}
 summary[kind+'-'+scope]={'pairs':pairs,'metrics':metrics,'pairedImprovementPercent':stats(percentages),'pairedSavedWallMS':stats([p['savedWallMS']for p in pairs]),'pairedSavedCpuMS':stats([p['savedCpuMS']for p in pairs]),'candidateFasterPairs':sum(p['savedWallMS']>0 for p in pairs),'medianBootstrap95Percent':ci,'bootstrapCaveat':'Exact empirical resampling of six observed pairs; descriptive, weak small-sample inference, not a guarantee or host population interval'}
for f in ['cold','warm']:
 a=next(x for x in rows if x['kind']==f and x['variant']=='count-control');b=next(x for x in rows if x['kind']==f and x['variant']=='count-candidate');assert a['result']['physicalChecksum']==b['result']['physicalChecksum']
# Overhead is separate process-level observation. Includes natural runtime/JIT variation.
overhead={}
for f in ['cold','warm']:
 out={}
 for v in ['control','candidate']:
  primary=[x for x in rows if x['pair']>0 and x['kind']==f and x['variant']==v];count=next(x for x in rows if x['kind']==f and x['variant']=='count-'+v);no=next(x for x in rows if x['kind']=='notimer-'+f and x['variant']==v)
  out[v]={'primaryMedianAdvanceMS':statistics.median(x['scopes']['advance']['wallMS']for x in primary),'countOnlyAdvanceMS':count['scopes']['advance']['wallMS'],'countOnlyRatioToPrimaryMedian':count['scopes']['advance']['wallMS']/statistics.median(x['scopes']['advance']['wallMS']for x in primary),'noInnerTimerProcessWallMS':no['processWallMS'],'primaryMedianProcessWallMS':statistics.median(x['processWallMS']for x in primary),'noInnerTimerPhysicalChecksumEqual':no['result']['physicalChecksum']==primary[0]['result']['physicalChecksum'],'counts':count['counts']}
 overhead[f]=out
(E/'performance-analysis.json').write_text(json.dumps({'primarySamples':36,'supplementalSamples':8,'validPairsPerWorkload':6,'allSamplesRetained':True,'statistics':summary,'overhead':overhead,'limitations':['Fresh-process JIT/GC variation; preliminary v1 vapor outlier retained separately without attribution',f"Final cold candidate slower in {6-summary['cold-advance']['candidateFasterPairs']} of six pairs; no universal speed claim",'No browser performance benchmark, service latency or worker transport measurement','No causal sum of nested diagnostic scopes','GC PerformanceObserver arrays empty at disconnect, not evidence of zero collections; supplemental V8 trace used separately']},indent=2)+'\n')
for k,x in summary.items():print(k,'paired median',x['pairedImprovementPercent']['median'],'saved ms',x['pairedSavedWallMS']['median'],'bootstrap',x['medianBootstrap95Percent'])
