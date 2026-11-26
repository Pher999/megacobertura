import json, math, re, base64, sys, collections
from pyproj import Transformer
from shapely.geometry import LineString
S=sys.argv[1]
T=Transformer.from_crs(32616,4326,always_xy=True)
W18=256*2**18; X0=8463*256*8; Y0=14401*256*8; SPAN=1792*4*8
def merc(lng,lat):
    r=math.radians(lat); return ((lng+180)/360*W18-X0, (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*W18-Y0)
def simp(pts,tol=3):
    if len(pts)<3: return pts
    return list(LineString(pts).simplify(tol,preserve_topology=False).coords)
# ---- DWG
d=json.load(open(f'{S}/work/dwg.json'))
skip={'COTAS','COTAS POLIGONOS','TICS','PARAM','CUADRO','PIE-PLANO','PIE-DE-PLANO','DEFPOINTS','EJES-VIALIDAD','POINTS','CORDS','POINT-PARAM'}
dwg=[]
SH=json.load(open(f'{S}/work/shifts.json'))
def shift(lay):
    r=SH.get(lay)
    return (r['dx'],r['dy']) if r and r['n']>=5000 else (0,-208)
for lay,ss in d['segs'].items():
    if lay in skip: continue
    dx,dy=shift(lay)
    for s in ss:
        xs,ys=zip(*s)
        if min(xs)<505000 or min(ys)<2330000: continue
        xs=[x+dx for x in xs]; ys=[y+dy for y in ys]
        lo,la=T.transform(xs,ys); p=[merc(a,b) for a,b in zip(lo,la)]
        p=simp(p,2)
        if len(p)>=2 and max(math.dist(p[0],q) for q in p)>4: dwg.append(p)
# footprint grid (cells of 64 units ~36 m)
C=64; fp=set()
for p in dwg:
    for (x1,y1),(x2,y2) in zip(p,p[1:]):
        n=max(1,int(math.dist((x1,y1),(x2,y2))/C*2))
        for i in range(n+1):
            fp.add((int((x1+(x2-x1)*i/n)//C),int((y1+(y2-y1)*i/n)//C)))
fp2=set()
for (a,b) in fp:
    for dx in range(-2,3):
        for dy in range(-2,3): fp2.add((a+dx,b+dy))
# fill: a cell is inside if footprint dense nearby -> use fp2 as is
inside=lambda x,y:False
# SM labels
sm=[]
for lay,txt,x,y,rot in d['texts']:
    if x<505000: continue
    x+=shift(lay)[0]; y+=shift(lay)[1]
    m=re.match(r'^\s*S\.?\s*M\.?\s*-?\s*(\d{1,3})\s*$',txt or '',re.I)
    if m:
        lo,la=T.transform(x,y); sm.append((int(m.group(1)),*merc(lo,la)))
# ---- OSM
o=json.load(open(f'{S}/osmin/export.geojson'))
MAJOR={'motorway','trunk','primary','secondary','tertiary'}
major=[];minor=[];names=collections.defaultdict(list);mnames=collections.defaultdict(list)
for f in o['features']:
    g=f['geometry']
    if g['type']!='LineString': continue
    h=f['properties'].get('highway',''); base=h.replace('_link','')
    p=[merc(a,b) for a,b in g['coordinates']]
    if base in MAJOR and not h.endswith('_link'):
        p=simp(p,3); major.append((p,{'motorway':3,'trunk':3,'primary':3,'secondary':2,'tertiary':1}[base]))
        nm=f['properties'].get('name')
        if nm: names[nm].append(p)
    else:
        nm=f['properties'].get('name')
        if nm and h!='service': mnames[nm].append(p)
        # drop parts inside DWG footprint
        run=[]
        for q in p:
            if inside(*q):
                if len(run)>=2: minor.append(simp(run,3))
                run=[]
            else: run.append(q)
        if len(run)>=2: minor.append(simp(run,3))
# road labels: for each name, pick points spaced >=1500 units (~800m) along long segments
labels=[]
for nm,ps in names.items():
    nm=re.sub(r'^Avenida ','Av. ',nm); nm=re.sub(r'^Boulevard ','Blvd. ',nm)
    placed=[]
    for p in sorted(ps,key=lambda p:-LineString(p).length):
        L=LineString(p)
        if L.length<300: continue
        for t in [i*1600+800 for i in range(int(L.length//1600)+1)]:
            if t>L.length: break
            pt=L.interpolate(t); a=L.interpolate(max(0,t-40)); b=L.interpolate(min(L.length,t+40))
            if all(math.dist((pt.x,pt.y),q)>1400 for q in placed):
                ang=math.atan2(b.y-a.y,b.x-a.x)
                if ang>math.pi/2: ang-=math.pi
                if ang<-math.pi/2: ang+=math.pi
                placed.append((pt.x,pt.y)); labels.append([nm,round(pt.x),round(pt.y),round(ang,2)])
# ---- encode
def enc(lines):
    out=bytearray(); px=py=0
    def v(n):
        while n>=128: out.append((n&127)|128); n>>=7
        out.append(n)
    zz=lambda n:(n<<1) if n>=0 else ((-n<<1)-1)
    for p in lines:
        p=[(round(x),round(y)) for x,y in p]
        q=[p[0]]+[b for a,b in zip(p,p[1:]) if b!=a]
        if len(q)<2: continue
        v(len(q))
        for x,y in q: v(zz(x-px)); v(zz(y-py)); px,py=x,y
    return base64.b64encode(bytes(out)).decode()
majs={k:enc([p for p,c in major if c==k]) for k in (1,2,3)}
dwg=[];sm=[]
mlabels=[]
for nm,ps in mnames.items():
    nm=re.sub(r'^Calle ','C. ',nm); nm=re.sub(r'^Avenida ','Av. ',nm); nm=re.sub(r'^Retorno ','Ret. ',nm); nm=re.sub(r'^Privada ','Priv. ',nm); nm=re.sub(r'^Cerrada ','Cda. ',nm); nm=re.sub(r'^Andador ','And. ',nm)
    placed=[]
    for p in sorted(ps,key=lambda p:-LineString(p).length):
        L=LineString(p)
        if L.length<120: continue
        for tt in [i*700+350 for i in range(int(L.length//700)+1)]:
            if tt>L.length: break
            pt=L.interpolate(tt); a=L.interpolate(max(0,tt-30)); b=L.interpolate(min(L.length,tt+30))
            if all(math.dist((pt.x,pt.y),q)>600 for q in placed):
                ang=math.atan2(b.y-a.y,b.x-a.x)
                if ang>math.pi/2: ang-=math.pi
                if ang<-math.pi/2: ang+=math.pi
                placed.append((pt.x,pt.y)); mlabels.append([nm,round(pt.x),round(pt.y),round(ang,2)])
data={'mlabels':mlabels,'dwg':enc(dwg),'minor':enc(minor),'maj1':majs[1],'maj2':majs[2],'maj3':majs[3],'labels':labels,'sm':sorted(set(sm))}
json.dump(data,open(f'{S}/work/mapdata.json','w'),ensure_ascii=False,separators=(',',':'))
print('dwg',len(dwg),len(data['dwg']),'minor',len(minor),len(data['minor']),'major',len(major),sum(len(v) for v in majs.values()),'labels',len(labels),'mlabels',len(mlabels),'sm',len(data['sm']))
