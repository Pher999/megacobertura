# Uso: python3 add_custom.py archivo_con_textos.txt  -> agrega los "CALLES:[...]" pegados a custom.json
import json, sys, re, os
import os as _os; _R=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
S=_R+'/scripts'; P=f'{S}/custom.json'
cur=json.load(open(P)) if os.path.exists(P) else []
def key(flat):
    x=y=0;pts=[]
    for i in range(0,len(flat),2): x+=flat[i];y+=flat[i+1];pts.append((x,y))
    return (pts[0],pts[-1])
seen={key(g):i for i,(n,g) in enumerate(cur)}
txt=open(sys.argv[1]).read(); added=upd=0
for m in re.finditer(r'CALLES:(\[.*?\]\]\]\])',txt,re.S):
    for n,p in json.loads(m.group(1)):
        flat=[];x=y=0
        for a,b in p: flat+= [a-x,b-y]; x,y=a,b
        k=key(flat)
        if k in seen: cur[seen[k]]=[n,flat]; upd+=1
        else: seen[k]=len(cur); cur.append([n,flat]); added+=1
json.dump(cur,open(P,'w'),ensure_ascii=False,separators=(',',':'))
print('nuevas',added,'actualizadas',upd,'total',len(cur))
# Colonias añadidas por el equipo: "COLONIAS:[[nombre,tipo,x,y],...]" -> custom_cols.json (cuadro de ~600 m alrededor del punto)
PC=f'{S}/custom_cols.json'; cols=json.load(open(PC)) if os.path.exists(PC) else []
have={(c[0].lower(),c[2]//200,c[3]//200):i for i,c in enumerate(cols)}; nc=0
for m in re.finditer(r'COLONIAS:(\[.*?\]\])',txt,re.S):
    for n,k,x,y in json.loads(m.group(1)):
        R=540; z=[n,k,x,y,x-R,y-R,x+R,y+R,1]; kk=(n.lower(),x//200,y//200)
        if kk in have: cols[have[kk]]=z
        else: have[kk]=len(cols); cols.append(z); nc+=1
json.dump(cols,open(PC,'w'),ensure_ascii=False,separators=(',',':'))
print('colonias nuevas',nc,'total equipo',len(cols))
