# Proyecto: Landings con verificador de cobertura (MEGA · Cancún)

Resumen para la base de conocimiento del proyecto "Estrategia landing megacable".
Actualizado: 26 de noviembre de 2026. Dueño: Chris (Christopher Ashley Medina García), asesor y trafficker.

---

## 1. Páginas activas

| Página | Dirección | Para qué es |
|---|---|---|
| Landing de Chris | https://ofertas.megaventaspeninsula.com.mx/chris | La de sus anuncios. WhatsApp y Pixel de Chris. |
| Landing de Marlon | https://ofertas.megaventaspeninsula.com.mx/marlon | La de los anuncios de Marlon. WhatsApp y Pixel de Marlon. |
| Raíz del subdominio | https://ofertas.megaventaspeninsula.com.mx | Redirige a la home principal. |
| Home principal | https://megaventaspeninsula.com.mx | Sitio original de Chris (ya existía). Tiene el aviso de privacidad. |
| Aviso de privacidad | https://megaventaspeninsula.com.mx/aviso-privacidad.html | Aviso único para todo el sitio y todos los asesores (responsable: Chris). |
| Verificador solo | https://pher999.github.io/megacobertura/ | Herramienta "¿Llega la fibra a tu casa?" sin la landing. |
| Modo editor | https://pher999.github.io/megacobertura/#editar | Para que el equipo nombre calles sin nombre y agregue colonias faltantes. |
| Landing de prueba | https://pher999.github.io/megacobertura/prueba/ | Copia para probar cambios. Sin Pixel, oculta a Google, con registro de eventos en el pie. |
| Artefacto en Claude | https://claude.ai/artifact/2DTy55zFPNiP94yqHSxWqv | Versión del verificador publicada en Claude (pública). |
| Mapa del sitio (doc) | https://claude.ai/artifact/2mC3Vn5SG6ZUneZ9SXCBng | Plan de estructura: home, /empresas, /moviles, subdominio ofertas. |

Las landings en `ofertas.` están ocultas a Google (noindex): viven de anuncios, no de búsquedas.

---

## 2. Asesores con landing

| Asesor | Carpeta | WhatsApp (botones) | Pixel de Meta |
|---|---|---|---|
| Chris | `chris` | 52 990 401 1439 | 823622827257783 (el de su landing original) |
| Marlon | `marlon` | 52 998 900 7279 | 3735798569922403 ("Marlon pixel", cuenta MegaChadChad) |

Para sumar a otro asesor se piden: nombre como quiere aparecer, WhatsApp de 10 dígitos, ID de su Pixel (si no tiene, se usa el de Chris y los eventos llevan su nombre), y su visto bueno para publicar nombre y número.

---

## 3. Dónde está alojado

**Hosting: Neubox**, plan Hosting cPanel "TELL IT".
- Área de cliente: clientes.neubox.com → Productos/Servicios → Hosting cPanel → Ingresar a cPanel.
- cPanel (tema Jupiter, versión 138). Servidor `svgt447.serverneubox.com.mx`, usuario `megavent`.
- Límites del plan: subdominios ilimitados; 3 dominios adicionales (addon), sin usar.

**Carpetas en el servidor**
```
/home/megavent/
  public_html/                              → megaventaspeninsula.com.mx (home)
  ofertas.megaventaspeninsula.com.mx/       → ofertas.megaventaspeninsula.com.mx
    index.html                              → redirige a la home
    chris/index.html                        → landing de Chris
    marlon/index.html                       → landing de Marlon
    cgi-bin/, php.ini                       → los creó cPanel, no tocar
```

**Seguridad**
- SSL Let's Encrypt activo en ambos dominios (AutoSSL).
- Force HTTPS Redirect: encendido en los dos (cPanel → Dominios).
- `*.ofertas…` (comodín) no tiene SSL y no se necesita.

