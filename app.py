import streamlit as st
import time
import pandas as pd
from index_check import limpiar_url, obtener_enlaces_internos, analizar_indexabilidad, clasificar_tipo_pagina
from contenido_repetido import detectar_bloques_comunes, extraer_texto_limpio

st.set_page_config(page_title="Análisis de Indexabilidad", layout="wide")
st.title("🔍 Análisis de Indexabilidad de URLs")

url_blog = st.text_input("📍 URL del blog principal")

# Estado inicial
if 'estado' not in st.session_state:
    st.session_state.estado = 'inicio'
if 'modo_contenido' not in st.session_state:
    st.session_state.modo_contenido = False
if 'url_listado' not in st.session_state:
    st.session_state.url_listado = []
if 'bloques_repetidos' not in st.session_state:
    st.session_state.bloques_repetidos = []

# Botón de inicio
if st.session_state.estado == 'inicio':
    if st.button("🚀 Iniciar proceso") and url_blog:
        st.session_state.estado = 'activo'
        st.session_state.modo_contenido = False
        st.session_state.url_listado = [{
            "url": limpiar_url(url_blog),
            "estado": "pendiente",
            "indexable": None,
            "codigo": None,
            "canonicals": [],
            "robots": None,
            "tipo_pagina": "home"
        }]
        st.rerun()
else:
    # Botones de control
    col1, col2 = st.columns(2)
    with col1:
        label = "⏸ Pausar proceso" if st.session_state.estado == 'activo' else "▶ Reanudar proceso"
        if st.button(label):
            st.session_state.estado = 'pausado' if st.session_state.estado == 'activo' else 'activo'
            st.rerun()

    with col2:
        indexables = [
            u for u in st.session_state.url_listado
            if u['estado'] == 'evaluado' and u['indexable'] and u.get('tipo_pagina') == 'contenido'
        ]
        if len(indexables) >= 3:
            label = "⏸ Pausar análisis de contenido" if st.session_state.modo_contenido else "🧠 Evaluar contenido de valor"
            if st.button(label):
                if st.session_state.modo_contenido:
                    st.session_state.modo_contenido = False
                    st.session_state.estado = 'activo'
                else:
                    st.session_state.modo_contenido = True
                    st.session_state.estado = 'pausado'
                    urls_validas = [u['url'] for u in indexables[:3]]
                    st.session_state.bloques_repetidos = detectar_bloques_comunes(urls_validas, n_docs=2)
                    st.session_state.url_listado = [
                        u for u in st.session_state.url_listado
                        if not u.get('indexable') or u['url'] in urls_validas
                    ]
                st.rerun()

# Mostrar progreso
if st.session_state.estado != 'inicio' and not st.session_state.modo_contenido:
    total = len(st.session_state.url_listado)
    evaluadas = len([u for u in st.session_state.url_listado if u['estado'] == 'evaluado'])
    pendientes = total - evaluadas

    st.markdown("### 📊 Progreso del análisis")
    st.progress(evaluadas / total if total else 0.0)
    st.markdown(f"**URLs evaluadas:** {evaluadas}")
    st.markdown(f"**URLs pendientes:** {pendientes}")
    st.markdown(f"**Total de URLs:** {total}")

    st.markdown("### 📄 URLs encontradas")

    datos = [{
        "Índice": i + 1,
        "URL": item["url"],
        "Estado": item["estado"],
        "Indexable": "✅" if item.get("indexable") else ("❌" if item.get("indexable") is False else "⏳"),
        "Tipo de página": item.get("tipo_pagina", "desconocido")
    } for i, item in enumerate(st.session_state.url_listado)]

    st.dataframe(pd.DataFrame(datos).set_index("Índice"), use_container_width=True)

# Proceso de indexabilidad
if st.session_state.estado == 'activo':
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
            break
    time.sleep(0.3)
    st.rerun()

# Proceso de evaluación de contenido de valor
if st.session_state.modo_contenido:
    urls_restantes = [
        u for u in st.session_state.url_listado
        if u['estado'] == 'evaluado' and u.get('indexable') and u.get('tipo_pagina') == 'contenido'
    ]
    if urls_restantes:
        siguiente = urls_restantes[0]
        st.markdown(f"### 🧪 Evaluando contenido único: {siguiente['url']}")
        texto = extraer_texto_limpio(siguiente['url'], st.session_state.bloques_repetidos)
        st.code(texto[:3000] or "(contenido vacío)", language="markdown")
    else:
        st.success("✅ Proceso de contenido finalizado.")

