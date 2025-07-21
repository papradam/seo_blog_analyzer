import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud

def graficar_barra(serie, color, titulo=None, ylabel=None, height=2.5):
    fig, ax = plt.subplots(figsize=(6, height))
    serie.plot(kind='bar', ax=ax, color=color)
    if titulo:
        ax.set_title(titulo)
    if ylabel:
        ax.set_ylabel(ylabel)
    st.pyplot(fig)

def mostrar_informe_resultados():
    st.title("Informe General del Análisis SEO")

    urls_completadas = [u for u in st.session_state.url_listado if u.get("analisis_contenido") == "completado"]
    if not urls_completadas:
        st.warning("Aún no hay análisis de contenido disponibles.")
        return

    # ---------------- SEMÁNTICO ----------------
    st.header("Análisis Semántico del Contenido")
    datos, palabras_clave_totales, detalle_urls = [], [], []

    for u in urls_completadas:
        res = u["resultado_seo"]
        datos.append({
            "URL": u["url"],
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"]
        })
        palabras_clave_totales.extend([kw for kw, _ in res["palabras_clave"]])
        detalle_urls.append({
            "URL": u["url"],
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"],
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Palabras clave": ", ".join([f"{kw} ({count})" for kw, count in res["palabras_clave"]]) or "-"
        })

    df = pd.DataFrame(datos)

    st.subheader("Promedios")
    col1, col2, col3 = st.columns(3)
    col1.metric("Legibilidad", f"{df['Legibilidad'].mean():.2f}")
    col2.metric("Palabras", f"{df['Palabras'].mean():.0f}")
    col3.metric("Párrafos", f"{df['Párrafos'].mean():.0f}")

    st.subheader("Distribución de Palabras y Párrafos")
    col4, col5 = st.columns(2)

    with col4:
        df["Rango de palabras"] = pd.cut(df["Palabras"], bins=[0,300,600,900,1200,1500,2000,3000,5000,10000])
        graficar_barra(df["Rango de palabras"].value_counts().sort_index(), "#69b3a2", "Distribución de Palabras", "Cantidad de URLs")

    with col5:
        df["Rango de párrafos"] = pd.cut(df["Párrafos"], bins=[0,3,6,9,12,15,20,30,50,100])
        graficar_barra(df["Rango de párrafos"].value_counts().sort_index(), "#ffb347", "Distribución de Párrafos", "Cantidad de URLs")

    st.subheader("Nivel Educativo Estimado")
    st.bar_chart(df["Nivel educativo"].value_counts())

    st.subheader("Nube de Palabras Clave")
    if palabras_clave_totales:
        wc = WordCloud(width=800, height=300, background_color="white").generate(" ".join(palabras_clave_totales))
        fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
        ax_wc.imshow(wc, interpolation='bilinear')
        ax_wc.axis("off")
        st.pyplot(fig_wc)
    else:
        st.info("No se han identificado palabras clave.")

    with st.expander("Ver tabla de análisis por URL"):
        st.dataframe(pd.DataFrame(detalle_urls).set_index("URL"), use_container_width=True)

    st.divider()

    # ---------------- TÉCNICO ----------------
    st.header("Análisis Técnico")

    tecnicos = [u.get("resultado_tecnico", {}) for u in urls_completadas]
    codigos, robots_list = [], []
    canonicals_count = {"Falta": 0, "Múltiple": 0}

    for res in tecnicos:
        codigos.append(res.get("codigo"))
        robots_list.append(res.get("robots") or "N/A")
        canonicals = res.get("canonicals", [])
        if not canonicals:
            canonicals_count["Falta"] += 1
        elif len(canonicals) > 1:
            canonicals_count["Múltiple"] += 1
        # Si hay solo una canonical, no se cuenta como múltiple

    st.subheader("Indexabilidad")
    colx1, colx2, colx3 = st.columns(3)

    with colx1:
        st.markdown("#### Código de estado")
        if codigos:
            codigos_series = pd.Series(codigos).value_counts()
            fig, ax = plt.subplots()
            ax.pie(codigos_series, labels=codigos_series.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

    with colx2:
        st.markdown("#### Meta Robots")
        graficar_barra(pd.Series(robots_list).value_counts(), "#6c9fbc", "Distribución de Robots", "Cantidad de URLs", height=2.5)

    with colx3:
        st.markdown("#### Canonicals")
        graficar_barra(pd.Series(canonicals_count), "#d4a5a5", "Tipos de Canonicals", "Cantidad de URLs", height=2.5)
    
    st.subheader("Etiquetas")

    def procesar_meta(tecnicos):
        resultados = {
            "titles": {"Falta": 0, "Duplicado": 0, ">60 caracteres": 0, "<30 caracteres": 0, "Igual que h1": 0, "Múltiple": 0},
            "descriptions": {"Falta": 0, "Duplicado": 0, ">150 caracteres": 0, "<120 caracteres": 0, "Múltiple": 0},
            "keywords": {"Falta": 0, "Duplicado": 0, "Múltiple": 0},
            "h1s": {"Falta": 0, "Duplicado": 0, ">70 caracteres": 0, "Múltiple": 0},
        }
        trackers = {"titles": {}, "descriptions": {}, "keywords": {}, "h1s": {}}

        for res in tecnicos:
            ts, ds, ks, h1s = res.get("titles", []), res.get("meta_descriptions", []), res.get("meta_keywords", []), res.get("h1s", [])

            def contar(meta, lista, minlen, maxlen, igual_h1=False):
                if not lista:
                    resultados[meta]["Falta"] += 1
                else:
                    if len(lista) > 1:
                        resultados[meta]["Múltiple"] += 1
                    valor = lista[0].strip().lower()
                    trackers[meta][valor] = trackers[meta].get(valor, 0) + 1
                    if len(valor) < minlen:
                        resultados[meta][f"<{minlen} caracteres"] += 1
                    if len(valor) > maxlen:
                        resultados[meta][f">{maxlen} caracteres"] += 1
                    if igual_h1 and h1s and valor == h1s[0].strip().lower():
                        resultados["titles"]["Igual que h1"] += 1

            contar("titles", ts, 30, 60, igual_h1=True)
            contar("descriptions", ds, 120, 150)
            contar("keywords", ks, 0, 999)
            contar("h1s", h1s, 0, 70)

        for meta in trackers:
            resultados[meta]["Duplicado"] = sum(1 for v in trackers[meta].values() if v > 1)
        return resultados

    resultados_meta = procesar_meta(tecnicos)

    colm1, colm2 = st.columns(2)
    with colm1:
        st.markdown("#### Titles")
        graficar_barra(pd.Series(resultados_meta["titles"]), "#8faadc", height=2.5)

    with colm2:
        st.markdown("#### Meta Descriptions")
        graficar_barra(pd.Series(resultados_meta["descriptions"]), "#fac27b", height=2.5)

    colm3, colm4 = st.columns(2)
    with colm3:
        st.markdown("#### Meta Keywords")
        graficar_barra(pd.Series(resultados_meta["keywords"]), "#d88fa3", height=2.5)

    with colm4:
        st.markdown("#### Encabezados H1")
        graficar_barra(pd.Series(resultados_meta["h1s"]), "#94d0cc", height=2.5)

    # Evaluación de imágenes
    st.markdown("### Evaluación de Imágenes")

    imagenes_unicas = {}
    detalle_imagenes = []

    for res in tecnicos:
        for img in res.get("imagenes", []):
            url = img.get("URL", "").strip()
            if url and url not in imagenes_unicas:
                alt = img.get("ALT", "").strip()
                peso = img.get("Peso (bytes)", 0)
                imagenes_unicas[url] = {"ALT": alt, "Peso": peso}
                detalle_imagenes.append({
                    "URL": url,
                    "ALT": alt,
                    "Peso (bytes)": peso,
                    "Falta ALT": not bool(alt),
                    "ALT > 100": len(alt) > 100,
                    "> 100KB": peso > 100_000
                })

    alt_largos = sum(1 for i in imagenes_unicas.values() if len(i["ALT"]) > 100)
    sin_alt = sum(1 for i in imagenes_unicas.values() if not i["ALT"])
    peso_alto = sum(1 for i in imagenes_unicas.values() if i["Peso"] > 100_000)

    imagenes_eval = {
        "Falta ALT": sin_alt,
        "ALT > 100 caracteres": alt_largos,
        "> 100KB": peso_alto
    }

    fig, ax = plt.subplots(figsize=(6, 2))  # <-- Tamaño más pequeño (ancho=6, alto=2.5)
    pd.Series(imagenes_eval).plot(kind="bar", ax=ax, color="#cdb4db")
    ax.set_ylabel("Cantidad de imágenes únicas")
    ax.set_title("Problemas comunes en imágenes")
    st.pyplot(fig)

    if detalle_imagenes:
        with st.expander("Ver detalle de imágenes únicas"):
            df_img = pd.DataFrame(detalle_imagenes)
            df_img_visual = df_img[["URL", "ALT", "Peso (bytes)", "Falta ALT", "ALT > 100", "> 100KB"]].copy()
            df_img_visual.set_index("URL", inplace=True)
            st.dataframe(df_img_visual, use_container_width=True)
    else:
        st.info("No se han identificado imágenes únicas.")

   

   
    # ---------------- DATOS ESTRUCTURADOS ----------------
    st.header("Datos Estructurados")

    tipo_schema = {}
    detalle_schema = {}
    resumen_tecnico = []

    for u in urls_completadas:
        res = u.get("resultado_tecnico", {})
        resumen = {
            "URL": u["url"],
            "Código de estado": res.get("codigo", "-"),
            "Meta Robots": res.get("robots", "-"),
            "Canonical": ", ".join(res.get("canonicals", []) or ["-"]),
            "Title": ", ".join(res.get("titles", []) or ["-"]),
            "Meta descripción": ", ".join(res.get("meta_descriptions", []) or ["-"]),
            "Meta keywords": ", ".join(res.get("meta_keywords", []) or ["-"]),
            "H1": ", ".join(res.get("h1s", []) or ["-"]),
            "Imágenes": ", ".join(sorted(set(img.get("URL", "") for img in res.get("imagenes", [])))) or "-",
            "Tipos de datos estructurados": "-"
        }

        tipos_actuales = set()
        vistos = set()
        for schema in res.get("datos_estructurados", []):
            bloques = schema.get("@graph", [schema])
            for item in bloques:
                tipo = item.get("@type")
                if not tipo:
                    continue
                if isinstance(tipo, list):
                    tipo = "/".join(tipo)
                clave_id = f"{u['url']}::{tipo}"
                if clave_id in vistos:
                    continue
                vistos.add(clave_id)

                tipo_schema[tipo] = tipo_schema.get(tipo, 0) + 1
                if tipo not in detalle_schema:
                    detalle_schema[tipo] = []
                detalle_schema[tipo].append((u["url"], item))
                tipos_actuales.add(tipo)

        resumen["Tipos de datos estructurados"] = ", ".join(sorted(tipos_actuales)) or "-"
        resumen_tecnico.append(resumen)

    if tipo_schema:
        st.bar_chart(pd.Series(tipo_schema).sort_values(ascending=False))
        for tipo, elementos in detalle_schema.items():
            with st.expander(f"{tipo} ({len(elementos)})"):
                for url, item in elementos:
                    st.markdown(f"**URL:** {url}")
                    for k, v in item.items():
                        if k != "@type":
                            st.write(f"- **{k}**: {v}")
                    st.markdown("---")
    else:
        st.info("No se encontraron datos estructurados.")

    st.divider()
    with st.expander("Ver tabla resumen técnica por URL"):
        df_resumen = pd.DataFrame(resumen_tecnico)
        st.dataframe(df_resumen, use_container_width=True)