**Código y respaldo: GitHub**
- Repositorio: https://github.com/pher999/megacobertura (GitHub Pages).
- `index.html` = verificador; `prueba/index.html` = landing de prueba.
- `fuente/` = todo lo necesario para regenerar las páginas (ver sección 7).

---

## 4. Cómo funciona la landing

Flujo (4 pasos + resultados), basado en la landing original de Chris:
1. Perfil de uso (cuánto internet necesita).
2. **Cobertura**: "Estoy en mi casa: usar mi ubicación", o buscar colonia/fraccionamiento/región, calle o cruce, pegar link de Google Maps o coordenadas, o tocar la casa en el mapa. Resultado: Sí hay fibra / En el borde (≤60 m, confirmar con asesor) / No hay / Fuera de zona.
   - Con cobertura: botón Continuar.
   - Sin cobertura: formulario "Avísenme cuando llegue" (abre WhatsApp, no guarda datos en servidor) y enlace "¿Crees que es un error? Escríbeme".
3. Situación actual (proveedor, pago, TV, velocidad).
4. Presupuesto (precios grandes en turquesa).
5. Resultados: tarjetas Solo Internet / Internet + Xview+. En celular hay un selector y se ve una tarjeta a la vez; en computadora, las dos lado a lado. Botón Solicitar → WhatsApp con plan, zona, calle/colonia y link de ubicación.

Botones Atrás en pasos 2, 3 y 4, y "Cambiar mis respuestas" en resultados.

Pie: Aviso de Privacidad, Términos y Condiciones (mega.mx), IFT, Contratos de Adhesión (PDF de mega.mx), y la leyenda "Sitio independiente operado por el asesor; no es la página oficial de Megacable. MEGA y su logotipo son marcas de Megacable Holdings S.A.B. de C.V." Bajo cada formulario: "Al enviar… aceptas el aviso de privacidad".

---

## 5. Medición (Pixel de Meta)

Cada landing usa el Pixel de su asesor. Todos los eventos llevan el parámetro `asesor` (chris, marlon…).

| Evento | Tipo | Cuándo se dispara | Parámetros útiles |
|---|---|---|---|
| PageView | estándar | Al abrir la página | — |
| IniciaDiagnostico | personalizado | Elige su perfil en el paso 1 | perfil |
| VerCobertura | personalizado | Llega al paso 2 (una vez por visita) | — |
| BusquedaColonia | personalizado | Elige una colonia en el buscador | colonia, tipo |
| CoberturaPositiva | personalizado | Resultado con fibra (sí o borde) | resultado, metodo (gps/colonia/mapa/búsqueda), zona, colonia, distancia_m |
| CoberturaNegativa | personalizado | Resultado sin fibra o fuera de zona | igual que arriba |
| RevisionCobertura | personalizado | Toca "¿Crees que es un error?" | zona |
| InitiateCheckout | estándar | Termina el paso 3 | value (lo que paga hoy), compania_actual |
| Lead | estándar | Ve sus resultados | plan_mb, tipo_paquete |
| Contact | estándar | Envía la solicitud por WhatsApp | — |

Embudo para revisar: PageView → VerCobertura → CoberturaPositiva → Lead → Contact. Si menos del 60-70 % de VerCobertura llega a un resultado de cobertura, el paso 2 está frenando.

Pendiente: crear conversiones personalizadas (por ejemplo, con CoberturaPositiva) en el Administrador de eventos de cada asesor.

---

## 6. Datos del verificador

