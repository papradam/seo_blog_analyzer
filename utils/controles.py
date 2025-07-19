# controles.py
import streamlit as st
from contenido_repetido import extraer_bloques_editoriales
from rapidfuzz import fuzz


def mostrar_botones_control(url_blog):
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

                    urls_para_comparar = [u['url'] for u in indexables[:3]]
                    bloques_por_url = {
                        url: extraer_bloques_editoriales(url)
                        for url in urls_para_comparar
                    }

                    bloques_repetidos = set()
                    for i in range(3):
                        for j in range(i + 1, 3):
                            for b1 in bloques_por_url[urls_para_comparar[i]]:
                                for b2 in bloques_por_url[urls_para_comparar[j]]:
                                    if fuzz.token_set_ratio(b1["texto"], b2["texto"]) >= 90:
                                        bloques_repetidos.add(b1["texto"])
                                        bloques_repetidos.add(b2["texto"])

                    htmls_repetidos = {
                        x["html"] for url in urls_para_comparar for x in bloques_por_url[url]
                        if x["texto"] in bloques_repetidos
                    }

                    st.session_state.contenido_variable = {}
                    for u in indexables:
                        todos_bloques = extraer_bloques_editoriales(u['url'])
                        bloques_unicos = [b for b in todos_bloques if b["html"] not in htmls_repetidos]
                        if bloques_unicos:
                            st.session_state.contenido_variable[u['url']] = bloques_unicos

                st.rerun()
