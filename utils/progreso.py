# progreso.py
import streamlit as st
import pandas as pd

def mostrar_panel_progreso():
    total = len(st.session_state.url_listado)
    evaluadas = len([u for u in st.session_state.url_listado if u['estado'] == 'evaluado'])
    pendientes = total - evaluadas
    contenido_valor = len([
        u for u in st.session_state.url_listado
        if u['estado'] == 'evaluado' and u['indexable'] and u.get('tipo_pagina') == 'contenido'
    ])

    st.markdown("### 📊 Progreso del análisis")
    st.progress(evaluadas / total if total else 0.0)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**URLs evaluadas:** {evaluadas}")
        st.markdown(f"**URLs pendientes:** {pendientes}")
    with col2:
        st.markdown(f"**Total de URLs:** {total}")
        st.markdown(f"**Contenido de valor encontrado:** {contenido_valor}")

    st.markdown("### 📄 URLs encontradas")
    datos = [
        {
            "Índice": i + 1,
            "URL": item["url"],
            "Estado": item["estado"],
            "Indexable": "✅" if item.get("indexable") else ("❌" if item.get("indexable") is False else "⏳"),
            "Tipo de página": item.get("tipo_pagina", "desconocido")
        }
        for i, item in enumerate(st.session_state.url_listado)
    ]

    st.dataframe(pd.DataFrame(datos).set_index("Índice"), use_container_width=True)
