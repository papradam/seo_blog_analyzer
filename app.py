# app.py
import streamlit as st
import pandas as pd

from utils.estado import inicializar_estado
from utils.controles import mostrar_botones_control
from utils.progreso import mostrar_panel_progreso
from utils.indexabilidad import procesar_indexabilidad
from utils.analisis_contenido import procesar_analisis_contenido
from utils.visualizacion import mostrar_resultado_individual, mostrar_detalle_url
from utils.informe import mostrar_informe_resultados

# Configuración general
st.set_page_config(page_title="Análisis de Indexabilidad", layout="wide")
st.title("🔍 Análisis de Indexabilidad de URLs")

# Input principal
url_blog = st.text_input("📍 URL del blog principal")

def main():
    # Estado inicial
    inicializar_estado()

    # Fase de arranque
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

    # Progreso de indexabilidad (solo si no está en análisis de contenido)
    if st.session_state.estado != 'inicio' and not st.session_state.modo_contenido:
        mostrar_panel_progreso()

    # Evaluación de indexabilidad
    if st.session_state.estado == 'activo':
        procesar_indexabilidad(url_blog)

    # Análisis de contenido
    if st.session_state.modo_contenido:
        procesar_analisis_contenido()

    # === Visualización (pantalla principal dinámica) ===
    # 1. Mostrar siempre el sidebar
    mostrar_resultado_individual()

    # 2. Mostrar contenido en la pantalla principal según lo seleccionado
    if st.session_state.get("ver_informe", False):
        mostrar_informe_resultados()
    elif st.session_state.get("radio_seleccion_url"):
        mostrar_detalle_url(st.session_state["radio_seleccion_url"])

if __name__ == "__main__":
    main()
