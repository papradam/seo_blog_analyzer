# visualizacion.py
import streamlit as st

def mostrar_resultado_individual():
    urls_analizadas = list(st.session_state.resultados_seo.keys())
    if urls_analizadas:
        st.sidebar.markdown("## 🔗 Selecciona una URL")
        seleccion = st.sidebar.radio(
            "URLs con análisis semántico",
            urls_analizadas,
            key="seleccion_url",
            index=0
        )
    else:
        seleccion = None

    # Mostrar mensaje mientras se evalúan más URLs
    if st.session_state.modo_contenido and st.session_state.contenido_variable:
        st.sidebar.info("🔄 Evaluando más URLs, actualizando automáticamente...")

    if seleccion:
        st.markdown(f"## 📊 Detalle SEO para: `{seleccion}`")
        res = st.session_state.resultados_seo[seleccion]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📖 Legibilidad", f"{res['indice_legibilidad']:.2f}")
            st.metric("🎓 Nivel educativo", res['nivel_educativo'])

        with col2:
            st.metric("📝 Palabras", res['num_palabras'])
            st.metric("📄 Párrafos", res['num_parrafos'])

        st.markdown("### 🔍 Palabras clave extraídas")
        for frase, count in res['palabras_clave']:
            st.write(f"- {frase} ({count})")

        if seleccion in st.session_state.html_analizado_por_url:
            with st.expander("🗾 Contenido analizado (HTML renderizado)"):
                html = st.session_state.html_analizado_por_url.get(seleccion, "")
                st.markdown(html, unsafe_allow_html=True)

        if seleccion in st.session_state.resultados_tecnicos:
            tecnico = st.session_state.resultados_tecnicos[seleccion]
            st.markdown("---")
            st.markdown("## 🛠️ Análisis Técnico")

            if 'error' in tecnico:
                st.error(f"Error al analizar: {tecnico['error']}")
            else:
                st.markdown(f"**Código de estado:** {tecnico['codigo']}")
                st.markdown(f"**Robots:** {tecnico['robots'] or 'N/A'}")
                st.markdown(f"**Canonical:** {', '.join(tecnico['canonicals']) if tecnico['canonicals'] else 'N/A'}")

                st.markdown("**Títulos:**")
                for t in tecnico['titles']:
                    st.write(f"- {t}")

                st.markdown("**Meta Descriptions:**")
                for d in tecnico['meta_descriptions']:
                    st.write(f"- {d}")

                st.markdown("**Meta Keywords:**")
                for k in tecnico['meta_keywords']:
                    st.write(f"- {k}")

                st.markdown("**Encabezados H1:**")
                for h in tecnico['h1s']:
                    st.write(f"- {h}")

                st.markdown("**Imágenes encontradas:**")
                for img in tecnico['imagenes']:
                    st.write(f"- 🖼 {img['URL']} | ALT: `{img['ALT']}` | Peso: {img['Peso (bytes)']} bytes")

                st.markdown("### 📦 Datos estructurados")
                if tecnico['datos_estructurados']:
                    for idx, schema in enumerate(tecnico['datos_estructurados']):
                        if '@graph' in schema and isinstance(schema['@graph'], list):
                            for subidx, sub_schema in enumerate(schema['@graph']):
                                tipo = sub_schema.get('@type', f"Schema #{idx+1}-{subidx+1}")
                                if isinstance(tipo, list):
                                    tipo = "/".join(tipo)
                                with st.expander(f"🔖 {tipo}"):
                                    st.json(sub_schema)
                        else:
                            tipo = schema.get('@type', f"Schema #{idx+1}")
                            if isinstance(tipo, list):
                                tipo = "/".join(tipo)
                            with st.expander(f"🔖 {tipo}"):
                                st.json(schema)
                else:
                    st.info("No se encontraron datos estructurados.")
