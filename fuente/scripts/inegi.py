import shapefile, json, math, sys, collections
from pyproj import CRS, Transformer
S=sys.argv[1]
crs=CRS.from_wkt(open(f'{S}/inegi/conjunto_de_datos/23e.prj').read())
T=Transformer.from_crs(crs,4326,always_xy=True)
r=shapefile.Reader(f'{S}/inegi/conjunto_de_datos/23e',encoding='latin-1')
W18=256*2**18; X0=8463*256*8; Y0=14401*256*8; SPAN=1792*4*8
def merc(lng,lat):
    rr=math.radians(lat); return ((lng+180)/360*W18-X0,(1-math.log(math.tan(rr)+1/math.cos(rr))/math.pi)/2*W18-Y0)
out=[]; tipos=collections.Counter(); muns=collections.Counter()
for sr in r.iterShapeRecords(fields=['CVE_MUN','NOMVIAL','TIPOVIAL','AMBITO']):
    rec=sr.record; 
    if rec['CVE_MUN'] not in ('005','003'): continue  # Benito Juárez, Isla Mujeres (continental)
    pts=sr.shape.points
    lo,la=T.transform([p[0] for p in pts],[p[1] for p in pts])
    m=[merc(a,b) for a,b in zip(lo,la)]
    if max(x for x,y in m)<0 or min(x for x,y in m)>SPAN or max(y for x,y in m)<0 or min(y for x,y in m)>SPAN: continue
    nm=(rec['NOMVIAL'] or '').strip(); tp=(rec['TIPOVIAL'] or '').strip()
    tipos[tp]+=1; muns[rec['CVE_MUN']]+=1
    out.append({'n':nm,'t':tp,'p':[(round(x),round(y)) for x,y in m]})
print(len(out), muns.most_common(), tipos.most_common(15))
print(collections.Counter(o['n'] for o in out).most_common(12))
json.dump(out,open(f'{S}/work/inegi_cancun.json','w'),ensure_ascii=False)
