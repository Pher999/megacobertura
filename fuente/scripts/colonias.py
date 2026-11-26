import csv, collections, re, math, json, unicodedata
W='/home/claude/work'; W18=256*2**18; X0=8463*256*8; Y0=14401*256*8; SPAN=1792*32
def merc(lng,lat):
    r=math.radians(lat); return ((lng+180)/360*W18-X0,(1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*W18-Y0)
def strip(s): return unicodedata.normalize('NFD',s).encode('ascii','ignore').decode()
def clean(tipo,n):
    n=strip(n.upper()); n=re.sub(r'[^A-Z0-9 ]',' ',n); n=re.sub(r'\s+',' ',n).strip()
    # quitar sufijos de manzana/lote
    n=re.sub(r'\b(MZ|MZA|MANZANA|LT|LOTE|M)\s*\d+.*$','',n).strip()
    # region / supermanzana numerica
    m=re.fullmatch(r'(?:REGION|REG|R)\s*(\d{1,3})',n) or (re.fullmatch(r'(\d{1,3})',n) if tipo in('REGION','') else None)
    if m: return ('Región',m.group(1))
    m=re.fullmatch(r'(?:SUPERMANZANA|SUPERMANZA|SUPER MANZANA|SUPMZA|SUPMZ|SMZA|SMZ|SM|S M)\s*(\d{1,3})[A-Z]?',n) or (re.fullmatch(r'(\d{1,3})',n) if tipo=='SUPERMANZANA' else None)
    if m: return ('SM',m.group(1))
    if re.fullmatch(r'\d{1,3}[A-Z]?',n): return ('Región',re.match(r'\d+',n).group(0))
    m=re.match(r'(?:SUPERMANZANA|SUPMZA|SMZA|SM)\s*\d{1,3}\s+(.+)',n)
    if m: n=m.group(1)
    n=re.sub(r'^(FRACCIONAMIENTO|FRACC|COLONIA|COL|RESIDENCIAL|PRIVADA|CONDOMINIO|UNIDAD HABITACIONAL)\s+','',n)
    n=re.sub(r'\b(ETAPA|SECCION)\s*[IVX0-9]+.*$','',n).strip()
    if len(n)<3 or n in('CANCUN','CENTRO','ZONA HOTELERA','BENITO JUAREZ','QUINTANA ROO','ISLA MUJERES','URBANA','SUPER','ABC','MEXICO','SUPERMANZANA','REGION','NINGUNA','CONOCIDO'): return None
    return ('', n)
groups=collections.defaultdict(list); tipos=collections.defaultdict(collections.Counter)
with open(f'{W}/data/denue/conjunto_de_datos/denue_inegi_23_.csv',encoding='latin-1') as fh:
    for r in csv.DictReader(fh):
        if r['cve_mun'] not in('005','003'): continue
        tipo=r['tipo_asent'].strip().upper(); raw=r['nomb_asent'].strip()
        if not raw or raw.upper() in('NINGUNO','SIN NOMBRE'): continue
        k=clean(tipo,raw)
        if not k: continue
        try: x,y=merc(float(r['longitud']),float(r['latitud']))
        except: continue
        if not(0<=x<SPAN and 0<=y<SPAN): continue
        groups[k].append((x,y)); tipos[k][tipo]+=1
# fusionar variantes simples: PASEO/PASEOS, plurales
def base(n): return re.sub(r'\bPASEO\b','PASEOS',n)
merged=collections.defaultdict(list); mt=collections.defaultdict(collections.Counter)
for (t,n),p in groups.items():
    k=(t,base(n)); merged[k]+=p; mt[k].update(tipos[(t,n)])
out=[]
def title(n):
    small={'DE','DEL','LA','LAS','LOS','Y','EL','EN'}
    return ' '.join(w.lower() if (i>0 and w in small) else (w if re.fullmatch(r'[IVX]+',w) else w.capitalize()) for i,w in enumerate(n.split()))
for (t,n),p in merged.items():
    if len(p)<2: continue
    # agrupar en celdas de ~450 m y quedarse con el grupo conectado más grande
    G=800; cells=collections.defaultdict(list)
    for a,b in p: cells[(int(a//G),int(b//G))].append((a,b))
    seen=set(); comps=[]
    for c0 in cells:
        if c0 in seen: continue
        st=[c0]; seen.add(c0); comp=[]
        while st:
            c=st.pop(); comp+=cells[c]
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    nb=(c[0]+dx,c[1]+dy)
                    if nb in cells and nb not in seen: seen.add(nb); st.append(nb)
        comps.append(comp)
    comp=max(comps,key=len)
    if len(comp)<2: continue
    p=comp
    xs=sorted(a for a,b in p); ys=sorted(b for a,b in p)
    # núcleo robusto: mediana y percentiles 10-90 para quitar puntos mal ubicados
    q=lambda arr,f: arr[min(len(arr)-1,int(f*len(arr)))]
    cx,cy=q(xs,.5),q(ys,.5); x0,x1,y0,y1=q(xs,.1),q(xs,.9),q(ys,.1),q(ys,.9)
    # descartar si demasiado disperso (>4 km) -> nombre ambiguo
    if (x1-x0)>7200 or (y1-y0)>7200: continue
    tp=mt[(t,n)].most_common(1)[0][0]
    if t=='Región': label=f'Región {n}'; kind='Región'
    elif t=='SM': label=f'SM {n}'; kind='Supermanzana'
    else:
        label=title(n); kind={'FRACCIONAMIENTO':'Fraccionamiento','COLONIA':'Colonia','RESIDENCIAL':'Residencial','REGION':'Región','SUPERMANZANA':'Supermanzana'}.get(tp,'Colonia')
    pad=150
    out.append([label,kind,round(cx),round(cy),round(x0-pad),round(y0-pad),round(x1+pad),round(y1+pad),len(p)])
# Región N y SM N son lo mismo en Cancún: unir por número
byNum=collections.defaultdict(list)
for o in out:
    m=re.fullmatch(r'(Región|SM) (\d+)',o[0])
    if m: byNum[m.group(2)].append(o)
final=[o for o in out if not re.fullmatch(r'(Región|SM) \d+',o[0])]
for num,lst in byNum.items():
    best=max(lst,key=lambda o:o[8]); best=list(best); best[0]=f'Región {num} (SM {num})'; best[1]='Región / Supermanzana'
    final.append(best)
final.sort(key=lambda o:-o[8])
# quitar variantes ruidosas: nombre que contiene a otro más grande y cercano
def core(s): return re.sub(r'\b(sm|mz|\d+)\b','',strip(s.lower())).replace('  ',' ').strip()
keep=[]
for o in final:
    dup=False
    if o[1]=='Región / Supermanzana': keep.append(o); continue
    for k in keep:
        if k[1]=='Región / Supermanzana': continue
        if (core(k[0]) in core(o[0]) or core(o[0]) in core(k[0]) or (len(core(o[0]))>6 and sum(a!=b for a,b in zip(core(o[0]),core(k[0])))<=1 and len(core(o[0]))==len(core(k[0])))) and math.hypot(k[2]-o[2],k[3]-o[3])<3600 and k[8]>=o[8]:
            dup=True;break
    if not dup and o[8]>=3: keep.append(o)
final=keep
json.dump(final,open(f'{W}/scripts/colonias.json','w'),ensure_ascii=False,separators=(',',':'))
print('zonas',len(final)); 
for q in ['Villas Otoch','Paraiso Maya','Tierra Maya','Kusamil','Región 94','Cuna Maya','Prado Norte','Capistrano']:
    print(q,[(o[0],o[1],o[8]) for o in final if q.lower() in o[0].lower()][:4])
