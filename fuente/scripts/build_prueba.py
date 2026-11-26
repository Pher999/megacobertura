import re, json, os, sys
# Uso: python3 build_prueba.py                      -> out/prueba.html (versión de prueba)
#      python3 build_prueba.py prod chris "Chris" 529904011439 [pixel_id]  -> out/ofertas/chris/index.html
import os as _os; _R=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PROD = len(sys.argv)>1 and sys.argv[1]=='prod'
SLUG, NOMBRE, NUMERO = (sys.argv[2], sys.argv[3], sys.argv[4]) if PROD else ('prueba','Chris',None)
PIXEL = sys.argv[5] if PROD and len(sys.argv)>5 else None
S=_R+'/scripts'; L=_R+'/landing'
h=open(f'{L}/original.html',encoding='utf-8').read()
tpl=open(f'{S}/template2.html').read()
cov=tpl[tpl.index('<script>')+8:tpl.rindex('</script>')]
# quitar modo editor (la prueba no lo necesita)
a=cov.index('// ===== Modo editor'); b=cov.index('\nresize();',a)
cov=cov[:a]+cov[b:]
cov=cov.replace('geoBtn.textContent="📍 Usar mi ubicación actual"','geoBtn.innerHTML=GEO_HTML')
cust=(json.load(open(f'{S}/denue_names.json')) if os.path.exists(f'{S}/denue_names.json') else [])+(json.load(open(f'{S}/custom.json')) if os.path.exists(f'{S}/custom.json') else [])
cov=(cov.replace('__ENC__',open(f'{S}/enc.txt').read().strip()).replace('__MAP__',open(f'{S}/mapdata.json').read())
       .replace('__STREETS__',open(f'{S}/streets.json').read()).replace('__COLS__',__import__('json').dumps(__import__('json').load(open(f'{S}/colonias.json'))+(__import__('json').load(open(f'{S}/custom_cols.json')) if __import__('os').path.exists(f'{S}/custom_cols.json') else []),ensure_ascii=False,separators=(',',':'))).replace('__CUSTOM__',json.dumps(cust,ensure_ascii=False,separators=(',',':'))))

def sub(old,new,count=1):
    global h
    assert old in h, old[:60]
    h=h.replace(old,new,count)

# 1) Pixel apagado en la prueba
if PROD:
    if PIXEL: h=h.replace('823622827257783',PIXEL)
    sub('<title>MEGA CABLE - ¿Cuánto internet necesitas?</title>','<title>'+NOMBRE+' · Asesor MEGA · ¿Cuánto internet necesitas?</title>\n<meta name="robots" content="noindex,nofollow">')
    if NUMERO: h=re.sub(r'const NUMERO_VENTAS = "\d+";','const NUMERO_VENTAS = "'+NUMERO+'";',h)
else:
    h=re.sub(r'<!-- Meta Pixel Code -->.*?<!-- End Meta Pixel Code -->','<!-- Pixel de Meta desactivado en la versión de prueba -->',h,flags=re.S)
    sub('<title>MEGA CABLE - ¿Cuánto internet necesitas?</title>','<title>Prueba · ¿Cuánto internet necesitas?</title>\n<meta name="robots" content="noindex,nofollow">')
# 2) Identidad: herramienta del asesor, no sitio oficial
h=re.sub(r'<img alt="MEGA" class="h-7 w-auto" src="data:[^"]*">','<span class="font-section-title" style="font-weight:800;font-size:18px">'+NOMBRE+' · <span style="color:#2BE8D6">Asesor MEGA</span></span>'+('' if PROD else '<span class="prueba-badge">Prueba</span>'),h,count=1)
h=re.sub(r'<img alt="MEGA" class="h-8 w-auto mb-4" src="data:[^"]*">','<div class="font-section-title" style="font-weight:800;font-size:18px;margin-bottom:12px">'+NOMBRE+' · <span style="color:#2BE8D6">Asesor MEGA</span></div>',h,count=1)
sub('<p class="font-body-sm text-body-sm text-ink-soft max-w-xs">© 2026 Megacable Holdings S.A. de C.V. Todos los derechos reservados.</p>',
    '<p class="font-body-sm text-body-sm text-ink-soft max-w-xs">'+(('Página de '+NOMBRE+', asesor de ventas MEGA.') if PROD else 'Versión de prueba de la herramienta de Chris, asesor MEGA.')+' No es un sitio oficial de Megacable. Calles © colaboradores de OpenStreetMap (ODbL) e INEGI. La zona con fibra se tomó del mapa público de cobertura el 11 de noviembre de 2026; el servicio está sujeto a factibilidad técnica.</p>')
