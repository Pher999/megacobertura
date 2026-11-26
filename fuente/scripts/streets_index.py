import json, math, sys, collections, unicodedata, re
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge, unary_union
S=sys.argv[1]
ine=json.load(open(f'/home/claude/work/scripts/inegi_cancun.json')); m=json.load(open(f'/home/claude/work/scripts/mapdata.json'))
AB={'Calle':'C.','Avenida':'Av.','Privada':'Priv.','Andador':'And.','Circuito':'Cto.','Cerrada':'Cda.','Boulevard':'Blvd.','Calzada':'Calz.','Retorno':'Ret.','Prolongación':'Prol.','Peatonal':'Peat.','Carretera':'Carr.','Callejón':'Cjón.'}
groups=collections.defaultdict(list)
for o in ine:
    if o['n'] in ('Ninguno',''): continue
    groups[(AB.get(o['t'],o['t']),o['n'])].append(LineString(o['p']) if len(o['p'])>1 else None)
# --- OpenStreetMap: tramos con nombre donde el INEGI no tiene nombre ---
from shapely.strtree import STRtree
W18=256*2**18; X0=8463*256*8; Y0=14401*256*8
def merc(lng,lat):
    rr=math.radians(lat); return ((lng+180)/360*W18-X0,(1-math.log(math.tan(rr)+1/math.cos(rr))/math.pi)/2*W18-Y0)
inamed=[LineString(o['p']) for o in ine if o['n'] not in('Ninguno','') and len(o['p'])>1]
itree=STRtree(inamed)
OSMAB={'Calle':'C.','Avenida':'Av.','Privada':'Priv.','Andador':'And.','Circuito':'Cto.','Cerrada':'Cda.','Boulevard':'Blvd.','Retorno':'Ret.','Calzada':'Calz.','Prolongación':'Prol.'}
osm=json.load(open('/home/claude/work/data/export.geojson')); nosm=0
for f in osm['features']:
    g=f['geometry']; nm=f['properties'].get('name')
    if g['type']!='LineString' or not nm or f['properties'].get('highway') in('footway','path','cycleway','steps'): continue
    L=LineString([merc(a,b) for a,b in g['coordinates']]); n=max(2,int(L.length/20)); cur=[]; pieces=[]
    for i in range(n+1):
        dpos=i/n*L.length; q=L.interpolate(dpos)
        qa=L.interpolate(max(0,dpos-8)); qb=L.interpolate(min(L.length,dpos+8)); ang=math.atan2(qb.y-qa.y,qb.x-qa.x)
        def parallel(j):
            Lj=inamed[j]
            if Lj.distance(q)>=45: return False
            s=Lj.project(q); a=Lj.interpolate(max(0,s-8)); b=Lj.interpolate(min(Lj.length,s+8)); aj=math.atan2(b.y-a.y,b.x-a.x)
            d=abs((ang-aj+math.pi/2)%math.pi-math.pi/2)
            return d<math.radians(30)
        if any(parallel(j) for j in itree.query(q.buffer(45))):
            if len(cur)>=2: pieces.append(cur)
            cur=[]
        else: cur.append((q.x,q.y))
    if len(cur)>=2: pieces.append(cur)
    m0=re.match(r'^(\w+)\s+(.*)$',nm); tp,rest=(OSMAB[m0.group(1)],m0.group(2)) if m0 and m0.group(1) in OSMAB else ('',nm)
    for pc in pieces:
        if LineString(pc).length>40: groups[(tp,rest)].append(LineString(pc)); nosm+=1
print('tramos agregados desde OSM',nosm)
majors=[(l[0],l[1],l[2]) for l in m['labels']]
def near_major(x,y,exclude):
    best=None
    for n,mx,my in majors:
        if n==exclude: continue
        d=math.hypot(mx-x,my-y)
        if best is None or d<best[0]: best=(d,n)
    return best[1] if best and best[0]<2500 else ''
streets=[]
for (tp,nm),ls in groups.items():
    ls=[l for l in ls if l is not None]
    if not ls: continue
    merged=linemerge(unary_union(ls)) if len(ls)>1 else ls[0]
    parts=list(merged.geoms) if hasattr(merged,'geoms') else [merged]
    # agrupar partes cercanas (<700 u ≈ 380 m) en una sola "zona"
    zones=[]
    for p in sorted(parts,key=lambda l:-l.length):
        c=p.centroid
        for z in zones:
            if math.hypot(z['cx']-c.x,z['cy']-c.y)<1400: z['parts'].append(p); break
        else: zones.append({'cx':c.x,'cy':c.y,'parts':[p]})
    for z in zones:
        geom=[ [ (round(x),round(y)) for x,y in p.simplify(12).coords ] for p in z['parts'] ]
        L=sum(p.length for p in z['parts'])
        if L<60: continue
        nm2=re.sub(r'^(Av\.?|Avenida|Calle|C\.|Blvd\.?|Boulevard|Priv\.?|Privada|Cto\.?|Circuito|Cda\.?|Cerrada|And\.?|Andador|Ret\.?|Retorno)\s+','',nm,flags=re.I)
        label=f'{tp} {nm2}'.strip()
        streets.append({'n':label,'r':near_major(z['cx'],z['cy'],label),'g':geom})
def norm(s): return re.sub(r'[^a-z0-9 ]','',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
print('calles indexadas',len(streets),'nombres',len(groups))
# compactar: coordenadas relativas
out=[]
for s in streets:
    g=[]
    for p in s['g']:
        px=py=0;q=[]
        for x,y in p: q.append(x-px);q.append(y-py);px,py=x,y
        g.append(q)
    out.append([s['n'],s['r'],g])
j=json.dumps(out,ensure_ascii=False,separators=(',',':')); print('bytes',len(j))
open(f'/home/claude/work/scripts/streets.json','w').write(j)
