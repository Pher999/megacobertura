import json, math, re, sys, collections, numpy as np
from shapely.geometry import LineString
from shapely.strtree import STRtree
S=sys.argv[1]
ine=json.load(open(f'{S}/work/inegi_cancun.json'))
osm=json.load(open(f'{S}/osmin/export.geojson'))
W18=256*2**18; X0=8463*256*8; Y0=14401*256*8
def merc(lng,lat):
    rr=math.radians(lat); return ((lng+180)/360*W18-X0,(1-math.log(math.tan(rr)+1/math.cos(rr))/math.pi)/2*W18-Y0)
MPU=156543.03392*math.cos(math.radians(21.15))/2**18  # metros por unidad
# alineación: distancia de vértices INEGI a la red OSM
osm_lines=[LineString([merc(a,b) for a,b in f['geometry']['coordinates']]) for f in osm['features'] if f['geometry']['type']=='LineString']
tree=STRtree(osm_lines)
ds=[]
import random; random.seed(1)
for o in random.sample(ine,3000):
    for x,y in o['p'][:1]:
        from shapely.geometry import Point
        P=Point(x,y); i=tree.nearest(P); ds.append(osm_lines[i].distance(P)*MPU)
ds=np.array(ds); print('alineacion INEGI vs OSM: mediana %.1f m, p75 %.1f m, p90 %.1f m'%(np.median(ds),np.percentile(ds,75),np.percentile(ds,90)))
# etiquetas desde INEGI
AB={'Calle':'C.','Avenida':'Av.','Privada':'Priv.','Andador':'And.','Circuito':'Cto.','Cerrada':'Cda.','Boulevard':'Blvd.','Calzada':'Calz.','Retorno':'Ret.','Prolongación':'Prol.','Peatonal':'Peat.','Carretera':'Carr.','Callejón':'Cjón.'}
MAJOR_T={'Avenida','Boulevard','Calzada','Carretera','Circunvalación'}
groups=collections.defaultdict(list)
for o in ine:
    if o['n'] in ('Ninguno','','NINGUNO'): continue
    nm2=re.sub(r'^(Av\.?|Avenida|Calle|C\.|Blvd\.?|Boulevard|Priv\.?|Privada|Cto\.?|Circuito|Cda\.?|Cerrada|And\.?|Andador|Ret\.?|Retorno)\s+','',o['n'],flags=re.I)
    label=(AB.get(o['t'],o['t'])+' '+nm2).strip()
    groups[(label,o['t'] in MAJOR_T)].append(o['p'])
def place(ps,gap,minlen,sep):
    # une segmentos con el mismo nombre y coloca etiquetas espaciadas
    from shapely.ops import linemerge
    ml=linemerge([LineString(p) for p in ps if len(p)>1])
    lines=list(ml.geoms) if hasattr(ml,'geoms') else [ml]
    placed=[];res=[]
    for L in sorted(lines,key=lambda l:-l.length):
        if L.length<minlen: continue
        for t in [i*gap+gap/2 for i in range(int(L.length//gap)+1)]:
            if t>L.length: break
            pt=L.interpolate(t); a=L.interpolate(max(0,t-30)); b=L.interpolate(min(L.length,t+30))
            if all(math.dist((pt.x,pt.y),q)>sep for q in placed):
                ang=math.atan2(b.y-a.y,b.x-a.x)
                if ang>math.pi/2: ang-=math.pi
                if ang<-math.pi/2: ang+=math.pi
                placed.append((pt.x,pt.y)); res.append([round(pt.x),round(pt.y),round(ang,2)])
    return res
major=[];minor=[]
for (label,ismaj),ps in groups.items():
    if ismaj:
        for x,y,a in place(ps,1600,300,1400): major.append([label,x,y,a])
    else:
        for x,y,a in place(ps,700,120,600): minor.append([label,x,y,a])
print('etiquetas INEGI: avenidas',len(major),'calles',len(minor),'nombres distintos',len(groups))
json.dump({'labels':major,'mlabels':minor},open(f'{S}/work/inegi_labels.json','w'),ensure_ascii=False,separators=(',',':'))