h=re.sub(r'<div class="col-span-1 lg:col-span-2 flex flex-col md:flex-row gap-4 md:gap-8">.*?</div>\s*</div>\s*</footer>',
 '''<div class="col-span-1 lg:col-span-2">
'''+'''<div class="flex flex-wrap gap-x-6 gap-y-2 mb-4" role="navigation" aria-label="Información legal"><a class="font-body-sm text-body-sm text-ink-soft hover:text-ink transition-colors" href="https://megaventaspeninsula.com.mx/aviso-privacidad.html" target="_blank" rel="noopener">Aviso de Privacidad</a><a class="font-body-sm text-body-sm text-ink-soft hover:text-ink transition-colors" href="https://mega.mx/terminos-y-condiciones" target="_blank" rel="noopener">Términos y Condiciones</a><a class="font-body-sm text-body-sm text-ink-soft hover:text-ink transition-colors" href="https://www.ift.org.mx/" target="_blank" rel="noopener">IFT</a><a class="font-body-sm text-body-sm text-ink-soft hover:text-ink transition-colors" href="https://mega.mx/uploads/legales/1756225004665-a0bc0ns7n3l.pdf" target="_blank" rel="noopener">Contratos de Adhesión</a></div><p class="font-body-sm text-body-sm text-ink-soft">Sitio independiente operado por el asesor; no es la página oficial de Megacable. MEGA y su logotipo son marcas de Megacable Holdings S.A.B. de C.V.</p>
'''+('' if PROD else '''<details class="eventos-prueba"><summary>Eventos que se medirían (solo en la prueba)</summary><ol id="log-eventos"><li class="vacio">Todavía ninguno. Recorre el flujo y aquí aparecen.</li></ol></details>''')+'''
</div>
</div>
</footer>''',h,count=1,flags=re.S)
# 3) Paso 2 nuevo
a=h.index('<!-- Step 2: Coverage -->'); b=h.index('<!-- Step 3: Current Situation -->')
step2='''<!-- Step 2: Coverage (herramienta de cobertura real) -->
<div class="step-container" id="step-2">
<button class="flex items-center gap-1 text-ink-soft hover:text-primary mb-4 transition-colors font-body-sm" type="button" onclick="nextStep(1)"><span class="material-symbols-outlined text-sm">arrow_back</span> Atrás</button>
<h2 class="font-section-title text-section-title mb-2 text-2xl">¿Llega la fibra a tu casa?</h2>
<p class="font-body-sm text-body-sm text-ink-soft mb-6">Comparte tu ubicación o busca tu colonia. Solo la usamos para revisar la cobertura.</p>
<button class="btn-primary w-full rounded-lg py-3 font-body-lg text-body-lg flex items-center justify-center gap-2" id="geo" type="button"><span class="material-symbols-outlined">my_location</span> Estoy en mi casa: usar mi ubicación</button>
<div class="cob-or">¿No estás en casa? Busca tu colonia o calle</div>
<form id="manual" autocomplete="off">
<label class="block font-eyebrow text-eyebrow text-signal-deep mb-2" for="q">COLONIA, CALLE O ENLACE DE GOOGLE MAPS</label>
<div class="cob-sbox">
<span class="material-symbols-outlined cob-ico">search</span>
<input class="w-full bg-surface-container-highest border border-outline-variant rounded-lg py-3 pl-12 pr-24 text-ink focus:border-signal focus:ring-1 focus:ring-signal outline-none transition-all" id="q" type="text" autocapitalize="off" spellcheck="false" placeholder="Ej. Villas Otoch, Región 94 o Chilam Balam" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="sug">
<button class="cob-buscar" type="submit">Buscar</button>
<ul id="sug" role="listbox" hidden></ul>
</div>
<p class="cob-err" id="err" hidden></p>
</form>
<div class="cob-mapbox"><canvas id="map" tabindex="0" aria-label="Mapa de Cancún con la zona de fibra. Toca para colocar tu ubicación."></canvas>
<div class="cob-zoom"><button id="zin" type="button" aria-label="Acercar">+</button><button id="zout" type="button" aria-label="Alejar">−</button></div></div>
<p class="cob-hint"><span class="cob-sw"></span> Zona con fibra · Toca tu casa en el mapa o arrastra el pin para afinar.</p>
<div id="out"></div>
<div class="hidden mb-6" id="sin-cobertura-form">
<p class="font-body-sm text-body-sm text-ink-soft mb-4">Déjanos tus datos y te avisamos en cuanto lleguemos a tu calle.</p>
<div class="space-y-3">
<input class="w-full bg-surface-container-highest border border-outline-variant rounded-lg py-3 px-4 text-ink focus:border-signal outline-none" id="sc-nombre" placeholder="Nombre" type="text">
<input class="w-full bg-surface-container-highest border border-outline-variant rounded-lg py-3 px-4 text-ink focus:border-signal outline-none" id="sc-tel" placeholder="Teléfono / WhatsApp" type="tel">
<button class="btn-secondary w-full rounded-lg py-3 font-body-lg text-body-lg" onclick="avisarCobertura()" type="button">Avísenme cuando llegue</button>
</div>
</div>
<div id="cta" hidden><a id="wa"></a></div>
</div>
'''
h=h[:a]+step2+h[b:]
NOTA=lambda txt:'<p class="font-body-sm text-ink-soft" style="font-size:12px;margin-top:8px;text-align:center">'+txt+' aceptas el <a href="https://megaventaspeninsula.com.mx/aviso-privacidad.html" target="_blank" rel="noopener" style="text-decoration:underline">aviso de privacidad</a>.</p>'
old='onclick="avisarCobertura()" type="button">Avísenme cuando llegue</button>'
assert h.count(old)==1; h=h.replace(old,old+NOTA('Al enviar tus datos'))
old='<span class="material-symbols-outlined">send</span> Enviar por WhatsApp\n</button>'
assert h.count(old)==1; h=h.replace(old,old+NOTA('Al enviar tu solicitud'))
for v in ('400','600','800'):
    old='<span class="font-label text-label text-ink-soft">Hasta $'+v+'/mes</span>'
    assert h.count(old)==1
    h=h.replace(old,'<span class="presu-precio"><small>Hasta</small>$'+v+'<small>/mes</small></span>')
