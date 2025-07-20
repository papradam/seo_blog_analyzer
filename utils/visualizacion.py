import streamlit as st

def mostrar_resultado_individual():
    """Muestra el sidebar con el botón de informe y el selector de URL."""
    urls_analizadas = [
        u['url'] for u in st.session_state.url_listado
        if u.get('tipo_pagina') == 'contenido' and u.get('analisis_contenido') == 'completado'
    ]

    if not urls_analizadas:
        return

    # Asegurar que la selección actual sea válida
    seleccion_actual = st.session_state.get("radio_seleccion_url")
    if seleccion_actual not in urls_analizadas:
        seleccion_actual = urls_analizadas[0]
        st.session_state["radio_seleccion_url"] = seleccion_actual

    with st.sidebar:
        st.markdown("## 📈 Resultados globales ")

        st.button(
            "📊 Resultados del análisis",
            key="btn_resultados_sidebar",
            on_click=lambda: st.session_state.update({
                "ver_informe": True,
                "radio_seleccion_url": None  # limpia selección individual
            })
        )

        st.markdown("---")
        st.markdown("## 🔗 Selecciona una URL")

        nueva_seleccion = st.radio(
            "URLs con análisis de contenido y técnico",
            urls_analizadas,
            index=urls_analizadas.index(st.session_state["radio_seleccion_url"])
            if st.session_state.get("radio_seleccion_url") in urls_analizadas
            else 0
        )

        # Si cambia la selección, actualiza estado y oculta informe
        if nueva_seleccion != st.session_state.get("radio_seleccion_url"):
            st.session_state["radio_seleccion_url"] = nueva_seleccion
            st.session_state["ver_informe"] = False

def mostrar_detalle_url(url):
    """Muestra el análisis SEO y técnico de una URL individual en pantalla principal."""
    datos_url = next((u for u in st.session_state.url_listado if u['url'] == url), None)
    if not datos_url:
        st.error("Error: datos de la URL no encontrados en el estado.")
        return

    res = datos_url.get('resultado_seo', {})
    tecnico = datos_url.get('resultado_tecnico', {})
    html = datos_url.get('bloques_html', [])

    st.markdown(f"## 📊 Detalle SEO para: `{url}`")
    st.markdown("---")
    st.markdown("## 🖋 Análisis de Contenido")

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
        with st.expander("🗾 Contenido analizado (Contenido único para esta página)"):
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
