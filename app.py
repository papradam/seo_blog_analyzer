import streamlit as st
import time
from index_check import limpiar_url, obtener_enlaces_internos, analizar_indexabilidad

st.set_page_config(page_title="Análisis de Indexabilidad", layout="wide")
st.title("🔍 Análisis de Indexabilidad de URLs")

url_blog = st.text_input("📍 URL del blog principal")

# Estado inicial
if 'estado' not in st.session_state:
    st.session_state.estado = 'inicio'
if 'url_listado' not in st.session_state:
    st.session_state.url_listado = []

# Botón de inicio y control
if st.session_state.estado == 'inicio':
    if st.button("🚀 Iniciar proceso") and url_blog:
        st.session_state.estado = 'activo'
        st.session_state.url_listado = [{
            "url": limpiar_url(url_blog),
            "estado": "pendiente",
            "indexable": None,
            "codigo": None,
            "canonicals": [],
            "robots": None
        }]
        st.rerun()
else:
    if st.session_state.estado == 'activo':
        if st.button("⏸ Pausar proceso"):
            st.session_state.estado = 'pausado'
            st.rerun()
    elif st.session_state.estado == 'pausado':
        if st.button("▶ Reanudar proceso"):
            st.session_state.estado = 'activo'
            st.rerun()

# Progreso y métricas
if st.session_state.estado != 'inicio':
    total = len(st.session_state.url_listado)
    evaluadas = len([u for u in st.session_state.url_listado if u['estado'] == 'evaluado'])
    pendientes = total - evaluadas

    st.markdown("### 📊 Progreso del análisis")
    st.progress(evaluadas / total if total else 0.0)

    st.markdown(f"**URLs evaluadas:** {evaluadas}")
    st.markdown(f"**URLs pendientes:** {pendientes}")
    st.markdown(f"**Total de URLs:** {total}")

    st.markdown("### 📄 URLs encontradas")
    for i, item in enumerate(st.session_state.url_listado):
        index_str = "✅" if item.get("indexable") else ("❌" if item.get("indexable") is False else "⏳")
        canon_count = len(item.get("canonicals") or [])
        st.write(f"{i+1}. [{item['estado'].upper()}] {index_str} {item['url']} (Canonicals: {canon_count})")

# Proceso principal paso a paso
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
                            "robots": None
                        })
            break  # Procesa solo una por ejecución

    time.sleep(0.3)
    st.rerun()

if st.session_state.url_listado and all(u['estado'] == 'evaluado' for u in st.session_state.url_listado):
    st.success("✅ Proceso finalizado. Todas las URLs han sido evaluadas.")