for n in (3,4):
    tag='<div class="step-container" id="step-%d">'%n
    assert h.count(tag)==1
    h=h.replace(tag,tag+'''<button class="flex items-center gap-1 text-ink-soft hover:text-primary mb-4 transition-colors font-body-sm" type="button" onclick="nextStep(%d)"><span class="material-symbols-outlined text-sm">arrow_back</span> Atrás</button>'''%(n-1))
tag='<section class="w-full hidden" id="results-section">'
assert h.count(tag)==1
m=re.search(r'<div class="[^"]*" id="grid-planes">',h); assert m
h=h[:m.start()]+'''<div class="paq-switch md:hidden" role="group" aria-label="Ver paquete"><button type="button" onclick="verPaquete(0)" class="on" aria-pressed="true">Solo Internet</button><button type="button" onclick="verPaquete(1)" aria-pressed="false">Internet + TV</button></div>'''+h[m.start():]
h=h.replace(tag,tag+'''<button class="flex items-center gap-1 text-ink-soft hover:text-primary mb-4 transition-colors font-body-sm" type="button" onclick="document.getElementById('results-section').classList.add('hidden');document.getElementById('wizard-section').classList.remove('hidden');nextStep(4);"><span class="material-symbols-outlined text-sm">arrow_back</span> Cambiar mis respuestas</button>''')
# 4) CSS del módulo
css='''
        :root{--land:#11172E;--street:#2A3561;--road:#4D5E93;--road-case:#0F1426;--label:#C7D0E6;--halo:#11172E;--smlabel:#2BE8D6;--fiber:#2BE8D6;--pin:#F2F5FA;--hl:#2E5BFF;--no:#FFB4AB}
        .prueba-badge{margin-left:10px;font:700 11px/1 Manrope,sans-serif;letter-spacing:.06em;text-transform:uppercase;padding:5px 8px;border-radius:999px;background:rgba(43,232,214,.14);color:#2BE8D6;border:1px solid rgba(43,232,214,.4)}
        .cob-or{display:flex;align-items:center;gap:10px;color:#8B95AD;font-size:13px;margin:18px 0}
        .cob-or::before,.cob-or::after{content:"";flex:1;height:1px;background:#1D2440}
        .cob-sbox{position:relative}
        .cob-ico{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#8B95AD;pointer-events:none}
        .cob-buscar{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:#2E5BFF;color:#F2F5FA;border:0;border-radius:8px;padding:8px 14px;font:600 14px Manrope,sans-serif}
        html,body{overflow-x:hidden;overflow-x:clip}
        .paq-switch{position:relative;z-index:30;display:flex;gap:6px;padding:6px;margin:0 0 16px;background:#141A33;border:1px solid #2A3561;border-radius:999px}
        .paq-switch button{flex:1;padding:10px 8px;border-radius:999px;font:700 14px Manrope,sans-serif;color:#C7D0E6;background:transparent;border:0}
        .paq-switch button.on{background:#2E5BFF;color:#F2F5FA}
        @media (max-width:767px){#grid-planes > div.paq-off{display:none}}
        .presu-precio{display:block;margin-top:2px;font:800 26px/1.1 Sora,Manrope,sans-serif;color:#2BE8D6;font-variant-numeric:tabular-nums}
        .presu-precio small{font:600 14px Manrope,sans-serif;color:#C7D0E6;margin:0 2px}
        #q{font-size:16px}
        #sug{position:absolute;top:calc(100% + 6px);left:0;right:0;z-index:20;margin:0;padding:6px;list-style:none;background:#141A33;border:1px solid #2A3561;border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,.45);max-height:280px;overflow:auto}
        #sug li{padding:10px 12px;border-radius:8px;cursor:pointer;display:flex;flex-direction:column;gap:2px}
        #sug li:hover,#sug li[aria-selected="true"]{background:rgba(46,91,255,.15)}
        #sug b{font-weight:600;color:#F2F5FA}#sug small{color:#8B95AD;font-size:12px}#sug li.x b{color:#2BE8D6}
        .cob-err{color:#FFB4AB;font-size:14px;margin:8px 0 0}
        .cob-mapbox{position:relative;height:min(52vh,380px);min-height:280px;border-radius:12px;overflow:hidden;background:var(--land);border:1px solid #1D2440;margin-top:18px;touch-action:none}
        #map{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab}#map.dragging{cursor:grabbing}
        .cob-zoom{position:absolute;right:10px;top:10px;display:flex;flex-direction:column;gap:6px}
        .cob-zoom button{width:40px;height:40px;border-radius:10px;border:1px solid #2A3561;background:#141A33;color:#F2F5FA;font:600 20px/1 Manrope,sans-serif}
        .cob-hint{display:flex;align-items:center;gap:8px;color:#8B95AD;font-size:13px;margin:10px 0 18px}
        .cob-sw{width:14px;height:14px;border-radius:3px;background:#2BE8D6;opacity:.6;flex:none}
        .cob-res{border-radius:12px;padding:18px 20px;margin-bottom:18px;border:1px solid}
        .cob-res h3{font-family:Sora,sans-serif;font-weight:800;font-size:22px;line-height:1.2;margin:0 0 6px}
        .cob-res p{margin:0 0 4px;font-size:15px;color:#C7D0E6}
        .cob-res .meta{font-size:13px;color:#8B95AD;font-variant-numeric:tabular-nums}
        .cob-res a{color:inherit;font-weight:600;text-decoration:underline}
        .cob-si{background:rgba(43,232,214,.10);border-color:rgba(43,232,214,.55)}.cob-si h3{color:#2BE8D6}
        .cob-info{background:rgba(46,91,255,.10);border-color:rgba(46,91,255,.6)}.cob-info h3{color:#F2F5FA}.cob-info .meta{text-transform:uppercase;letter-spacing:.08em;color:#2BE8D6;margin:0 0 4px}
        .cob-borde{background:rgba(255,190,90,.10);border-color:rgba(255,190,90,.55)}.cob-borde h3{color:#FFC46B}
        .cob-no{background:rgba(255,180,171,.08);border-color:rgba(255,180,171,.5)}.cob-no h3{color:#FFB4AB}
        .eventos-prueba{font-size:13px;color:#8B95AD}.eventos-prueba summary{cursor:pointer;color:#C7D0E6;margin-bottom:8px}
        .eventos-prueba ol{margin:0;padding-left:20px;font-variant-numeric:tabular-nums}.eventos-prueba li{margin:3px 0;overflow-wrap:anywhere}
        #map:focus-visible,#q:focus-visible,.cob-zoom button:focus-visible{outline:3px solid #2BE8D6;outline-offset:2px}
    </style>'''
