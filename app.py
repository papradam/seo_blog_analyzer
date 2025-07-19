# app.py (versión modularizada)
import streamlit as st
import pandas as pd
import time

from utils.estado import inicializar_estado
from utils.controles import mostrar_botones_control
from utils.progreso import mostrar_panel_progreso
from utils.indexabilidad import procesar_indexabilidad, expandir_enlaces_si_indexable
from utils.analisis_contenido import iniciar_analisis_contenido, procesar_analisis_contenido
from utils.visualizacion import mostrar_resultado_individual
from utils.informe import mostrar_informe_resultados

st.set_page_config(page_title="Análisis de Indexabilidad", layout="wide")
st.title("🔍 Análisis de Indexabilidad de URLs")

url_blog = st.text_input("📍 URL del blog principal")

# Estado inicial
def main():
    inicializar_estado()

    # Mostrar botón de informe solo si hay resultados
    if st.session_state.resultados_seo:
        with st.sidebar:
            if st.button("📊 Resultados del análisis"):
                st.session_state.ver_informe = True

    if st.session_state.get("ver_informe", False):
        mostrar_informe_resultados()
        st.stop()

    if st.session_state.estado == 'inicio':
        if st.button("🚀 Iniciar proceso") and url_blog:
            st.session_state.estado = 'activo'
            st.session_state.modo_contenido = False
            st.session_state.url_listado = [
                {
                    "url": url_blog,
                    "estado": "pendiente",
                    "indexable": None,
                    "codigo": None,
                    "canonicals": [],
                    "robots": None,
                    "tipo_pagina": "home"
                }
            ]
            st.rerun()
    else:
        mostrar_botones_control(url_blog)

    if st.session_state.estado != 'inicio' and not st.session_state.modo_contenido:
        mostrar_panel_progreso()

    if st.session_state.estado == 'activo':
        procesar_indexabilidad(url_blog)

    if st.session_state.modo_contenido:
        procesar_analisis_contenido()

    mostrar_resultado_individual()

if __name__ == "__main__":
    main()
