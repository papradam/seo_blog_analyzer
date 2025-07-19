# informe.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud


def mostrar_informe_resultados():
    st.title("📊 Informe General del Análisis SEO")

    if not st.session_state.resultados_seo:
        st.warning("Aún no hay análisis de contenido disponibles.")
        return

    datos = []
    palabras_clave_totales = []
    detalle_urls = []

    for url, res in st.session_state.resultados_seo.items():
        datos.append({
            "URL": url,
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"]
        })
        palabras_clave_totales.extend([frase for frase, _ in res["palabras_clave"]])

        detalle_urls.append({
            "URL": url,
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"],
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Palabras clave": ", ".join([f"{frase} ({count})" for frase, count in res["palabras_clave"]]) or "-"
        })

    df = pd.DataFrame(datos)

    st.markdown("### 🧮 Métricas promedio generales")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📖 Legibilidad promedio", f"{df['Legibilidad'].mean():.2f}")
    with col2:
        st.metric("📝 Palabras promedio", f"{df['Palabras'].mean():.0f}")
    with col3:
        st.metric("📄 Párrafos promedio", f"{df['Párrafos'].mean():.0f}")

    st.markdown("### 📏 Distribución por rangos de contenido")
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("#### 📊 Rango de palabras")
        bins_palabras = [0, 300, 600, 900, 1200, 1500, 2000, 3000, 5000, 10000]
        df["Rango de palabras"] = pd.cut(df["Palabras"], bins=bins_palabras)
        palabras_rangos = df["Rango de palabras"].value_counts().sort_index()
        fig1, ax1 = plt.subplots()
        palabras_rangos.plot(kind='bar', ax=ax1, color="#69b3a2")
        ax1.set_xlabel("Franja de palabras")
        ax1.set_ylabel("Cantidad de URLs")
        ax1.set_title("Distribución de palabras")
        st.pyplot(fig1)

    with col5:
        st.markdown("#### 📊 Rango de párrafos")
        bins_parrafos = [0, 3, 6, 9, 12, 15, 20, 30, 50, 100]
        df["Rango de párrafos"] = pd.cut(df["Párrafos"], bins=bins_parrafos)
        parrafos_rangos = df["Rango de párrafos"].value_counts().sort_index()
        fig2, ax2 = plt.subplots()
        parrafos_rangos.plot(kind='bar', ax=ax2, color="#ffb347")
        ax2.set_xlabel("Franja de párrafos")
        ax2.set_ylabel("Cantidad de URLs")
        ax2.set_title("Distribución de párrafos")
        st.pyplot(fig2)

    st.markdown("### 🎓 Nivel educativo estimado (conteo)")
    nivel_counts = df["Nivel educativo"].value_counts()
    st.bar_chart(nivel_counts)

    st.markdown("### ☁️ Nube de palabras clave")
    if palabras_clave_totales:
        texto_keywords = " ".join(palabras_clave_totales)
        wordcloud = WordCloud(width=800, height=300, background_color="white").generate(texto_keywords)
        fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
        ax_wc.imshow(wordcloud, interpolation='bilinear')
        ax_wc.axis("off")
        st.pyplot(fig_wc)
    else:
        st.info("No se han identificado palabras clave en los análisis.")

    st.markdown("### 📄 Detalle por URL")
    with st.expander("Ver tabla completa de análisis por URL"):
        detalle_df = pd.DataFrame(detalle_urls).set_index("URL")
        st.dataframe(detalle_df, use_container_width=True)

    # 🔧 Sección técnica: encabezado
    st.title("🛠️ Análisis Técnico")

    # Procesamiento inicial de resultados técnicos
    tecnicos = st.session_state.get("resultados_tecnicos", {})
    codigos = []
    robots_list = []
    canonicals_count = {"Falta": 0, "Múltiple": 0}

    for res in tecnicos.values():
        if "codigo" in res:
            codigos.append(res["codigo"])
        if "robots" in res:
            robots_list.append(res["robots"] or "N/A")
        if "canonicals" in res:
            canonicals = res["canonicals"]
            if not canonicals:
                canonicals_count["Falta"] += 1
            elif len(canonicals) > 1:
                canonicals_count["Múltiple"] += 1
            else:
                canonicals_count["Múltiple"] += 1

    st.markdown("### 🔎 Análisis de indexabilidad")
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
        if robots_list:
            robots_series = pd.Series(robots_list).value_counts()
            fig, ax = plt.subplots()
            robots_series.plot(kind="bar", ax=ax, color="#6c9fbc")
            ax.set_ylabel("Cantidad de URLs")
            ax.set_title("Distribución de robots")
            st.pyplot(fig)
        else:
            st.info("No hay datos de robots disponibles.")

    with colx3:
        st.markdown("#### Canonicals")
        fig, ax = plt.subplots()
        pd.Series(canonicals_count).plot(kind="bar", ax=ax, color="#d4a5a5")
        ax.set_ylabel("Cantidad de URLs")
        ax.set_title("Tipos de canonicals")
        st.pyplot(fig)

    # 🧠 Subtítulo de metadatos
    st.markdown("### 🧾 Meta datos")

    # Inicializar contadores
    titles = {"Falta": 0, "Duplicado": 0, ">60 caracteres": 0, "<30 caracteres": 0, "Igual que h1": 0, "Múltiple": 0}
    descriptions = {"Falta": 0, "Duplicado": 0, ">150 caracteres": 0, "<120 caracteres": 0, "Múltiple": 0}
    keywords = {"Falta": 0, "Duplicado": 0, "Múltiple": 0}

    title_global_tracker = {}
    desc_global_tracker = {}
    keyw_global_tracker = {}

    all_titles = []
    all_descriptions = []
    all_keywords = []

    for url, res in tecnicos.items():
        # Titles
        ts = res.get("titles", [])
        all_titles.extend(ts)
        if not ts:
            titles["Falta"] += 1
        for t in ts:
            title_global_tracker[t.strip().lower()] = title_global_tracker.get(t.strip().lower(), 0) + 1
        else:
            if len(ts) > 1:
                titles["Múltiple"] += 1
            if len(set(ts)) == 1:
                titles["Duplicado"] += 1
            if len(ts[0]) > 60:
                titles[">60 caracteres"] += 1
            if len(ts[0]) < 30:
                titles["<30 caracteres"] += 1

        # H1 para comparar
        h1 = res.get("h1s", [])
        if ts and h1 and ts[0].strip().lower() == h1[0].strip().lower():
            titles["Igual que h1"] += 1

        # Descriptions
        ds = res.get("meta_descriptions", [])
        all_descriptions.extend(ds)
        if not ds:
            descriptions["Falta"] += 1
        for d in ds:
            desc_global_tracker[d.strip().lower()] = desc_global_tracker.get(d.strip().lower(), 0) + 1
        else:
            if len(ds) > 1:
                descriptions["Múltiple"] += 1
            if len(set(ds)) == 1:
                descriptions["Duplicado"] += 1
            if len(ds[0]) > 150:
                descriptions[">150 caracteres"] += 1
            if len(ds[0]) < 120:
                descriptions["<120 caracteres"] += 1

        # Keywords
        ks = res.get("meta_keywords", [])
        all_keywords.extend(ks)
        if not ks:
            keywords["Falta"] += 1
        for k in ks:
            keyw_global_tracker[k.strip().lower()] = keyw_global_tracker.get(k.strip().lower(), 0) + 1
        else:
            if len(ks) > 1:
                keywords["Múltiple"] += 1
            if len(set(ks)) == 1:
                keywords["Duplicado"] += 1

    # Recontar duplicados globales
    titles["Duplicado"] = sum(1 for v in title_global_tracker.values() if v > 1)
    descriptions["Duplicado"] = sum(1 for v in desc_global_tracker.values() if v > 1)
    keywords["Duplicado"] = sum(1 for v in keyw_global_tracker.values() if v > 1)

    # Contar encabezados H1
    h1_counts = {"Falta": 0, "Duplicado": 0, ">70 caracteres": 0, "Múltiple": 0}
    h1_tracker = {}
    for res in tecnicos.values():
        h1s = res.get("h1s", [])
        if not h1s:
            h1_counts["Falta"] += 1
        else:
            if len(h1s) > 1:
                h1_counts["Múltiple"] += 1
            if len(set(h1s)) == 1:
                h1_tracker[h1s[0].strip().lower()] = h1_tracker.get(h1s[0].strip().lower(), 0) + 1
            if len(h1s[0]) > 70:
                h1_counts[">70 caracteres"] += 1
    h1_counts["Duplicado"] = sum(1 for v in h1_tracker.values() if v > 1)

    # Mostrar gráficos en dos filas
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown("#### Titles")
        fig, ax = plt.subplots()
        pd.Series(titles).plot(kind="bar", ax=ax, color="#8faadc")
        ax.set_ylabel("Cantidad de URLs")
        st.pyplot(fig)

    with col_meta2:
        st.markdown("#### Meta Descriptions")
        fig, ax = plt.subplots()
        pd.Series(descriptions).plot(kind="bar", ax=ax, color="#fac27b")
        ax.set_ylabel("Cantidad de URLs")
        st.pyplot(fig)

    

    col_meta3, col_meta4 = st.columns(2)
    with col_meta3:
        st.markdown("#### Meta Keywords")
        fig, ax = plt.subplots()
        pd.Series(keywords).plot(kind="bar", ax=ax, color="#d88fa3")
        ax.set_ylabel("Cantidad de URLs")
        st.pyplot(fig)

    with col_meta4:
        st.markdown("#### Encabezados H1")
        fig, ax = plt.subplots()
        pd.Series(h1_counts).plot(kind="bar", ax=ax, color="#94d0cc")
        ax.set_ylabel("Cantidad de URLs")
        st.pyplot(fig)

    

    # 🖼 Evaluación de imágenes
    st.markdown("### 🖼 Evaluación de Imágenes")
    imagenes_unicas = {}
    detalle_imagenes = []
    for res in tecnicos.values():
        for img in res.get("imagenes", []):
            url = img.get("URL")
            if url not in imagenes_unicas:
                imagenes_unicas[url] = {
                    "ALT": img.get("ALT", ""),
                    "Peso": img.get("Peso (bytes)", 0)
                }
                detalle_imagenes.append({
                    "URL": url,
                    "ALT": img.get("ALT", ""),
                    "Peso (bytes)": img.get("Peso (bytes)", 0)
                })

    alt_largos = sum(1 for i in imagenes_unicas.values() if len(i["ALT"]) > 100)
    sin_alt = sum(1 for i in imagenes_unicas.values() if not i["ALT"].strip())
    peso_alto = sum(1 for i in imagenes_unicas.values() if i["Peso"] > 100000)

    imagenes_eval = {
        "Falta ALT": sin_alt,
        "ALT > 100 caracteres": alt_largos,
        "> 100KB": peso_alto
    }

    fig, ax = plt.subplots()
    pd.Series(imagenes_eval).plot(kind="bar", ax=ax, color="#cdb4db")
    ax.set_ylabel("Cantidad de imágenes únicas")
    st.pyplot(fig)

    with st.expander("🔍 Ver detalle de imágenes únicas"):
        df_img = pd.DataFrame(detalle_imagenes)
        st.dataframe(df_img, use_container_width=True)

    # 📦 Análisis de datos estructurados
    st.markdown("### 📦 Datos estructurados")
    tipo_schema = {}
    detalle_schema = {}
    resumen_tecnico = []

    for url, res in tecnicos.items():
        resumen = {
            "URL": url,
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

        tipos_actuales = []
        for schema in res.get("datos_estructurados", []):
            bloques = schema.get("@graph", [schema])
            for item in bloques:
                tipo = item.get("@type", "Sin tipo")
                if isinstance(tipo, list):
                    tipo = "/".join(tipo)
                tipo_schema[tipo] = tipo_schema.get(tipo, 0) + 1
                if tipo not in detalle_schema:
                    detalle_schema[tipo] = []
                detalle_schema[tipo].append((url, item))
                tipos_actuales.append(tipo)

        resumen["Tipos de datos estructurados"] = ", ".join(sorted(set(tipos_actuales))) or "-"
        resumen_tecnico.append(resumen)

    with st.expander("🗂️ Ver tabla resumen técnica por URL"):
        df_resumen = pd.DataFrame(resumen_tecnico)
        st.dataframe(df_resumen, use_container_width=True)

    if tipo_schema:
        tipo_df = pd.Series(tipo_schema).sort_values(ascending=False)
        st.bar_chart(tipo_df)

        for tipo, elementos in detalle_schema.items():
            with st.expander(f"🔍 {tipo} ({len(elementos)})"):
                for url, item in elementos:
                    st.markdown(f"**URL:** {url}")
                    for k, v in item.items():
                        if k != "@type":
                            st.write(f"- **{k}**: {v}")
                    st.markdown("---")
    else:
        st.info("No se encontraron datos estructurados.")

    

    

    

    

    

    

    

    

    

    
