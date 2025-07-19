import streamlit as st
import time
import pandas as pd
from index_check import limpiar_url, obtener_enlaces_internos, analizar_indexabilidad, clasificar_tipo_pagina
from contenido_repetido import extraer_bloques_editoriales
from analisis_seo import analizar_texto
from analisis_tecnico import analizar_tecnico
from rapidfuzz import fuzz

st.set_page_config(page_title="Análisis de Indexabilidad", layout="wide")
st.title("🔍 Análisis de Indexabilidad de URLs")

url_blog = st.text_input("📍 URL del blog principal")

# Estado inicial
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

# Botón de inicio
if st.session_state.estado == 'inicio':
    if st.button("🚀 Iniciar proceso") and url_blog:
        st.session_state.estado = 'activo'
        st.session_state.modo_contenido = False
        st.session_state.url_listado = [{
            "url": limpiar_url(url_blog),
            "estado": "pendiente",
            "indexable": None,
            "codigo": None,
            "canonicals": [],
            "robots": None,
            "tipo_pagina": "home"
        }]
        st.rerun()
else:
    # Botones de control
    col1, col2 = st.columns(2)
    with col1:
        label = "⏸ Pausar proceso" if st.session_state.estado == 'activo' else "▶ Reanudar proceso"
        if st.button(label):
            st.session_state.estado = 'pausado' if st.session_state.estado == 'activo' else 'activo'
            st.rerun()

    with col2:
        indexables = [
            u for u in st.session_state.url_listado
            if u['estado'] == 'evaluado' and u['indexable'] and u.get('tipo_pagina') == 'contenido'
        ]
        if len(indexables) >= 3:
            label = "⏸ Pausar análisis de contenido" if st.session_state.modo_contenido else "🧠 Evaluar contenido de valor"
            if st.button(label):
                if st.session_state.modo_contenido:
                    st.session_state.modo_contenido = False
                    st.session_state.estado = 'activo'
                else:
                    st.session_state.modo_contenido = True
                    st.session_state.estado = 'pausado'

                    # Detectar bloques repetidos entre 3 URLs
                    urls_para_comparar = [u['url'] for u in indexables[:3]]
                    bloques_por_url = {
                        url: extraer_bloques_editoriales(url)
                        for url in urls_para_comparar
                    }

                    bloques_repetidos = set()
                    for i in range(3):
                        for j in range(i + 1, 3):
                            for b1 in bloques_por_url[urls_para_comparar[i]]:
                                for b2 in bloques_por_url[urls_para_comparar[j]]:
                                    if fuzz.token_set_ratio(b1["texto"], b2["texto"]) >= 90:
                                        bloques_repetidos.add(b1["texto"])
                                        bloques_repetidos.add(b2["texto"])

                    # Aplicar filtrado a todas las URLs válidas
                    st.session_state.contenido_variable = {}
                    for u in indexables:
                        todos_bloques = extraer_bloques_editoriales(u['url'])
                        bloques_unicos = [b for b in todos_bloques if b["html"] not in {x["html"] for url in urls_para_comparar for x in bloques_por_url[url] if x["texto"] in bloques_repetidos}]
                        if bloques_unicos:
                            st.session_state.contenido_variable[u['url']] = bloques_unicos

                st.rerun()

# Mostrar progreso
if st.session_state.estado != 'inicio' and not st.session_state.modo_contenido:
    total = len(st.session_state.url_listado)
    evaluadas = len([u for u in st.session_state.url_listado if u['estado'] == 'evaluado'])
    pendientes = total - evaluadas

    st.markdown("### 📊 Progreso del análisis")
    st.progress(evaluadas / total if total else 0.0)
    st.markdown(f"**URLs evaluadas:** {evaluadas}")
    st.markdown(f"**URLs pendientes:** {pendientes}")
    st.markdown(f"**Total de URLs:** {total}")

    st.markdown("### 📄 URLs encontradas")

    datos = [{
        "Índice": i + 1,
        "URL": item["url"],
        "Estado": item["estado"],
        "Indexable": "✅" if item.get("indexable") else ("❌" if item.get("indexable") is False else "⏳"),
        "Tipo de página": item.get("tipo_pagina", "desconocido")
    } for i, item in enumerate(st.session_state.url_listado)]

    st.dataframe(pd.DataFrame(datos).set_index("Índice"), use_container_width=True)

# Proceso de indexabilidad
if st.session_state.estado == 'activo':
    for registro in st.session_state.url_listado:
        if registro['estado'] == 'pendiente':
            url_actual = limpiar_url(registro['url'])
            registro['estado'] = 'evaluado'
            codigo, canonicals, robots, indexable = analizar_indexabilidad(url_actual)
            registro['indexable'] = indexable
            registro['codigo'] = codigo
            registro['canonicals'] = canonicals
            registro['robots'] = robots

            if indexable:
                nuevos = obtener_enlaces_internos(url_actual, url_blog)
                for nueva_url in nuevos:
                    nueva_url_limpia = limpiar_url(nueva_url)
                    if not any(u['url'] == nueva_url_limpia for u in st.session_state.url_listado):
                        st.session_state.url_listado.append({
                            "url": nueva_url_limpia,
                            "estado": "pendiente",
                            "indexable": None,
                            "codigo": None,
                            "canonicals": [],
                            "robots": None,
                            "tipo_pagina": clasificar_tipo_pagina(nueva_url_limpia)
                        })
            break
    time.sleep(0.3)
    st.rerun()

# Proceso de evaluación de contenido de valor
if st.session_state.modo_contenido:
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

# Mostrar análisis SEO disponibles mientras se evalúa
urls_analizadas = list(st.session_state.resultados_seo.keys())
if urls_analizadas:
    st.sidebar.markdown("## 🔗 Selecciona una URL")
    seleccion = st.sidebar.radio(
        "URLs con análisis semántico",
        urls_analizadas,
        key="seleccion_url"
    )
else:
    seleccion = None

# Mostrar detalle del análisis
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

    # Mostrar análisis técnico
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
