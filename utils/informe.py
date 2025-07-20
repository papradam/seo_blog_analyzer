import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud


def mostrar_informe_resultados():
    st.title("📊 Informe General del Análisis SEO")

    # --- Obtener datos desde url_listado ---
    urls_completadas = [
        u for u in st.session_state.url_listado
        if u.get("analisis_contenido") == "completado"
    ]

    if not urls_completadas:
        st.warning("Aún no hay análisis de contenido disponibles.")
        return

    datos = []
    palabras_clave_totales = []
    detalle_urls = []

    for u in urls_completadas:
        res = u["resultado_seo"]
        datos.append({
            "URL": u["url"],
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"]
        })
        palabras_clave_totales.extend([frase for frase, _ in res["palabras_clave"]])
        detalle_urls.append({
            "URL": u["url"],
            "Legibilidad": res["indice_legibilidad"],
            "Nivel educativo": res["nivel_educativo"],
            "Palabras": res["num_palabras"],
            "Párrafos": res["num_parrafos"],
            "Palabras clave": ", ".join([f"{frase} ({count})" for frase, count in res["palabras_clave"]]) or "-"
        })

    df = pd.DataFrame(datos)

    # --- Métricas generales ---
    st.markdown("### 🧮 Métricas promedio generales")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📖 Legibilidad promedio", f"{df['Legibilidad'].mean():.2f}")
    with col2:
        st.metric("📝 Palabras promedio", f"{df['Palabras'].mean():.0f}")
    with col3:
        st.metric("📄 Párrafos promedio", f"{df['Párrafos'].mean():.0f}")

    # --- Distribuciones gráficas ---
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

    # --- Wordcloud ---
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

    # === ANÁLISIS TÉCNICO ===
    st.title("🛠️ Análisis Técnico")
    tecnicos = [u["resultado_tecnico"] for u in urls_completadas if "resultado_tecnico" in u]

    codigos = []
    robots_list = []
    canonicals_count = {"Falta": 0, "Múltiple": 0}
    resumen_tecnico = []

    for u in urls_completadas:
        t = u.get("resultado_tecnico", {})
        if not t:
            continue

        resumen_tecnico.append({
            "URL": u["url"],
            "Código de estado": t.get("codigo", "-"),
            "Meta Robots": t.get("robots", "-"),
            "Canonical": ", ".join(t.get("canonicals", []) or ["-"]),
            "Title": ", ".join(t.get("titles", []) or ["-"]),
            "Meta descripción": ", ".join(t.get("meta_descriptions", []) or ["-"]),
            "Meta keywords": ", ".join(t.get("meta_keywords", []) or ["-"]),
            "H1": ", ".join(t.get("h1s", []) or ["-"]),
            "Imágenes": ", ".join(sorted(set(img.get("URL", "") for img in t.get("imagenes", [])))) or "-",
            "Tipos de datos estructurados": ", ".join(
                sorted(set(
                    item.get("@type", "Sin tipo") if isinstance(item.get("@type", ""), str)
                    else "/".join(item.get("@type", []))
                    for schema in t.get("datos_estructurados", [])
                    for item in (schema.get("@graph", [schema]) if schema else [])
                ))
            ) or "-"
        })

        codigos.append(t.get("codigo", 0))
        robots_list.append(t.get("robots") or "N/A")
        canonicals = t.get("canonicals", [])
        if not canonicals:
            canonicals_count["Falta"] += 1
        elif len(canonicals) > 1:
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

    with colx3:
        st.markdown("#### Canonicals")
        fig, ax = plt.subplots()
        pd.Series(canonicals_count).plot(kind="bar", ax=ax, color="#d4a5a5")
        ax.set_ylabel("Cantidad de URLs")
        ax.set_title("Tipos de canonicals")
        st.pyplot(fig)

    # --- Tabla técnica final ---
    with st.expander("🗂️ Ver tabla resumen técnica por URL"):
        df_resumen = pd.DataFrame(resumen_tecnico)
        st.dataframe(df_resumen, use_container_width=True)
