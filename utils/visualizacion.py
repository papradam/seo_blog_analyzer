# utils/visualizacion.py
import streamlit as st

def mostrar_resultado_individual():
    # Filtrar solo URLs completadas de tipo contenido
    urls_analizadas = [
        u['url'] for u in st.session_state.url_listado
        if u.get('tipo_pagina') == 'contenido' and u.get('analisis_contenido') == 'completado'
    ]

    # Si no hay URLs listas, no mostrar la sección
    if not urls_analizadas:
        return

    # Sidebar con botón de informe y selector de URLs
    with st.sidebar:
        st.markdown("## 📊 Resultados Disponibles")
        # Botón que activa el informe en un solo clic
        st.button(
            "📊 Resultados del análisis",
            key="btn_resultados_sidebar",
            on_click=lambda: st.session_state.update({"ver_informe": True})
        )
        st.markdown("---")
        st.markdown("## 🔗 Selecciona una URL")
        seleccion = st.radio(
            "URLs con análisis semántico",
            urls_analizadas,
            key="radio_seleccion_url",
            index=0
        )

    # Mostrar detalles SEO y técnico de la URL seleccionada
    datos_url = next((u for u in st.session_state.url_listado if u['url'] == seleccion), None)
    if not datos_url:
        st.error("Error: datos de la URL no encontrados en el estado.")
        return

    res = datos_url.get('resultado_seo', {})
    tecnico = datos_url.get('resultado_tecnico', {})
    html = datos_url.get('bloques_html', [])

    st.markdown(f"## 📊 Detalle SEO para: `{seleccion}`")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📖 Legibilidad", f"{res.get('indice_legibilidad', 0):.2f}")
        st.metric("🎓 Nivel educativo", res.get('nivel_educativo', 'N/A'))
    with col2:
        st.metric("📝 Palabras", res.get('num_palabras', 0))
        st.metric("📄 Párrafos", res.get('num_parrafos', 0))

    st.markdown("### 🔍 Palabras clave extraídas")
    for frase, count in res.get('palabras_clave', []):
        st.write(f"- {frase} ({count})")

    if html:
        with st.expander("🗾 Contenido analizado (HTML renderizado)"):
            st.markdown("".join(html), unsafe_allow_html=True)

    if tecnico:
        st.markdown("---")
        st.markdown("## 🛠️ Análisis Técnico")
        if 'error' in tecnico:
            st.error(f"Error al analizar: {tecnico['error']}")
        else:
            st.markdown(f"**Código de estado:** {tecnico.get('codigo', 'N/A')}")
            st.markdown(f"**Robots:** {tecnico.get('robots') or 'N/A'}")
            st.markdown(f"**Canonical:** {', '.join(tecnico.get('canonicals') or []) or 'N/A'}")

            for label, field in [
                ("Títulos", 'titles'),
                ("Meta Descriptions", 'meta_descriptions'),
                ("Meta Keywords", 'meta_keywords'),
                ("Encabezados H1", 'h1s')
            ]:
                st.markdown(f"**{label}:**")
                for item in tecnico.get(field, []):
                    st.write(f"- {item}")

            st.markdown("**Imágenes encontradas:**")
            for img in tecnico.get('imagenes', []):
                st.write(f"- 🖼 {img.get('URL')} | ALT: `{img.get('ALT')}` | Peso: {img.get('Peso (bytes)', 0)} bytes")

            st.markdown("### 📦 Datos estructurados")
            esquemas = tecnico.get('datos_estructurados', [])
            if esquemas:
                for idx, schema in enumerate(esquemas):
                    grafos = schema.get('@graph') if '@graph' in schema else [schema]
                    for sub in grafos:
                        tipo = sub.get('@type', f"Schema #{idx+1}")
                        if isinstance(tipo, list): tipo = "/".join(tipo)
                        with st.expander(f"🔖 {tipo}"):
                            st.json(sub)
            else:
                st.info("No se encontraron datos estructurados.")
