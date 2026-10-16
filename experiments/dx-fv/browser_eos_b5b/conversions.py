"""Exact rational interpretation of actual binary64 Pa/bar operations."""
import json,math,struct
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
def bits(x):return struct.pack('>d',x).hex()
def rational(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def row(p,label):
    b=p/1e5;back=b*1e5
    return dict(label=label,pPa=p,pBits=bits(p),bar=b,barBits=bits(b),PaAfterRoundTrip=back,roundTripBits=bits(back),exactPa=rational(F(p)),exactBar=rational(F(p)/100000),actualRoundedBar=rational(F(b)),conversionErrorBar=rational(F(b)-F(p)/100000),roundTripErrorPa=rational(F(back)-F(p)),strictPaInside=p<=3500000,strictBarInside=b<=35)
rows=[row(p,n) for n,p in [('one-Pa-ULP-below',math.nextafter(3500000.,-math.inf)),('exact-maximum',3500000.),('one-Pa-ULP-above',math.nextafter(3500000.,math.inf))]]
rows += [row(r['rawDU']['values']['p'],r['key']) for r in json.loads((E/'seven-case-analysis.json').read_text())['rows']]
assert all(r['strictPaInside']==r['strictBarInside'] for r in rows)
(E/'exact-conversions.json').write_text(json.dumps(dict(rows=rows,pressureULPPa=math.ulp(3500000.),unitConvention='1 bar = exactly 100000 Pa; actual operations are binary64.'),indent=2)+'\n')
print('ten Pa/bar exact-rational conversions; no guard-side change')
