# indexabilidad.py
import streamlit as st
import time
from index_check import limpiar_url, obtener_enlaces_internos, analizar_indexabilidad, clasificar_tipo_pagina

def procesar_indexabilidad(url_blog):
    for registro in st.session_state.url_listado:
        if registro['estado'] == 'pendiente':
            url_actual = limpiar_url(registro['url'])
            registro['estado'] = 'evaluado'
            codigo, canonicals, robots, indexable = analizar_indexabilidad(url_actual)

            registro['indexable'] = indexable
            registro['codigo'] = codigo
            registro['canonicals'] = canonicals
            registro['robots'] = robots

            if indexable:
                expandir_enlaces_si_indexable(url_actual, url_blog)
            break
    time.sleep(0.3)
    st.rerun()

def expandir_enlaces_si_indexable(url_actual, url_blog):
    nuevos = obtener_enlaces_internos(url_actual, url_blog)
    for nueva_url in nuevos:
        nueva_url_limpia = limpiar_url(nueva_url)
        if not any(u['url'] == nueva_url_limpia for u in st.session_state.url_listado):
            st.session_state.url_listado.append({
                "url": nueva_url_limpia,
                "estado": "pendiente",
                "indexable": None,
                "codigo": None,
                "canonicals": [],
                "robots": None,
                "tipo_pagina": clasificar_tipo_pagina(nueva_url_limpia)
            })
