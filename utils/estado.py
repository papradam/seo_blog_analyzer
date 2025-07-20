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

    if 'ver_informe' not in st.session_state:
        st.session_state.ver_informe = False
