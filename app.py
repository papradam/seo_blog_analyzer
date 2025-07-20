# app.py
import streamlit as st
import pandas as pd

from utils.estado import inicializar_estado
from utils.controles import mostrar_botones_control
from utils.progreso import mostrar_panel_progreso
from utils.indexabilidad import procesar_indexabilidad
from utils.analisis_contenido import procesar_analisis_contenido
from utils.visualizacion import mostrar_resultado_individual
from utils.informe import mostrar_informe_resultados

st.set_page_config(page_title="Análisis de Indexabilidad", layout="wide")
st.title("🔍 Análisis de Indexabilidad de URLs")

url_blog = st.text_input("📍 URL del blog principal")

def main():
    inicializar_estado()

    # Si el usuario ya pidió ver el informe, lo muestro y paro la app
    if st.session_state.get("ver_informe", False):
        mostrar_informe_resultados()
        st.stop()

    # Paso inicial: solicitar la URL y arrancar
    if st.session_state.estado == 'inicio':
        if st.button("🚀 Iniciar proceso") and url_blog:
            st.session_state.estado = 'activo'
            st.session_state.modo_contenido = False
            st.session_state.url_listado = [{
                "url": url_blog,
                "estado": "pendiente",
                "indexable": None,
                "codigo": None,
                "canonicals": [],
                "robots": None,
                "tipo_pagina": "home",
                "analisis_contenido": None,
                "resultado_seo": None,
                "resultado_tecnico": None,
                "bloques_html": None,
                "bloques_texto": None
            }]
            st.rerun()
    else:
        mostrar_botones_control(url_blog)

    # Barra de progreso de indexabilidad (antes de contenido)
    if st.session_state.estado != 'inicio' and not st.session_state.modo_contenido:
        mostrar_panel_progreso()

    # Lógica de indexabilidad
    if st.session_state.estado == 'activo':
        procesar_indexabilidad(url_blog)

    # Lógica de análisis de contenido
    if st.session_state.modo_contenido:
        procesar_analisis_contenido()

    # Solo queda llamar a la visualización de resultados (que ya inyecta el botón correcto)
    mostrar_resultado_individual()

if __name__ == "__main__":
    main()
