import streamlit as st
from analisis_seo import analizar_texto
from analisis_tecnico import analizar_tecnico

def procesar_analisis_contenido():
    urls_totales = [
        u for u in st.session_state.url_listado
        if u.get("analisis_contenido") in [None, "pendiente", "completado", "omitido"]
        and u.get("bloques_texto")
    ]
    total = len(urls_totales)
    completadas = 0

    # Contenedores temporales
    texto_estado = st.empty()
    barra = st.empty()

    texto_estado.markdown("## Análisis de contenido en curso...")
    progreso = barra.progress(0)

    while st.session_state.modo_contenido:
        url_pendiente = next(
            (u for u in st.session_state.url_listado if u.get("analisis_contenido") == "pendiente"),
            None
        )

        if not url_pendiente:
            break

        texto = "\n\n".join(url_pendiente.get("bloques_texto", [])).strip()
        html = "".join(url_pendiente.get("bloques_html", [])).strip()

        if texto:
            url_pendiente["resultado_seo"] = analizar_texto(texto, html)
            url_pendiente["resultado_tecnico"] = analizar_tecnico(url_pendiente["url"])
            url_pendiente["analisis_contenido"] = "completado"
        else:
            url_pendiente["analisis_contenido"] = "omitido"
            st.warning(f"⚠ El contenido de `{url_pendiente['url']}` está vacío o fue filtrado.")

        completadas = sum(1 for u in st.session_state.url_listado if u.get("analisis_contenido") == "completado")
        progreso.progress(completadas / total if total else 1.0)

        if not st.session_state.modo_contenido:
            st.warning("⏸ Análisis pausado por el usuario.")
            break

    # Limpiar los elementos temporales
    texto_estado.empty()
    barra.empty()

    if completadas == total:
        st.success("✅ Análisis de contenido finalizado.")