- **Zona con fibra**: capa pública del mapa de cobertura de MEGA (WMTS `cobertura_fibra_cob`, zoom 15), tomada el 11 de noviembre de 2026. Rejilla de ~18 m por celda. Si MEGA amplía cobertura, hay que volver a tomarla.
- **Calles**: INEGI (Marco Geoestadístico, Quintana Roo) + OpenStreetMap (OSM, por Overpass Turbo) + DENUE para nombres faltantes. Unos 5,000 nombres; ~6,100 tramos siguen sin nombre en ninguna fuente → se nombran con el modo editor.
- **Colonias**: 374 zonas (colonias, fraccionamientos, regiones/supermanzanas) sacadas del DENUE (INEGI). Los contornos son aproximados. Faltan algunas (ej. Capistrano) → "Agregar colonia" en el modo editor.
- **Modo editor** (`#editar`): calles sin nombre en rojo; tocar, escribir nombre, guardar. "Agregar colonia": tocar el centro y escribir nombre y tipo. "Copiar para enviar" genera un texto `CALLES:[…]` y `COLONIAS:[…]` que se integra con `add_custom.py`.
- Créditos en el pie: OpenStreetMap (ODbL) e INEGI.

---

## 7. Cómo corregir o regenerar las páginas

Todo vive en `fuente/` del repositorio de GitHub:
- `scripts/template2.html` – plantilla del verificador (mapa, búsqueda, editor).
- `scripts/build_page.py` – genera el verificador (`out/index.html`, que va a la raíz de GitHub Pages, y la versión para el artefacto).
- `scripts/build_prueba.py` – genera las landings a partir de `landing/original.html` (la landing original de Chris).
  - Prueba: `python3 build_prueba.py` → `out/prueba.html`
  - Asesor: `python3 build_prueba.py prod <carpeta> "<Nombre>" <52+WhatsApp> [pixel]` → `out/ofertas/<carpeta>/index.html`
  - Ejemplos: `prod chris "Chris" 529904011439` · `prod marlon "Marlon" 529989007279 3735798569922403`
- `scripts/add_custom.py <archivo.txt>` – integra los textos CALLES/COLONIAS del modo editor; después se corren los builds.
- Datos: `enc.txt` (cobertura), `mapdata.json` (mapa), `streets.json` (calles), `colonias.json`, `custom.json`, `denue_names.json`.
- Los demás scripts (`colonias.py`, `streets_index.py`, `denue_match.py`, `build_unn.py`…) son los que generaron los datos; necesitan los archivos crudos de INEGI/DENUE/OSM, que no están en el repo por su tamaño.

**Para publicar un cambio en una landing**
1. Regenerar con `build_prueba.py` (prueba primero, revisarla en GitHub Pages).
2. Comprimir la carpeta del asesor en un .zip (sin carpeta de más arriba).
3. cPanel → Administrador de archivos → `ofertas.megaventaspeninsula.com.mx` → Cargar (marcar "Overwrite existing files") → Extraer → borrar el zip.

Consejo: desactivar la traducción automática de Chrome en cPanel; cambia la mayúscula de los nombres de carpetas en pantalla (por ejemplo, muestra "Chris" cuando la carpeta es "chris").

---

## 8. Decisiones tomadas

- Una carpeta por asesor dentro de un solo subdominio (`ofertas.`), no un subdominio por persona.
- Empresas y Móviles irán como carpetas de la home (`/empresas`, `/moviles`) para sumar en Google; subdominio propio solo si luego llevan anuncios y diseño propio.
- Las landings no se presentan como sitio oficial de Megacable. Se quitó "usadas con autorización" porque MEGA no dio permiso por escrito.
- Un solo aviso de privacidad (el de la home) para todos los asesores.
- Fuentes de calles: no se usan datos de Google ni el sitio de MEGA; el plano DWG se descartó por estar desplazado ~200 m.

## 9. Pendientes

- [ ] Conversiones personalizadas en Meta (CoberturaPositiva, Contact) para Chris y Marlon.
- [ ] Cambiar anuncios a las nuevas URLs y revisar el embudo tras unos días.
- [ ] Quitar "usadas con autorización" y "asesor de ventas autorizado" de la home y del aviso de privacidad.
- [ ] Integrar los nombres de calles/colonias que mande el equipo (modo editor).
- [ ] Botón de WhatsApp del verificador solo (GitHub) aún sin número.
- [ ] Home nueva según el mapa del sitio (oferta, planes, cobertura, /empresas, /moviles).
- [ ] Landings de más asesores cuando haya datos.
