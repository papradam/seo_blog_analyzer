# utils/controles.py
import streamlit as st
from contenido_repetido import extraer_bloques_editoriales
from rapidfuzz import fuzz

def mostrar_botones_control(url_blog):
    col1, col2 = st.columns(2)

    # Botón de pausa/reanudar para indexabilidad
    with col1:
        label = "⏸ Pausar proceso" if st.session_state.estado == 'activo' else "▶ Reanudar proceso"
        if st.button(label):
            st.session_state.estado = 'pausado' if st.session_state.estado == 'activo' else 'activo'
            st.rerun()

    # Botón para iniciar/pausar el análisis de contenido
    with col2:
        indexables = [
            u for u in st.session_state.url_listado
            if u['estado'] == 'evaluado' and u['indexable'] and u.get('tipo_pagina') == 'contenido'
        ]

        if len(indexables) >= 3:
            label = "⏸ Pausar análisis de contenido" if st.session_state.modo_contenido else "🔍 Evaluar contenido de valor"
            if st.button(label):
                if st.session_state.modo_contenido:
                    st.session_state.modo_contenido = False
                    st.session_state.estado = 'activo'
                else:
                    st.session_state.modo_contenido = True
                    st.session_state.estado = 'pausado'

                    # Solo extraer bloques si aún no se ha hecho
                    ya_tienen_bloques = all(u["bloques_html"] for u in indexables)
                    if not ya_tienen_bloques:
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

                        for u in indexables:
                            bloques = extraer_bloques_editoriales(u['url'])
                            bloques_unicos = [b for b in bloques if b["html"] not in htmls_repetidos]
                            if bloques_unicos:
                                u["bloques_html"] = [b["html"] for b in bloques_unicos]
                                u["bloques_texto"] = [b["texto"] for b in bloques_unicos]
                                u["analisis_contenido"] = "pendiente"
                            else:
                                u["analisis_contenido"] = "omitido"

                        st.rerun()
