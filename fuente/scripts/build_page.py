import json, sys, os
import os as _os; _R=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
S=_R+'/scripts'; O=_R+'/out'
t=open(f'{S}/template2.html').read()
cust=(json.load(open(f'{S}/denue_names.json')) if os.path.exists(f'{S}/denue_names.json') else [])+(json.load(open(f'{S}/custom.json')) if os.path.exists(f'{S}/custom.json') else [])
custom=json.dumps(cust,ensure_ascii=False,separators=(',',':'))
page=(t.replace('__ENC__',open(f'{S}/enc.txt').read().strip()).replace('__MAP__',open(f'{S}/mapdata.json').read())
      .replace('__STREETS__',open(f'{S}/streets.json').read()).replace('__COLS__',__import__('json').dumps(__import__('json').load(open(f'{S}/colonias.json'))+(__import__('json').load(open(f'{S}/custom_cols.json')) if __import__('os').path.exists(f'{S}/custom_cols.json') else []),ensure_ascii=False,separators=(',',':'))).replace('__CUSTOM__',custom))
open(f'{O}/cobertura-fibra-cancun.html','w').write(page)
head='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
open(f'{O}/index.html','w').write(head+page+'</body></html>'); print('bytes',len(page))
