# estado.py
import streamlit as st

def inicializar_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = 'inicio'
    if 'modo_contenido' not in st.session_state:
        st.session_state.modo_contenido = False
    if 'url_listado' not in st.session_state:
        st.session_state.url_listado = []
    if 'contenido_variable' not in st.session_state:
        st.session_state.contenido_variable = {}
    if 'resultados_seo' not in st.session_state:
        st.session_state.resultados_seo = {}
    if 'resultados_tecnicos' not in st.session_state:
        st.session_state.resultados_tecnicos = {}
    if 'texto_analizado_por_url' not in st.session_state:
        st.session_state.texto_analizado_por_url = {}
    if 'html_analizado_por_url' not in st.session_state:
        st.session_state.html_analizado_por_url = {}
