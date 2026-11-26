import csv, json, math, re, collections, unicodedata
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
W='/home/claude/work'
W18=256*2**18; X0=8463*256*8; Y0=14401*256*8; SPAN=1792*32; MPU=0.557
def merc(lng,lat):
    r=math.radians(lat); return ((lng+180)/360*W18-X0,(1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*W18-Y0)
def norm(s): return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())).strip()
BAD={'ninguno','sin nombre','s n','sn','no aplica','na','n a','ninguna','sin referencia','domicilio conocido','conocido','',
     'manzana','lote','sin numero'}
# calles con nombre (INEGI + OSM) para saber nombres vecinos
ine=json.load(open(f'{W}/scripts/inegi_cancun.json')); osm=json.load(open(f'{W}/data/export.geojson'))
named=[];nnames=[]
for o in ine:
    if o['n'] not in('Ninguno','') and len(o['p'])>1: named.append(LineString(o['p'])); nnames.append(norm(o['n']))
for f in osm['features']:
    g=f['geometry']
    if g['type']=='LineString' and f['properties'].get('name'):
        named.append(LineString([merc(a,b) for a,b in g['coordinates']])); nnames.append(norm(re.sub(r'^(Calle|Avenida|Privada|Retorno|Andador|Circuito|Cerrada)\s+','',f['properties']['name'])))
ntree=STRtree(named)
runs=[LineString(r) for r in json.load(open(f'{W}/data/unn_runs.json'))]
rtree=STRtree(runs)
TIPO={'CALLE':'C.','AVENIDA':'Av.','PRIVADA':'Priv.','ANDADOR':'And.','RETORNO':'Ret.','CIRCUITO':'Cto.','CERRADA':'Cda.','BOULEVARD':'Blvd.','CALZADA':'Calz.','PROLONGACION':'Prol.','PROLONGACIÓN':'Prol.','CALLEJON':'Cjón.','CALLEJÓN':'Cjón.','PEATONAL':'Peat.'}
votes=collections.defaultdict(collections.Counter); tipos=collections.defaultdict(collections.Counter); used=0; tot=0
with open(f'{W}/data/denue/conjunto_de_datos/denue_inegi_23_.csv',encoding='latin-1') as fh:
    for r in csv.DictReader(fh):
        if r['cve_mun'] not in('005','003'): continue
        try: lat=float(r['latitud']); lng=float(r['longitud'])
        except: continue
        x,y=merc(lng,lat)
        if not(0<=x<SPAN and 0<=y<SPAN): continue
        tot+=1
        nm=r['nom_vial'].strip(); n=norm(nm); n2=re.sub(r'^(calle|avenida|privada|retorno|andador|circuito|cerrada|av|c)\s+','',n)
        if n2 in BAD or len(n2)<2 or re.fullmatch(r'(mz|mza|manzana|lt|lote|sm|smza|supermanzana|region|reg)\b.*',n2): continue
        P=Point(x,y)
        # tramo sin nombre más cercano a <=35 m
        ri=rtree.query(P.buffer(63)); best=None
        for j in ri:
            d=runs[j].distance(P)
            if d<63 and (best is None or d<best[0]): best=(d,j)
        if not best: continue
        # si una calle con nombre igual está cerca, el negocio pertenece a esa calle
        near=[k for k in ntree.query(P.buffer(110)) if named[k].distance(P)<110]
        if any(nnames[k]==n2 or nnames[k].endswith(n2) for k in near): continue
        # si una calle con nombre (cualquiera) está más cerca que el tramo, no votar
        if any(named[k].distance(P)<best[0]*0.8 for k in near): continue
        votes[best[1]][n2]+=1; tipos[(best[1],n2)][r['tipo_vial'].strip().upper()]+=1; used+=1
def pretty(s):
    small={'de','del','la','las','los','y','el','en'}
    w=s.split(); return ' '.join(x if (i>0 and x in small) else (x.upper() if re.fullmatch(r'[ivxlc]+',x) and len(x)<5 else x.capitalize()) for i,x in enumerate(w))
out=[];named_len=0
for j,c in votes.items():
    (nm,k),=c.most_common(1); total=sum(c.values())
    if k>=2 and k/total>=0.66:
        tp=tipos[(j,nm)].most_common(1)[0][0]; label=(TIPO.get(tp,'C.')+' '+pretty(nm))
        pts=[(round(x),round(y)) for x,y in runs[j].coords]
        flat=[];px=py=0
        for a,b in pts: flat+=[a-px,b-py]; px,py=a,b
        out.append([label,flat]); named_len+=runs[j].length
print('negocios en Cancun',tot,'votos usados',used,'tramos con votos',len(votes),'tramos nombrados',len(out),'de',len(runs),'km',round(named_len*MPU/1000))
print([o[0] for o in out[:25]])
json.dump(out,open(f'{W}/scripts/denue_names.json','w'),ensure_ascii=False,separators=(',',':'))
