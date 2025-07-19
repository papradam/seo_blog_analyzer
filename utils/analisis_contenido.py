# analisis_contenido.py
import streamlit as st
import time
from analisis_seo import analizar_texto
from analisis_tecnico import analizar_tecnico

def procesar_analisis_contenido():
    urls_restantes = list(st.session_state.contenido_variable.keys())
    if urls_restantes:
        siguiente = urls_restantes[0]
        bloques = st.session_state.contenido_variable[siguiente]

        texto = "\n\n".join([b["texto"] for b in bloques]).strip()
        html = "".join([b["html"] for b in bloques]).strip()

        if texto:
            resultado = analizar_texto(texto, html)
            st.session_state.resultados_seo[siguiente] = resultado
            st.session_state.texto_analizado_por_url[siguiente] = texto
            st.session_state.html_analizado_por_url[siguiente] = html

            resultado_tecnico = analizar_tecnico(siguiente)
            st.session_state.resultados_tecnicos[siguiente] = resultado_tecnico
        else:
            st.warning(f"El contenido de `{siguiente}` está vacío o fue totalmente filtrado.")

        del st.session_state.contenido_variable[siguiente]
        time.sleep(0.3)
        st.rerun()

def iniciar_analisis_contenido():
    st.session_state.modo_contenido = True
    st.session_state.estado = 'pausado'