sub('    </style>\n</head>',css+'\n</head>')
# 5) WhatsApp con ubicación y eventos visibles en la prueba
sub("'*Colonia/SM:* ' + encodeURIComponent(estado.zona || 'no indicada') + '%0A' +",
    "'*Calle/zona:* ' + encodeURIComponent(estado.zona || 'no indicada') + '%0A' +\n    '*Ubicación:* ' + encodeURIComponent(estado.ubicacion || 'no indicada') + '%0A' +")
sub("'*Colonia/SM:* ' + encodeURIComponent(estado.zona) + '%0A' +",
    "'*Calle/zona:* ' + encodeURIComponent(estado.zona) + '%0A' +\n    '*Ubicación:* ' + encodeURIComponent(estado.ubicacion || 'no indicada') + '%0A' +")
sub("function evento(nombre, params){\n  if (typeof fbq === 'function') fbq('track', nombre, params || {});\n}",
"""function evento(nombre, params){
  params = Object.assign({asesor: ASESOR}, params || {});
  const STD = ['Lead','Contact','InitiateCheckout','ViewContent','Search','SubmitApplication','CompleteRegistration','Schedule'];
  if (typeof fbq === 'function') fbq(STD.indexOf(nombre) >= 0 ? 'track' : 'trackCustom', nombre, params);
  // Prueba: en vez de mandarlo a Meta, se muestra en el pie de página.
  try{
    const ol=document.getElementById('log-eventos'); if(!ol) return;
    const v=ol.querySelector('.vacio'); if(v) v.remove();
    const li=document.createElement('li');
    li.textContent=new Date().toLocaleTimeString('es-MX')+' · '+nombre+' '+JSON.stringify(params||{});
    ol.appendChild(li);
  }catch(e){}
}""")
glue='''
<script>
const ASESOR='__ASESOR__';
const GEO_HTML='<span class="material-symbols-outlined">my_location</span> Estoy en mi casa: usar mi ubicación';
''' + cov + '''
// ===== Conexión con la landing =====
function calleCercana(x,y){
  let best=null,bd=110; // ~60 m
  for(const s of SIDX){ if(s.bx1<x-bd||s.bx0>x+bd||s.by1<y-bd||s.by0>y+bd) continue;
    for(const p of s.geo) for(let k=1;k<p.length;k++){
      const ax=p[k-1][0],ay=p[k-1][1],dx=p[k][0]-ax,dy=p[k][1]-ay,L=dx*dx+dy*dy;
      let t=L?((x-ax)*dx+(y-ay)*dy)/L:0;t=Math.max(0,Math.min(1,t));
      const d=Math.hypot(ax+t*dx-x,ay+t*dy-y); if(d<bd){bd=d;best=s}}}
  return best?best.n:null;
}
let metodoCob='mapa',porColonia=false;
window.zoneMessage=function(z){porColonia=true;out.innerHTML='';const box=document.createElement('div');box.className='cob-res cob-info';
  const h3=document.createElement('h3');h3.textContent=z.short;const p=document.createElement('p');p.textContent='Ahora toca tu casa en el mapa (o arrastra el pin) para saber si te llega la fibra.';
  const m=document.createElement('p');m.className='meta';m.textContent=z.k;box.append(m,h3,p);out.append(box);document.getElementById('sin-cobertura-form').classList.add('hidden');
  evento('BusquedaColonia',{colonia:z.short,tipo:z.k});out.scrollIntoView({behavior:'smooth',block:'nearest'})};
show=function(lat,lng,source,recenter=true){
  err.hidden=true; const r=check(lat,lng); const [x,y]=toU(lat,lng);
  pin={x,y,res:r,m:metersPerU(lat)};
  if(recenter&&r.status!=="out"){view.cx=x;view.cy=y;view.s=Math.max(view.s,0.3);clampView()}
  draw();
  metodoCob=porColonia&&/mapa|Pin/i.test(source)?'colonia':/teléfono/.test(source)?'gps':/Calle|Cruce/.test(source)?'calle':/pegada/.test(source)?'enlace':'mapa';
  const calle=calleCercana(x,y),col=zoneLabel(x,y);
  estado.zona = [calle,col].filter(Boolean).join(', ') || (lat.toFixed(5)+', '+lng.toFixed(5));
  ZONE=null;
  estado.ubicacion = 'https://www.google.com/maps?q='+lat.toFixed(6)+','+lng.toFixed(6);
  estado.conCobertura = (r.status==='yes'||r.status==='edge');
  const formSC=document.getElementById('sin-cobertura-form');
  const cfg={
    yes:['cob-si','¡Sí llega la fibra a tu casa!','Tu ubicación está dentro de la zona con fibra óptica.',true,'Continuar'],
    edge:['cob-borde','Estás en el borde de la zona con fibra','La fibra está a unos '+fmtD(r.dist)+'. Es muy probable que sí llegue; un asesor lo confirmará con tu dirección.',true,'Continuar'],
    no:['cob-no','Aún no llegamos a tu calle',isFinite(r.dist)?'La zona con fibra más cercana está a unos '+fmtD(r.dist)+'. Déjanos tus datos y te avisamos.':'Déjanos tus datos y te avisamos en cuanto lleguemos.',false],
    out:['cob-no','Esta revisión solo cubre Cancún','Tu punto está fuera de Cancún, Puerto Juárez y Alfredo V. Bonfil. Déjanos tus datos y un asesor lo revisa.',false]
  }[r.status];
  out.innerHTML='';
  const box=document.createElement('div'); box.className='cob-res '+cfg[0];
  const h3=document.createElement('h3'); h3.textContent=cfg[1];
  const p=document.createElement('p'); p.textContent=cfg[2];
  const m=document.createElement('p'); m.className='meta';
  m.append((calle?calle+' · ':'')+(col?col+' · ':'')+lat.toFixed(5)+', '+lng.toFixed(5)+' · ');
  const a=document.createElement('a'); a.href=estado.ubicacion; a.target='_blank'; a.rel='noopener'; a.textContent='ver en Google Maps'; m.append(a);
  box.append(h3,p,m);
  if(!cfg[3]){const w=document.createElement('p');w.style.marginTop='10px';const wa=document.createElement('a');wa.href='https://wa.me/'+NUMERO_VENTAS+'?text='+encodeURIComponent('Hola, el verificador dice que no hay cobertura en mi casa, ¿me ayudas a revisarlo?\\n\\nUbicación: '+estado.ubicacion+'\\nZona: '+estado.zona);wa.target='_blank';wa.rel='noopener';wa.textContent='¿Crees que es un error? Escríbeme y lo reviso con tu dirección';wa.onclick=()=>evento('RevisionCobertura',{zona:estado.zona});w.append(wa);box.append(w)}
  if(cfg[3]){const b=document.createElement('button'); b.type='button'; b.className='btn-primary w-full rounded-lg py-3 font-body-lg text-body-lg mt-4'; b.textContent=cfg[4]; b.onclick=()=>nextStep(3); box.append(b)}
  out.append(box);
  formSC.classList.toggle('hidden', cfg[3]);
  evento(cfg[3]?'CoberturaPositiva':'CoberturaNegativa',{resultado:r.status,metodo:metodoCob,zona:estado.zona,colonia:col,distancia_m:Math.round(r.dist||0)});
  if(recenter) out.scrollIntoView({behavior:'smooth',block:'nearest',inline:'nearest'});
};
document.getElementById('start-wizard-btn').addEventListener('click',()=>setTimeout(resize,50));
function verPaquete(i){const cs=document.querySelectorAll('#grid-planes > div');if(!cs[i])return;cs.forEach((c,k)=>c.classList.toggle('paq-off',k!==i));document.querySelectorAll('.paq-switch button').forEach((x,k)=>{x.classList.toggle('on',k===i);x.setAttribute('aria-pressed',k===i)});
  const sw=document.querySelector('.paq-switch');if(sw&&sw.getBoundingClientRect().top<0)sw.scrollIntoView({block:'start'})}
{const _mr=mostrarResultados;mostrarResultados=function(){_mr();document.body.scrollLeft=0;window.scrollTo(0,0);verPaquete(estado.tieneTV===true?1:0)}}
{const _ns=nextStep;let vio=false;nextStep=function(n){_ns(n);document.body.scrollLeft=0;document.documentElement.scrollLeft=0;if(n===2){setTimeout(resize,50);if(!vio){vio=true;evento('VerCobertura',{})}}}}
</script>
</body>'''
glue=glue.replace('__ASESOR__',SLUG)
h=h.replace('</body>',glue,1) if h.count('</body>')==1 else None
assert h
dst=_R+'/out/'+('ofertas/'+SLUG+'/index.html' if PROD else 'prueba.html')
os.makedirs(os.path.dirname(dst),exist_ok=True)
open(dst,'w',encoding='utf-8').write(h)
print('ok',len(h))
