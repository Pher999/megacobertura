import json, math, base64
from shapely.geometry import LineString
from shapely.strtree import STRtree
W='/home/claude/work'
W18=256*2**18; X0=8463*256*8; Y0=14401*256*8; SPAN=1792*32
def merc(lng,lat):
    r=math.radians(lat); return ((lng+180)/360*W18-X0,(1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*W18-Y0)
osm=json.load(open(f'{W}/data/export.geojson')); ine=json.load(open(f'{W}/scripts/inegi_cancun.json'))
named=[LineString(o['p']) for o in ine if o['n'] not in('Ninguno','') and len(o['p'])>1]
cand=[]
for f in osm['features']:
    g=f['geometry']; h=f['properties'].get('highway','')
    if g['type']!='LineString' or h in('service','footway','path','track','cycleway','steps','pedestrian'): continue
    L=LineString([merc(a,b) for a,b in g['coordinates']])
    if f['properties'].get('name'): named.append(L)
    else: cand.append(L)
tree=STRtree(named); TOL=45  # ~25 m
runs=[]
for L in cand:
    n=max(2,int(L.length/20)); cur=[]
    for i in range(n+1):
        dpos=i/n*L.length; p=L.interpolate(dpos)
        qa=L.interpolate(max(0,dpos-8)); qb=L.interpolate(min(L.length,dpos+8)); ang=math.atan2(qb.y-qa.y,qb.x-qa.x)
        def par(j):
            Lj=named[j]
            if Lj.distance(p)>=TOL: return False
            s=Lj.project(p); a=Lj.interpolate(max(0,s-8)); b=Lj.interpolate(min(Lj.length,s+8)); aj=math.atan2(b.y-a.y,b.x-a.x)
            return abs((ang-aj+math.pi/2)%math.pi-math.pi/2)<math.radians(30)
        near=any(par(j) for j in tree.query(p.buffer(TOL)))
        if not near: cur.append((p.x,p.y))
        else:
            if len(cur)>=2: runs.append(cur)
            cur=[]
    if len(cur)>=2: runs.append(cur)
runs=[list(LineString(r).simplify(3).coords) for r in runs if LineString(r).length>40]
runs=[r for r in runs if all(-500<x<SPAN+500 and -500<y<SPAN+500 for x,y in r)]
def enc(lines):
    out=bytearray(); px=py=0
    def v(n):
        while n>=128: out.append((n&127)|128); n>>=7
        out.append(n)
    zz=lambda n:(n<<1) if n>=0 else ((-n<<1)-1)
    for p in lines:
        p=[(round(x),round(y)) for x,y in p]; q=[p[0]]+[b for a,b in zip(p,p[1:]) if b!=a]
        if len(q)<2: continue
        v(len(q))
        for x,y in q: v(zz(x-px)); v(zz(y-py)); px,py=x,y
    return base64.b64encode(bytes(out)).decode()
json.dump([[ (round(x),round(y)) for x,y in r] for r in runs],open(f'{W}/data/unn_runs.json','w'))
m=json.load(open(f'{W}/scripts/mapdata.json')); m['unn']=enc(runs)
json.dump(m,open(f'{W}/scripts/mapdata.json','w'),ensure_ascii=False,separators=(',',':'))
print('tramos sin nombre',len(runs),'bytes',len(m['unn']))
